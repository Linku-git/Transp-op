from __future__ import annotations

import logging
import math
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ligne import Ligne

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Moroccan urban calibration defaults
# ---------------------------------------------------------------------------
DEFAULT_BETA: float = 0.08  # Calibrated for Moroccan urban commute (~12km avg)
DEFAULT_K: float = 0.001  # Scaling factor


# ---------------------------------------------------------------------------
# Haversine distance (local implementation — intentionally not shared)
# ---------------------------------------------------------------------------
def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return the great-circle distance in km between two points."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------------------------------------------------------------------------
# Core gravity model functions
# ---------------------------------------------------------------------------
def compute_gravity_flow(
    pop_i: float,
    pop_j: float,
    distance_km: float,
    beta: float = DEFAULT_BETA,
    k: float = DEFAULT_K,
) -> float:
    """Compute the gravity flow between two zones.

    Wilson 1967 gravity model:
        T_ij = k * P_i * P_j * f(d_ij)
    where:
        f(d_ij) = exp(-beta * d_ij)

    Args:
        pop_i: Population (or demand proxy) at origin.
        pop_j: Population (or demand proxy) at destination.
        distance_km: Distance between origin and destination in km.
        beta: Distance decay parameter.
        k: Scaling constant.

    Returns:
        Estimated flow value (non-negative float).
    """
    if distance_km < 0:
        raise ValueError(f"distance_km must be non-negative, got {distance_km}")
    if pop_i <= 0 or pop_j <= 0:
        return 0.0

    impedance = math.exp(-beta * distance_km)
    flow = k * pop_i * pop_j * impedance
    return flow


def compute_od_matrix(
    zones: list[dict],
    beta: float = DEFAULT_BETA,
    k: float = DEFAULT_K,
) -> list[dict]:
    """Compute a full NxN origin-destination matrix using the gravity model.

    Args:
        zones: List of zone dicts, each with keys:
            ``id``, ``name``, ``lat``, ``lng``, ``population``.
        beta: Distance decay parameter.
        k: Scaling constant.

    Returns:
        List of OD pair dicts with ``origin_id``, ``dest_id``,
        ``origin_name``, ``dest_name``, ``distance_km``,
        ``flow_estimate``, ``gravity_score``.
    """
    if not zones:
        return []

    od_pairs: list[dict] = []
    n = len(zones)

    # Pre-validate zone structure
    for z in zones:
        for key in ("id", "name", "lat", "lng", "population"):
            if key not in z:
                raise ValueError(f"Zone dict missing required key '{key}': {z}")

    # Compute total flow for normalization (gravity_score)
    max_flow = 0.0

    # First pass: compute all flows
    raw_pairs: list[tuple[dict, dict, float, float]] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue  # skip self-flows

            zi = zones[i]
            zj = zones[j]
            distance = _haversine_km(zi["lat"], zi["lng"], zj["lat"], zj["lng"])
            flow = compute_gravity_flow(
                pop_i=float(zi["population"]),
                pop_j=float(zj["population"]),
                distance_km=distance,
                beta=beta,
                k=k,
            )
            raw_pairs.append((zi, zj, distance, flow))
            if flow > max_flow:
                max_flow = flow

    # Second pass: build output with normalized gravity_score
    for zi, zj, distance, flow in raw_pairs:
        gravity_score = (flow / max_flow * 100.0) if max_flow > 0 else 0.0

        od_pairs.append(
            {
                "origin_id": str(zi["id"]),
                "dest_id": str(zj["id"]),
                "origin_name": zi["name"],
                "dest_name": zj["name"],
                "distance_km": round(distance, 2),
                "flow_estimate": round(flow, 6),
                "gravity_score": round(gravity_score, 2),
            }
        )

    logger.info(
        "Computed OD matrix: %d zones -> %d pairs, max_flow=%.6f",
        n,
        len(od_pairs),
        max_flow,
    )
    return od_pairs


