"""Genetic Algorithm Optimizer for fleet routing (CVRP).

Implements a GA with Order Crossover (OX), swap/inversion/insertion
mutation, tournament selection with elitism, and stagnation-based
early stopping. Integrates as ``strategy="ga"`` alongside OR-Tools
and Clarke & Wright.

Session 118 — CDC SOTREG v5.0 Module M8.
"""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class GAConfig:
    """Genetic Algorithm configuration parameters."""

    population_size: int = 100
    max_generations: int = 500
    crossover_rate: float = 0.85
    mutation_rate: float = 0.05
    tournament_size: int = 5
    elitism_pct: float = 0.05  # top 5%
    stagnation_limit: int = 50
    seed: int | None = None


@dataclass
class GASolution:
    """Complete solution from the GA solver."""

    routes: list[list[int]]  # depot-bracketed routes
    total_distance: float
    num_vehicles: int
    computation_time_ms: float
    generations_run: int
    best_fitness_history: list[float] = field(default_factory=list)
    early_stopped: bool = False


# ---------------------------------------------------------------------------
# Chromosome encoding
# ---------------------------------------------------------------------------
# A chromosome is a flat permutation of customer indices.
# Routes are decoded by splitting at capacity boundaries.


def encode_chromosome(customers: list[int]) -> list[int]:
    """Create a random permutation of customer indices."""
    perm = list(customers)
    random.shuffle(perm)
    return perm


def decode_chromosome(
    chromosome: list[int],
    demands: list[int],
    vehicle_capacity: int,
    depot_index: int = 0,
) -> list[list[int]]:
    """Decode a flat chromosome into depot-bracketed routes.

    Greedily assigns customers to routes until capacity is reached,
    then starts a new route.

    Args:
        chromosome: Flat permutation of customer indices.
        demands: Demand per node (depot = 0).
        vehicle_capacity: Max demand per vehicle.
        depot_index: Depot node index.

    Returns:
        List of routes, each starting/ending with depot.
    """
    routes: list[list[int]] = []
    current_route: list[int] = []
    current_demand = 0

    for c in chromosome:
        d = demands[c]
        if current_demand + d > vehicle_capacity and current_route:
            routes.append([depot_index] + current_route + [depot_index])
            current_route = [c]
            current_demand = d
        else:
            current_route.append(c)
            current_demand += d

    if current_route:
        routes.append([depot_index] + current_route + [depot_index])

    return routes


# ---------------------------------------------------------------------------
# Fitness function
# ---------------------------------------------------------------------------


def compute_fitness(
    chromosome: list[int],
    distance_matrix: list[list[float]],
    demands: list[int],
    vehicle_capacity: int,
    depot_index: int = 0,
) -> float:
    """Compute fitness (lower is better) = total route distance.

    Includes a penalty for capacity violations to keep the search
    in feasible regions.

    Args:
        chromosome: Flat customer permutation.
        distance_matrix: NxN distance matrix.
        demands: Demand per node.
        vehicle_capacity: Max vehicle capacity.
        depot_index: Depot index.

    Returns:
        Fitness value (total distance + penalties). Lower is better.
    """
    routes = decode_chromosome(chromosome, demands, vehicle_capacity, depot_index)
    total_dist = 0.0
    penalty = 0.0

    for route in routes:
        # Route distance
        for k in range(len(route) - 1):
            total_dist += distance_matrix[route[k]][route[k + 1]]

        # Capacity check (should be satisfied by decode, but penalize violations)
        route_demand = sum(demands[c] for c in route[1:-1])
        if route_demand > vehicle_capacity:
            penalty += (route_demand - vehicle_capacity) * 10000

    return total_dist + penalty


# ---------------------------------------------------------------------------
# Order Crossover (OX)
# ---------------------------------------------------------------------------


def order_crossover(parent1: list[int], parent2: list[int]) -> list[int]:
    """Perform Order Crossover (OX) to produce one offspring.

    1. Select random substring from parent1.
    2. Fill remaining positions from parent2 preserving relative order.
    3. Result is always a valid permutation.

    Args:
        parent1: First parent chromosome.
        parent2: Second parent chromosome.

    Returns:
        Offspring chromosome (valid permutation).
    """
    n = len(parent1)
    if n <= 2:
        return list(parent1)

    # Select crossover points
    cx1 = random.randint(0, n - 2)
    cx2 = random.randint(cx1 + 1, n)

    # Substring from parent1
    substring = parent1[cx1:cx2]
    substring_set = set(substring)

    # Fill remaining from parent2 preserving order
    remaining = [g for g in parent2 if g not in substring_set]

    offspring = remaining[:cx1] + substring + remaining[cx1:]
    return offspring


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------


def swap_mutation(chromosome: list[int]) -> list[int]:
    """Swap two random positions in the chromosome."""
    result = list(chromosome)
    n = len(result)
    if n < 2:
        return result
    i, j = random.sample(range(n), 2)
    result[i], result[j] = result[j], result[i]
    return result


def inversion_mutation(chromosome: list[int]) -> list[int]:
    """Reverse a random contiguous subsequence."""
    result = list(chromosome)
    n = len(result)
    if n < 2:
        return result
    i = random.randint(0, n - 2)
    j = random.randint(i + 1, n)
    result[i:j] = reversed(result[i:j])
    return result


def insertion_mutation(chromosome: list[int]) -> list[int]:
    """Remove a random stop and reinsert at a random position."""
    result = list(chromosome)
    n = len(result)
    if n < 2:
        return result
    idx = random.randint(0, n - 1)
    gene = result.pop(idx)
    new_pos = random.randint(0, len(result))
    result.insert(new_pos, gene)
    return result


