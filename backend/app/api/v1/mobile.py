from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.device_registration import DeviceRegistration
from app.schemas.trip_booking import (
    TripBookingCreate,
    TripBookingUpdate,
    TripBookingResponse,
    TripBookingListResponse,
)
from app.schemas.device_registration import (
    DeviceRegisterRequest,
    DeviceRegistrationResponse,
)
from app.services.trip_booking_service import (
    create_booking,
    update_booking,
    cancel_booking,
    get_my_trips,
    get_upcoming_trips,
)
from app.services.offline_manifest_service import generate_offline_manifest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile")


# ─── Trip Booking ────────────────────────────────────────────


@router.post("/trips/book", response_model=TripBookingResponse)
async def book_trip(
    body: TripBookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripBookingResponse:
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    booking = await create_booking(
        db=db,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
        departure_time=body.departure_time,
        route_id=body.route_id,
        seat_number=body.seat_number,
        pickup_point_id=body.pickup_point_id,
        shift_id=body.shift_id,
    )
    return TripBookingResponse.model_validate(booking)


@router.put("/trips/{trip_id}", response_model=TripBookingResponse)
async def modify_trip(
    trip_id: uuid.UUID,
    body: TripBookingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripBookingResponse:
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    booking = await update_booking(
        db=db,
        booking_id=trip_id,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
        shift_id=body.shift_id,
        pickup_point_id=body.pickup_point_id,
        seat_number=body.seat_number,
    )
    return TripBookingResponse.model_validate(booking)


@router.delete("/trips/{trip_id}", response_model=TripBookingResponse)
async def cancel_trip(
    trip_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripBookingResponse:
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    booking = await cancel_booking(
        db=db,
        booking_id=trip_id,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
    )
    return TripBookingResponse.model_validate(booking)


@router.get("/trips/my", response_model=TripBookingListResponse)
async def my_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripBookingListResponse:
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    trips = await get_my_trips(
        db=db,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
    )
    return TripBookingListResponse(
        data=[TripBookingResponse.model_validate(t) for t in trips],
        total=len(trips),
    )


@router.get("/trips/upcoming", response_model=TripBookingListResponse)
async def upcoming_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TripBookingListResponse:
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="User has no linked employee")

    trips = await get_upcoming_trips(
        db=db,
        tenant_id=current_user.tenant_id,
        employee_id=employee_id,
    )
    return TripBookingListResponse(
        data=[TripBookingResponse.model_validate(t) for t in trips],
        total=len(trips),
    )


# ─── Device Registration ────────────────────────────────────


@router.post("/devices/register", response_model=DeviceRegistrationResponse)
async def register_device(
    body: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DeviceRegistrationResponse:
    # Upsert: update if token exists, create if new
    result = await db.execute(
        select(DeviceRegistration).where(
            DeviceRegistration.device_token == body.token,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.user_id = current_user.id
        existing.platform = body.platform
        existing.last_seen = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(existing)
        return DeviceRegistrationResponse.model_validate(existing)

    registration = DeviceRegistration(
        user_id=current_user.id,
        device_token=body.token,
        platform=body.platform,
        last_seen=datetime.now(timezone.utc),
    )
    db.add(registration)
    await db.flush()
    await db.refresh(registration)
    return DeviceRegistrationResponse.model_validate(registration)


@router.delete("/devices/{token}")
async def unregister_device(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    await db.execute(
        delete(DeviceRegistration).where(
            DeviceRegistration.device_token == token,
            DeviceRegistration.user_id == current_user.id,
        )
    )
    return {"detail": "Device unregistered"}


# ─── Offline Manifest ────────────────────────────────────────


@router.get("/offline-manifest")
async def offline_manifest(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await generate_offline_manifest(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        employee_id=current_user.employee_id,
    )
