"""Clarke & Wright Savings Algorithm — alternative CVRP solver.

Implements the Clarke & Wright (1964) savings heuristic for the
Capacitated Vehicle Routing Problem (CVRP), with both sequential
and parallel merge variants.

Session 117 — CDC SOTREG v5.0 Module M8.

Reference:
    Clarke, G. & Wright, J.W. (1964). Scheduling of Vehicles from a
    Central Depot to a Number of Delivery Points. Operations Research,
    12(4), 568-581.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Saving:
    """A savings value for merging two customers into one route."""

    i: int  # customer index
    j: int  # customer index
    value: float  # s(i,j) = d(depot,i) + d(depot,j) - d(i,j)


@dataclass
class CWRoute:
    """A route in the Clarke & Wright solution."""

    stops: list[int] = field(default_factory=list)
    demand: int = 0
    distance: float = 0.0

    @property
    def first(self) -> int | None:
        """First customer (not depot) in the route."""
        return self.stops[0] if self.stops else None

    @property
    def last(self) -> int | None:
        """Last customer (not depot) in the route."""
        return self.stops[-1] if self.stops else None


@dataclass
class CWSolution:
    """Complete solution from Clarke & Wright solver."""

    routes: list[list[int]]  # list of routes, each a list of node indices (incl depot)
    total_distance: float
    num_vehicles: int
    computation_time_ms: float
    variant: str  # "sequential" or "parallel"


# ---------------------------------------------------------------------------
# Savings computation
# ---------------------------------------------------------------------------


def compute_savings(
    distance_matrix: list[list[float]],
    depot_index: int = 0,
) -> list[Saving]:
    """Compute pairwise savings for all customer pairs.

    The saving of merging customers i and j is::

        s(i,j) = d(depot, i) + d(depot, j) - d(i, j)

    A higher saving means merging i and j into one route saves more
    distance compared to serving them on separate routes.

    Args:
        distance_matrix: NxN distance matrix (meters or km).
        depot_index: Index of the depot node.

    Returns:
        List of Saving objects sorted by value descending.
    """
    n = len(distance_matrix)
    customers = [i for i in range(n) if i != depot_index]
    savings: list[Saving] = []

    for idx_a, i in enumerate(customers):
        for j in customers[idx_a + 1:]:
            s_val = (
                distance_matrix[depot_index][i]
                + distance_matrix[depot_index][j]
                - distance_matrix[i][j]
            )
            if s_val > 0:
                savings.append(Saving(i=i, j=j, value=s_val))

    savings.sort(key=lambda s: s.value, reverse=True)
    return savings


# ---------------------------------------------------------------------------
# Sequential merge
# ---------------------------------------------------------------------------


def _route_total_distance(
    stops: list[int],
    depot_index: int,
    distance_matrix: list[list[float]],
) -> float:
    """Compute total distance for a route including depot legs."""
    if not stops:
        return 0.0
    d = distance_matrix[depot_index][stops[0]]
    for k in range(len(stops) - 1):
        d += distance_matrix[stops[k]][stops[k + 1]]
    d += distance_matrix[stops[-1]][depot_index]
    return d


def solve_sequential(
    distance_matrix: list[list[float]],
    demands: list[int],
    depot_index: int = 0,
    vehicle_capacity: int = 50,
) -> CWSolution:
    """Solve CVRP using the sequential Clarke & Wright savings heuristic.

    Iterates through savings in descending order. For each saving (i, j),
    attempts to merge the routes containing i and j if:
      - i is at the end of its route and j is at the start of its route
        (or vice versa)
      - The combined demand does not exceed vehicle capacity

    Args:
        distance_matrix: NxN distance matrix.
        demands: Demand per node (depot demand should be 0).
        depot_index: Index of the depot.
        vehicle_capacity: Maximum capacity per vehicle.

    Returns:
        CWSolution with routes, distances, and metadata.
    """
    t0 = time.perf_counter()
    n = len(distance_matrix)

    if n <= 1:
        return CWSolution(
            routes=[], total_distance=0.0, num_vehicles=0,
            computation_time_ms=0.0, variant="sequential",
        )

    customers = [i for i in range(n) if i != depot_index]

    if not customers:
        return CWSolution(
            routes=[], total_distance=0.0, num_vehicles=0,
            computation_time_ms=0.0, variant="sequential",
        )

    # Initialize: one route per customer
    routes: list[CWRoute] = []
    customer_route: dict[int, int] = {}  # customer -> route index

    for c in customers:
        idx = len(routes)
        routes.append(CWRoute(
            stops=[c],
            demand=demands[c],
            distance=distance_matrix[depot_index][c] + distance_matrix[c][depot_index],
        ))
        customer_route[c] = idx

    # Compute and sort savings
    savings = compute_savings(distance_matrix, depot_index)

    # Greedy merge
    for s in savings:
        ri = customer_route.get(s.i)
        rj = customer_route.get(s.j)

        if ri is None or rj is None or ri == rj:
            continue

        route_i = routes[ri]
        route_j = routes[rj]

        # Check capacity
        combined_demand = route_i.demand + route_j.demand
        if combined_demand > vehicle_capacity:
            continue

        # Check that i and j are at route endpoints (terminals)
        # Case 1: i is last of route_i, j is first of route_j → append
        if route_i.last == s.i and route_j.first == s.j:
            merged_stops = route_i.stops + route_j.stops
        # Case 2: j is last of route_j, i is first of route_i → append
        elif route_j.last == s.j and route_i.first == s.i:
            merged_stops = route_j.stops + route_i.stops
        # Case 3: both at end → reverse route_j
        elif route_i.last == s.i and route_j.last == s.j:
            merged_stops = route_i.stops + list(reversed(route_j.stops))
        # Case 4: both at front → reverse route_i
        elif route_i.first == s.i and route_j.first == s.j:
            merged_stops = list(reversed(route_i.stops)) + route_j.stops
        else:
            continue

        # Perform merge
        new_distance = _route_total_distance(merged_stops, depot_index, distance_matrix)
        route_i.stops = merged_stops
        route_i.demand = combined_demand
        route_i.distance = new_distance

        # Mark route_j as empty
        route_j.stops = []
        route_j.demand = 0
        route_j.distance = 0.0

        # Update customer-route mapping
        for c in merged_stops:
            customer_route[c] = ri

    # Collect non-empty routes with depot
    result_routes: list[list[int]] = []
    total_dist = 0.0
    for route in routes:
        if route.stops:
            full_route = [depot_index] + route.stops + [depot_index]
            result_routes.append(full_route)
            total_dist += route.distance

    elapsed_ms = (time.perf_counter() - t0) * 1000

    logger.info(
        "CW sequential: %d routes, %.1f total dist, %.1f ms",
        len(result_routes), total_dist, elapsed_ms,
    )

    return CWSolution(
        routes=result_routes,
        total_distance=total_dist,
        num_vehicles=len(result_routes),
        computation_time_ms=elapsed_ms,
        variant="sequential",
    )


# ---------------------------------------------------------------------------
# Parallel merge variant
# ---------------------------------------------------------------------------


def solve_parallel(
    distance_matrix: list[list[float]],
    demands: list[int],
    depot_index: int = 0,
    vehicle_capacity: int = 50,
) -> CWSolution:
    """Solve CVRP using the parallel Clarke & Wright savings heuristic.

    Unlike the sequential variant, the parallel variant considers multiple
    non-conflicting merges per iteration, selecting the best set of merges
    that don't share routes.

    Args:
        distance_matrix: NxN distance matrix.
        demands: Demand per node.
        depot_index: Index of the depot.
        vehicle_capacity: Maximum capacity per vehicle.

    Returns:
        CWSolution with routes, distances, and metadata.
    """
    t0 = time.perf_counter()
    n = len(distance_matrix)

    if n <= 1:
        return CWSolution(
            routes=[], total_distance=0.0, num_vehicles=0,
            computation_time_ms=0.0, variant="parallel",
        )

    customers = [i for i in range(n) if i != depot_index]
    if not customers:
        return CWSolution(
            routes=[], total_distance=0.0, num_vehicles=0,
            computation_time_ms=0.0, variant="parallel",
        )

    # Initialize: one route per customer
    routes: list[CWRoute] = []
    customer_route: dict[int, int] = {}

    for c in customers:
        idx = len(routes)
        routes.append(CWRoute(
            stops=[c],
            demand=demands[c],
            distance=distance_matrix[depot_index][c] + distance_matrix[c][depot_index],
        ))
        customer_route[c] = idx

    savings = compute_savings(distance_matrix, depot_index)

    # Parallel: process savings in rounds, merging multiple non-conflicting
    merged_any = True
    while merged_any:
        merged_any = False
        merged_routes_this_round: set[int] = set()

        for s in savings:
            ri = customer_route.get(s.i)
            rj = customer_route.get(s.j)

            if ri is None or rj is None or ri == rj:
                continue

            # Skip if either route already merged this round
            if ri in merged_routes_this_round or rj in merged_routes_this_round:
                continue

            route_i = routes[ri]
            route_j = routes[rj]

            if not route_i.stops or not route_j.stops:
                continue

            combined_demand = route_i.demand + route_j.demand
            if combined_demand > vehicle_capacity:
                continue

            # Check terminals
            if route_i.last == s.i and route_j.first == s.j:
                merged_stops = route_i.stops + route_j.stops
            elif route_j.last == s.j and route_i.first == s.i:
                merged_stops = route_j.stops + route_i.stops
            elif route_i.last == s.i and route_j.last == s.j:
                merged_stops = route_i.stops + list(reversed(route_j.stops))
            elif route_i.first == s.i and route_j.first == s.j:
                merged_stops = list(reversed(route_i.stops)) + route_j.stops
            else:
                continue

            # Merge
            new_distance = _route_total_distance(merged_stops, depot_index, distance_matrix)
            route_i.stops = merged_stops
            route_i.demand = combined_demand
            route_i.distance = new_distance

            route_j.stops = []
            route_j.demand = 0
            route_j.distance = 0.0

            for c in merged_stops:
                customer_route[c] = ri

            merged_routes_this_round.add(ri)
            merged_routes_this_round.add(rj)
            merged_any = True

    # Collect results
    result_routes: list[list[int]] = []
    total_dist = 0.0
    for route in routes:
        if route.stops:
            full_route = [depot_index] + route.stops + [depot_index]
            result_routes.append(full_route)
            total_dist += route.distance

    elapsed_ms = (time.perf_counter() - t0) * 1000

    logger.info(
        "CW parallel: %d routes, %.1f total dist, %.1f ms",
        len(result_routes), total_dist, elapsed_ms,
    )

    return CWSolution(
        routes=result_routes,
        total_distance=total_dist,
        num_vehicles=len(result_routes),
        computation_time_ms=elapsed_ms,
        variant="parallel",
    )


# ---------------------------------------------------------------------------
# Unified solver interface
# ---------------------------------------------------------------------------


def solve_cvrp_cw(
    distance_matrix: list[list[float]],
    demands: list[int],
    depot_index: int = 0,
    vehicle_capacity: int = 50,
    variant: str = "parallel",
) -> CWSolution:
    """Solve CVRP using Clarke & Wright savings algorithm.

    This is the main entry point for the CW solver, matching the
    interface expected by the routing pipeline.

    Args:
        distance_matrix: NxN distance matrix (meters).
        demands: Demand per node (depot = 0).
        depot_index: Index of the depot node.
        vehicle_capacity: Maximum demand per vehicle.
        variant: ``"sequential"`` or ``"parallel"`` (default).

    Returns:
        CWSolution with routes in depot-bracketed format.
    """
    if variant == "sequential":
        return solve_sequential(
            distance_matrix, demands, depot_index, vehicle_capacity,
        )
    return solve_parallel(
        distance_matrix, demands, depot_index, vehicle_capacity,
    )


# ---------------------------------------------------------------------------
# Benchmark utility
# ---------------------------------------------------------------------------


def benchmark_cw_vs_ortools(
    distance_matrix: list[list[float]],
    duration_matrix: list[list[float]],
    demands: list[int],
    vehicle_capacity: int,
    depot_index: int = 0,
) -> dict:
    """Run both CW and OR-Tools solvers and compare results.

    Args:
        distance_matrix: NxN distance matrix.
        duration_matrix: NxN duration matrix (for OR-Tools).
        demands: Demand per node.
        vehicle_capacity: Vehicle capacity.
        depot_index: Depot index.

    Returns:
        Dict with comparison metrics.
    """
    # CW solve
    cw_result = solve_cvrp_cw(
        distance_matrix, demands, depot_index, vehicle_capacity,
    )

    # OR-Tools solve
    ortools_routes: list[list[int]] = []
    ortools_dist = 0.0
    ortools_time_ms = 0.0

    try:
        from app.services.routing import solve_cvrp
        t0 = time.perf_counter()
        ortools_routes = solve_cvrp(
            duration_matrix=duration_matrix,
            distance_matrix=distance_matrix,
            demands=demands,
            vehicle_capacities=[vehicle_capacity] * len(demands),
            depot_index=depot_index,
        )
        ortools_time_ms = (time.perf_counter() - t0) * 1000

        for route in ortools_routes:
            for k in range(len(route) - 1):
                ortools_dist += distance_matrix[route[k]][route[k + 1]]
    except Exception as exc:
        logger.warning("OR-Tools benchmark failed: %s", exc)

    # Compute gap
    gap_pct = 0.0
    if ortools_dist > 0:
        gap_pct = ((cw_result.total_distance - ortools_dist) / ortools_dist) * 100

    result = {
        "cw_distance": cw_result.total_distance,
        "cw_vehicles": cw_result.num_vehicles,
        "cw_time_ms": cw_result.computation_time_ms,
        "cw_variant": cw_result.variant,
        "ortools_distance": ortools_dist,
        "ortools_vehicles": len(ortools_routes),
        "ortools_time_ms": ortools_time_ms,
        "gap_pct": round(gap_pct, 2),
        "n_customers": len(demands) - 1,
    }

    logger.info(
        "Benchmark: CW=%.1f (%d veh, %.1f ms) vs OR-Tools=%.1f (%d veh, %.1f ms), gap=%.1f%%",
        cw_result.total_distance, cw_result.num_vehicles, cw_result.computation_time_ms,
        ortools_dist, len(ortools_routes), ortools_time_ms,
        gap_pct,
    )

    return result
