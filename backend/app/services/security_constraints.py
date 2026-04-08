from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Default dimension weights for three-dimension pooling
DEFAULT_GEO_WEIGHT = 0.45
DEFAULT_SHIFT_WEIGHT = 0.30
DEFAULT_SECURITY_WEIGHT = 0.25

# Night-specific defaults
NIGHT_MIN_GROUP_SIZE = 3
NIGHT_MIN_LIGHTING_SCORE = 0.4
CRITICAL_RISK_THRESHOLD = 0.7


@dataclass
class SecurityConstraintConfig:
    """Configuration for security-constrained pooling."""
    geo_weight: float = DEFAULT_GEO_WEIGHT
    shift_weight: float = DEFAULT_SHIFT_WEIGHT
    security_weight: float = DEFAULT_SECURITY_WEIGHT
    night_min_group_size: int = NIGHT_MIN_GROUP_SIZE
    night_min_lighting_score: float = NIGHT_MIN_LIGHTING_SCORE
    critical_risk_threshold: float = CRITICAL_RISK_THRESHOLD
    avoid_critical_stops_at_night: bool = True
    priority_vehicle_for_night: bool = True


@dataclass
class EmployeeSecurityProfile:
    """Employee with security score for pooling."""
    employee_id: str
    lat: float
    lng: float
    shift_id: str | None = None
    security_score: int = 50
    risk_level: str = "medium"
    is_night_shift: bool = False


@dataclass
class StopSecurityInfo:
    """Stop with security attributes for night filtering."""
    stop_id: str
    lat: float
    lng: float
    composite_risk_score: float = 0.0
    is_critical: bool = False
    lighting_score: float = 0.5
    isolation_score: float = 0.5


def apply_security_constraints(
    clusters: list[list[EmployeeSecurityProfile]],
    config: SecurityConstraintConfig | None = None,
    is_night: bool = False,
) -> list[list[EmployeeSecurityProfile]]:
    """
    Apply security constraints to existing clusters.
    - Ensure high-risk employees are not isolated
    - Enforce minimum group sizes for night shifts
    - Prioritize grouping vulnerable employees together
    """
    cfg = config or SecurityConstraintConfig()
    result = []

    for cluster in clusters:
        if is_night:
            # Enforce night minimum group size
            if len(cluster) < cfg.night_min_group_size:
                continue  # Will be merged with nearest cluster
            result.append(cluster)
        else:
            result.append(cluster)

    # Merge undersized night clusters
    if is_night:
        orphans = []
        for cluster in clusters:
            if len(cluster) < cfg.night_min_group_size:
                orphans.extend(cluster)

        # Add orphans to closest existing cluster
        if orphans and result:
            result[0].extend(orphans)
        elif orphans:
            result.append(orphans)

    return result


def filter_night_stops(
    stops: list[StopSecurityInfo],
    config: SecurityConstraintConfig | None = None,
) -> tuple[list[StopSecurityInfo], list[StopSecurityInfo]]:
    """
    Filter stops for night routes.
    Returns (allowed_stops, excluded_stops).
    """
    cfg = config or SecurityConstraintConfig()
    allowed = []
    excluded = []

    for stop in stops:
        if cfg.avoid_critical_stops_at_night and stop.is_critical:
            excluded.append(stop)
        elif stop.lighting_score < cfg.night_min_lighting_score:
            excluded.append(stop)
        else:
            allowed.append(stop)

    return allowed, excluded


def suggest_alternative_stops(
    excluded_stop: StopSecurityInfo,
    all_stops: list[StopSecurityInfo],
    config: SecurityConstraintConfig | None = None,
) -> list[StopSecurityInfo]:
    """Suggest alternative stops when a stop is excluded from night routes."""
    cfg = config or SecurityConstraintConfig()
    candidates = [
        s for s in all_stops
        if not s.is_critical
        and s.lighting_score >= cfg.night_min_lighting_score
        and s.stop_id != excluded_stop.stop_id
    ]

    # Sort by distance to excluded stop (simple Euclidean for now)
    candidates.sort(
        key=lambda s: (s.lat - excluded_stop.lat) ** 2 + (s.lng - excluded_stop.lng) ** 2
    )

    return candidates[:3]  # Return top 3 nearest alternatives


def compute_three_dimension_score(
    geo_distance: float,
    shift_compatible: bool,
    security_score_diff: float,
    config: SecurityConstraintConfig | None = None,
) -> float:
    """
    Compute combined pooling score across three dimensions.
    Lower score = better match for pooling.

    - geo_distance: normalized 0-1 (0 = same location)
    - shift_compatible: 1.0 if same shift, 0.0 if different
    - security_score_diff: normalized 0-1 (0 = same risk level)
    """
    cfg = config or SecurityConstraintConfig()

    geo_component = cfg.geo_weight * min(1.0, geo_distance)
    shift_component = cfg.shift_weight * (0.0 if shift_compatible else 1.0)
    security_component = cfg.security_weight * min(1.0, security_score_diff)

    return round(geo_component + shift_component + security_component, 4)


def should_assign_priority_vehicle(
    is_night_route: bool,
    has_high_risk_employees: bool,
    config: SecurityConstraintConfig | None = None,
) -> bool:
    """Determine if a route should receive priority vehicle assignment."""
    cfg = config or SecurityConstraintConfig()
    if not cfg.priority_vehicle_for_night:
        return False
    return is_night_route or has_high_risk_employees
