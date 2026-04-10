from __future__ import annotations

import logging
import math
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _q(value: Decimal, places: str = "0.01") -> Decimal:
    """Round to *places* decimal places using banker's rounding."""
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def _to_dec(value: float | int | str) -> Decimal:
    """Convert a numeric value to Decimal via string to avoid float artifacts."""
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# KPI thresholds from CDC SOTREG v5.0
# ---------------------------------------------------------------------------

OTP_THRESHOLD_SECONDS: float = 90.0      # On-time if |actual - scheduled| < 90s
OTP_TARGET_PCT: float = 95.0             # Target OTP > 95%
HEADWAY_COV_TARGET: float = 0.30         # Target COV < 0.30
METRIC_TYPES: list[str] = ["otp", "headway_cov", "load_factor", "commercial_speed"]
PERIOD_TYPES: list[str] = ["daily", "weekly", "monthly"]


# ---------------------------------------------------------------------------
# OTP — On-Time Performance
# ---------------------------------------------------------------------------

def compute_otp(
    arrivals: list[dict],
    threshold_seconds: float = OTP_THRESHOLD_SECONDS,
) -> dict:
    """Compute On-Time Performance (OTP) from arrival data.

    Each arrival dict must contain::

        {
            "scheduled_time": datetime,
            "actual_time": datetime,
            "stop_id": str,          # optional, for traceability
        }

    OTP is the percentage of arrivals where the absolute difference between
    actual and scheduled time is strictly less than *threshold_seconds*.

    Args:
        arrivals: List of arrival observations.
        threshold_seconds: Maximum acceptable deviation in seconds.  Defaults
            to 90 s per CDC SOTREG v5.0.

    Returns:
        Dict with:
        - ``otp_pct`` -- float (0--100)
        - ``total_arrivals`` -- int
        - ``on_time_count`` -- int
        - ``late_count`` -- int (arrived more than *threshold* after schedule)
        - ``early_count`` -- int (arrived more than *threshold* before schedule)
        - ``avg_delay_seconds`` -- float (signed: positive = late)
        - ``max_delay_seconds`` -- float (absolute)
        - ``meets_target`` -- bool (otp_pct >= 95)
        - ``threshold_seconds`` -- float
    """
    if not arrivals:
        logger.warning("compute_otp called with empty arrivals list")
        return {
            "otp_pct": 0.0,
            "total_arrivals": 0,
            "on_time_count": 0,
            "late_count": 0,
            "early_count": 0,
            "avg_delay_seconds": 0.0,
            "max_delay_seconds": 0.0,
            "meets_target": False,
            "threshold_seconds": threshold_seconds,
        }

    on_time = 0
    late = 0
    early = 0
    delays: list[float] = []

    for arrival in arrivals:
        scheduled: datetime = arrival["scheduled_time"]
        actual: datetime = arrival["actual_time"]
        delta_seconds = (actual - scheduled).total_seconds()
        abs_delta = abs(delta_seconds)
        delays.append(delta_seconds)

        if abs_delta < threshold_seconds:
            on_time += 1
        elif delta_seconds > 0:
            late += 1
        else:
            early += 1

    total = len(arrivals)
    otp_pct = float(_q(_to_dec(on_time) / _to_dec(total) * _to_dec(100)))
    avg_delay = float(_q(_to_dec(sum(delays)) / _to_dec(total)))
    max_delay = float(_q(_to_dec(max(abs(d) for d in delays))))

    meets = otp_pct >= OTP_TARGET_PCT

    logger.info(
        "OTP computed: %.1f%% (%d/%d on-time, threshold=%ss, target=%s)",
        otp_pct,
        on_time,
        total,
        threshold_seconds,
        "MET" if meets else "NOT MET",
    )

    return {
        "otp_pct": otp_pct,
        "total_arrivals": total,
        "on_time_count": on_time,
        "late_count": late,
        "early_count": early,
        "avg_delay_seconds": avg_delay,
        "max_delay_seconds": max_delay,
        "meets_target": meets,
        "threshold_seconds": threshold_seconds,
    }


# ---------------------------------------------------------------------------
# Headway COV — Regularity metric
# ---------------------------------------------------------------------------

