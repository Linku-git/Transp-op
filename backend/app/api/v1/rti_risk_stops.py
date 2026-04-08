from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import functions as geo_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.stop_risk_score import StopRiskScore
from app.schemas.stop_risk_score import (
    StopRiskScoreCreate,
    StopRiskScoreUpdate,
    StopRiskScoreResponse,
    StopRiskScoreListResponse,
)
from app.services.risk_scoring import compute_and_flag

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rti")


@router.get("/risk-stops", response_model=StopRiskScoreListResponse)
async def list_risk_stops(
    site_id: uuid.UUID | None = Query(default=None),
    is_critical: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StopRiskScoreListResponse:
    conditions = [StopRiskScore.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(StopRiskScore.site_id == site_id)
    if is_critical is not None:
        conditions.append(StopRiskScore.is_critical == is_critical)

    result = await db.execute(
        select(StopRiskScore)
        .where(*conditions)
        .order_by(StopRiskScore.composite_risk_score.desc())
    )
    stops = list(result.scalars().all())

    return StopRiskScoreListResponse(
        data=[StopRiskScoreResponse.model_validate(s) for s in stops],
        total=len(stops),
    )


@router.post("/risk-stops", response_model=StopRiskScoreResponse)
async def create_risk_stop(
    body: StopRiskScoreCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StopRiskScoreResponse:
    composite, critical = compute_and_flag(
        isolation_score=body.isolation_score,
        lighting_score=body.lighting_score,
        tc_frequency_score=body.tc_frequency_score,
        night_risk_multiplier=body.night_risk_multiplier,
        employee_perception_avg=body.employee_perception_avg,
    )

    stop = StopRiskScore(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        stop_name=body.stop_name,
        lat=body.lat,
        lng=body.lng,
        geom=geo_func.ST_MakePoint(body.lng, body.lat),
        isolation_score=body.isolation_score,
        lighting_score=body.lighting_score,
        tc_frequency_score=body.tc_frequency_score,
        night_risk_multiplier=body.night_risk_multiplier,
        employee_perception_avg=body.employee_perception_avg,
        composite_risk_score=composite,
        is_critical=critical,
    )
    db.add(stop)
    await db.flush()
    await db.refresh(stop)
    return StopRiskScoreResponse.model_validate(stop)


@router.put("/risk-stops/{stop_id}", response_model=StopRiskScoreResponse)
async def update_risk_stop(
    stop_id: uuid.UUID,
    body: StopRiskScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StopRiskScoreResponse:
    result = await db.execute(
        select(StopRiskScore).where(
            StopRiskScore.id == stop_id,
            StopRiskScore.tenant_id == current_user.tenant_id,
        )
    )
    stop = result.scalar_one_or_none()
    if not stop:
        raise HTTPException(status_code=404, detail="Risk stop not found")

    # Apply updates
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stop, field, value)

    # Update geometry if lat/lng changed
    if "lat" in update_data or "lng" in update_data:
        stop.geom = geo_func.ST_MakePoint(stop.lng, stop.lat)

    # Recompute composite score
    composite, critical = compute_and_flag(
        isolation_score=stop.isolation_score,
        lighting_score=stop.lighting_score,
        tc_frequency_score=stop.tc_frequency_score,
        night_risk_multiplier=stop.night_risk_multiplier,
        employee_perception_avg=stop.employee_perception_avg,
    )
    stop.composite_risk_score = composite
    stop.is_critical = critical

    await db.flush()
    await db.refresh(stop)
    return StopRiskScoreResponse.model_validate(stop)
