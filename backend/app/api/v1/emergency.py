from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import functions as geo_func
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.emergency_alert import EmergencyAlert
from app.schemas.emergency_alert import (
    EmergencyAlertTrigger,
    EmergencyAlertResolve,
    EmergencyAlertResponse,
    EmergencyAlertListResponse,
)
from app.services.emergency_routing import determine_responders
from app.services.location_sharing import start_location_sharing, stop_location_sharing

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security")


@router.post("/emergency", response_model=EmergencyAlertResponse)
async def trigger_emergency(
    body: EmergencyAlertTrigger,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyAlertResponse:
    """Trigger an emergency alert from the mobile app."""
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    now = datetime.now(timezone.utc)

    # Determine responders
    responders = determine_responders(body.alert_type)

    alert = EmergencyAlert(
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
        triggered_at=now,
        location=geo_func.ST_MakePoint(body.lng, body.lat),
        lat=body.lat,
        lng=body.lng,
        alert_type=body.alert_type,
        responders_notified=responders,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)

    # Start location sharing
    start_location_sharing(alert.id, employee_id, body.lat, body.lng)

    logger.warning(
        f"EMERGENCY ALERT TRIGGERED: {alert.id} by employee {employee_id}, "
        f"type={body.alert_type}, location=({body.lat}, {body.lng})"
    )

    return EmergencyAlertResponse.model_validate(alert)


@router.put("/emergency/{alert_id}/resolve", response_model=EmergencyAlertResponse)
async def resolve_emergency(
    alert_id: uuid.UUID,
    body: EmergencyAlertResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyAlertResponse:
    """Resolve an active emergency alert."""
    result = await db.execute(
        select(EmergencyAlert).where(
            EmergencyAlert.id == alert_id,
            EmergencyAlert.tenant_id == current_user.tenant_id,
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Emergency alert not found")
    if alert.resolved_at:
        raise HTTPException(status_code=400, detail="Alert already resolved")

    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolution_notes = body.resolution_notes

    # Stop location sharing
    stop_location_sharing(alert_id)

    await db.flush()
    await db.refresh(alert)

    logger.info(f"Emergency alert {alert_id} resolved")

    return EmergencyAlertResponse.model_validate(alert)


@router.get("/emergency/history", response_model=EmergencyAlertListResponse)
async def get_emergency_history(
    alert_type: str | None = Query(default=None),
    resolved: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EmergencyAlertListResponse:
    """Retrieve emergency alert history."""
    conditions = [EmergencyAlert.tenant_id == current_user.tenant_id]
    if alert_type:
        conditions.append(EmergencyAlert.alert_type == alert_type)
    if resolved is True:
        conditions.append(EmergencyAlert.resolved_at.is_not(None))
    elif resolved is False:
        conditions.append(EmergencyAlert.resolved_at.is_(None))

    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(EmergencyAlert).where(*conditions)
    )
    total = total_result.scalar() or 0

    # Paginated results
    result = await db.execute(
        select(EmergencyAlert)
        .where(*conditions)
        .order_by(EmergencyAlert.triggered_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    alerts = list(result.scalars().all())

    pages = max(1, (total + page_size - 1) // page_size)

    return EmergencyAlertListResponse(
        data=[EmergencyAlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        pages=pages,
    )