# ---------------------------------------------------------------------------
# Database-driven OD computation from lignes
# ---------------------------------------------------------------------------
async def compute_od_from_lignes(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    beta: float = DEFAULT_BETA,
    k: float = DEFAULT_K,
) -> list[dict]:
    """Compute an OD matrix from active transport lignes.

    Each ligne's origin and destination become zones in the gravity model.
    ``passenger_count_avg`` is used as the population proxy (defaults to 30
    if null).

    Args:
        db: Async database session.
        tenant_id: Tenant UUID.
        beta: Distance decay parameter.
        k: Scaling constant.

    Returns:
        List of OD pair dicts (same format as ``compute_od_matrix``) with
        an additional ``ligne_id`` field.
    """
    stmt = select(Ligne).where(
        Ligne.tenant_id == tenant_id,
        Ligne.is_active.is_(True),
    )
    result = await db.execute(stmt)
    lignes = result.scalars().all()

    if not lignes:
        logger.info("No active lignes found for tenant %s", tenant_id)
        return []

    od_pairs: list[dict] = []
    max_flow = 0.0

    # First pass: compute flows for all lignes
    raw_entries: list[tuple[Ligne, float, float]] = []
    for ligne in lignes:
        pop = float(ligne.passenger_count_avg or 30)
        distance = _haversine_km(
            ligne.origin_lat,
            ligne.origin_lng,
            ligne.dest_lat,
            ligne.dest_lng,
        )
        flow = compute_gravity_flow(
            pop_i=pop,
            pop_j=pop,
            distance_km=distance,
            beta=beta,
            k=k,
        )
        raw_entries.append((ligne, distance, flow))
        if flow > max_flow:
            max_flow = flow

    # Second pass: build output with normalized gravity_score
    for ligne, distance, flow in raw_entries:
        gravity_score = (flow / max_flow * 100.0) if max_flow > 0 else 0.0

        od_pairs.append(
            {
                "ligne_id": str(ligne.id),
                "origin_id": str(ligne.id) + "_origin",
                "dest_id": str(ligne.id) + "_dest",
                "origin_name": f"{ligne.name} (origin)",
                "dest_name": f"{ligne.name} (dest)",
                "distance_km": round(distance, 2),
                "flow_estimate": round(flow, 6),
                "gravity_score": round(gravity_score, 2),
            }
        )

    logger.info(
        "Computed OD matrix from %d lignes for tenant %s, max_flow=%.6f",
        len(lignes),
        tenant_id,
        max_flow,
    )
    return od_pairs


# ---------------------------------------------------------------------------
# Beta calibration (least squares stub)
# ---------------------------------------------------------------------------
def calibrate_beta(
    observed_distances: list[float],
    observed_flows: list[float],
) -> float:
    """Calibrate the beta parameter using simple least-squares regression.

    Fits beta in the impedance function f(d) = exp(-beta * d) by taking
    the log transform: ln(flow) = ln(k*Pi*Pj) - beta*d, then solving
    for the slope via linear regression on (d, ln(flow)).

    If calibration fails (e.g., insufficient data, zero/negative flows),
    returns ``DEFAULT_BETA``.

    Args:
        observed_distances: List of observed distances in km.
        observed_flows: List of observed flow values (must be >0).

    Returns:
        Calibrated beta value (positive float).
    """
    if len(observed_distances) != len(observed_flows):
        raise ValueError(
            "observed_distances and observed_flows must have equal length"
        )

    n = len(observed_distances)
    if n < 2:
        logger.warning(
            "Insufficient data for beta calibration (%d points), "
            "returning default %.4f",
            n,
            DEFAULT_BETA,
        )
        return DEFAULT_BETA

    # Filter out non-positive flows (cannot take log)
    valid_pairs = [
        (d, f)
        for d, f in zip(observed_distances, observed_flows)
        if f > 0 and d >= 0
    ]

    if len(valid_pairs) < 2:
        logger.warning(
            "Insufficient valid data points for beta calibration, "
            "returning default %.4f",
            DEFAULT_BETA,
        )
        return DEFAULT_BETA

    # Linear regression: ln(flow) = intercept - beta * distance
    # We solve for slope = -beta using ordinary least squares
    distances = [p[0] for p in valid_pairs]
    log_flows = [math.log(p[1]) for p in valid_pairs]
    n_valid = len(valid_pairs)

    mean_d = sum(distances) / n_valid
    mean_lf = sum(log_flows) / n_valid

    # Covariance(d, ln(flow)) and variance(d)
    cov_d_lf = sum(
        (distances[i] - mean_d) * (log_flows[i] - mean_lf)
        for i in range(n_valid)
    )
    var_d = sum((distances[i] - mean_d) ** 2 for i in range(n_valid))

    if var_d < 1e-12:
        logger.warning(
            "Zero variance in distances, returning default beta %.4f",
            DEFAULT_BETA,
        )
        return DEFAULT_BETA

    slope = cov_d_lf / var_d
    # slope = -beta, so beta = -slope
    beta = -slope

    # Ensure beta is positive and reasonable
    if beta <= 0:
        logger.warning(
            "Calibrated beta is non-positive (%.4f), using default %.4f",
            beta,
            DEFAULT_BETA,
        )
        return DEFAULT_BETA

    # Clamp to a reasonable range [0.001, 1.0]
    beta = max(0.001, min(1.0, beta))

    logger.info(
        "Beta calibrated from %d data points: beta=%.4f (slope=%.4f)",
        n_valid,
        beta,
        slope,
    )
    return beta
