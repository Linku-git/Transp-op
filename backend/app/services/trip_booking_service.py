from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_booking import TripBooking

logger = logging.getLogger(__name__)

MIN_MODIFICATION_MINUTES = 30


async def create_booking(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    departure_time: datetime,
    route_id: uuid.UUID | None = None,
    seat_number: int | None = None,
    pickup_point_id: uuid.UUID | None = None,
    shift_id: uuid.UUID | None = None,
) -> TripBooking:
    _validate_modification_window(departure_time)

    booking = TripBooking(
        tenant_id=tenant_id,
        employee_id=employee_id,
        route_id=route_id,
        departure_time=departure_time,
        status="confirmed",
        seat_number=seat_number,
        pickup_point_id=pickup_point_id,
        shift_id=shift_id,
    )
    db.add(booking)
    await db.flush()
    await db.refresh(booking)
    return booking


async def update_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
    shift_id: uuid.UUID | None = None,
    pickup_point_id: uuid.UUID | None = None,
    seat_number: int | None = None,
) -> TripBooking:
    booking = await _get_booking(db, booking_id, tenant_id, employee_id)
    _validate_modification_window(booking.departure_time)

    if shift_id is not None:
        booking.shift_id = shift_id
    if pickup_point_id is not None:
        booking.pickup_point_id = pickup_point_id
    if seat_number is not None:
        booking.seat_number = seat_number

    await db.flush()
    await db.refresh(booking)
    return booking


async def cancel_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> TripBooking:
    booking = await _get_booking(db, booking_id, tenant_id, employee_id)
    _validate_modification_window(booking.departure_time)

    booking.status = "cancelled"
    booking.cancelled_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(booking)
    return booking


async def get_my_trips(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> list[TripBooking]:
    result = await db.execute(
        select(TripBooking)
        .where(
            TripBooking.tenant_id == tenant_id,
            TripBooking.employee_id == employee_id,
        )
        .order_by(TripBooking.departure_time.desc())
    )
    return list(result.scalars().all())


async def get_upcoming_trips(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> list[TripBooking]:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(TripBooking)
        .where(
            TripBooking.tenant_id == tenant_id,
            TripBooking.employee_id == employee_id,
            TripBooking.departure_time > now,
            TripBooking.status.in_(["confirmed", "booked"]),
        )
        .order_by(TripBooking.departure_time.asc())
    )
    return list(result.scalars().all())


async def _get_booking(
    db: AsyncSession,
    booking_id: uuid.UUID,
    tenant_id: uuid.UUID,
    employee_id: uuid.UUID,
) -> TripBooking:
    result = await db.execute(
        select(TripBooking).where(
            TripBooking.id == booking_id,
            TripBooking.tenant_id == tenant_id,
            TripBooking.employee_id == employee_id,
        )
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Trip booking not found")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    return booking


def _validate_modification_window(departure_time: datetime) -> None:
    now = datetime.now(timezone.utc)
    if departure_time.tzinfo is None:
        departure_time = departure_time.replace(tzinfo=timezone.utc)
    if departure_time - now < timedelta(minutes=MIN_MODIFICATION_MINUTES):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot modify booking less than {MIN_MODIFICATION_MINUTES} minutes before departure",
        )
