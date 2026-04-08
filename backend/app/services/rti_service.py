from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from geoalchemy2 import functions as geo_func
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle_position import VehiclePosition
from app.models.rti_event import RTIEvent

logger = logging.getLogger(__name__)

COMPLIANCE_THRESHOLD_SECONDS = 90


async def store_position(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    lat: float,
    lng: float,
    heading: float | None = None,
    speed: float | None = None,
    recorded_at: datetime | None = None,
) -> VehiclePosition:
    """Store position in database (history). Redis caching handled by caller."""
    position = VehiclePosition(
        tenant_id=tenant_id,
        vehicle_id=vehicle_id,
        lat=lat,
        lng=lng,
        geom=geo_func.ST_MakePoint(lng, lat),
        heading=heading,
        speed=speed,
        recorded_at=recorded_at or datetime.now(timezone.utc),
    )
    db.add(position)
    await db.flush()
    await db.refresh(position)
    return position


async def get_latest_position(
    db: AsyncSession,
    vehicle_id: uuid.UUID,
) -> VehiclePosition | None:
    """Get latest position from DB (fallback when Redis unavailable)."""
    result = await db.execute(
        select(VehiclePosition)
        .where(VehiclePosition.vehicle_id == vehicle_id)
        .order_by(VehiclePosition.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def log_rti_event(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    stop_id: uuid.UUID | None = None,
    event_type: str = "arrival",
    scheduled_at: datetime | None = None,
    actual_at: datetime | None = None,
) -> RTIEvent:
    """Log an RTI event for compliance tracking."""
    wait_seconds = None
    if scheduled_at and actual_at:
        delta = (actual_at - scheduled_at).total_seconds()
        wait_seconds = max(0, int(delta))

    event = RTIEvent(
        tenant_id=tenant_id,
        vehicle_id=vehicle_id,
        stop_id=stop_id,
        event_type=event_type,
        scheduled_at=scheduled_at,
        actual_at=actual_at,
        wait_duration_seconds=wait_seconds,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


async def get_compliance_metrics(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    threshold_seconds: int = COMPLIANCE_THRESHOLD_SECONDS,
) -> dict:
    """Calculate RTI compliance: % of arrivals within threshold."""
    total_result = await db.execute(
        select(func.count())
        .select_from(RTIEvent)
        .where(
            RTIEvent.tenant_id == tenant_id,
            RTIEvent.event_type == "arrival",
            RTIEvent.wait_duration_seconds.is_not(None),
        )
    )
    total = total_result.scalar() or 0

    compliant_result = await db.execute(
        select(func.count())
        .select_from(RTIEvent)
        .where(
            RTIEvent.tenant_id == tenant_id,
            RTIEvent.event_type == "arrival",
            RTIEvent.wait_duration_seconds.is_not(None),
            RTIEvent.wait_duration_seconds <= threshold_seconds,
        )
    )
    compliant = compliant_result.scalar() or 0

    pct = (compliant / total * 100.0) if total > 0 else 100.0

    return {
        "total_events": total,
        "compliant_events": compliant,
        "compliance_percentage": round(pct, 2),
        "threshold_seconds": threshold_seconds,
    }


def position_to_redis_dict(
    vehicle_id: uuid.UUID,
    lat: float,
    lng: float,
    heading: float | None,
    speed: float | None,
    recorded_at: datetime,
    eta_seconds: int | None = None,
) -> dict:
    """Serialize position for Redis storage."""
    return {
        "vehicle_id": str(vehicle_id),
        "lat": lat,
        "lng": lng,
        "heading": heading,
        "speed": speed,
        "recorded_at": recorded_at.isoformat(),
        "eta_seconds": eta_seconds,
    }
