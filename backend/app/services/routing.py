from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from app.services.clustering import ClusterResult
from app.services.osrm_client import (
    MultiRouteResult,
    _haversine_meters,
    osrm_route,
    osrm_route_multi,
    osrm_table,
)
from app.services.vehicle_assignment import AssignmentResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OR-Tools import (graceful degradation)
# ---------------------------------------------------------------------------

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    HAS_ORTOOLS = True
except ImportError:
    HAS_ORTOOLS = False
    logger.warning(
        "OR-Tools is not installed. CVRP solver will fall back to sequential "
        "assignment. Install with: pip install ortools"
    )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

LARGE_DURATION = 999_999  # sentinel for unreachable nodes (seconds)


@dataclass
class RouteStop:
    """A stop along a vehicle route."""

    employee_id: uuid.UUID | None  # None for depot (site)
    lat: float
    lng: float
    is_pickup: bool = True  # True for pickup, False for dropoff (site)
    eta_seconds: float = 0.0  # ETA from route start
    cumulative_distance_meters: float = 0.0


@dataclass
class OptimizedRoute:
    """Result of route optimization for a single vehicle."""

    vehicle_id: uuid.UUID | None
    cluster_index: int
    stops: list[RouteStop]  # ordered stops including depot
    total_distance_meters: float
    total_duration_seconds: float
    polyline: str | None = None
    employee_count: int = 0


@dataclass
class RoutingResult:
    """Full routing optimization result."""

    routes: list[OptimizedRoute] = field(default_factory=list)
    total_distance_km: float = 0.0
    total_duration_minutes: float = 0.0
    avg_occupancy_rate: float = 0.0


# ---------------------------------------------------------------------------
# Distance matrix builder
# ---------------------------------------------------------------------------


async def build_distance_matrix(
    coordinates: list[tuple[float, float]],
    use_osrm: bool = True,
) -> tuple[list[list[float]], list[list[float]]]:
    """Build duration and distance matrices for the given coordinates.

    Args:
        coordinates: List of (lat, lng) tuples.
        use_osrm: Whether to use the OSRM table service. Falls back to
            haversine if False or if OSRM is unavailable.

    Returns:
        A tuple of (duration_matrix, distance_matrix) where durations are
        in seconds and distances are in meters.
    """
    if len(coordinates) < 2:
        return [[0.0]], [[0.0]]

    if use_osrm:
        table_result = await osrm_table(coordinates)
    else:
        from app.services.osrm_client import _haversine_table_fallback

        table_result = _haversine_table_fallback(coordinates)

    duration_matrix = table_result.durations
    distance_matrix = table_result.distances

    # Replace None values with a large sentinel so OR-Tools does not choke
    n = len(coordinates)
    for i in range(n):
        for j in range(n):
            if duration_matrix[i][j] is None:
                duration_matrix[i][j] = LARGE_DURATION
            if distance_matrix[i][j] is None:
                distance_matrix[i][j] = LARGE_DURATION

    return duration_matrix, distance_matrix


# ---------------------------------------------------------------------------
# CVRP solver (pure synchronous, no I/O)
# ---------------------------------------------------------------------------


def solve_cvrp(
    duration_matrix: list[list[float]],
    distance_matrix: list[list[float]],
    demands: list[int],
    vehicle_capacities: list[int],
    depot_index: int = 0,
    max_route_duration_seconds: int = 5400,
) -> list[list[int]]:
    """Solve a Capacitated Vehicle Routing Problem using OR-Tools.

    Args:
        duration_matrix: NxN matrix of travel durations in seconds.
        distance_matrix: NxN matrix of travel distances in meters.
        demands: Demand at each node (1 per employee pickup, 0 for depot).
        vehicle_capacities: Capacity per vehicle.
        depot_index: Index of the depot/site in the matrices.
        max_route_duration_seconds: Maximum route duration (default 90 min).

    Returns:
        A list of routes, where each route is a list of node indices
        (starting and ending at the depot).
    """
    if not HAS_ORTOOLS:
        logger.warning("OR-Tools unavailable, using sequential assignment fallback")
        return _sequential_fallback(demands, vehicle_capacities, depot_index)

    num_nodes = len(duration_matrix)
    num_vehicles = len(vehicle_capacities)

    if num_nodes < 2 or num_vehicles == 0:
        return []

    # ---- OR-Tools setup ----
    manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, depot_index)
    routing = pywrapcp.RoutingModel(manager)

    # Duration callback
    def duration_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(duration_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Time dimension (for max route duration constraint)
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        max_route_duration_seconds,
        True,  # start cumul to zero
        "Time",
    )

    # Demand callback
    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no slack
        vehicle_capacities,
        True,  # start cumul to zero
        "Capacity",
    )

    # Allow dropping nodes if infeasible (large penalty)
    penalty = 100_000
    for node in range(num_nodes):
        if node == depot_index:
            continue
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # Search strategy
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        logger.warning("OR-Tools found no solution, falling back to sequential")
        return _sequential_fallback(demands, vehicle_capacities, depot_index)

    # Extract routes from solution
    routes: list[list[int]] = []
    for vehicle_id in range(num_vehicles):
        route: list[int] = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # add depot at end

        # Only include routes that visit at least one non-depot node
        if len(route) > 2:
            routes.append(route)

    return routes


