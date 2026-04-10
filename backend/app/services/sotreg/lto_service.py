from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LTO trigger thresholds (CDC SOTREG v5.0)
# ---------------------------------------------------------------------------

COV_HEADWAY_THRESHOLD = 0.30       # Trigger LTO when COV > 0.30
DEVIATION_THRESHOLD_SECONDS = 180  # 3 minutes real-planned deviation
MAX_OFFSET_SECONDS = 300           # Max adjustment: +/- 5 minutes
DEFAULT_MIN_HEADWAY_SECONDS = 120  # Minimum 2 min between departures


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _datetimes_to_seconds(times: list[datetime]) -> np.ndarray:
    """Convert a list of datetimes to seconds since the earliest time.

    The times are sorted chronologically before conversion so that the
    resulting array is monotonically non-decreasing.
    """
    if not times:
        return np.array([], dtype=np.float64)
    sorted_times = sorted(times)
    origin = sorted_times[0]
    return np.array(
        [(t - origin).total_seconds() for t in sorted_times],
        dtype=np.float64,
    )


def _compute_headways(times_seconds: np.ndarray) -> np.ndarray:
    """Compute inter-departure headways from sorted time-of-day offsets."""
    if len(times_seconds) < 2:
        return np.array([], dtype=np.float64)
    return np.diff(np.sort(times_seconds))


def _compute_cov(headways: np.ndarray) -> float:
    """Coefficient of variation = std / mean.  Returns 0.0 when undefined."""
    if len(headways) == 0:
        return 0.0
    mean = float(np.mean(headways))
    if mean == 0.0:
        return 0.0
    return float(np.std(headways, ddof=0) / mean)


# ---------------------------------------------------------------------------
# Platooning detection
# ---------------------------------------------------------------------------

