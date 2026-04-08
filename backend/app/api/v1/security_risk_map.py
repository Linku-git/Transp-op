from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.stop_risk_score import StopRiskScore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security")


@router.get("/risk-map")
async def get_risk_map(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return all stops with risk scores and coordinates for map rendering."""
    result = await db.execute(
        select(StopRiskScore)
        .where(StopRiskScore.tenant_id == current_user.tenant_id)
        .order_by(StopRiskScore.composite_risk_score.desc())
    )
    stops = result.scalars().all()

    return {
        "stops": [
            {
                "id": str(s.id),
                "stop_name": s.stop_name,
                "lat": s.lat,
                "lng": s.lng,
                "composite_risk_score": s.composite_risk_score,
                "is_critical": s.is_critical,
                "isolation_score": s.isolation_score,
                "lighting_score": s.lighting_score,
                "tc_frequency_score": s.tc_frequency_score,
                "employee_perception_avg": s.employee_perception_avg,
            }
            for s in stops
        ],
        "total": len(stops),
    }