def compute_headway_cov(
    departure_times: list[datetime],
) -> dict:
    """Compute Coefficient of Variation of headway (regularity metric).

    COV = std_dev(headways) / mean(headways)

    A low COV indicates regular, predictable service.  The CDC SOTREG v5.0
    target is COV < 0.30.

    Args:
        departure_times: Chronologically ordered departure datetimes.  The
            function will sort them internally for safety.

    Returns:
        Dict with:
        - ``cov`` -- float (0.0+; lower is better)
        - ``mean_headway_seconds`` -- float
        - ``std_headway_seconds`` -- float
        - ``min_headway_seconds`` -- float
        - ``max_headway_seconds`` -- float
        - ``headway_count`` -- int (number of inter-departure intervals)
        - ``meets_target`` -- bool (cov < 0.30)
    """
    if len(departure_times) < 2:
        logger.warning(
            "compute_headway_cov called with %d departure(s); need >= 2",
            len(departure_times),
        )
        return {
            "cov": 0.0,
            "mean_headway_seconds": 0.0,
            "std_headway_seconds": 0.0,
            "min_headway_seconds": 0.0,
            "max_headway_seconds": 0.0,
            "headway_count": 0,
            "meets_target": True,
        }

    sorted_times = sorted(departure_times)
    headways: list[float] = [
        (sorted_times[i + 1] - sorted_times[i]).total_seconds()
        for i in range(len(sorted_times) - 1)
    ]

    n = len(headways)
    mean_hw = sum(headways) / n
    min_hw = min(headways)
    max_hw = max(headways)

    if mean_hw == 0.0:
        # All departures at the same instant -- degenerate case
        logger.warning(
            "compute_headway_cov: mean headway is zero (all departures simultaneous)"
        )
        return {
            "cov": 0.0,
            "mean_headway_seconds": 0.0,
            "std_headway_seconds": 0.0,
            "min_headway_seconds": 0.0,
            "max_headway_seconds": 0.0,
            "headway_count": n,
            "meets_target": True,
        }

    # Population standard deviation (we have all observations, not a sample)
    variance = sum((h - mean_hw) ** 2 for h in headways) / n
    std_hw = math.sqrt(variance)
    cov = std_hw / mean_hw

    cov_rounded = float(_q(_to_dec(cov), "0.0001"))
    mean_rounded = float(_q(_to_dec(mean_hw)))
    std_rounded = float(_q(_to_dec(std_hw)))
    min_rounded = float(_q(_to_dec(min_hw)))
    max_rounded = float(_q(_to_dec(max_hw)))

    meets = cov_rounded < HEADWAY_COV_TARGET

    logger.info(
        "Headway COV computed: %.4f (mean=%.1fs, std=%.1fs, n=%d, target=%s)",
        cov_rounded,
        mean_rounded,
        std_rounded,
        n,
        "MET" if meets else "NOT MET",
    )

    return {
        "cov": cov_rounded,
        "mean_headway_seconds": mean_rounded,
        "std_headway_seconds": std_rounded,
        "min_headway_seconds": min_rounded,
        "max_headway_seconds": max_rounded,
        "headway_count": n,
        "meets_target": meets,
    }


# ---------------------------------------------------------------------------
# Load Factor
# ---------------------------------------------------------------------------

def compute_load_factor(
    observations: list[dict],
) -> dict:
    """Compute average load factor from passenger count observations.

    Each observation dict must contain::

        {
            "passenger_count": int,
            "vehicle_capacity": int,
        }

    Load factor for a single observation is
    ``passenger_count / vehicle_capacity``.  Observations with
    ``vehicle_capacity <= 0`` are skipped with a warning.

    Args:
        observations: List of passenger-count snapshots.

    Returns:
        Dict with:
        - ``load_factor`` -- float (0.0 to 1.0+; >1.0 means overcrowded)
        - ``avg_passengers`` -- float
        - ``avg_capacity`` -- float
        - ``peak_load_factor`` -- float (max observed)
        - ``min_load_factor`` -- float (min observed)
        - ``observation_count`` -- int (valid observations used)
    """
    if not observations:
        logger.warning("compute_load_factor called with empty observations list")
        return {
            "load_factor": 0.0,
            "avg_passengers": 0.0,
            "avg_capacity": 0.0,
            "peak_load_factor": 0.0,
            "min_load_factor": 0.0,
            "observation_count": 0,
        }

    factors: list[Decimal] = []
    total_passengers = Decimal("0")
    total_capacity = Decimal("0")
    skipped = 0

    for obs in observations:
        capacity = obs.get("vehicle_capacity", 0)
        passengers = obs.get("passenger_count", 0)

        if capacity <= 0:
            logger.warning(
                "Skipping observation with invalid capacity: %s", capacity
            )
            skipped += 1
            continue

        pax = _to_dec(passengers)
        cap = _to_dec(capacity)
        factors.append(pax / cap)
        total_passengers += pax
        total_capacity += cap

    valid_count = len(factors)

    if valid_count == 0:
        logger.warning(
            "compute_load_factor: all %d observations had invalid capacity",
            skipped,
        )
        return {
            "load_factor": 0.0,
            "avg_passengers": 0.0,
            "avg_capacity": 0.0,
            "peak_load_factor": 0.0,
            "min_load_factor": 0.0,
            "observation_count": 0,
        }

    avg_lf = _q(sum(factors) / _to_dec(valid_count), "0.0001")
    peak_lf = _q(max(factors), "0.0001")
    min_lf = _q(min(factors), "0.0001")
    avg_pax = _q(total_passengers / _to_dec(valid_count))
    avg_cap = _q(total_capacity / _to_dec(valid_count))

    logger.info(
        "Load factor computed: avg=%.4f, peak=%.4f, min=%.4f (%d obs, %d skipped)",
        float(avg_lf),
        float(peak_lf),
        float(min_lf),
        valid_count,
        skipped,
    )

    return {
        "load_factor": float(avg_lf),
        "avg_passengers": float(avg_pax),
        "avg_capacity": float(avg_cap),
        "peak_load_factor": float(peak_lf),
        "min_load_factor": float(min_lf),
        "observation_count": valid_count,
    }