def _sequential_fallback(
    demands: list[int],
    vehicle_capacities: list[int],
    depot_index: int,
) -> list[list[int]]:
    """Simple sequential assignment when OR-Tools is unavailable.

    Assigns nodes to vehicles in order until each vehicle is full.
    """
    pickup_nodes = [i for i, d in enumerate(demands) if d > 0 and i != depot_index]

    if not pickup_nodes or not vehicle_capacities:
        return []

    routes: list[list[int]] = []
    node_idx = 0

    for capacity in vehicle_capacities:
        if node_idx >= len(pickup_nodes):
            break
        route = [depot_index]
        loaded = 0
        while node_idx < len(pickup_nodes) and loaded < capacity:
            route.append(pickup_nodes[node_idx])
            loaded += demands[pickup_nodes[node_idx]]
            node_idx += 1
        route.append(depot_index)
        if len(route) > 2:
            routes.append(route)

    # If there are remaining nodes, add them to the last route
    if node_idx < len(pickup_nodes) and routes:
        last_route = routes[-1]
        # Remove trailing depot, add remaining, re-add depot
        last_route.pop()
        while node_idx < len(pickup_nodes):
            last_route.append(pickup_nodes[node_idx])
            node_idx += 1
        last_route.append(depot_index)

    return routes


# ---------------------------------------------------------------------------
# Main optimization entry point
# ---------------------------------------------------------------------------


async def optimize_routes(
    clusters: list[ClusterResult],
    assignments: list[AssignmentResult],
    site_lat: float,
    site_lng: float,
    employee_locations: dict[uuid.UUID, tuple[float, float]],
    use_osrm: bool = True,
    max_route_duration_seconds: int = 5400,
) -> RoutingResult:
    """Run full route optimization across all assigned clusters.

    For each assignment with a vehicle, builds a distance matrix, solves the
    CVRP, and fetches the polyline for the resulting route.

    Args:
        clusters: List of cluster results from the clustering engine.
        assignments: List of vehicle assignments from the assignment service.
        site_lat: Latitude of the depot/site.
        site_lng: Longitude of the depot/site.
        employee_locations: Mapping of employee_id to (lat, lng).
        use_osrm: Whether to use OSRM for distance matrix and routes.
        max_route_duration_seconds: Maximum route duration in seconds.

    Returns:
        RoutingResult with optimized routes and aggregate metrics.
    """
    all_routes: list[OptimizedRoute] = []
    total_employees_routed = 0
    total_capacity_used = 0

    for assignment in assignments:
        if assignment.vehicle_id is None:
            logger.info(
                "Skipping cluster_index=%d: no vehicle assigned",
                assignment.cluster_index,
            )
            continue

        if not assignment.employee_ids:
            continue

        # Build coordinate list: depot (index 0) + employee pickups
        coords: list[tuple[float, float]] = [(site_lat, site_lng)]
        employee_order: list[uuid.UUID] = []

        for emp_id in assignment.employee_ids:
            loc = employee_locations.get(emp_id)
            if loc is None:
                logger.warning("No location for employee %s, skipping", emp_id)
                continue
            coords.append(loc)
            employee_order.append(emp_id)

        if len(coords) < 2:
            continue

        # Build distance/duration matrix
        duration_matrix, distance_matrix = await build_distance_matrix(
            coords, use_osrm=use_osrm
        )

        # Demands: depot=0, each employee=1
        demands = [0] + [1] * len(employee_order)
        vehicle_capacities = [len(employee_order)]  # single vehicle for this cluster

        # Solve CVRP
        cvrp_routes = solve_cvrp(
            duration_matrix=duration_matrix,
            distance_matrix=distance_matrix,
            demands=demands,
            vehicle_capacities=vehicle_capacities,
            depot_index=0,
            max_route_duration_seconds=max_route_duration_seconds,
        )

        if not cvrp_routes:
            # Build a simple linear route if CVRP fails
            cvrp_routes = [[0] + list(range(1, len(coords))) + [0]]

        for cvrp_route in cvrp_routes:
            # Build ordered waypoints for polyline fetch
            waypoint_coords = [coords[idx] for idx in cvrp_route]

            # Fetch polyline via OSRM
            polyline: str | None = None
            multi_route: MultiRouteResult | None = None
            if use_osrm and len(waypoint_coords) >= 2:
                multi_route = await osrm_route_multi(waypoint_coords)
                polyline = multi_route.geometry

            # Build stops with ETAs
            stops: list[RouteStop] = []
            cumulative_duration = 0.0
            cumulative_distance = 0.0

            for stop_idx, node_idx in enumerate(cvrp_route):
                if stop_idx > 0:
                    prev_node = cvrp_route[stop_idx - 1]
                    cumulative_duration += duration_matrix[prev_node][node_idx]
                    cumulative_distance += distance_matrix[prev_node][node_idx]

                if node_idx == 0:
                    # Depot stop
                    stops.append(
                        RouteStop(
                            employee_id=None,
                            lat=site_lat,
                            lng=site_lng,
                            is_pickup=False,
                            eta_seconds=cumulative_duration,
                            cumulative_distance_meters=cumulative_distance,
                        )
                    )
                else:
                    emp_idx = node_idx - 1  # offset by depot
                    emp_id = employee_order[emp_idx] if emp_idx < len(employee_order) else None
                    lat, lng = coords[node_idx]
                    stops.append(
                        RouteStop(
                            employee_id=emp_id,
                            lat=lat,
                            lng=lng,
                            is_pickup=True,
                            eta_seconds=cumulative_duration,
                            cumulative_distance_meters=cumulative_distance,
                        )
                    )

            # Count actual employees in this route
            emp_count = sum(1 for s in stops if s.employee_id is not None)

            # Total distance/duration from matrix traversal
            total_dist = cumulative_distance
            total_dur = cumulative_duration

            # Use OSRM totals if available (more accurate)
            if multi_route is not None:
                total_dist = multi_route.distance_meters
                total_dur = multi_route.duration_seconds

            all_routes.append(
                OptimizedRoute(
                    vehicle_id=assignment.vehicle_id,
                    cluster_index=assignment.cluster_index,
                    stops=stops,
                    total_distance_meters=total_dist,
                    total_duration_seconds=total_dur,
                    polyline=polyline,
                    employee_count=emp_count,
                )
            )

            total_employees_routed += emp_count
            total_capacity_used += len(employee_order)

    # Aggregate metrics
    total_distance_km = sum(r.total_distance_meters for r in all_routes) / 1000.0
    total_duration_minutes = sum(r.total_duration_seconds for r in all_routes) / 60.0
    avg_occupancy = (
        total_employees_routed / total_capacity_used
        if total_capacity_used > 0
        else 0.0
    )

    return RoutingResult(
        routes=all_routes,
        total_distance_km=round(total_distance_km, 2),
        total_duration_minutes=round(total_duration_minutes, 2),
        avg_occupancy_rate=round(avg_occupancy, 3),
    )