def mutate(chromosome: list[int]) -> list[int]:
    """Apply a random mutation operator."""
    op = random.choice([swap_mutation, inversion_mutation, insertion_mutation])
    return op(chromosome)


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def tournament_selection(
    population: list[list[int]],
    fitnesses: list[float],
    tournament_size: int = 5,
) -> list[int]:
    """Select one individual via tournament selection.

    Picks ``tournament_size`` random individuals, returns the one
    with the lowest (best) fitness.

    Args:
        population: List of chromosomes.
        fitnesses: Fitness value per chromosome.
        tournament_size: Number of competitors.

    Returns:
        Selected chromosome.
    """
    n = len(population)
    candidates = random.sample(range(n), min(tournament_size, n))
    best_idx = min(candidates, key=lambda i: fitnesses[i])
    return list(population[best_idx])


# ---------------------------------------------------------------------------
# Main GA solver
# ---------------------------------------------------------------------------


def solve_cvrp_ga(
    distance_matrix: list[list[float]],
    demands: list[int],
    depot_index: int = 0,
    vehicle_capacity: int = 50,
    config: GAConfig | None = None,
) -> GASolution:
    """Solve CVRP using a Genetic Algorithm.

    Args:
        distance_matrix: NxN distance matrix.
        demands: Demand per node (depot = 0).
        depot_index: Index of the depot.
        vehicle_capacity: Max demand per vehicle.
        config: GA configuration. Defaults to GAConfig().

    Returns:
        GASolution with routes, distance, and convergence info.
    """
    if config is None:
        config = GAConfig()

    if config.seed is not None:
        random.seed(config.seed)

    t0 = time.perf_counter()
    n = len(distance_matrix)

    # Edge cases
    customers = [i for i in range(n) if i != depot_index]

    if not customers:
        return GASolution(
            routes=[], total_distance=0.0, num_vehicles=0,
            computation_time_ms=0.0, generations_run=0,
        )

    if len(customers) == 1:
        c = customers[0]
        dist = distance_matrix[depot_index][c] + distance_matrix[c][depot_index]
        return GASolution(
            routes=[[depot_index, c, depot_index]],
            total_distance=dist,
            num_vehicles=1,
            computation_time_ms=(time.perf_counter() - t0) * 1000,
            generations_run=0,
        )

    # --- Initialize population ---
    population: list[list[int]] = []
    for _ in range(config.population_size):
        population.append(encode_chromosome(customers))

    # Compute initial fitnesses
    fitnesses = [
        compute_fitness(chrom, distance_matrix, demands, vehicle_capacity, depot_index)
        for chrom in population
    ]

    best_fitness = min(fitnesses)
    best_idx = fitnesses.index(best_fitness)
    best_chromosome = list(population[best_idx])
    best_fitness_history: list[float] = [best_fitness]
    stagnation_counter = 0

    elite_count = max(1, int(config.population_size * config.elitism_pct))

    # --- Evolve ---
    generations_run = 0
    for gen in range(config.max_generations):
        generations_run = gen + 1

        # Sort by fitness for elitism
        indexed = list(enumerate(fitnesses))
        indexed.sort(key=lambda x: x[1])

        # Elitism: carry over top individuals
        new_population: list[list[int]] = []
        for i in range(elite_count):
            new_population.append(list(population[indexed[i][0]]))

        # Fill rest via crossover and mutation
        while len(new_population) < config.population_size:
            # Selection
            p1 = tournament_selection(population, fitnesses, config.tournament_size)
            p2 = tournament_selection(population, fitnesses, config.tournament_size)

            # Crossover
            if random.random() < config.crossover_rate:
                offspring = order_crossover(p1, p2)
            else:
                offspring = list(p1)

            # Mutation
            if random.random() < config.mutation_rate:
                offspring = mutate(offspring)

            new_population.append(offspring)

        population = new_population[:config.population_size]

        # Recompute fitnesses
        fitnesses = [
            compute_fitness(chrom, distance_matrix, demands, vehicle_capacity, depot_index)
            for chrom in population
        ]

        gen_best = min(fitnesses)
        gen_best_idx = fitnesses.index(gen_best)

        if gen_best < best_fitness:
            best_fitness = gen_best
            best_chromosome = list(population[gen_best_idx])
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        best_fitness_history.append(best_fitness)

        # Early stopping
        if stagnation_counter >= config.stagnation_limit:
            logger.info(
                "GA early stop at gen %d (stagnation %d)",
                generations_run, config.stagnation_limit,
            )
            break

    # Decode best solution
    routes = decode_chromosome(best_chromosome, demands, vehicle_capacity, depot_index)
    total_dist = 0.0
    for route in routes:
        for k in range(len(route) - 1):
            total_dist += distance_matrix[route[k]][route[k + 1]]

    elapsed_ms = (time.perf_counter() - t0) * 1000

    logger.info(
        "GA completed: %d gen, %d routes, %.1f dist, %.1f ms, early_stop=%s",
        generations_run, len(routes), total_dist, elapsed_ms,
        stagnation_counter >= config.stagnation_limit,
    )

    return GASolution(
        routes=routes,
        total_distance=total_dist,
        num_vehicles=len(routes),
        computation_time_ms=elapsed_ms,
        generations_run=generations_run,
        best_fitness_history=best_fitness_history,
        early_stopped=stagnation_counter >= config.stagnation_limit,
    )