# ---------------------------------------------------------------------------
# Commercial Speed
# ---------------------------------------------------------------------------

def compute_commercial_speed(
    trips: list[dict],
) -> dict:
    """Compute commercial speed from trip data.

    Each trip dict supports two formats:

    **Format A** (pre-computed duration)::

        {"distance_km": float, "duration_hours": float}

    **Format B** (start/end timestamps)::

        {"distance_km": float, "start_time": datetime, "end_time": datetime}

    If ``duration_hours`` is present it takes precedence.  Trips with zero
    or negative distance or duration are skipped with a warning.

    Args:
        trips: List of trip observations.

    Returns:
        Dict with:
        - ``commercial_speed_kmh`` -- float (total_distance / total_hours)
        - ``total_distance_km`` -- float
        - ``total_hours`` -- float
        - ``trip_count`` -- int (valid trips used)
        - ``min_speed_kmh`` -- float
        - ``max_speed_kmh`` -- float
    """
    if not trips:
        logger.warning("compute_commercial_speed called with empty trips list")
        return {
            "commercial_speed_kmh": 0.0,
            "total_distance_km": 0.0,
            "total_hours": 0.0,
            "trip_count": 0,
            "min_speed_kmh": 0.0,
            "max_speed_kmh": 0.0,
        }

    total_distance = Decimal("0")
    total_hours = Decimal("0")
    speeds: list[Decimal] = []
    skipped = 0

    for trip in trips:
        distance_km = trip.get("distance_km", 0)
        if distance_km is None or float(distance_km) <= 0:
            logger.warning(
                "Skipping trip with invalid distance_km: %s", distance_km
            )
            skipped += 1
            continue

        # Resolve duration
        duration_hours: float | None = trip.get("duration_hours")
        if duration_hours is None:
            start_time: datetime | None = trip.get("start_time")
            end_time: datetime | None = trip.get("end_time")
            if start_time is not None and end_time is not None:
                delta_seconds = (end_time - start_time).total_seconds()
                if delta_seconds <= 0:
                    logger.warning(
                        "Skipping trip with non-positive duration: %.1fs",
                        delta_seconds,
                    )
                    skipped += 1
                    continue
                duration_hours = delta_seconds / 3600.0
            else:
                logger.warning(
                    "Skipping trip without duration_hours or start/end times"
                )
                skipped += 1
                continue

        if duration_hours <= 0:
            logger.warning(
                "Skipping trip with non-positive duration_hours: %s",
                duration_hours,
            )
            skipped += 1
            continue

        dist = _to_dec(distance_km)
        dur = _to_dec(duration_hours)
        speed = dist / dur

        total_distance += dist
        total_hours += dur
        speeds.append(speed)

    valid_count = len(speeds)

    if valid_count == 0:
        logger.warning(
            "compute_commercial_speed: all %d trips were invalid", skipped
        )
        return {
            "commercial_speed_kmh": 0.0,
            "total_distance_km": 0.0,
            "total_hours": 0.0,
            "trip_count": 0,
            "min_speed_kmh": 0.0,
            "max_speed_kmh": 0.0,
        }

    commercial_speed = _q(total_distance / total_hours)
    min_speed = _q(min(speeds))
    max_speed = _q(max(speeds))

    logger.info(
        "Commercial speed computed: %.2f km/h "
        "(total=%.1f km in %.2f h, %d trips, %d skipped)",
        float(commercial_speed),
        float(_q(total_distance)),
        float(_q(total_hours)),
        valid_count,
        skipped,
    )

    return {
        "commercial_speed_kmh": float(commercial_speed),
        "total_distance_km": float(_q(total_distance)),
        "total_hours": float(_q(total_hours)),
        "trip_count": valid_count,
        "min_speed_kmh": float(min_speed),
        "max_speed_kmh": float(max_speed),
    }


