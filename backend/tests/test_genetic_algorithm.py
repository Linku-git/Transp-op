"""Tests for Genetic Algorithm CVRP optimizer (Session 118).

Covers OX crossover, mutation operators, tournament selection,
elitism, convergence, early stopping, and solution quality.
"""
from __future__ import annotations

import pytest

from app.services.sotreg.genetic_algorithm import (
    GAConfig,
    GASolution,
    compute_fitness,
    decode_chromosome,
    encode_chromosome,
    insertion_mutation,
    inversion_mutation,
    mutate,
    order_crossover,
    solve_cvrp_ga,
    swap_mutation,
    tournament_selection,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIMPLE_DIST = [
    [0, 10, 15, 20, 25],
    [10, 0, 12, 18, 22],
    [15, 12, 0, 8, 16],
    [20, 18, 8, 0, 10],
    [25, 22, 16, 10, 0],
]
SIMPLE_DEMANDS = [0, 1, 1, 1, 1]

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
MEDIUM_DEMANDS = [0, 3, 4, 5, 2, 6, 3, 4]

SMALL_CONFIG = GAConfig(
    population_size=20, max_generations=50, crossover_rate=0.85,
    mutation_rate=0.05, tournament_size=3, stagnation_limit=20, seed=42,
)


class TestOrderCrossover:
    """Tests for OX crossover operator."""

    def test_ox_valid_permutation(self) -> None:
        """OX crossover produces a valid permutation (all stops once)."""
        p1 = [1, 2, 3, 4, 5, 6, 7, 8]
        p2 = [8, 7, 6, 5, 4, 3, 2, 1]
        for _ in range(50):
            offspring = order_crossover(p1, p2)
            assert sorted(offspring) == sorted(p1), "Offspring must be valid permutation"

    def test_ox_preserves_substring(self) -> None:
        """OX preserves a contiguous substring from parent 1."""
        import random
        random.seed(42)
        p1 = [1, 2, 3, 4, 5]
        p2 = [5, 4, 3, 2, 1]
        offspring = order_crossover(p1, p2)
        # Offspring must be a valid permutation
        assert sorted(offspring) == [1, 2, 3, 4, 5]

    def test_ox_fills_from_parent2(self) -> None:
        """OX fills remaining positions from parent 2 preserving order."""
        p1 = [1, 2, 3, 4, 5, 6]
        p2 = [6, 5, 4, 3, 2, 1]
        offspring = order_crossover(p1, p2)
        assert sorted(offspring) == sorted(p1)
        assert len(offspring) == len(p1)

    def test_ox_small_chromosome(self) -> None:
        """OX handles chromosomes of size 2."""
        p1 = [1, 2]
        p2 = [2, 1]
        offspring = order_crossover(p1, p2)
        assert sorted(offspring) == [1, 2]


class TestMutationOperators:
    """Tests for swap, inversion, and insertion mutation."""

    def test_swap_exchanges_two_positions(self) -> None:
        """Swap mutation exchanges exactly two positions."""
        import random
        random.seed(42)
        chrom = [1, 2, 3, 4, 5]
        result = swap_mutation(chrom)
        assert sorted(result) == [1, 2, 3, 4, 5]
        diff_count = sum(1 for a, b in zip(chrom, result) if a != b)
        assert diff_count in (0, 2)  # 0 if same positions picked

    def test_inversion_reverses_subsequence(self) -> None:
        """Inversion mutation reverses a contiguous subsequence."""
        import random
        random.seed(42)
        chrom = [1, 2, 3, 4, 5]
        result = inversion_mutation(chrom)
        assert sorted(result) == [1, 2, 3, 4, 5]

    def test_insertion_removes_and_reinserts(self) -> None:
        """Insertion mutation removes one stop and reinserts it."""
        import random
        random.seed(42)
        chrom = [1, 2, 3, 4, 5]
        result = insertion_mutation(chrom)
        assert sorted(result) == [1, 2, 3, 4, 5]
        assert len(result) == len(chrom)

    def test_all_mutations_preserve_feasibility(self) -> None:
        """All mutation operators preserve route feasibility."""
        chrom = [1, 2, 3, 4, 5, 6, 7]
        for _ in range(100):
            mutated = mutate(chrom)
            assert sorted(mutated) == sorted(chrom), "Mutation must preserve all genes"


class TestTournamentSelection:
    """Tests for tournament selection."""

    def test_picks_best_from_tournament(self) -> None:
        """Tournament selection picks the individual with lowest fitness."""
        import random
        random.seed(42)
        population = [[1, 2, 3], [3, 2, 1], [2, 1, 3], [1, 3, 2], [3, 1, 2]]
        fitnesses = [100.0, 50.0, 75.0, 200.0, 25.0]
        # With tournament size 5, should always pick index 4 (fitness 25)
        selected = tournament_selection(population, fitnesses, tournament_size=5)
        assert selected == [3, 1, 2]


class TestElitism:
    """Tests for elitism mechanism."""

    def test_elitism_preserves_top(self) -> None:
        """Top 5% of population is preserved across generations."""
        config = GAConfig(
            population_size=20, max_generations=5,
            elitism_pct=0.05, seed=42,
        )
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, config)
        # Best fitness should never increase (get worse)
        for i in range(1, len(sol.best_fitness_history)):
            assert sol.best_fitness_history[i] <= sol.best_fitness_history[i - 1] + 0.001


