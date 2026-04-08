from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.rti_event import RTIEvent
from app.services.rti_service import get_compliance_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kpis")


@router.get("/rti")
async def get_rti_kpis(
    period: str = Query(default="day", pattern="^(day|week|month)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """RTI KPI dashboard data: compliance %, avg wait, violations, trend."""
    tenant_id = current_user.tenant_id

    # Current compliance
    metrics = await get_compliance_metrics(db, tenant_id)

    # Average wait time
    avg_result = await db.execute(
        select(func.avg(RTIEvent.wait_duration_seconds))
        .where(
            RTIEvent.tenant_id == tenant_id,
            RTIEvent.event_type == "arrival",
            RTIEvent.wait_duration_seconds.is_not(None),
        )
    )
    avg_wait = avg_result.scalar() or 0

    # Active violations (wait > 90s in last 24h)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    violations_result = await db.execute(
        select(func.count())
        .select_from(RTIEvent)
        .where(
            RTIEvent.tenant_id == tenant_id,
            RTIEvent.event_type == "arrival",
            RTIEvent.wait_duration_seconds.is_not(None),
            RTIEvent.wait_duration_seconds > 90,
            RTIEvent.created_at >= cutoff,
        )
    )
    violations = violations_result.scalar() or 0

    # Trend data
    days = {"day": 1, "week": 7, "month": 30}[period]
    trend_start = datetime.now(timezone.utc) - timedelta(days=days)

    trend_result = await db.execute(
        select(
            func.date(RTIEvent.created_at).label("date"),
            func.count().label("total"),
            func.count()
            .filter(RTIEvent.wait_duration_seconds <= 90)
            .label("compliant"),
        )
        .where(
            RTIEvent.tenant_id == tenant_id,
            RTIEvent.event_type == "arrival",
            RTIEvent.wait_duration_seconds.is_not(None),
            RTIEvent.created_at >= trend_start,
        )
        .group_by(func.date(RTIEvent.created_at))
        .order_by(func.date(RTIEvent.created_at))
    )
    trend = [
        {
            "date": str(row.date),
            "compliance_pct": round(row.compliant / row.total * 100, 1) if row.total > 0 else 100,
        }
        for row in trend_result.all()
    ]

    return {
        "compliance_pct": metrics["compliance_percentage"],
        "avg_wait_seconds": round(avg_wait, 1),
        "active_violations": violations,
        "total_events": metrics["total_events"],
        "trend": trend,
        "period": period,
    }
