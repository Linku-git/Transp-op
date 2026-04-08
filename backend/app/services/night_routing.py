from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.security_constraints import (
    SecurityConstraintConfig,
    StopSecurityInfo,
    filter_night_stops,
    suggest_alternative_stops,
)

logger = logging.getLogger(__name__)


@dataclass
class NightRouteResult:
    """Result of night route processing."""
    route_stops: list[StopSecurityInfo]
    excluded_stops: list[StopSecurityInfo]
    alternatives: dict[str, list[StopSecurityInfo]]  # excluded_stop_id -> alternatives
    is_valid: bool
    warnings: list[str]


def process_night_route(
    route_stops: list[StopSecurityInfo],
    all_available_stops: list[StopSecurityInfo],
    config: SecurityConstraintConfig | None = None,
) -> NightRouteResult:
    """
    Process a route for night hours:
    1. Filter out critical/poorly-lit stops
    2. Find alternatives for excluded stops
    3. Validate minimum safety requirements
    """
    cfg = config or SecurityConstraintConfig()
    warnings: list[str] = []

    # Filter stops
    allowed, excluded = filter_night_stops(route_stops, cfg)

    # Find alternatives for excluded stops
    alternatives: dict[str, list[StopSecurityInfo]] = {}
    for stop in excluded:
        alts = suggest_alternative_stops(stop, all_available_stops, cfg)
        alternatives[stop.stop_id] = alts
        if not alts:
            warnings.append(f"No alternatives for excluded stop {stop.stop_id}")

    # Validate route viability
    is_valid = len(allowed) > 0
    if not is_valid:
        warnings.append("No safe stops remaining on route after filtering")

    if len(excluded) > 0:
        warnings.append(
            f"{len(excluded)} stops excluded from night route "
            f"({len([s for s in excluded if s.is_critical])} critical, "
            f"{len([s for s in excluded if s.lighting_score < cfg.night_min_lighting_score])} poorly lit)"
        )

    return NightRouteResult(
        route_stops=allowed,
        excluded_stops=excluded,
        alternatives=alternatives,
        is_valid=is_valid,
        warnings=warnings,
    )


def is_night_shift(shift_start_hour: int) -> bool:
    """Determine if a shift is a night shift (starts at or after 20h or before 6h30)."""
    return shift_start_hour >= 20 or shift_start_hour < 7
