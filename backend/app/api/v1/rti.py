from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.vehicle_position import (
    VehiclePositionCreate,
    VehiclePositionResponse,
    VehiclePositionCurrent,
)
from app.schemas.rti_event import (
    RTIEventCreate,
    RTIEventResponse,
    RTIComplianceResponse,
)
from app.services.rti_service import (
    store_position,
    get_latest_position,
    log_rti_event,
    get_compliance_metrics,
    position_to_redis_dict,
)
from app.services.eta_calculator import calculate_eta_seconds

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rti")


@router.post("/vehicle-position", response_model=VehiclePositionResponse)
async def post_vehicle_position(
    body: VehiclePositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VehiclePositionResponse:
    """Receive GPS tracker update. Stores in DB (and Redis if available)."""
    position = await store_position(
        db=db,
        tenant_id=current_user.tenant_id,
        vehicle_id=body.vehicle_id,
        lat=body.lat,
        lng=body.lng,
        heading=body.heading,
        speed=body.speed,
        recorded_at=body.recorded_at,
    )

    # Attempt Redis cache (graceful failure)
    try:
        from app.config import settings
        if settings.redis_url:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.redis_url)
            redis_data = position_to_redis_dict(
                body.vehicle_id, body.lat, body.lng,
                body.heading, body.speed, body.recorded_at,
            )
            await r.set(
                f"rti:vehicle:{body.vehicle_id}:pos",
                json.dumps(redis_data),
                ex=30,
            )
            await r.close()
    except Exception as e:
        logger.warning(f"Redis cache failed: {e}")

    return VehiclePositionResponse.model_validate(position)


@router.get("/vehicle-position/{vehicle_id}", response_model=VehiclePositionCurrent)
async def get_vehicle_position(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VehiclePositionCurrent:
    """Get current vehicle position. Tries Redis first, falls back to DB."""
    # Try Redis first
    try:
        from app.config import settings
        if settings.redis_url:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.redis_url)
            cached = await r.get(f"rti:vehicle:{vehicle_id}:pos")
            await r.close()
            if cached:
                data = json.loads(cached)
                return VehiclePositionCurrent(**data)
    except Exception as e:
        logger.warning(f"Redis read failed: {e}")

    # Fallback to DB
    position = await get_latest_position(db, vehicle_id)
    if not position:
        raise HTTPException(status_code=404, detail="No position data for vehicle")

    return VehiclePositionCurrent(
        vehicle_id=str(position.vehicle_id),
        lat=position.lat,
        lng=position.lng,
        heading=position.heading,
        speed=position.speed,
        recorded_at=position.recorded_at.isoformat(),
    )


@router.get("/stop/{stop_id}/eta")
async def get_stop_eta(
    stop_id: uuid.UUID,
    vehicle_id: uuid.UUID = Query(...),
    stop_lat: float = Query(..., ge=-90, le=90),
    stop_lng: float = Query(..., ge=-180, le=180),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Calculate ETA for vehicle arriving at stop."""
    position = await get_latest_position(db, vehicle_id)
    if not position:
        raise HTTPException(status_code=404, detail="No position data for vehicle")

    eta = calculate_eta_seconds(
        vehicle_lat=position.lat,
        vehicle_lng=position.lng,
        stop_lat=stop_lat,
        stop_lng=stop_lng,
        vehicle_speed_kmh=position.speed,
    )

    return {
        "vehicle_id": str(vehicle_id),
        "stop_id": str(stop_id),
        "eta_seconds": eta,
        "vehicle_lat": position.lat,
        "vehicle_lng": position.lng,
    }


@router.post("/events", response_model=RTIEventResponse)
async def create_rti_event(
    body: RTIEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RTIEventResponse:
    """Log an RTI event (arrival, departure, delay, breakdown)."""
    event = await log_rti_event(
        db=db,
        tenant_id=current_user.tenant_id,
        vehicle_id=body.vehicle_id,
        stop_id=body.stop_id,
        event_type=body.event_type,
        scheduled_at=body.scheduled_at,
        actual_at=body.actual_at,
    )
    return RTIEventResponse.model_validate(event)


@router.get("/compliance", response_model=RTIComplianceResponse)
async def get_compliance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RTIComplianceResponse:
    """Get RTI compliance metrics (% arrivals within 90s threshold)."""
    metrics = await get_compliance_metrics(db, current_user.tenant_id)
    return RTIComplianceResponse(**metrics)
