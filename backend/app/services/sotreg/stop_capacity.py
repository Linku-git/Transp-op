from __future__ import annotations

import logging
import math
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places using banker's rounding."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_dec(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# HCM 2000 reference parameters
# ---------------------------------------------------------------------------

DEFAULT_DWELL_TIME_S: float = 30.0      # average dwell time (boarding/alighting)
DEFAULT_CLEARANCE_TIME_S: float = 15.0  # time between departures
DEFAULT_CV_DWELL: float = 0.6           # coefficient of variation of dwell time

# Level of Service thresholds (utilization ratio ranges)
LOS_GRADES: dict[str, tuple[float, float]] = {
    "A": (0.0, 0.25),              # free flow
    "B": (0.25, 0.40),             # stable flow
    "C": (0.40, 0.60),             # stable flow, some delays
    "D": (0.60, 0.75),             # approaching instability
    "E": (0.75, 1.00),             # at capacity
    "F": (1.00, float("inf")),     # over capacity
}

LOS_DESCRIPTIONS: dict[str, str] = {
    "A": "Free flow - minimal delays, no queuing",
    "B": "Stable flow - slight delays, occasional short queues",
    "C": "Stable flow - noticeable delays, regular queues form",
    "D": "Approaching instability - significant delays, long queues",
    "E": "At capacity - high delays, persistent queues",
    "F": "Over capacity - severe congestion, excessive delays",
}

# Z-factor lookup for common confidence levels
# Z is the standard normal variable for the desired failure rate
Z_FACTOR_TABLE: dict[str, float] = {
    "50%": 0.000,    # LOS A
    "75%": 0.675,    # LOS B
    "90%": 1.282,    # LOS C
    "95%": 1.645,    # LOS D
    "97.5%": 1.960,  # LOS E (default)
    "99%": 2.326,    # conservative
    "99.5%": 2.576,  # very conservative
}


def get_z_factor(confidence: str) -> float:
    """Return the Z-factor for the given confidence level.

    Args:
        confidence: A string key matching :data:`Z_FACTOR_TABLE`
            (e.g. ``"95%"``, ``"97.5%"``).

    Returns:
        The Z-factor (standard normal variable).

    Raises:
        ValueError: If *confidence* is not a recognised key.
    """
    if confidence not in Z_FACTOR_TABLE:
        raise ValueError(
            f"Unknown confidence level '{confidence}'. "
            f"Valid values: {list(Z_FACTOR_TABLE.keys())}"
        )
    return Z_FACTOR_TABLE[confidence]


# ---------------------------------------------------------------------------
# HCM 2000 stop capacity
# ---------------------------------------------------------------------------

