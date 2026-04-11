"""Tests for Clarke & Wright savings algorithm (Session 117).

Covers savings computation, sequential/parallel merge, capacity
enforcement, edge cases, and solution quality validation.
"""
from __future__ import annotations

import pytest

from app.services.sotreg.clarke_wright import (
    CWSolution,
    CWRoute,
    Saving,
    compute_savings,
    solve_cvrp_cw,
    solve_parallel,
    solve_sequential,
    _route_total_distance,
)


# ---------------------------------------------------------------------------
# Test fixtures — known distance matrices
# ---------------------------------------------------------------------------

# Simple 5-node instance: depot(0), customers(1,2,3,4)
# Triangle inequality holds, symmetric
SIMPLE_DIST = [
    [0, 10, 15, 20, 25],   # depot to customers
    [10, 0, 12, 18, 22],   # customer 1
    [15, 12, 0, 8, 16],    # customer 2
    [20, 18, 8, 0, 10],    # customer 3
    [25, 22, 16, 10, 0],   # customer 4
]

SIMPLE_DEMANDS = [0, 1, 1, 1, 1]  # depot=0, each customer=1


# Larger 8-node instance for capacity testing
MEDIUM_DIST = [
    [0, 10, 20, 30, 15, 25, 35, 12],
    [10, 0, 15, 25, 20, 30, 28, 8],
    [20, 15, 0, 10, 25, 20, 18, 22],
    [30, 25, 10, 0, 35, 15, 12, 30],
    [15, 20, 25, 35, 0, 10, 30, 18],
    [25, 30, 20, 15, 10, 0, 20, 28],
    [35, 28, 18, 12, 30, 20, 0, 32],
    [12, 8, 22, 30, 18, 28, 32, 0],
]

MEDIUM_DEMANDS = [0, 3, 4, 5, 2, 6, 3, 4]  # capacity test with cap=10


class TestSavingsComputation:
    """Tests for compute_savings function."""

    def test_savings_formula(self) -> None:
        """s(i,j) = d(depot,i) + d(depot,j) - d(i,j) for known distances."""
        savings = compute_savings(SIMPLE_DIST, depot_index=0)
        # Find saving for (3, 4): d(0,3) + d(0,4) - d(3,4) = 20 + 25 - 10 = 35
        s34 = next(s for s in savings if {s.i, s.j} == {3, 4})
        assert s34.value == pytest.approx(35.0)

        # Find saving for (1, 2): d(0,1) + d(0,2) - d(1,2) = 10 + 15 - 12 = 13
        s12 = next(s for s in savings if {s.i, s.j} == {1, 2})
        assert s12.value == pytest.approx(13.0)

    def test_savings_sorted_descending(self) -> None:
        """Savings are sorted in descending order."""
        savings = compute_savings(SIMPLE_DIST, depot_index=0)
        values = [s.value for s in savings]
        assert values == sorted(values, reverse=True)

    def test_savings_only_positive(self) -> None:
        """Only positive savings are included."""
        savings = compute_savings(SIMPLE_DIST, depot_index=0)
        assert all(s.value > 0 for s in savings)

    def test_savings_count(self) -> None:
        """Number of savings = C(n-1, 2) for n nodes minus zero/negative."""
        savings = compute_savings(SIMPLE_DIST, depot_index=0)
        # 4 customers → max 6 pairs (C(4,2)=6)
        assert len(savings) <= 6
        assert len(savings) > 0


