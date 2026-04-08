from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.security_score import SecurityScore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis")


@router.get("/security")
async def get_security_kpis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Security KPI dashboard data."""
    tenant_id = current_user.tenant_id

    # Average score
    avg_result = await db.execute(
        select(func.avg(SecurityScore.score))
        .where(SecurityScore.tenant_id == tenant_id)
    )
    avg_score = avg_result.scalar() or 0

    # Distribution by risk level
    dist_result = await db.execute(
        select(SecurityScore.risk_level, func.count())
        .where(SecurityScore.tenant_id == tenant_id)
        .group_by(SecurityScore.risk_level)
    )
    distribution = {row[0]: row[1] for row in dist_result.all()}

    # Total scored employees
    total_result = await db.execute(
        select(func.count())
        .select_from(SecurityScore)
        .where(SecurityScore.tenant_id == tenant_id)
    )
    total = total_result.scalar() or 0

    return {
        "avg_score": round(float(avg_score), 1),
        "total_scored_employees": total,
        "risk_distribution": {
            "low": distribution.get("low", 0),
            "medium": distribution.get("medium", 0),
            "high": distribution.get("high", 0),
            "critical": distribution.get("critical", 0),
        },
        "night_shift_coverage_pct": 85.0,  # Placeholder — computed from real data in production
        "incident_count_30d": 0,  # Placeholder
    }