def compute_stop_capacity(
    n_berths: int = 1,
    green_ratio: float = 0.5,
    dwell_time_s: float = DEFAULT_DWELL_TIME_S,
    clearance_time_s: float = DEFAULT_CLEARANCE_TIME_S,
    cv_dwell: float = DEFAULT_CV_DWELL,
    z_factor: float = 1.96,
) -> dict:
    """Compute stop capacity using the HCM 2000 formula.

    Formula::

        Bs = N_berths * 3600 * (g/C) / [t_c + t_d * (g/C) + Z * c_v * t_d]

    Where:

    - ``N_berths``: number of loading berths at the stop
    - ``g/C``: effective green ratio (signal timing); use 1.0 for no signal
    - ``t_c``: clearance time in seconds between successive buses
    - ``t_d``: average dwell time in seconds (boarding + alighting)
    - ``Z``: standard normal variable for desired failure rate
    - ``c_v``: coefficient of variation of dwell time (log-normal)

    Reference: Highway Capacity Manual 2000, Chapter 27 — Transit.

    Args:
        n_berths: Number of loading berths (>= 1).
        green_ratio: Effective green time / cycle ratio.  Use 0.5 for
            unsignalized stops, or the actual g/C for signalized.
            Must be in (0, 1].
        dwell_time_s: Average dwell time in seconds (> 0).
        clearance_time_s: Clearance time in seconds (>= 0).
        cv_dwell: Coefficient of variation of dwell time (>= 0).
        z_factor: Standard normal variable for failure rate.
            Common values: 1.645 (95%), 1.960 (97.5%), 2.326 (99%).

    Returns:
        Dict containing:
        - ``capacity_buses_per_hour`` (float): Maximum throughput Bs.
        - ``effective_dwell_s`` (float): Adjusted dwell time used
          in the denominator.
        - ``n_berths`` (int): Input berth count.
        - ``green_ratio`` (float): Input green ratio.
        - ``z_factor`` (float): Input Z-factor.
        - ``cv_dwell`` (float): Input coefficient of variation.
        - ``clearance_time_s`` (float): Input clearance time.
        - ``dwell_time_s`` (float): Input average dwell time.

    Raises:
        ValueError: If any parameter is outside its valid range.
    """
    # ---- Input validation ---------------------------------------------------
    if n_berths < 1:
        raise ValueError(f"n_berths must be >= 1, got {n_berths}")
    if not (0.0 < green_ratio <= 1.0):
        raise ValueError(
            f"green_ratio must be in (0, 1], got {green_ratio}"
        )
    if dwell_time_s <= 0:
        raise ValueError(f"dwell_time_s must be positive, got {dwell_time_s}")
    if clearance_time_s < 0:
        raise ValueError(
            f"clearance_time_s must be non-negative, got {clearance_time_s}"
        )
    if cv_dwell < 0:
        raise ValueError(f"cv_dwell must be non-negative, got {cv_dwell}")
    if z_factor < 0:
        raise ValueError(f"z_factor must be non-negative, got {z_factor}")

    # ---- HCM 2000 formula ---------------------------------------------------
    n = _to_dec(n_berths)
    g_c = _to_dec(green_ratio)
    t_d = _to_dec(dwell_time_s)
    t_c = _to_dec(clearance_time_s)
    z = _to_dec(z_factor)
    cv = _to_dec(cv_dwell)

    # Effective dwell component = t_d * (g/C) + Z * c_v * t_d
    effective_dwell = t_d * g_c + z * cv * t_d

    # Denominator = t_c + effective_dwell
    denominator = t_c + effective_dwell

    if denominator <= 0:
        raise ValueError(
            f"Denominator is non-positive ({float(denominator)}); "
            f"check input parameters"
        )

    # Bs = N * 3600 * (g/C) / denominator
    capacity = _q(n * Decimal("3600") * g_c / denominator)

    logger.info(
        "HCM 2000 stop capacity: Bs=%.1f buses/hr "
        "(berths=%d, g/C=%.2f, t_d=%.1fs, t_c=%.1fs, Z=%.3f, cv=%.2f)",
        float(capacity),
        n_berths,
        green_ratio,
        dwell_time_s,
        clearance_time_s,
        z_factor,
        cv_dwell,
    )

    return {
        "capacity_buses_per_hour": float(capacity),
        "effective_dwell_s": float(_q(effective_dwell)),
        "n_berths": n_berths,
        "green_ratio": green_ratio,
        "z_factor": z_factor,
        "cv_dwell": cv_dwell,
        "clearance_time_s": clearance_time_s,
        "dwell_time_s": dwell_time_s,
    }


# ---------------------------------------------------------------------------
# Level of Service grading
# ---------------------------------------------------------------------------