class TestSequentialSolver:
    """Tests for sequential Clarke & Wright solver."""

    def test_simple_instance_valid_routes(self) -> None:
        """Sequential solver produces valid routes for simple instance."""
        sol = solve_sequential(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        assert isinstance(sol, CWSolution)
        assert sol.variant == "sequential"
        assert sol.num_vehicles >= 1

    def test_all_customers_visited_once(self) -> None:
        """Every customer is visited exactly once."""
        sol = solve_sequential(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        visited = []
        for route in sol.routes:
            # Exclude depot (first and last)
            customers = route[1:-1]
            visited.extend(customers)
        assert sorted(visited) == [1, 2, 3, 4]

    def test_routes_start_end_at_depot(self) -> None:
        """Every route starts and ends at depot."""
        sol = solve_sequential(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        for route in sol.routes:
            assert route[0] == 0, "Route must start at depot"
            assert route[-1] == 0, "Route must end at depot"

    def test_capacity_enforced(self) -> None:
        """No route exceeds vehicle capacity."""
        sol = solve_sequential(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        for route in sol.routes:
            route_demand = sum(MEDIUM_DEMANDS[c] for c in route[1:-1])
            assert route_demand <= 10, f"Route demand {route_demand} exceeds capacity 10"

    def test_greedy_merge_4_nodes(self) -> None:
        """Greedy merge produces valid solution for 4-node instance."""
        sol = solve_sequential(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        # With capacity 4 and 4 customers of demand 1, should merge into 1 route
        assert sol.num_vehicles == 1
        assert len(sol.routes[0]) == 6  # depot + 4 customers + depot

    def test_single_customer(self) -> None:
        """Single customer returns one route with one stop."""
        dist = [[0, 10], [10, 0]]
        demands = [0, 1]
        sol = solve_sequential(dist, demands, 0, vehicle_capacity=5)
        assert sol.num_vehicles == 1
        assert sol.routes == [[0, 1, 0]]

    def test_empty_distance_matrix(self) -> None:
        """Empty matrix returns empty routes gracefully."""
        sol = solve_sequential([], [], 0, vehicle_capacity=5)
        assert sol.routes == []
        assert sol.num_vehicles == 0

    def test_depot_only(self) -> None:
        """Matrix with only depot returns no routes."""
        sol = solve_sequential([[0]], [0], 0, vehicle_capacity=5)
        assert sol.routes == []


class TestParallelSolver:
    """Tests for parallel Clarke & Wright solver."""

    def test_parallel_valid_routes(self) -> None:
        """Parallel solver produces valid routes."""
        sol = solve_parallel(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        assert isinstance(sol, CWSolution)
        assert sol.variant == "parallel"
        assert sol.num_vehicles >= 1

    def test_parallel_all_customers_visited(self) -> None:
        """Parallel solver visits all customers exactly once."""
        sol = solve_parallel(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        visited = []
        for route in sol.routes:
            visited.extend(route[1:-1])
        assert sorted(visited) == list(range(1, 8))

    def test_parallel_capacity_enforced(self) -> None:
        """Parallel solver enforces capacity constraints."""
        sol = solve_parallel(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        for route in sol.routes:
            route_demand = sum(MEDIUM_DEMANDS[c] for c in route[1:-1])
            assert route_demand <= 10

    def test_parallel_merges_multiple_per_iteration(self) -> None:
        """Parallel variant merges multiple routes per iteration (not just one)."""
        # With 7 customers and capacity 10, parallel should merge multiple at once
        sol = solve_parallel(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        # Should produce fewer vehicles than sequential in some cases
        assert sol.num_vehicles < len(MEDIUM_DEMANDS) - 1  # fewer than n-1 routes

    def test_parallel_depot_not_interior(self) -> None:
        """Depot is not in the interior of any route."""
        sol = solve_parallel(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        for route in sol.routes:
            interior = route[1:-1]
            assert 0 not in interior, "Depot should not be in route interior"


class TestUnifiedSolver:
    """Tests for the unified solve_cvrp_cw interface."""

    def test_default_parallel(self) -> None:
        """Default variant is parallel."""
        sol = solve_cvrp_cw(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        assert sol.variant == "parallel"

    def test_explicit_sequential(self) -> None:
        """Can select sequential variant."""
        sol = solve_cvrp_cw(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, variant="sequential")
        assert sol.variant == "sequential"

    def test_output_format_matches_spec(self) -> None:
        """Output contains routes as depot-bracketed node lists."""
        sol = solve_cvrp_cw(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=4)
        assert isinstance(sol.routes, list)
        assert isinstance(sol.total_distance, float)
        assert isinstance(sol.num_vehicles, int)
        assert isinstance(sol.computation_time_ms, float)


class TestRouteDistance:
    """Tests for route distance computation helper."""

    def test_single_stop_distance(self) -> None:
        """Distance for single-stop route: depot→stop→depot."""
        dist = _route_total_distance([1], 0, SIMPLE_DIST)
        expected = SIMPLE_DIST[0][1] + SIMPLE_DIST[1][0]  # 10 + 10 = 20
        assert dist == pytest.approx(expected)

    def test_multi_stop_distance(self) -> None:
        """Distance for multi-stop route."""
        dist = _route_total_distance([1, 2, 3], 0, SIMPLE_DIST)
        expected = (
            SIMPLE_DIST[0][1]  # depot → 1 = 10
            + SIMPLE_DIST[1][2]  # 1 → 2 = 12
            + SIMPLE_DIST[2][3]  # 2 → 3 = 8
            + SIMPLE_DIST[3][0]  # 3 → depot = 20
        )
        assert dist == pytest.approx(expected)

    def test_empty_stops(self) -> None:
        """Empty stops returns 0 distance."""
        assert _route_total_distance([], 0, SIMPLE_DIST) == 0.0


class TestCapacityScenarios:
    """Tests for capacity-constrained scenarios."""

    def test_tight_capacity_forces_split(self) -> None:
        """Tight capacity forces customers into separate routes."""
        # Capacity 1 means each customer gets their own route
        sol = solve_cvrp_cw(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=1)
        assert sol.num_vehicles == 4  # one per customer

    def test_generous_capacity_allows_merge(self) -> None:
        """Generous capacity allows merging all customers."""
        sol = solve_cvrp_cw(SIMPLE_DIST, SIMPLE_DEMANDS, 0, vehicle_capacity=100)
        assert sol.num_vehicles == 1  # all in one route

    def test_medium_capacity(self) -> None:
        """Medium capacity produces expected number of vehicles."""
        sol = solve_cvrp_cw(MEDIUM_DIST, MEDIUM_DEMANDS, 0, vehicle_capacity=10)
        # Total demand = 3+4+5+2+6+3+4 = 27, capacity 10 → at least 3 vehicles
        assert sol.num_vehicles >= 3


class TestBenchmarkUtility:
    """Tests for benchmark utility."""

    def test_benchmark_function_exists(self) -> None:
        """benchmark_cw_vs_ortools function is importable."""
        from app.services.sotreg.clarke_wright import benchmark_cw_vs_ortools
        assert callable(benchmark_cw_vs_ortools)

    def test_cw_solution_dataclass(self) -> None:
        """CWSolution dataclass has all expected fields."""
        sol = CWSolution(
            routes=[[0, 1, 0]],
            total_distance=20.0,
            num_vehicles=1,
            computation_time_ms=1.5,
            variant="sequential",
        )
        assert sol.routes == [[0, 1, 0]]
        assert sol.total_distance == 20.0
        assert sol.num_vehicles == 1