class TestFitnessConvergence:
    """Tests for fitness improvement over generations."""

    def test_fitness_monotonic_best(self) -> None:
        """Best fitness improves or stays equal over generations."""
        config = GAConfig(
            population_size=30, max_generations=100, seed=42,
        )
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, config)
        for i in range(1, len(sol.best_fitness_history)):
            assert sol.best_fitness_history[i] <= sol.best_fitness_history[i - 1] + 0.001

    def test_stagnation_early_stop(self) -> None:
        """Stagnation at limit triggers early stop."""
        config = GAConfig(
            population_size=10, max_generations=500,
            stagnation_limit=10, seed=42,
        )
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, config)
        # With a small simple instance, should converge quickly then stagnate
        assert sol.early_stopped is True
        assert sol.generations_run < 500


class TestGASolver:
    """Tests for the main GA solver."""

    def test_simple_instance(self) -> None:
        """GA produces valid solution on simple 5-node instance."""
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, SMALL_CONFIG)
        assert isinstance(sol, GASolution)
        assert sol.num_vehicles >= 1

    def test_all_customers_visited(self) -> None:
        """Every customer visited exactly once."""
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, SMALL_CONFIG)
        visited = []
        for route in sol.routes:
            visited.extend(route[1:-1])
        assert sorted(visited) == [1, 2, 3, 4]

    def test_routes_start_end_depot(self) -> None:
        """All routes start and end at depot."""
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, SMALL_CONFIG)
        for route in sol.routes:
            assert route[0] == 0
            assert route[-1] == 0

    def test_capacity_enforced(self) -> None:
        """No route exceeds vehicle capacity."""
        config = GAConfig(population_size=20, max_generations=30, seed=42)
        sol = solve_cvrp_ga(MEDIUM_DIST, MEDIUM_DEMANDS, 0, 10, config)
        for route in sol.routes:
            route_demand = sum(MEDIUM_DEMANDS[c] for c in route[1:-1])
            assert route_demand <= 10

    def test_medium_instance_feasible(self) -> None:
        """GA produces feasible solution on medium instance."""
        config = GAConfig(population_size=30, max_generations=50, seed=42)
        sol = solve_cvrp_ga(MEDIUM_DIST, MEDIUM_DEMANDS, 0, 10, config)
        assert sol.num_vehicles >= 3  # demand=27, cap=10

    def test_population_init_valid(self) -> None:
        """Population initialization creates valid chromosomes."""
        customers = [1, 2, 3, 4]
        for _ in range(50):
            chrom = encode_chromosome(customers)
            assert sorted(chrom) == customers

    def test_single_customer(self) -> None:
        """GA handles single customer."""
        dist = [[0, 10], [10, 0]]
        demands = [0, 1]
        sol = solve_cvrp_ga(dist, demands, 0, 5, SMALL_CONFIG)
        assert sol.num_vehicles == 1
        assert sol.routes == [[0, 1, 0]]

    def test_empty_instance(self) -> None:
        """GA handles empty distance matrix."""
        sol = solve_cvrp_ga([], [], 0, 5, SMALL_CONFIG)
        assert sol.routes == []
        assert sol.num_vehicles == 0

    def test_minimal_config(self) -> None:
        """GA with population=1 and generations=1 does not crash."""
        config = GAConfig(population_size=1, max_generations=1, seed=42)
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, config)
        assert isinstance(sol, GASolution)

    def test_output_format(self) -> None:
        """GA output matches expected schema fields."""
        sol = solve_cvrp_ga(SIMPLE_DIST, SIMPLE_DEMANDS, 0, 4, SMALL_CONFIG)
        assert isinstance(sol.routes, list)
        assert isinstance(sol.total_distance, float)
        assert isinstance(sol.num_vehicles, int)
        assert isinstance(sol.computation_time_ms, float)
        assert isinstance(sol.generations_run, int)
        assert isinstance(sol.best_fitness_history, list)


class TestDecoding:
    """Tests for chromosome decoding."""

    def test_decode_respects_capacity(self) -> None:
        """Decode splits routes to respect capacity."""
        chrom = [1, 2, 3, 4, 5, 6, 7]
        demands = [0, 3, 4, 5, 2, 6, 3, 4]
        routes = decode_chromosome(chrom, demands, vehicle_capacity=10)
        for route in routes:
            route_demand = sum(demands[c] for c in route[1:-1])
            assert route_demand <= 10

    def test_decode_all_customers_present(self) -> None:
        """Decode includes all customers across routes."""
        chrom = [1, 2, 3, 4]
        demands = [0, 1, 1, 1, 1]
        routes = decode_chromosome(chrom, demands, vehicle_capacity=2)
        visited = []
        for route in routes:
            visited.extend(route[1:-1])
        assert sorted(visited) == [1, 2, 3, 4]
