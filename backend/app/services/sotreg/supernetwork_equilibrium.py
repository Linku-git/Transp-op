from __future__ import annotations

import logging
from collections import defaultdict

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MAX_ITERATIONS = 1000
DEFAULT_TOLERANCE = 1e-6

# BPR (Bureau of Public Roads) default parameters
BPR_ALPHA = 0.15
BPR_BETA = 4.0


# ---------------------------------------------------------------------------
# BPR link cost function
# ---------------------------------------------------------------------------

def _link_cost_function(
    flow: float,
    free_flow_cost: float,
    capacity: float,
    alpha: float = BPR_ALPHA,
    beta: float = BPR_BETA,
) -> float:
    """BPR (Bureau of Public Roads) link cost function.

    Formula::

        c(f) = c0 * (1 + alpha * (f / capacity) ^ beta)

    This is the standard volume-delay function used in traffic assignment
    models worldwide.  Default parameters ``alpha=0.15``, ``beta=4.0``
    follow the original BPR specification.

    Args:
        flow: Current flow on the link (vehicles/hour or equivalent).
        free_flow_cost: Free-flow travel cost (time or generalised cost).
            Must be > 0.
        capacity: Link capacity.  Must be > 0.
        alpha: BPR alpha parameter (default 0.15).
        beta: BPR beta parameter (default 4.0).

    Returns:
        Link cost at the given flow level.

    Raises:
        ValueError: If *free_flow_cost* or *capacity* is non-positive.
    """
    if free_flow_cost <= 0:
        raise ValueError(
            f"free_flow_cost must be positive, got {free_flow_cost}"
        )
    if capacity <= 0:
        raise ValueError(f"capacity must be positive, got {capacity}")

    if flow <= 0:
        return free_flow_cost

    ratio = flow / capacity
    return free_flow_cost * (1.0 + alpha * (ratio ** beta))


# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------

def _build_adjacency(
    links: list[dict],
    n_nodes: int,
) -> dict[int, list[tuple[int, int]]]:
    """Build adjacency list mapping node -> [(neighbour, link_index), ...].

    Args:
        links: List of link dicts with ``from_node`` and ``to_node``.
        n_nodes: Total number of nodes in the network.

    Returns:
        Dict keyed by node index with list of (neighbour, link_index) tuples.
    """
    adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for idx, link in enumerate(links):
        adj[link["from_node"]].append((link["to_node"], idx))
    return adj