def detect_platooning(
    departure_times: list[datetime],
    scheduled_times: list[datetime],
    cov_threshold: float = COV_HEADWAY_THRESHOLD,
    deviation_threshold_s: float = DEVIATION_THRESHOLD_SECONDS,
) -> dict:
    """Detect if a line exhibits platooning behaviour.

    Platooning is defined as the conjunction of two conditions:

    1. The coefficient of variation of *actual* headways exceeds
       ``cov_threshold`` (default 0.30).
    2. The mean absolute deviation between actual and scheduled departure
       times exceeds ``deviation_threshold_s`` (default 180 s / 3 min).

    Args:
        departure_times: Observed (actual) departure datetimes.
        scheduled_times: Planned departure datetimes **in the same order**
            as *departure_times* (i.e. the i-th scheduled time corresponds
            to the i-th actual departure).
        cov_threshold: COV threshold above which headways are irregular.
        deviation_threshold_s: Mean deviation threshold in seconds.

    Returns:
        Dict with keys:

        - ``is_platooning`` -- bool
        - ``cov_headway`` -- float
        - ``avg_deviation_seconds`` -- float
        - ``max_deviation_seconds`` -- float
        - ``vehicle_count`` -- int
        - ``recommendation`` -- str
    """
    vehicle_count = len(departure_times)

    # -- Edge cases ----------------------------------------------------------
    if vehicle_count == 0:
        return {
            "is_platooning": False,
            "cov_headway": 0.0,
            "avg_deviation_seconds": 0.0,
            "max_deviation_seconds": 0.0,
            "vehicle_count": 0,
            "recommendation": "No departures to analyse.",
        }

    if vehicle_count == 1:
        dev = abs((departure_times[0] - scheduled_times[0]).total_seconds())
        return {
            "is_platooning": False,
            "cov_headway": 0.0,
            "avg_deviation_seconds": dev,
            "max_deviation_seconds": dev,
            "vehicle_count": 1,
            "recommendation": (
                "Single vehicle -- headway analysis not applicable."
            ),
        }

    # -- Headway COV ---------------------------------------------------------
    actual_seconds = _datetimes_to_seconds(departure_times)
    headways = _compute_headways(actual_seconds)
    cov_headway = _compute_cov(headways)

    # -- Deviation analysis --------------------------------------------------
    deviations = np.array([
        abs((a - s).total_seconds())
        for a, s in zip(departure_times, scheduled_times)
    ])
    avg_deviation = float(np.mean(deviations))
    max_deviation = float(np.max(deviations))

    # -- Platooning decision -------------------------------------------------
    is_platooning = (cov_headway > cov_threshold) and (
        avg_deviation > deviation_threshold_s
    )

    if is_platooning:
        recommendation = (
            f"Platooning detected (COV={cov_headway:.3f} > {cov_threshold}, "
            f"avg deviation={avg_deviation:.0f}s > {deviation_threshold_s:.0f}s). "
            "LTO optimisation recommended."
        )
    elif cov_headway > cov_threshold:
        recommendation = (
            f"Headway irregularity detected (COV={cov_headway:.3f} > "
            f"{cov_threshold}) but deviations are within tolerance. "
            "Monitor headways."
        )
    elif avg_deviation > deviation_threshold_s:
        recommendation = (
            f"Schedule adherence issue (avg deviation={avg_deviation:.0f}s > "
            f"{deviation_threshold_s:.0f}s) but headway regularity is "
            "acceptable. Review driver compliance."
        )
    else:
        recommendation = (
            "Headways and schedule adherence are within acceptable limits."
        )

    logger.info(
        "Platooning check: vehicles=%d, COV=%.3f, avg_dev=%.0fs, "
        "is_platooning=%s",
        vehicle_count,
        cov_headway,
        avg_deviation,
        is_platooning,
    )

    return {
        "is_platooning": is_platooning,
        "cov_headway": round(cov_headway, 4),
        "avg_deviation_seconds": round(avg_deviation, 1),
        "max_deviation_seconds": round(max_deviation, 1),
        "vehicle_count": vehicle_count,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Objective function for scipy
# ---------------------------------------------------------------------------

def _headway_variance_objective(
    offsets: np.ndarray,
    base_times_seconds: np.ndarray,
    target_headway: float,
) -> float:
    """Objective function for ``scipy.optimize.minimize``.

    Minimises the sum of squared deviations of headways from the target::

        J = sum_i (h_i - target_headway)^2

    where ``h_i = (t_{i+1} + offset_{i+1}) - (t_i + offset_i)`` after
    sorting the adjusted departure times.

    Args:
        offsets: Array of time offsets in seconds (one per departure).
        base_times_seconds: Sorted base departure times in seconds from
            an arbitrary origin.
        target_headway: Desired uniform headway in seconds.

    Returns:
        Scalar cost value.
    """
    adjusted = np.sort(base_times_seconds + offsets)
    headways = np.diff(adjusted)
    return float(np.sum((headways - target_headway) ** 2))


# ---------------------------------------------------------------------------
# Core LTO optimisation
# ---------------------------------------------------------------------------

def optimize_departure_times(
    scheduled_departures: list[datetime],
    target_headway_seconds: float = 600.0,
    min_headway_seconds: float = DEFAULT_MIN_HEADWAY_SECONDS,
    max_offset_seconds: float = MAX_OFFSET_SECONDS,
) -> dict:
    """Run LTO optimisation to minimise headway variance.

    Uses ``scipy.optimize.minimize`` with the **L-BFGS-B** method which
    supports box bounds on each variable.  Each offset is bounded to
    ``[-max_offset_seconds, +max_offset_seconds]``.

    After optimisation the minimum-headway constraint is enforced in a
    post-processing sweep: if any consecutive pair is closer than
    ``min_headway_seconds`` the later departure is pushed forward.

    Args:
        scheduled_departures: List of planned departure datetimes.
        target_headway_seconds: Desired uniform headway (seconds).
        min_headway_seconds: Hard minimum gap between consecutive departures.
        max_offset_seconds: Maximum absolute offset applied to any departure.

    Returns:
        Dict with keys:

        - ``optimized_departures`` -- list[datetime]
        - ``offsets_seconds`` -- list[float]
        - ``original_cov`` -- float
        - ``optimized_cov`` -- float
        - ``improvement_pct`` -- float
        - ``target_headway_seconds`` -- float
        - ``converged`` -- bool
        - ``iterations`` -- int

    Raises:
        ValueError: If ``min_headway_seconds`` is negative, or
            ``max_offset_seconds`` is negative.
    """
    if min_headway_seconds < 0:
        raise ValueError(
            f"min_headway_seconds must be non-negative, got "
            f"{min_headway_seconds}"
        )
    if max_offset_seconds < 0:
        raise ValueError(
            f"max_offset_seconds must be non-negative, got "
            f"{max_offset_seconds}"
        )

    n = len(scheduled_departures)

    # -- Edge cases ----------------------------------------------------------
    if n == 0:
        return {
            "optimized_departures": [],
            "offsets_seconds": [],
            "original_cov": 0.0,
            "optimized_cov": 0.0,
            "improvement_pct": 0.0,
            "target_headway_seconds": target_headway_seconds,
            "converged": True,
            "iterations": 0,
        }

    if n == 1:
        return {
            "optimized_departures": list(scheduled_departures),
            "offsets_seconds": [0.0],
            "original_cov": 0.0,
            "optimized_cov": 0.0,
            "improvement_pct": 0.0,
            "target_headway_seconds": target_headway_seconds,
            "converged": True,
            "iterations": 0,
        }

    # -- Sort departures and remember original order -------------------------
    indexed = sorted(enumerate(scheduled_departures), key=lambda t: t[1])
    sorted_indices = [i for i, _ in indexed]
    sorted_departures = [dt for _, dt in indexed]

    origin = sorted_departures[0]
    base_seconds = np.array(
        [(dt - origin).total_seconds() for dt in sorted_departures],
        dtype=np.float64,
    )

    # -- Original headway COV ------------------------------------------------
    original_headways = _compute_headways(base_seconds)
    original_cov = _compute_cov(original_headways)

    # -- Already optimal check -----------------------------------------------
    if original_cov == 0.0 and n >= 2:
        return {
            "optimized_departures": list(scheduled_departures),
            "offsets_seconds": [0.0] * n,
            "original_cov": 0.0,
            "optimized_cov": 0.0,
            "improvement_pct": 0.0,
            "target_headway_seconds": target_headway_seconds,
            "converged": True,
            "iterations": 0,
        }

    # -- scipy L-BFGS-B optimisation -----------------------------------------
    x0 = np.zeros(n, dtype=np.float64)
    bounds = [(-max_offset_seconds, max_offset_seconds)] * n

    result = minimize(
        _headway_variance_objective,
        x0,
        args=(base_seconds, target_headway_seconds),
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    optimized_offsets = result.x

    # -- Post-process: enforce minimum headway --------------------------------
    adjusted = base_seconds + optimized_offsets
    sort_order = np.argsort(adjusted)
    adjusted_sorted = adjusted[sort_order]

    for i in range(1, len(adjusted_sorted)):
        gap = adjusted_sorted[i] - adjusted_sorted[i - 1]
        if gap < min_headway_seconds:
            adjusted_sorted[i] = adjusted_sorted[i - 1] + min_headway_seconds

    # Map sorted-adjusted values back to the optimised offsets array
    inv_order = np.argsort(sort_order)
    adjusted_final = adjusted_sorted[inv_order]
    optimized_offsets = adjusted_final - base_seconds

    # Clip offsets to bounds (post-processing may have pushed beyond)
    optimized_offsets = np.clip(
        optimized_offsets, -max_offset_seconds, max_offset_seconds
    )

    # -- Rebuild datetimes ---------------------------------------------------
    optimized_sorted_datetimes = [
        sorted_departures[i] + timedelta(seconds=float(optimized_offsets[i]))
        for i in range(n)
    ]

    # -- Re-order back to original input order -------------------------------
    optimized_departures: list[datetime] = [datetime.min] * n
    offsets_output: list[float] = [0.0] * n
    for sorted_pos in range(n):
        orig_idx = sorted_indices[sorted_pos]
        optimized_departures[orig_idx] = optimized_sorted_datetimes[sorted_pos]
        offsets_output[orig_idx] = round(
            float(optimized_offsets[sorted_pos]), 1
        )

    # -- Optimised headway COV -----------------------------------------------
    optimized_seconds = base_seconds + optimized_offsets
    optimized_headways = _compute_headways(optimized_seconds)
    optimized_cov = _compute_cov(optimized_headways)

    improvement_pct = 0.0
    if original_cov > 0.0:
        improvement_pct = round(
            (1.0 - optimized_cov / original_cov) * 100.0, 2
        )

    logger.info(
        "LTO optimisation: n=%d, COV %.4f -> %.4f (improvement %.1f%%), "
        "converged=%s, iterations=%d",
        n,
        original_cov,
        optimized_cov,
        improvement_pct,
        result.success,
        result.nit,
    )

    return {
        "optimized_departures": optimized_departures,
        "offsets_seconds": offsets_output,
        "original_cov": round(original_cov, 4),
        "optimized_cov": round(optimized_cov, 4),
        "improvement_pct": improvement_pct,
        "target_headway_seconds": target_headway_seconds,
        "converged": bool(result.success),
        "iterations": int(result.nit),
    }


# ---------------------------------------------------------------------------
# Full LTO pipeline
# ---------------------------------------------------------------------------

def compute_lto_schedule(
    ligne_departures: list[dict],
    target_headway_seconds: float = 600.0,
    min_headway_seconds: float = DEFAULT_MIN_HEADWAY_SECONDS,
    max_offset_seconds: float = MAX_OFFSET_SECONDS,
) -> dict:
    """Full LTO pipeline: detect platooning, optimise, return schedule.

    Each entry in *ligne_departures* is a dict with:

    - ``vehicle_id`` (str): Identifier of the vehicle.
    - ``scheduled_departure`` (datetime): Planned departure time.
    - ``actual_departure`` (datetime | None): Observed departure time.  If
      ``None`` the scheduled time is used as actual for detection purposes.

    The function first runs :func:`detect_platooning`.  If platooning is
    detected it proceeds with :func:`optimize_departure_times`.  Otherwise
    it returns the original schedule with ``needs_optimization=False``.

    Args:
        ligne_departures: List of departure dicts.
        target_headway_seconds: Desired uniform headway (seconds).
        min_headway_seconds: Hard minimum gap between departures.
        max_offset_seconds: Maximum absolute offset.

    Returns:
        Dict with keys:

        - ``needs_optimization`` -- bool
        - ``platooning_check`` -- dict from :func:`detect_platooning`
        - ``schedule`` -- list of dicts with ``vehicle_id``,
          ``scheduled_departure``, ``optimized_departure``,
          ``offset_seconds``
        - ``optimization_result`` -- dict from
          :func:`optimize_departure_times` or ``None``
    """
    # -- Edge case: empty input ----------------------------------------------
    if not ligne_departures:
        return {
            "needs_optimization": False,
            "platooning_check": detect_platooning([], []),
            "schedule": [],
            "optimization_result": None,
        }

    # -- Extract times -------------------------------------------------------
    vehicle_ids: list[str] = []
    scheduled_times: list[datetime] = []
    actual_times: list[datetime] = []

    for entry in ligne_departures:
        vehicle_ids.append(str(entry["vehicle_id"]))
        sched = entry["scheduled_departure"]
        scheduled_times.append(sched)
        actual = entry.get("actual_departure")
        actual_times.append(actual if actual is not None else sched)

    # -- Platooning detection ------------------------------------------------
    platooning_check = detect_platooning(actual_times, scheduled_times)

    # -- Build schedule without optimisation if not needed -------------------
    if not platooning_check["is_platooning"]:
        schedule = [
            {
                "vehicle_id": vid,
                "scheduled_departure": sched,
                "optimized_departure": sched,
                "offset_seconds": 0.0,
            }
            for vid, sched in zip(vehicle_ids, scheduled_times)
        ]
        return {
            "needs_optimization": False,
            "platooning_check": platooning_check,
            "schedule": schedule,
            "optimization_result": None,
        }

    # -- Optimise ------------------------------------------------------------
    opt_result = optimize_departure_times(
        scheduled_departures=scheduled_times,
        target_headway_seconds=target_headway_seconds,
        min_headway_seconds=min_headway_seconds,
        max_offset_seconds=max_offset_seconds,
    )

    schedule = [
        {
            "vehicle_id": vid,
            "scheduled_departure": sched,
            "optimized_departure": opt_dt,
            "offset_seconds": offset,
        }
        for vid, sched, opt_dt, offset in zip(
            vehicle_ids,
            scheduled_times,
            opt_result["optimized_departures"],
            opt_result["offsets_seconds"],
        )
    ]

    logger.info(
        "LTO schedule computed: %d vehicles, needs_optimization=%s",
        len(schedule),
        True,
    )

    return {
        "needs_optimization": True,
        "platooning_check": platooning_check,
        "schedule": schedule,
        "optimization_result": {
            k: v
            for k, v in opt_result.items()
            if k != "optimized_departures"
        },
    }