# ---------------------------------------------------------------------------
# Two-leg route helper (access leg + main leg)
# ---------------------------------------------------------------------------


async def compute_two_leg_route(
    employee_lat: float,
    employee_lng: float,
    meeting_zone_lat: float,
    meeting_zone_lng: float,
    site_lat: float,
    site_lng: float,
    use_osrm: bool = True,
) -> dict:
    """Compute a two-leg route: employee walks to meeting zone, then drives to site.

    Args:
        employee_lat, employee_lng: Employee home coordinates.
        meeting_zone_lat, meeting_zone_lng: Meeting zone coordinates.
        site_lat, site_lng: Destination site coordinates.
        use_osrm: Whether to use OSRM for routing.

    Returns:
        A dict with 'access_leg' (walking) and 'main_leg' (driving) details,
        plus 'total_duration_seconds' and 'total_distance_meters'.
    """
    # Access leg: employee -> meeting zone (walking)
    if use_osrm:
        access = await osrm_route(
            employee_lat, employee_lng,
            meeting_zone_lat, meeting_zone_lng,
            profile="walking",
        )
    else:
        dist = _haversine_meters(
            employee_lat, employee_lng,
            meeting_zone_lat, meeting_zone_lng,
        )
        walking_speed_ms = 4.5 * 1000.0 / 3600.0  # 4.5 km/h
        access_dur = dist / walking_speed_ms
        from app.services.osrm_client import RouteResult

        access = RouteResult(distance_meters=dist, duration_seconds=access_dur)

    # Main leg: meeting zone -> site (driving)
    if use_osrm:
        main = await osrm_route(
            meeting_zone_lat, meeting_zone_lng,
            site_lat, site_lng,
            profile="driving",
        )
    else:
        dist = _haversine_meters(
            meeting_zone_lat, meeting_zone_lng,
            site_lat, site_lng,
        )
        driving_speed_ms = 40_000.0 / 3600.0  # 40 km/h
        main_dur = dist / driving_speed_ms
        from app.services.osrm_client import RouteResult

        main = RouteResult(distance_meters=dist, duration_seconds=main_dur)

    return {
        "access_leg": {
            "mode": "walking",
            "from": {"lat": employee_lat, "lng": employee_lng},
            "to": {"lat": meeting_zone_lat, "lng": meeting_zone_lng},
            "distance_meters": round(access.distance_meters, 1),
            "duration_seconds": round(access.duration_seconds, 1),
            "geometry": access.geometry,
        },
        "main_leg": {
            "mode": "driving",
            "from": {"lat": meeting_zone_lat, "lng": meeting_zone_lng},
            "to": {"lat": site_lat, "lng": site_lng},
            "distance_meters": round(main.distance_meters, 1),
            "duration_seconds": round(main.duration_seconds, 1),
            "geometry": main.geometry,
        },
        "total_duration_seconds": round(
            access.duration_seconds + main.duration_seconds, 1
        ),
        "total_distance_meters": round(
            access.distance_meters + main.distance_meters, 1
        ),
    }
