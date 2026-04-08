from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)

# Historical average breakdown rate per 100 vehicles per day
DEFAULT_BREAKDOWN_RATE = 0.03
# Historical average traffic delay factor
DEFAULT_TRAFFIC_DELAY_FACTOR = 0.15


def calculate_buffer_vehicles(
    total_fleet_size: int,
    breakdown_rate: float = DEFAULT_BREAKDOWN_RATE,
    traffic_delay_factor: float = DEFAULT_TRAFFIC_DELAY_FACTOR,
    min_buffer: int = 1,
) -> int:
    """
    Calculate recommended buffer vehicle count for degraded mode.

    Formula: buffer = ceil(fleet * breakdown_rate) + ceil(fleet * traffic_factor * 0.5)
    Minimum buffer is 1 vehicle.
    """
    breakdown_buffer = max(1, int(total_fleet_size * breakdown_rate + 0.5))
    traffic_buffer = max(0, int(total_fleet_size * traffic_delay_factor * 0.5 + 0.5))

    return max(min_buffer, breakdown_buffer + traffic_buffer)


def should_activate_buffer(
    current_compliance_pct: float,
    target_compliance_pct: float,
    degradation_threshold: float = 5.0,
) -> bool:
    """
    Determine if buffer vehicles should be activated.
    Activates when compliance drops more than degradation_threshold below target.
    """
    return current_compliance_pct < (target_compliance_pct - degradation_threshold)


def is_degraded_mode(
    current_compliance_pct: float,
    target_compliance_pct: float,
) -> bool:
    """Check if system is in degraded mode (compliance below target)."""
    return current_compliance_pct < target_compliance_pct