# ---------------------------------------------------------------------------
# Batch compute — all KPIs at once
# ---------------------------------------------------------------------------

def compute_all_kpis(
    arrivals: list[dict] | None = None,
    departure_times: list[datetime] | None = None,
    load_observations: list[dict] | None = None,
    trips: list[dict] | None = None,
    threshold_seconds: float = OTP_THRESHOLD_SECONDS,
) -> dict:
    """Compute all available KPIs from the provided data sets.

    Only KPIs whose corresponding data is supplied (non-None and non-empty)
    are computed.  The result always includes ``computed_at`` and a ``summary``
    with an overall health score.

    Args:
        arrivals: Arrival observations for OTP.
        departure_times: Departure datetimes for headway COV.
        load_observations: Passenger count observations for load factor.
        trips: Trip observations for commercial speed.
        threshold_seconds: OTP threshold (passed through to
            :func:`compute_otp`).

    Returns:
        Dict with optional keys ``otp``, ``headway_cov``, ``load_factor``,
        ``commercial_speed`` (each present only when data was provided),
        plus ``computed_at`` (ISO 8601) and ``summary``.
    """
    result: dict = {}
    scores: list[float] = []

    # ---- OTP ---------------------------------------------------------------
    if arrivals:
        otp = compute_otp(arrivals, threshold_seconds=threshold_seconds)
        result["otp"] = otp
        # Score: OTP percentage normalised to 0-100
        scores.append(min(otp["otp_pct"], 100.0))

    # ---- Headway COV -------------------------------------------------------
    if departure_times and len(departure_times) >= 2:
        hw = compute_headway_cov(departure_times)
        result["headway_cov"] = hw
        # Score: transform COV to 0-100 where 0.0 COV = 100, COV >= 1.0 = 0
        cov_score = max(0.0, (1.0 - hw["cov"]) * 100.0)
        scores.append(min(cov_score, 100.0))

    # ---- Load Factor -------------------------------------------------------
    if load_observations:
        lf = compute_load_factor(load_observations)
        result["load_factor"] = lf
        # Score: ideal load factor is 0.6-0.8; penalise <0.3 or >1.0
        lf_val = lf["load_factor"]
        if 0.3 <= lf_val <= 1.0:
            lf_score = 100.0
        elif lf_val < 0.3:
            # Under-utilised: linear scale 0 -> 0, 0.3 -> 100
            lf_score = (lf_val / 0.3) * 100.0
        else:
            # Overcrowded: linear decay 1.0 -> 100, 1.5 -> 0
            lf_score = max(0.0, (1.5 - lf_val) / 0.5 * 100.0)
        scores.append(min(lf_score, 100.0))

    # ---- Commercial Speed --------------------------------------------------
    if trips:
        cs = compute_commercial_speed(trips)
        result["commercial_speed"] = cs
        # Score: 15-50 km/h is good for urban transport; <5 or >80 penalised
        speed = cs["commercial_speed_kmh"]
        if 15.0 <= speed <= 50.0:
            cs_score = 100.0
        elif speed < 15.0:
            cs_score = max(0.0, (speed / 15.0) * 100.0)
        else:
            # >50 km/h is unusual for personnel transport, mild penalty
            cs_score = max(0.0, 100.0 - (speed - 50.0) * 2.0)
        scores.append(min(cs_score, 100.0))

    # ---- Summary -----------------------------------------------------------
    if scores:
        overall_score = float(_q(_to_dec(sum(scores) / len(scores))))
    else:
        overall_score = 0.0

    kpis_computed = [k for k in METRIC_TYPES if k in result]
    targets_met = sum(
        1
        for k in kpis_computed
        if result[k].get("meets_target", True)
    )

    result["computed_at"] = datetime.utcnow().isoformat()
    result["summary"] = {
        "overall_score": overall_score,
        "kpis_computed": kpis_computed,
        "kpi_count": len(kpis_computed),
        "targets_met": targets_met,
        "targets_total": len(kpis_computed),
        "health": (
            "excellent" if overall_score >= 90.0
            else "good" if overall_score >= 75.0
            else "fair" if overall_score >= 50.0
            else "poor"
        ),
    }

    logger.info(
        "All KPIs computed: score=%.1f, health=%s, %d/%d targets met",
        overall_score,
        result["summary"]["health"],
        targets_met,
        len(kpis_computed),
    )

    return result