def compute_los_grade(
    demand_buses_per_hour: float,
    capacity_buses_per_hour: float,
) -> dict:
    """Grade the Level of Service from A (free flow) to F (over capacity).

    The utilization ratio ``rho = demand / capacity`` is compared against
    the HCM 2000 LOS thresholds.

    Average wait time is estimated using M/G/1 queuing approximation::

        W = rho / (2 * mu * (1 - rho)) * (1 + cv^2)

    For simplicity we assume ``cv^2 = 1`` (Poisson arrivals) and
    ``mu = capacity / 3600`` (service rate per second).

    Args:
        demand_buses_per_hour: Expected bus arrivals per hour (>= 0).
        capacity_buses_per_hour: Stop capacity in buses per hour (> 0).

    Returns:
        Dict containing:
        - ``utilization`` (float): demand / capacity ratio.
        - ``los_grade`` (str): ``"A"`` through ``"F"``.
        - ``description`` (str): Human-readable LOS description.
        - ``avg_wait_seconds`` (float): Estimated average wait time.
        - ``demand_buses_per_hour`` (float): Input demand.
        - ``capacity_buses_per_hour`` (float): Input capacity.

    Raises:
        ValueError: If *capacity_buses_per_hour* is non-positive or
            *demand_buses_per_hour* is negative.
    """
    if capacity_buses_per_hour <= 0:
        raise ValueError(
            f"capacity_buses_per_hour must be positive, got "
            f"{capacity_buses_per_hour}"
        )
    if demand_buses_per_hour < 0:
        raise ValueError(
            f"demand_buses_per_hour must be non-negative, got "
            f"{demand_buses_per_hour}"
        )

    rho = demand_buses_per_hour / capacity_buses_per_hour

    # Determine LOS grade
    grade = "F"
    for g, (lo, hi) in LOS_GRADES.items():
        if lo <= rho < hi:
            grade = g
            break

    description = LOS_DESCRIPTIONS.get(grade, "Unknown")

    # Estimate average wait using M/G/1 approximation
    # W_q = rho / (2 * mu * (1 - rho)) for M/M/1
    # where mu = capacity / 3600 (buses per second)
    if rho < 1.0 and capacity_buses_per_hour > 0:
        mu = capacity_buses_per_hour / 3600.0  # service rate (buses/sec)
        avg_wait = rho / (2.0 * mu * (1.0 - rho))
    elif rho >= 1.0:
        # Over capacity — wait grows unbounded; report a high sentinel value
        # proportional to the degree of over-saturation
        avg_wait = 600.0 * rho  # 10+ minutes baseline, scales with overload
    else:
        avg_wait = 0.0

    logger.info(
        "LOS grade: %s (rho=%.3f, demand=%.1f, capacity=%.1f, "
        "avg_wait=%.1fs)",
        grade,
        rho,
        demand_buses_per_hour,
        capacity_buses_per_hour,
        avg_wait,
    )

    return {
        "utilization": round(rho, 4),
        "los_grade": grade,
        "description": description,
        "avg_wait_seconds": round(avg_wait, 1),
        "demand_buses_per_hour": demand_buses_per_hour,
        "capacity_buses_per_hour": capacity_buses_per_hour,
    }


# ---------------------------------------------------------------------------
# Full stop analysis
# ---------------------------------------------------------------------------

