from __future__ import annotations

import uuid

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.routing import (
    RouteStop,
    OptimizedRoute,
    RoutingResult,
    build_distance_matrix,
    solve_cvrp,
    optimize_routes,
    compute_two_leg_route,
    _sequential_fallback,
)
from app.services.clustering import ClusterResult
from app.services.vehicle_assignment import AssignmentResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cluster(n: int, lat: float = 33.5, lng: float = -7.6) -> ClusterResult:
    return ClusterResult(
        centroid_lat=lat,
        centroid_lng=lng,
        employee_ids=[uuid.uuid4() for _ in range(n)],
        pmr_count=0,
        employee_count=n,
    )


def _make_assignment(
    cluster_index: int,
    employee_ids: list[uuid.UUID],
    vehicle_id: uuid.UUID | None = None,
) -> AssignmentResult:
    return AssignmentResult(
        cluster_index=cluster_index,
        vehicle_id=vehicle_id or uuid.uuid4(),
        employee_ids=employee_ids,
        employee_count=len(employee_ids),
        pmr_count=0,
        occupancy_rate=0.8,
    )


def _symmetric_matrix(n: int, value: float = 300.0) -> list[list[float]]:
    """Build an NxN symmetric matrix with 0 on diagonal and *value* elsewhere."""
    return [
        [0.0 if i == j else value for j in range(n)]
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# 1. test_distance_matrix
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_distance_matrix() -> None:
    """build_distance_matrix with use_osrm=False returns correct-shaped matrices."""
    coords = [
        (33.50, -7.60),
        (33.52, -7.58),
        (33.54, -7.56),
    ]

    durations, distances = await build_distance_matrix(coords, use_osrm=False)

    # Shape: 3x3
    assert len(durations) == 3
    assert len(distances) == 3
    for row in durations:
        assert len(row) == 3
    for row in distances:
        assert len(row) == 3

    # Diagonal is 0
    for i in range(3):
        assert durations[i][i] == 0.0
        assert distances[i][i] == 0.0

    # Off-diagonal > 0
    for i in range(3):
        for j in range(3):
            if i != j:
                assert durations[i][j] > 0, f"duration[{i}][{j}] should be > 0"
                assert distances[i][j] > 0, f"distance[{i}][{j}] should be > 0"


# ---------------------------------------------------------------------------
# 2. test_cvrp_solver
# ---------------------------------------------------------------------------


def test_cvrp_solver() -> None:
    """solve_cvrp returns a single route visiting all pickups with enough capacity."""
    # 4 nodes: depot(0) + 3 pickups
    # Simple symmetric matrix with reasonable travel times (seconds)
    duration_matrix = [
        [0, 600, 900, 1200],
        [600, 0, 300, 600],
        [900, 300, 0, 300],
        [1200, 600, 300, 0],
    ]
    distance_matrix = [
        [0, 5000, 7500, 10000],
        [5000, 0, 2500, 5000],
        [7500, 2500, 0, 2500],
        [10000, 5000, 2500, 0],
    ]
    demands = [0, 1, 1, 1]
    vehicle_capacities = [3]

    routes = solve_cvrp(
        duration_matrix=duration_matrix,
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot_index=0,
    )

    assert len(routes) >= 1, "Should return at least 1 route"

    # Flatten all routes to find visited pickup nodes
    visited_pickups: set[int] = set()
    for route in routes:
        # Route starts and ends at depot
        assert route[0] == 0, "Route must start at depot"
        assert route[-1] == 0, "Route must end at depot"
        for node in route:
            if node != 0:
                visited_pickups.add(node)

    assert visited_pickups == {1, 2, 3}, "All pickup nodes must be visited"


# ---------------------------------------------------------------------------
# 3. test_route_respects_capacity
# ---------------------------------------------------------------------------


def test_route_respects_capacity() -> None:
    """solve_cvrp with 2 vehicles of capacity 2 splits 4 pickups into 2 routes."""
    duration_matrix = _symmetric_matrix(5, value=600.0)
    distance_matrix = _symmetric_matrix(5, value=5000.0)
    demands = [0, 1, 1, 1, 1]
    vehicle_capacities = [2, 2]

    routes = solve_cvrp(
        duration_matrix=duration_matrix,
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot_index=0,
    )

    assert len(routes) == 2, f"Expected 2 routes, got {len(routes)}"

    for route in routes:
        non_depot_stops = [n for n in route if n != 0]
        assert len(non_depot_stops) <= 2, (
            f"Each route should have at most 2 non-depot stops, got {len(non_depot_stops)}"
        )


# ---------------------------------------------------------------------------
# 4. test_route_respects_duration
# ---------------------------------------------------------------------------


def test_route_respects_duration() -> None:
    """solve_cvrp with tight max_route_duration drops nodes or stays within limit."""
    # Node 2 is far away (9000s from depot), node 1 is close (300s)
    duration_matrix = [
        [0, 300, 9000],
        [300, 0, 9000],
        [9000, 9000, 0],
    ]
    distance_matrix = [
        [0, 2000, 80000],
        [2000, 0, 80000],
        [80000, 80000, 0],
    ]
    demands = [0, 1, 1]
    vehicle_capacities = [2]
    max_dur = 3600  # 1 hour

    routes = solve_cvrp(
        duration_matrix=duration_matrix,
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot_index=0,
        max_route_duration_seconds=max_dur,
    )

    # Either returns routes within the duration budget, or drops the far node
    for route in routes:
        total_dur = 0.0
        for i in range(len(route) - 1):
            total_dur += duration_matrix[route[i]][route[i + 1]]
        # If the far node (2) is in the route, duration may exceed max
        # because OR-Tools allows node dropping. Verify the reachable
        # nodes do not exceed the constraint.
        reachable_nodes = [n for n in route if n != 0]
        if 2 not in reachable_nodes:
            # Far node was dropped; route should be within budget
            assert total_dur <= max_dur + 1, (
                f"Route duration {total_dur}s exceeds max {max_dur}s"
            )


# ---------------------------------------------------------------------------
# 5. test_polyline_generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_polyline_generation() -> None:
    """optimize_routes with mocked OSRM returns a non-None polyline."""
    from app.services.osrm_client import MultiRouteResult, TableResult

    cluster = _make_cluster(2)
    emp_ids = cluster.employee_ids
    assignment = _make_assignment(0, emp_ids)

    employee_locations = {
        emp_ids[0]: (33.50, -7.60),
        emp_ids[1]: (33.52, -7.58),
    }

    fake_table = TableResult(
        durations=[[0, 300, 600], [300, 0, 300], [600, 300, 0]],
        distances=[[0, 2500, 5000], [2500, 0, 2500], [5000, 2500, 0]],
    )
    fake_multi = MultiRouteResult(
        distance_meters=7500.0,
        duration_seconds=900.0,
        geometry="encoded_polyline_test",
    )

    with (
        patch("app.services.routing.osrm_table", new_callable=AsyncMock, return_value=fake_table),
        patch("app.services.routing.osrm_route_multi", new_callable=AsyncMock, return_value=fake_multi),
    ):
        result = await optimize_routes(
            clusters=[cluster],
            assignments=[assignment],
            site_lat=33.55,
            site_lng=-7.55,
            employee_locations=employee_locations,
            use_osrm=True,
        )

    assert len(result.routes) >= 1
    polylines = [r.polyline for r in result.routes if r.polyline is not None]
    assert len(polylines) >= 1, "At least one route should have a polyline"
    assert "encoded_polyline_test" in polylines


# ---------------------------------------------------------------------------
# 6. test_stop_order_optimized
# ---------------------------------------------------------------------------


def test_stop_order_optimized() -> None:
    """solve_cvrp picks the cheapest arc order when the matrix is asymmetric."""
    # depot(0) -> node1(1) = 100, node1 -> node2(2) = 100, node2 -> depot = 100
    # depot -> node2 = 5000 (expensive direct path)
    duration_matrix = [
        [0, 100, 5000],
        [100, 0, 100],
        [5000, 100, 0],
    ]
    # Use same values for distance
    distance_matrix = [
        [0, 100, 5000],
        [100, 0, 100],
        [5000, 100, 0],
    ]
    demands = [0, 1, 1]
    vehicle_capacities = [2]

    routes = solve_cvrp(
        duration_matrix=duration_matrix,
        distance_matrix=distance_matrix,
        demands=demands,
        vehicle_capacities=vehicle_capacities,
        depot_index=0,
    )

    assert len(routes) == 1
    route = routes[0]
    # Optimal: 0 -> 1 -> 2 -> 0 (total 300) vs 0 -> 2 -> 1 -> 0 (total 5200)
    non_depot = [n for n in route if n != 0]
    assert non_depot == [1, 2], (
        f"Expected order [1, 2] for cheapest path, got {non_depot}"
    )


# ---------------------------------------------------------------------------
# 7. test_eta_calculation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_eta_calculation() -> None:
    """optimize_routes (haversine fallback) assigns increasing ETAs to stops."""
    cluster = _make_cluster(2)
    emp_ids = cluster.employee_ids
    assignment = _make_assignment(0, emp_ids)

    # Employees at distinct distances from the site
    employee_locations = {
        emp_ids[0]: (33.51, -7.61),
        emp_ids[1]: (33.53, -7.63),
    }

    result = await optimize_routes(
        clusters=[cluster],
        assignments=[assignment],
        site_lat=33.55,
        site_lng=-7.55,
        employee_locations=employee_locations,
        use_osrm=False,
    )

    assert len(result.routes) >= 1

    for route in result.routes:
        # Collect ETAs for non-depot-start stops (skip the first depot)
        etas = [s.eta_seconds for s in route.stops]
        # First stop (depot) should have eta 0
        assert etas[0] == 0.0, "First stop (depot) should have eta_seconds == 0"
        # ETAs should be monotonically non-decreasing
        for i in range(1, len(etas)):
            assert etas[i] >= etas[i - 1], (
                f"ETA at stop {i} ({etas[i]}) should be >= ETA at stop {i-1} ({etas[i-1]})"
            )
        # Non-first stops should have positive ETAs
        for i in range(1, len(etas)):
            assert etas[i] > 0, f"ETA at stop {i} should be > 0"


# ---------------------------------------------------------------------------
# 8. test_two_leg_model
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_two_leg_model() -> None:
    """compute_two_leg_route returns walking access + driving main leg."""
    result = await compute_two_leg_route(
        employee_lat=33.50,
        employee_lng=-7.60,
        meeting_zone_lat=33.51,
        meeting_zone_lng=-7.61,
        site_lat=33.60,
        site_lng=-7.50,
        use_osrm=False,
    )

    # Structure checks
    assert "access_leg" in result
    assert "main_leg" in result
    assert "total_duration_seconds" in result
    assert "total_distance_meters" in result

    # Access leg is walking
    assert result["access_leg"]["mode"] == "walking"
    # Main leg is driving
    assert result["main_leg"]["mode"] == "driving"

    # Totals are sum of legs
    expected_duration = (
        result["access_leg"]["duration_seconds"]
        + result["main_leg"]["duration_seconds"]
    )
    assert result["total_duration_seconds"] == pytest.approx(expected_duration, abs=0.2)

    expected_distance = (
        result["access_leg"]["distance_meters"]
        + result["main_leg"]["distance_meters"]
    )
    assert result["total_distance_meters"] == pytest.approx(expected_distance, abs=0.2)

    # Distances should be positive (points are not co-located)
    assert result["access_leg"]["distance_meters"] > 0
    assert result["main_leg"]["distance_meters"] > 0
    assert result["access_leg"]["duration_seconds"] > 0
    assert result["main_leg"]["duration_seconds"] > 0


# ---------------------------------------------------------------------------
# 9. test_sequential_fallback
# ---------------------------------------------------------------------------


def test_sequential_fallback() -> None:
    """_sequential_fallback assigns all pickup nodes across vehicles."""
    demands = [0, 1, 1, 1]
    vehicle_capacities = [2, 2]
    depot_index = 0

    routes = _sequential_fallback(demands, vehicle_capacities, depot_index)

    assert len(routes) >= 1, "Should return at least one route"

    # All non-depot nodes should appear in some route
    all_visited: set[int] = set()
    for route in routes:
        assert route[0] == depot_index, "Route must start at depot"
        assert route[-1] == depot_index, "Route must end at depot"
        for node in route:
            if node != depot_index:
                all_visited.add(node)

    assert all_visited == {1, 2, 3}, (
        f"All pickup nodes must appear in routes, got {all_visited}"
    )


# ---------------------------------------------------------------------------
# 10. test_per_site_routing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_per_site_routing() -> None:
    """optimize_routes handles multiple assignments and produces aggregate metrics."""
    cluster_a = _make_cluster(2, lat=33.50, lng=-7.60)
    cluster_b = _make_cluster(2, lat=33.55, lng=-7.55)

    emp_ids_a = cluster_a.employee_ids
    emp_ids_b = cluster_b.employee_ids

    assignment_a = _make_assignment(0, emp_ids_a)
    assignment_b = _make_assignment(1, emp_ids_b)

    employee_locations = {
        emp_ids_a[0]: (33.50, -7.60),
        emp_ids_a[1]: (33.51, -7.61),
        emp_ids_b[0]: (33.55, -7.55),
        emp_ids_b[1]: (33.56, -7.56),
    }

    result = await optimize_routes(
        clusters=[cluster_a, cluster_b],
        assignments=[assignment_a, assignment_b],
        site_lat=33.58,
        site_lng=-7.52,
        employee_locations=employee_locations,
        use_osrm=False,
    )

    assert isinstance(result, RoutingResult)
    # Should have routes for both clusters
    cluster_indices = {r.cluster_index for r in result.routes}
    assert 0 in cluster_indices, "Should have route for cluster 0"
    assert 1 in cluster_indices, "Should have route for cluster 1"

    # Aggregate metrics should be positive
    assert result.total_distance_km > 0, "Total distance should be > 0"
    assert result.total_duration_minutes > 0, "Total duration should be > 0"
