from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class RecompositionTrigger(str, Enum):
    EMPLOYEE_ABSENCE = "employee_absence"
    SHIFT_CHANGE = "shift_change"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    COMPLIANCE_DROP = "compliance_drop"


class RecompositionResult:
    def __init__(
        self,
        trigger: RecompositionTrigger,
        site_id: uuid.UUID,
        vehicles_reassigned: int = 0,
        employees_affected: int = 0,
        success: bool = True,
        message: str = "",
    ):
        self.trigger = trigger
        self.site_id = site_id
        self.vehicles_reassigned = vehicles_reassigned
        self.employees_affected = employees_affected
        self.success = success
        self.message = message
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "trigger": self.trigger.value,
            "site_id": str(self.site_id),
            "vehicles_reassigned": self.vehicles_reassigned,
            "employees_affected": self.employees_affected,
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


def trigger_recomposition(
    trigger: RecompositionTrigger,
    site_id: uuid.UUID,
    affected_employee_ids: list[uuid.UUID] | None = None,
    affected_vehicle_id: uuid.UUID | None = None,
) -> RecompositionResult:
    """
    Trigger pool recomposition based on an event.
    In production, this would re-run the vehicle assignment algorithm
    for the affected routes/clusters. For now, it logs and returns a result.
    """
    affected = len(affected_employee_ids) if affected_employee_ids else 0

    logger.info(
        f"Pool recomposition triggered: {trigger.value} "
        f"for site {site_id}, {affected} employees affected"
    )

    # Estimate vehicles to reassign (1 per 15 affected employees)
    vehicles_to_reassign = max(1, affected // 15) if affected > 0 else 0

    return RecompositionResult(
        trigger=trigger,
        site_id=site_id,
        vehicles_reassigned=vehicles_to_reassign,
        employees_affected=affected,
        success=True,
        message=f"Recomposition completed for {trigger.value}",
    )
