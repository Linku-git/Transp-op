from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security_questionnaire import SecurityQuestionnaire

logger = logging.getLogger(__name__)


class ReassessmentInterval(str, Enum):
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


INTERVAL_DAYS = {
    ReassessmentInterval.QUARTERLY: 90,
    ReassessmentInterval.SEMI_ANNUAL: 180,
    ReassessmentInterval.ANNUAL: 365,
}


def get_interval_days(interval: ReassessmentInterval | str) -> int:
    if isinstance(interval, str):
        interval = ReassessmentInterval(interval)
    return INTERVAL_DAYS[interval]


def is_reassessment_due(
    last_submitted_at: datetime | None,
    interval: ReassessmentInterval = ReassessmentInterval.QUARTERLY,
    now: datetime | None = None,
) -> bool:
    """Check if an employee is due for reassessment."""
    if last_submitted_at is None:
        return True
    current = now or datetime.now(timezone.utc)
    days = get_interval_days(interval)
    return (current - last_submitted_at).days >= days


def next_due_date(
    last_submitted_at: datetime | None,
    interval: ReassessmentInterval = ReassessmentInterval.QUARTERLY,
) -> datetime | None:
    """Calculate next reassessment due date."""
    if last_submitted_at is None:
        return datetime.now(timezone.utc)
    days = get_interval_days(interval)
    return last_submitted_at + timedelta(days=days)


async def get_next_version(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> int:
    """Get the next version number for an employee's questionnaire."""
    result = await db.execute(
        select(func.max(SecurityQuestionnaire.version))
        .where(
            SecurityQuestionnaire.tenant_id == tenant_id,
            SecurityQuestionnaire.employee_id == employee_id,
        )
    )
    current_max = result.scalar() or 0
    return current_max + 1


async def get_employees_due_for_reassessment(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    interval: ReassessmentInterval = ReassessmentInterval.QUARTERLY,
) -> list[dict]:
    """Find employees whose last questionnaire exceeds the interval."""
    days = get_interval_days(interval)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Get latest submission per employee
    subquery = (
        select(
            SecurityQuestionnaire.employee_id,
            func.max(SecurityQuestionnaire.submitted_at).label("last_submitted"),
        )
        .where(SecurityQuestionnaire.tenant_id == tenant_id)
        .group_by(SecurityQuestionnaire.employee_id)
    ).subquery()

    result = await db.execute(
        select(subquery.c.employee_id, subquery.c.last_submitted)
        .where(subquery.c.last_submitted < cutoff)
    )

    return [
        {
            "employee_id": str(row.employee_id),
            "last_submitted_at": row.last_submitted.isoformat(),
            "is_due": True,
        }
        for row in result.all()
    ]
