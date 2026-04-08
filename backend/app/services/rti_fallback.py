from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class FallbackType(str, Enum):
    TAD_REQUEST = "tad_request"
    BUFFER_ACTIVATION = "buffer_activation"
    ROUTE_REROUTE = "route_reroute"
    ALERT_DISPATCHED = "alert_dispatched"


class FallbackAction:
    def __init__(
        self,
        fallback_type: FallbackType,
        site_id: uuid.UUID,
        reason: str,
        details: dict | None = None,
    ):
        self.fallback_type = fallback_type
        self.site_id = site_id
        self.reason = reason
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)
        self.executed = False

    def to_dict(self) -> dict:
        return {
            "type": self.fallback_type.value,
            "site_id": str(self.site_id),
            "reason": self.reason,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "executed": self.executed,
        }


def evaluate_fallback(
    site_id: uuid.UUID,
    current_compliance_pct: float,
    target_compliance_pct: float,
    buffer_vehicles_available: int,
    buffer_vehicles_active: int,
) -> FallbackAction | None:
    """
    Evaluate whether a fallback protocol should be activated.

    Decision tree:
    1. If compliance is within target → no action
    2. If buffer vehicles available → activate buffer
    3. If all buffers used and still below target → request TAD
    """
    if current_compliance_pct >= target_compliance_pct:
        return None

    buffer_remaining = buffer_vehicles_available - buffer_vehicles_active

    if buffer_remaining > 0:
        action = FallbackAction(
            fallback_type=FallbackType.BUFFER_ACTIVATION,
            site_id=site_id,
            reason=f"Compliance at {current_compliance_pct}% (target: {target_compliance_pct}%)",
            details={"buffers_to_activate": min(buffer_remaining, 2)},
        )
        action.executed = True
        logger.info(f"Buffer activation for site {site_id}: {buffer_remaining} available")
        return action

    # All buffers exhausted — request TAD
    action = FallbackAction(
        fallback_type=FallbackType.TAD_REQUEST,
        site_id=site_id,
        reason=(
            f"Compliance at {current_compliance_pct}% (target: {target_compliance_pct}%), "
            f"all {buffer_vehicles_available} buffer vehicles in use"
        ),
        details={
            "tad_vehicles_needed": max(1, int((target_compliance_pct - current_compliance_pct) / 5)),
        },
    )
    action.executed = True
    logger.warning(f"TAD request triggered for site {site_id}")
    return action
