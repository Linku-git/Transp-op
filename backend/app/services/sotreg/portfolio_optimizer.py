from __future__ import annotations

import logging

import numpy as np
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Bank Al-Maghrib base rate (risk-free proxy for Sharpe ratio)
BAM_RISK_FREE_RATE = 0.03

# Default technology labels when none provided
DEFAULT_TECH_NAMES = [
    "Diesel",
    "GNV",
    "Hybride",
    "Electrique_AC",
    "Electrique_DC",
    "Hydrogene",
]


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def _validate_inputs(
    expected_returns: list[float],
    covariance_matrix: list[list[float]],
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and convert inputs to numpy arrays.

    Args:
        expected_returns: Vector of expected annual returns per technology.
        covariance_matrix: NxN covariance matrix of returns.

    Returns:
        Tuple of (mu, sigma) as numpy arrays.

    Raises:
        ValueError: If inputs are empty, mismatched, or matrix is not square.
    """
    if not expected_returns:
        raise ValueError("expected_returns must be a non-empty list")

    n = len(expected_returns)

    if not covariance_matrix or len(covariance_matrix) != n:
        raise ValueError(
            f"covariance_matrix must be {n}x{n} to match "
            f"{n} expected_returns, got {len(covariance_matrix)} rows"
        )

    for i, row in enumerate(covariance_matrix):
        if len(row) != n:
            raise ValueError(
                f"covariance_matrix row {i} has {len(row)} columns, "
                f"expected {n}"
            )

    mu = np.array(expected_returns, dtype=np.float64)
    sigma = np.array(covariance_matrix, dtype=np.float64)

    # Check symmetry (within floating-point tolerance)
    if not np.allclose(sigma, sigma.T, atol=1e-10):
        raise ValueError("covariance_matrix must be symmetric")

    return mu, sigma


def _resolve_tech_names(
    technology_names: list[str] | None,
    n: int,
) -> list[str]:
    """Resolve technology names, falling back to generic labels.

    Args:
        technology_names: Optional list of labels.
        n: Expected number of technologies.

    Returns:
        List of *n* technology name strings.

    Raises:
        ValueError: If provided list length does not match *n*.
    """
    if technology_names is None:
        if n <= len(DEFAULT_TECH_NAMES):
            return DEFAULT_TECH_NAMES[:n]
        return [f"Tech_{i + 1}" for i in range(n)]

    if len(technology_names) != n:
        raise ValueError(
            f"technology_names length ({len(technology_names)}) "
            f"does not match expected_returns length ({n})"
        )
    return list(technology_names)


# ---------------------------------------------------------------------------
# Core optimisation: single portfolio for a given risk aversion
# ---------------------------------------------------------------------------

def compute_portfolio_optimization(
    expected_returns: list[float],
    covariance_matrix: list[list[float]],
    risk_aversion: float = 1.0,
    technology_names: list[str] | None = None,
) -> dict:
    """Markowitz mean-variance portfolio optimization.

    Maximizes the utility function::

        U(w) = w^T * mu  -  (lambda / 2) * w^T * Sigma * w

    subject to::

        sum(w) = 1,  w_i >= 0  (no short-selling)

    The optimization is performed via ``scipy.optimize.minimize`` using the
    SLSQP sequential quadratic programming method.

    Args:
        expected_returns: Vector of expected annual returns per technology.
            Length *n* defines the number of assets.
        covariance_matrix: NxN covariance matrix of returns.
        risk_aversion: Lambda parameter controlling the risk/return trade-off.
            Higher values produce more conservative (lower-variance)
            allocations.  Must be > 0.
        technology_names: Optional labels for each technology.

    Returns:
        Dict containing:

        - ``weights`` -- optimal allocation (list[float], sums to 1.0)
        - ``expected_return`` -- portfolio expected return (float)
        - ``portfolio_variance`` -- portfolio variance (float)
        - ``portfolio_std`` -- portfolio standard deviation / risk (float)
        - ``sharpe_ratio`` -- (return - BAM 3%) / std (float)
        - ``technology_names`` -- resolved label list
        - ``risk_aversion`` -- the lambda used
        - ``currency`` -- always ``"MAD"``

    Raises:
        ValueError: If inputs are invalid or risk_aversion is non-positive.
    """
    if risk_aversion <= 0:
        raise ValueError(
            f"risk_aversion must be positive, got {risk_aversion}"
        )

    mu, sigma = _validate_inputs(expected_returns, covariance_matrix)
    n = len(mu)
    names = _resolve_tech_names(technology_names, n)

    # --- Single-asset trivial case ----------------------------------------
    if n == 1:
        ret = float(mu[0])
        var = float(sigma[0, 0])
        std = float(np.sqrt(var))
        sharpe = (ret - BAM_RISK_FREE_RATE) / std if std > 0 else 0.0
        logger.info(
            "Single-asset portfolio: %s weight=1.0, return=%.4f",
            names[0],
            ret,
        )
        return {
            "weights": [1.0],
            "expected_return": ret,
            "portfolio_variance": var,
            "portfolio_std": std,
            "sharpe_ratio": round(sharpe, 6),
            "technology_names": names,
            "risk_aversion": risk_aversion,
            "currency": "MAD",
        }

    # --- Objective: minimise negative utility (= maximise utility) --------
    def _neg_utility(w: np.ndarray) -> float:
        port_return = w @ mu
        port_var = w @ sigma @ w
        return -(port_return - (risk_aversion / 2.0) * port_var)

    # --- Constraints and bounds -------------------------------------------
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    w0 = np.ones(n) / n  # equal-weight initial guess

    result = minimize(
        _neg_utility,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    if not result.success:
        logger.warning(
            "Portfolio optimization did not converge: %s. "
            "Returning equal-weight fallback.",
            result.message,
        )
        weights = np.ones(n) / n
    else:
        weights = result.x

    # Clamp tiny negatives to zero and re-normalise
    weights = np.maximum(weights, 0.0)
    w_sum = weights.sum()
    if w_sum > 0:
        weights = weights / w_sum

    # --- Portfolio metrics ------------------------------------------------
    port_return = float(weights @ mu)
    port_var = float(weights @ sigma @ weights)
    port_std = float(np.sqrt(max(port_var, 0.0)))
    sharpe = (
        (port_return - BAM_RISK_FREE_RATE) / port_std
        if port_std > 0
        else 0.0
    )

    logger.info(
        "Portfolio optimized (lambda=%.2f): return=%.4f, risk=%.4f, "
        "sharpe=%.4f, weights=%s",
        risk_aversion,
        port_return,
        port_std,
        sharpe,
        {n: round(w, 4) for n, w in zip(names, weights)},
    )

    return {
        "weights": [round(float(w), 6) for w in weights],
        "expected_return": round(port_return, 6),
        "portfolio_variance": round(port_var, 6),
        "portfolio_std": round(port_std, 6),
        "sharpe_ratio": round(sharpe, 6),
        "technology_names": names,
        "risk_aversion": risk_aversion,
        "currency": "MAD",
    }


# ---------------------------------------------------------------------------
# Minimum-variance portfolio
# ---------------------------------------------------------------------------

def compute_minimum_variance_portfolio(
    covariance_matrix: list[list[float]],
    technology_names: list[str] | None = None,
) -> dict:
    """Find the global minimum-variance portfolio.

    Minimises::

        w^T * Sigma * w

    subject to ``sum(w) = 1``, ``w_i >= 0``.

    Args:
        covariance_matrix: NxN covariance matrix of returns.
        technology_names: Optional labels for technologies.

    Returns:
        Dict with ``weights``, ``portfolio_variance``, ``portfolio_std``,
        and ``technology_names``.

    Raises:
        ValueError: If the covariance matrix is empty or not square.
    """
    if not covariance_matrix:
        raise ValueError("covariance_matrix must be non-empty")

    n = len(covariance_matrix)
    sigma = np.array(covariance_matrix, dtype=np.float64)

    if sigma.shape != (n, n):
        raise ValueError(
            f"covariance_matrix must be square, got shape {sigma.shape}"
        )

    names = _resolve_tech_names(technology_names, n)

    # --- Single-asset trivial case ----------------------------------------
    if n == 1:
        var = float(sigma[0, 0])
        logger.info("Single-asset min-variance: %s, var=%.6f", names[0], var)
        return {
            "weights": [1.0],
            "portfolio_variance": var,
            "portfolio_std": float(np.sqrt(max(var, 0.0))),
            "technology_names": names,
        }

    # --- Optimisation -----------------------------------------------------
    def _portfolio_variance(w: np.ndarray) -> float:
        return float(w @ sigma @ w)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 1.0)] * n
    w0 = np.ones(n) / n

    result = minimize(
        _portfolio_variance,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    if not result.success:
        logger.warning(
            "Min-variance optimization did not converge: %s. "
            "Returning equal-weight fallback.",
            result.message,
        )
        weights = np.ones(n) / n
    else:
        weights = result.x

    weights = np.maximum(weights, 0.0)
    w_sum = weights.sum()
    if w_sum > 0:
        weights = weights / w_sum

    port_var = float(weights @ sigma @ weights)
    port_std = float(np.sqrt(max(port_var, 0.0)))

    logger.info(
        "Minimum-variance portfolio: std=%.6f, weights=%s",
        port_std,
        {n: round(w, 4) for n, w in zip(names, weights)},
    )

    return {
        "weights": [round(float(w), 6) for w in weights],
        "portfolio_variance": round(port_var, 6),
        "portfolio_std": round(port_std, 6),
        "technology_names": names,
    }


# ---------------------------------------------------------------------------
# Efficient frontier
# ---------------------------------------------------------------------------

def compute_efficient_frontier(
    expected_returns: list[float],
    covariance_matrix: list[list[float]],
    n_points: int = 20,
    technology_names: list[str] | None = None,
) -> dict:
    """Compute the efficient frontier (Pareto-optimal portfolios).

    Generates *n_points* portfolios along the frontier from the global
    minimum-variance portfolio to the maximum-return portfolio.  Each
    point is obtained by constraining the minimum expected return and
    minimising variance subject to that constraint.

    Args:
        expected_returns: Vector of expected annual returns per technology.
        covariance_matrix: NxN covariance matrix of returns.
        n_points: Number of points to sample along the frontier (>= 2).
        technology_names: Optional labels for technologies.

    Returns:
        Dict containing:

        - ``frontier`` -- list of dicts, each with ``expected_return``,
          ``risk`` (std), and ``weights``
        - ``min_risk_portfolio`` -- the global minimum-variance portfolio
        - ``max_return_portfolio`` -- the maximum-return point on the frontier
        - ``technology_names`` -- resolved label list
        - ``n_points`` -- actual number of frontier points

    Raises:
        ValueError: If inputs are invalid or n_points < 2.
    """
    if n_points < 2:
        raise ValueError(f"n_points must be >= 2, got {n_points}")

    mu, sigma = _validate_inputs(expected_returns, covariance_matrix)
    n = len(mu)
    names = _resolve_tech_names(technology_names, n)

    # --- Single-asset trivial case ----------------------------------------
    if n == 1:
        ret = float(mu[0])
        var = float(sigma[0, 0])
        std = float(np.sqrt(max(var, 0.0)))
        point = {
            "expected_return": ret,
            "risk": std,
            "weights": [1.0],
        }
        logger.info("Single-asset frontier: return=%.4f, risk=%.4f", ret, std)
        return {
            "frontier": [point],
            "min_risk_portfolio": point,
            "max_return_portfolio": point,
            "technology_names": names,
            "n_points": 1,
        }

    # --- Equal-return edge case: all assets have same expected return -----
    if np.allclose(mu, mu[0]):
        mv = compute_minimum_variance_portfolio(
            covariance_matrix, technology_names=names
        )
        point = {
            "expected_return": float(mu[0]),
            "risk": mv["portfolio_std"],
            "weights": mv["weights"],
        }
        logger.info(
            "Equal-return frontier (degenerate): return=%.4f, risk=%.4f",
            float(mu[0]),
            mv["portfolio_std"],
        )
        return {
            "frontier": [point],
            "min_risk_portfolio": point,
            "max_return_portfolio": point,
            "technology_names": names,
            "n_points": 1,
        }

    # --- Min-variance portfolio (lower bound of frontier) -----------------
    mv = compute_minimum_variance_portfolio(
        covariance_matrix, technology_names=names
    )
    mv_return = float(np.array(mv["weights"]) @ mu)

    # --- Max-return portfolio (upper bound of frontier) -------------------
    max_ret = float(np.max(mu))

    # --- Generate target returns evenly spaced along the frontier ---------
    target_returns = np.linspace(mv_return, max_ret, n_points)

    frontier: list[dict] = []
    for target in target_returns:
        # Minimise variance subject to: sum(w)=1, w>=0, w^T*mu >= target
        def _obj(w: np.ndarray) -> float:
            return float(w @ sigma @ w)

        constraints_list = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "ineq", "fun": lambda w, t=target: w @ mu - t},
        ]
        bounds = [(0.0, 1.0)] * n
        w0 = np.ones(n) / n

        res = minimize(
            _obj,
            w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_list,
            options={"maxiter": 1000, "ftol": 1e-12},
        )

        if res.success:
            w = np.maximum(res.x, 0.0)
            w_sum = w.sum()
            if w_sum > 0:
                w = w / w_sum
        else:
            # Fallback to equal-weight
            w = np.ones(n) / n

        port_ret = float(w @ mu)
        port_std = float(np.sqrt(max(float(w @ sigma @ w), 0.0)))

        frontier.append({
            "expected_return": round(port_ret, 6),
            "risk": round(port_std, 6),
            "weights": [round(float(wi), 6) for wi in w],
        })

    # Remove any duplicate or dominated points
    # (keep unique by rounding to 6 decimal places)
    seen: set[tuple[float, float]] = set()
    unique_frontier: list[dict] = []
    for pt in frontier:
        key = (pt["expected_return"], pt["risk"])
        if key not in seen:
            seen.add(key)
            unique_frontier.append(pt)
    frontier = unique_frontier

    min_risk_pt = min(frontier, key=lambda p: p["risk"])
    max_ret_pt = max(frontier, key=lambda p: p["expected_return"])

    logger.info(
        "Efficient frontier computed: %d points, "
        "return range [%.4f, %.4f], risk range [%.4f, %.4f]",
        len(frontier),
        min_risk_pt["expected_return"],
        max_ret_pt["expected_return"],
        min_risk_pt["risk"],
        max_ret_pt["risk"],
    )

    return {
        "frontier": frontier,
        "min_risk_portfolio": min_risk_pt,
        "max_return_portfolio": max_ret_pt,
        "technology_names": names,
        "n_points": len(frontier),
    }