def _dijkstra(
    adj: dict[int, list[tuple[int, int]]],
    costs: np.ndarray,
    origin: int,
    n_nodes: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Dijkstra's shortest path from a single origin.

    Args:
        adj: Adjacency list from :func:`_build_adjacency`.
        costs: Current link costs (array of length *n_links*).
        origin: Source node index.
        n_nodes: Total number of nodes.

    Returns:
        Tuple of (dist, pred) where:
        - ``dist[v]`` is the shortest-path cost from *origin* to *v*
        - ``pred[v]`` is the link index on the shortest path to *v*
          (or -1 if unreachable / origin)
    """
    INF = 1e18
    dist = np.full(n_nodes, INF)
    pred = np.full(n_nodes, -1, dtype=np.int64)
    visited = np.zeros(n_nodes, dtype=bool)

    dist[origin] = 0.0

    for _ in range(n_nodes):
        # Find unvisited node with minimum distance
        u = -1
        u_dist = INF
        for v in range(n_nodes):
            if not visited[v] and dist[v] < u_dist:
                u = v
                u_dist = dist[v]
        if u == -1:
            break
        visited[u] = True

        for neighbour, link_idx in adj.get(u, []):
            new_dist = dist[u] + costs[link_idx]
            if new_dist < dist[neighbour]:
                dist[neighbour] = new_dist
                pred[neighbour] = link_idx

    return dist, pred


def _trace_path(
    pred: np.ndarray,
    links: list[dict],
    origin: int,
    destination: int,
) -> list[int]:
    """Trace back the shortest path and return link indices.

    Args:
        pred: Predecessor link array from :func:`_dijkstra`.
        links: List of link dicts.
        origin: Source node.
        destination: Target node.

    Returns:
        List of link indices forming the shortest path, or empty list if
        the destination is unreachable.
    """
    if pred[destination] == -1 and destination != origin:
        return []

    path_links: list[int] = []
    current = destination
    while current != origin:
        link_idx = int(pred[current])
        if link_idx == -1:
            return []  # unreachable
        path_links.append(link_idx)
        current = links[link_idx]["from_node"]

    path_links.reverse()
    return path_links


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _validate_links(links: list[dict]) -> None:
    """Validate link definitions.

    Each link must have ``from_node`` (int), ``to_node`` (int),
    ``free_flow_cost`` (> 0), and ``capacity`` (> 0).

    Raises:
        ValueError: If any link is malformed.
    """
    if not links:
        raise ValueError("links must be a non-empty list")

    required_keys = {"from_node", "to_node", "free_flow_cost", "capacity"}
    for i, link in enumerate(links):
        missing = required_keys - set(link.keys())
        if missing:
            raise ValueError(
                f"Link {i} missing required keys: {missing}"
            )
        if link["free_flow_cost"] <= 0:
            raise ValueError(
                f"Link {i} free_flow_cost must be positive, "
                f"got {link['free_flow_cost']}"
            )
        if link["capacity"] <= 0:
            raise ValueError(
                f"Link {i} capacity must be positive, "
                f"got {link['capacity']}"
            )


def _validate_od_demands(od_demands: list[dict]) -> None:
    """Validate OD demand definitions.

    Each entry must have ``origin`` (int), ``destination`` (int),
    ``demand`` (>= 0).

    Raises:
        ValueError: If any OD demand is malformed.
    """
    required_keys = {"origin", "destination", "demand"}
    for i, od in enumerate(od_demands):
        missing = required_keys - set(od.keys())
        if missing:
            raise ValueError(
                f"OD demand {i} missing required keys: {missing}"
            )
        if od["demand"] < 0:
            raise ValueError(
                f"OD demand {i} demand must be non-negative, "
                f"got {od['demand']}"
            )


# ---------------------------------------------------------------------------
# Frank-Wolfe user equilibrium
# ---------------------------------------------------------------------------

def compute_supernetwork_equilibrium(
    links: list[dict],
    od_demands: list[dict],
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict:
    """Compute user equilibrium using the Frank-Wolfe algorithm.

    The Frank-Wolfe (convex combinations) method solves the Beckmann
    formulation of the traffic assignment problem, finding link flows
    where no user can unilaterally reduce their travel cost by switching
    routes (Wardrop's first principle).

    Each link must provide:
    ``{from_node: int, to_node: int, free_flow_cost: float, capacity: float}``

    Each OD demand must provide:
    ``{origin: int, destination: int, demand: float}``

    Algorithm:

    1. **Initialise**: all-or-nothing assignment on free-flow costs.
    2. **Direction finding**: compute shortest paths with current BPR costs,
       then perform an all-or-nothing assignment to get *y*.
    3. **Line search**: find optimal step size *lambda* in [0, 1] that
       minimises the Beckmann objective along *x + lambda * (y - x)*.
    4. **Update**: ``x = x + lambda * (y - x)``.
    5. **Convergence**: stop when the relative gap falls below *tolerance*
       or *max_iterations* is reached.

    Args:
        links: Network links (see above for required keys).
        od_demands: Origin-destination demand pairs.
        max_iterations: Maximum Frank-Wolfe iterations.
        tolerance: Convergence tolerance on relative gap.

    Returns:
        Dict containing:

        - ``link_flows`` -- list of dicts with ``from_node``, ``to_node``,
          ``flow``, and ``cost``
        - ``total_system_cost`` -- sum of flow * cost over all links
        - ``iterations`` -- number of iterations performed
        - ``converged`` -- whether the algorithm converged
        - ``gap`` -- relative gap at termination

    Raises:
        ValueError: If inputs are malformed.
    """
    _validate_links(links)
    _validate_od_demands(od_demands)

    n_links = len(links)

    # Filter out zero-demand OD pairs
    active_demands = [od for od in od_demands if od["demand"] > 0]

    # Handle no-demand case
    if not active_demands:
        logger.info("No positive OD demands; returning zero flows")
        return {
            "link_flows": [
                {
                    "from_node": link["from_node"],
                    "to_node": link["to_node"],
                    "flow": 0.0,
                    "cost": link["free_flow_cost"],
                }
                for link in links
            ],
            "total_system_cost": 0.0,
            "iterations": 0,
            "converged": True,
            "gap": 0.0,
        }

    # Determine number of nodes
    all_nodes: set[int] = set()
    for link in links:
        all_nodes.add(link["from_node"])
        all_nodes.add(link["to_node"])
    for od in active_demands:
        all_nodes.add(od["origin"])
        all_nodes.add(od["destination"])
    n_nodes = max(all_nodes) + 1

    # Build adjacency
    adj = _build_adjacency(links, n_nodes)

    # Pre-extract link parameters as arrays for fast computation
    free_flow = np.array(
        [link["free_flow_cost"] for link in links], dtype=np.float64
    )
    capacity = np.array(
        [link["capacity"] for link in links], dtype=np.float64
    )
    alpha_arr = np.array(
        [link.get("alpha", BPR_ALPHA) for link in links], dtype=np.float64
    )
    beta_arr = np.array(
        [link.get("beta", BPR_BETA) for link in links], dtype=np.float64
    )

    # --- Vectorised BPR cost computation ----------------------------------
    def _compute_costs(flows: np.ndarray) -> np.ndarray:
        ratios = np.where(capacity > 0, flows / capacity, 0.0)
        ratios = np.maximum(ratios, 0.0)
        return free_flow * (1.0 + alpha_arr * np.power(ratios, beta_arr))

    # --- All-or-nothing assignment ----------------------------------------
    def _aon_assignment(costs: np.ndarray) -> np.ndarray:
        """Assign all demand to shortest paths given current costs."""
        aon_flows = np.zeros(n_links)
        for od in active_demands:
            origin = od["origin"]
            dest = od["destination"]
            demand = od["demand"]

            dist, pred = _dijkstra(adj, costs, origin, n_nodes)

            # Check reachability
            if dist[dest] >= 1e18:
                logger.warning(
                    "OD pair (%d -> %d) is disconnected; "
                    "demand %.2f cannot be assigned",
                    origin,
                    dest,
                    demand,
                )
                continue

            path = _trace_path(pred, links, origin, dest)
            for link_idx in path:
                aon_flows[link_idx] += demand

        return aon_flows

    # --- Step 1: Initialise with free-flow all-or-nothing -----------------
    x = _aon_assignment(free_flow)
    costs = _compute_costs(x)

    converged = False
    gap = float("inf")
    iteration = 0

    # --- Main Frank-Wolfe loop --------------------------------------------
    for iteration in range(1, max_iterations + 1):
        # Step 2: Direction finding (all-or-nothing on current costs)
        y = _aon_assignment(costs)

        # Step 3: Line search -- bisection on the Beckmann derivative
        # d/d_lambda [ Z(x + lambda*(y-x)) ] = sum_a (y_a - x_a) * c_a(...)
        direction = y - x

        # Bisection line search for optimal step size
        lo, hi = 0.0, 1.0
        for _ in range(50):  # bisection converges quickly
            mid = (lo + hi) / 2.0
            trial = x + mid * direction
            trial_costs = _compute_costs(trial)
            derivative = float(np.dot(direction, trial_costs))
            if derivative > 0:
                hi = mid
            else:
                lo = mid
        lam = (lo + hi) / 2.0

        # Step 4: Update
        x_new = x + lam * direction
        costs = _compute_costs(x_new)

        # Step 5: Convergence check (relative gap)
        # Gap = sum_a x_a * c_a - sum_a y_a * c_a (numerator)
        numerator = float(np.dot(x_new, costs) - np.dot(y, costs))
        denominator = float(np.dot(x_new, costs))
        if denominator > 0:
            gap = abs(numerator / denominator)
        else:
            gap = 0.0

        x = x_new

        if gap < tolerance:
            converged = True
            logger.info(
                "Frank-Wolfe converged at iteration %d "
                "(gap=%.2e, tolerance=%.2e)",
                iteration,
                gap,
                tolerance,
            )
            break

    if not converged:
        logger.warning(
            "Frank-Wolfe did not converge after %d iterations "
            "(gap=%.2e, tolerance=%.2e)",
            max_iterations,
            gap,
            tolerance,
        )

    # --- Build result -----------------------------------------------------
    final_costs = _compute_costs(x)
    total_system_cost = float(np.dot(x, final_costs))

    link_flows = [
        {
            "from_node": links[i]["from_node"],
            "to_node": links[i]["to_node"],
            "flow": round(float(x[i]), 6),
            "cost": round(float(final_costs[i]), 6),
        }
        for i in range(n_links)
    ]

    logger.info(
        "Supernetwork equilibrium: %d links, total_cost=%.2f, "
        "%d iterations, converged=%s, gap=%.2e",
        n_links,
        total_system_cost,
        iteration,
        converged,
        gap,
    )

    return {
        "link_flows": link_flows,
        "total_system_cost": round(total_system_cost, 4),
        "iterations": iteration,
        "converged": converged,
        "gap": round(gap, 10),
    }


# ---------------------------------------------------------------------------
# Multimodal equilibrium
# ---------------------------------------------------------------------------

def compute_multimodal_equilibrium(
    modes: list[dict],
    od_demands: list[dict],
    max_iterations: int = 500,
    tolerance: float = 1e-5,
) -> dict:
    """Multimodal network equilibrium for transport mode allocation.

    Extends the single-network Frank-Wolfe equilibrium to multiple modes
    competing for the same OD demand.  A logit model governs mode split
    based on generalised cost.

    Each mode dict must contain:

    - ``name`` (str): Mode identifier (e.g. "bus", "shuttle", "private_car")
    - ``links`` (list[dict]): Network links for this mode (same format as
      :func:`compute_supernetwork_equilibrium`)
    - ``mode_constant`` (float): Modal attractiveness constant (lower =
      more attractive); acts as an additive penalty in generalised cost.

    The logit mode split is::

        P(m) = exp(-theta * C_m) / sum_k exp(-theta * C_k)

    where ``C_m`` is the shortest-path cost in mode *m* plus the mode
    constant, and ``theta`` is the logit scale parameter (fixed at 0.1).

    Algorithm:

    1. Initialise equal mode split.
    2. For each mode, run single-mode Frank-Wolfe to get costs.
    3. Apply logit split to redistribute demand across modes.
    4. Iterate until mode shares stabilise.

    Args:
        modes: List of mode definitions (see above).
        od_demands: Origin-destination demand pairs.
        max_iterations: Maximum outer iterations.
        tolerance: Convergence tolerance on mode share change.

    Returns:
        Dict containing:

        - ``mode_flows`` -- dict mapping mode name to list of link flow dicts
        - ``mode_shares`` -- dict mapping mode name to market share (0-1)
        - ``total_cost`` -- sum of all link flow * cost across all modes
        - ``iterations`` -- outer iterations performed
        - ``converged`` -- whether mode shares converged
        - ``gap`` -- max absolute change in mode shares at termination

    Raises:
        ValueError: If modes or OD demands are invalid.
    """
    if not modes:
        raise ValueError("modes must be a non-empty list")

    _validate_od_demands(od_demands)

    for i, mode in enumerate(modes):
        if "name" not in mode:
            raise ValueError(f"Mode {i} missing required key 'name'")
        if "links" not in mode:
            raise ValueError(
                f"Mode {i} ('{mode.get('name', '?')}') missing 'links'"
            )
        if not mode["links"]:
            raise ValueError(
                f"Mode {i} ('{mode['name']}') has empty links list"
            )
        _validate_links(mode["links"])

    active_demands = [od for od in od_demands if od["demand"] > 0]
    n_modes = len(modes)
    mode_names = [m["name"] for m in modes]

    # Handle no-demand case
    if not active_demands:
        logger.info("No positive OD demands; returning zero multimodal flows")
        return {
            "mode_flows": {
                m["name"]: [
                    {
                        "from_node": link["from_node"],
                        "to_node": link["to_node"],
                        "flow": 0.0,
                        "cost": link["free_flow_cost"],
                    }
                    for link in m["links"]
                ]
                for m in modes
            },
            "mode_shares": {m["name"]: 1.0 / n_modes for m in modes},
            "total_cost": 0.0,
            "iterations": 0,
            "converged": True,
            "gap": 0.0,
        }

    # Logit scale parameter
    theta = 0.1

    # Initialise equal shares
    shares = np.ones(n_modes) / n_modes
    total_demand = sum(od["demand"] for od in active_demands)

    mode_results: dict[str, dict] = {}
    converged = False
    gap = float("inf")
    iteration = 0

    for iteration in range(1, max_iterations + 1):
        # --- Run single-mode equilibrium for each mode --------------------
        mode_costs_per_od: list[list[float]] = []  # [mode][od_idx]

        for m_idx, mode in enumerate(modes):
            mode_constant = mode.get("mode_constant", 0.0)

            # Scale OD demands by current mode share
            scaled_demands = [
                {
                    "origin": od["origin"],
                    "destination": od["destination"],
                    "demand": od["demand"] * shares[m_idx],
                }
                for od in active_demands
            ]

            result = compute_supernetwork_equilibrium(
                links=mode["links"],
                od_demands=scaled_demands,
                max_iterations=200,
                tolerance=tolerance * 10,
            )
            mode_results[mode["name"]] = result

            # Compute shortest-path cost for each OD pair in this mode
            # Use the equilibrium link costs
            all_nodes: set[int] = set()
            for link in mode["links"]:
                all_nodes.add(link["from_node"])
                all_nodes.add(link["to_node"])
            for od in active_demands:
                all_nodes.add(od["origin"])
                all_nodes.add(od["destination"])
            n_nodes = max(all_nodes) + 1 if all_nodes else 0

            adj = _build_adjacency(mode["links"], n_nodes)
            eq_costs = np.array(
                [lf["cost"] for lf in result["link_flows"]],
                dtype=np.float64,
            )

            od_costs: list[float] = []
            for od in active_demands:
                dist, _ = _dijkstra(adj, eq_costs, od["origin"], n_nodes)
                sp_cost = dist[od["destination"]]
                if sp_cost >= 1e18:
                    # Disconnected: assign very high cost
                    sp_cost = 1e6
                od_costs.append(sp_cost + mode_constant)

            mode_costs_per_od.append(od_costs)

        # --- Logit mode split per OD pair --------------------------------
        new_shares = np.zeros(n_modes)

        for od_idx, od in enumerate(active_demands):
            utilities = np.array(
                [-theta * mode_costs_per_od[m][od_idx] for m in range(n_modes)]
            )
            # Numerical stability: subtract max
            utilities -= np.max(utilities)
            exp_utils = np.exp(utilities)
            probabilities = exp_utils / np.sum(exp_utils)

            for m_idx in range(n_modes):
                new_shares[m_idx] += probabilities[m_idx] * od["demand"]

        # Normalise to get proportions
        if total_demand > 0:
            new_shares = new_shares / total_demand

        # --- Convergence check -------------------------------------------
        gap = float(np.max(np.abs(new_shares - shares)))
        shares = new_shares

        if gap < tolerance:
            converged = True
            logger.info(
                "Multimodal equilibrium converged at iteration %d "
                "(gap=%.2e)",
                iteration,
                gap,
            )
            break

    if not converged:
        logger.warning(
            "Multimodal equilibrium did not converge after %d iterations "
            "(gap=%.2e)",
            max_iterations,
            gap,
        )

    # --- Final run with converged shares to get accurate flows -----------
    final_mode_flows: dict[str, list[dict]] = {}
    total_cost = 0.0

    for m_idx, mode in enumerate(modes):
        scaled_demands = [
            {
                "origin": od["origin"],
                "destination": od["destination"],
                "demand": od["demand"] * shares[m_idx],
            }
            for od in active_demands
        ]
        result = compute_supernetwork_equilibrium(
            links=mode["links"],
            od_demands=scaled_demands,
            max_iterations=200,
            tolerance=tolerance * 10,
        )
        final_mode_flows[mode["name"]] = result["link_flows"]
        total_cost += result["total_system_cost"]

    mode_shares_dict = {
        mode_names[i]: round(float(shares[i]), 6)
        for i in range(n_modes)
    }

    logger.info(
        "Multimodal equilibrium: %d modes, shares=%s, total_cost=%.2f, "
        "%d iterations, converged=%s",
        n_modes,
        mode_shares_dict,
        total_cost,
        iteration,
        converged,
    )

    return {
        "mode_flows": final_mode_flows,
        "mode_shares": mode_shares_dict,
        "total_cost": round(total_cost, 4),
        "iterations": iteration,
        "converged": converged,
        "gap": round(gap, 10),
    }
