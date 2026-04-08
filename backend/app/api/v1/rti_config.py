from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.rti_config import RTIConfig
from app.schemas.rti_config import (
    RTIConfigCreate,
    RTIConfigUpdate,
    RTIConfigResponse,
    AdaptiveSizingResult,
)
from app.services.adaptive_sizing import (
    calculate_buffer_vehicles,
    should_activate_buffer,
    is_degraded_mode,
)
from app.services.rti_fallback import evaluate_fallback
from app.services.rti_service import get_compliance_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rti")


@router.get("/config/{site_id}", response_model=RTIConfigResponse)
async def get_rti_config(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RTIConfigResponse:
    result = await db.execute(
        select(RTIConfig).where(
            RTIConfig.tenant_id == current_user.tenant_id,
            RTIConfig.site_id == site_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="RTI config not found for site")
    return RTIConfigResponse.model_validate(config)


@router.put("/config/{site_id}", response_model=RTIConfigResponse)
async def update_rti_config(
    site_id: uuid.UUID,
    body: RTIConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RTIConfigResponse:
    result = await db.execute(
        select(RTIConfig).where(
            RTIConfig.tenant_id == current_user.tenant_id,
            RTIConfig.site_id == site_id,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        # Create new config
        config = RTIConfig(
            tenant_id=current_user.tenant_id,
            site_id=site_id,
            max_wait_seconds=body.max_wait_seconds or 90,
            compliance_target_pct=body.compliance_target_pct or 95.0,
            buffer_vehicle_count=body.buffer_vehicle_count or 2,
            night_mode_start=body.night_mode_start,
            night_mode_end=body.night_mode_end,
        )
        db.add(config)
    else:
        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    return RTIConfigResponse.model_validate(config)


@router.get("/adaptive-sizing/{site_id}", response_model=AdaptiveSizingResult)
async def get_adaptive_sizing(
    site_id: uuid.UUID,
    fleet_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AdaptiveSizingResult:
    """Get adaptive sizing recommendation for a site."""
    # Get config
    result = await db.execute(
        select(RTIConfig).where(
            RTIConfig.tenant_id == current_user.tenant_id,
            RTIConfig.site_id == site_id,
        )
    )
    config = result.scalar_one_or_none()
    target_pct = config.compliance_target_pct if config else 95.0
    buffer_count = config.buffer_vehicle_count if config else 2

    # Get current compliance
    metrics = await get_compliance_metrics(db, current_user.tenant_id)
    current_pct = metrics["compliance_percentage"]

    # Calculate recommendations
    recommended = calculate_buffer_vehicles(fleet_size)
    degraded = is_degraded_mode(current_pct, target_pct)
    activate = should_activate_buffer(current_pct, target_pct)

    # Check fallback
    fallback = evaluate_fallback(
        site_id=site_id,
        current_compliance_pct=current_pct,
        target_compliance_pct=target_pct,
        buffer_vehicles_available=buffer_count,
        buffer_vehicles_active=buffer_count if activate else 0,
    )

    return AdaptiveSizingResult(
        site_id=site_id,
        required_buffer=buffer_count,
        recommended_buffer=recommended,
        current_compliance_pct=current_pct,
        is_degraded=degraded,
        buffer_activated=activate,
        tad_requested=fallback is not None and fallback.fallback_type.value == "tad_request",
    )