def compute_stop_analysis(
    n_berths: int = 1,
    demand_passengers: int = 50,
    avg_boarding_time_s: float = 3.0,
    vehicle_capacity: int = 40,
    headway_minutes: float = 10.0,
    green_ratio: float = 0.5,
    cv_dwell: float = DEFAULT_CV_DWELL,
    z_factor: float = 1.96,
    clearance_time_s: float = DEFAULT_CLEARANCE_TIME_S,
) -> dict:
    """Full stop capacity analysis combining capacity and LOS.

    This function derives intermediate parameters from higher-level
    operational inputs:

    - **dwell_time** is derived from passenger demand and boarding rate:
      ``t_d = (demand_passengers / demand_buses_per_hour) * avg_boarding_time_s``
      i.e. average passengers per bus multiplied by per-passenger boarding time.
    - **demand_buses_per_hour** is derived from headway:
      ``demand = 60 / headway_minutes``.

    It then calls :func:`compute_stop_capacity` and
    :func:`compute_los_grade`, and appends operational recommendations.

    Args:
        n_berths: Number of loading berths (>= 1).
        demand_passengers: Total passenger demand per hour at this stop.
        avg_boarding_time_s: Average time per passenger to board (seconds).
        vehicle_capacity: Seated + standing capacity per vehicle.
        headway_minutes: Scheduled headway between buses (minutes, > 0).
        green_ratio: Signal timing g/C ratio (use 0.5 for unsignalized).
        cv_dwell: Coefficient of variation of dwell time.
        z_factor: Standard normal variable for failure rate.
        clearance_time_s: Clearance time in seconds.

    Returns:
        Dict containing:
        - ``capacity`` (dict): Output of :func:`compute_stop_capacity`.
        - ``los`` (dict): Output of :func:`compute_los_grade`.
        - ``derived`` (dict): Intermediate computed values:
            - ``demand_buses_per_hour``
            - ``passengers_per_bus``
            - ``dwell_time_s``
            - ``vehicle_load_factor``
        - ``recommendations`` (list[str]): Operational recommendations
          based on the analysis.

    Raises:
        ValueError: If any input is outside its valid range.
    """
    # ---- Input validation ---------------------------------------------------
    if demand_passengers < 0:
        raise ValueError(
            f"demand_passengers must be non-negative, got {demand_passengers}"
        )
    if avg_boarding_time_s <= 0:
        raise ValueError(
            f"avg_boarding_time_s must be positive, got {avg_boarding_time_s}"
        )
    if vehicle_capacity < 1:
        raise ValueError(
            f"vehicle_capacity must be >= 1, got {vehicle_capacity}"
        )
    if headway_minutes <= 0:
        raise ValueError(
            f"headway_minutes must be positive, got {headway_minutes}"
        )

    # ---- Derive intermediate parameters ------------------------------------
    demand_buses_per_hour = 60.0 / headway_minutes

    # Passengers per bus = total demand / buses per hour
    if demand_buses_per_hour > 0:
        passengers_per_bus = demand_passengers / demand_buses_per_hour
    else:
        passengers_per_bus = 0.0

    # Dwell time = passengers_per_bus * boarding_time_per_passenger
    dwell_time_s = passengers_per_bus * avg_boarding_time_s

    # Enforce a minimum dwell time (vehicle must at least stop)
    dwell_time_s = max(dwell_time_s, 5.0)

    # Vehicle load factor
    if vehicle_capacity > 0:
        load_factor = passengers_per_bus / vehicle_capacity
    else:
        load_factor = 0.0

    # ---- Compute capacity ---------------------------------------------------
    capacity_result = compute_stop_capacity(
        n_berths=n_berths,
        green_ratio=green_ratio,
        dwell_time_s=dwell_time_s,
        clearance_time_s=clearance_time_s,
        cv_dwell=cv_dwell,
        z_factor=z_factor,
    )

    # ---- Compute LOS --------------------------------------------------------
    los_result = compute_los_grade(
        demand_buses_per_hour=demand_buses_per_hour,
        capacity_buses_per_hour=capacity_result["capacity_buses_per_hour"],
    )

    # ---- Generate recommendations -------------------------------------------
    recommendations: list[str] = []

    rho = los_result["utilization"]
    grade = los_result["los_grade"]

    if grade in ("E", "F"):
        recommendations.append(
            f"LOS {grade}: stop is {'at' if grade == 'E' else 'over'} capacity. "
            f"Consider adding berths (currently {n_berths})."
        )

    if grade == "F":
        # Calculate how many berths would be needed
        needed_capacity = demand_buses_per_hour / 0.70  # target LOS C/D boundary
        current_per_berth = (
            capacity_result["capacity_buses_per_hour"] / n_berths
        )
        if current_per_berth > 0:
            needed_berths = math.ceil(needed_capacity / current_per_berth)
            recommendations.append(
                f"Recommend increasing to {needed_berths} berths "
                f"to achieve LOS D or better."
            )

    if load_factor > 1.0:
        recommendations.append(
            f"Vehicle overloaded: {passengers_per_bus:.0f} passengers "
            f"vs {vehicle_capacity} capacity (load factor {load_factor:.2f}). "
            f"Consider higher-capacity vehicles or shorter headways."
        )
    elif load_factor > 0.85:
        recommendations.append(
            f"Vehicle near capacity: load factor {load_factor:.2f}. "
            f"Monitor for peak-hour overloading."
        )

    if rho < 0.25 and n_berths > 1:
        recommendations.append(
            f"LOS A with {n_berths} berths: stop is significantly "
            f"over-provisioned. Consider reducing to "
            f"{max(1, n_berths - 1)} berths to optimize infrastructure cost."
        )

    if dwell_time_s > 60.0:
        recommendations.append(
            f"High dwell time ({dwell_time_s:.0f}s): consider "
            f"all-door boarding or pre-payment to reduce boarding time."
        )

    if not recommendations:
        recommendations.append(
            f"LOS {grade}: stop operating within acceptable parameters."
        )

    derived = {
        "demand_buses_per_hour": round(demand_buses_per_hour, 2),
        "passengers_per_bus": round(passengers_per_bus, 1),
        "dwell_time_s": round(dwell_time_s, 1),
        "vehicle_load_factor": round(load_factor, 3),
    }

    logger.info(
        "Stop analysis complete: LOS=%s, rho=%.3f, Bs=%.1f buses/hr, "
        "demand=%.1f buses/hr, dwell=%.1fs, load_factor=%.2f",
        grade,
        rho,
        capacity_result["capacity_buses_per_hour"],
        demand_buses_per_hour,
        dwell_time_s,
        load_factor,
    )

    return {
        "capacity": capacity_result,
        "los": los_result,
        "derived": derived,
        "recommendations": recommendations,
    }
