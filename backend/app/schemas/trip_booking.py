from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripBookingCreate(BaseModel):
    route_id: uuid.UUID | None = None
    departure_time: datetime
    seat_number: int | None = None
    pickup_point_id: uuid.UUID | None = None
    shift_id: uuid.UUID | None = None


class TripBookingUpdate(BaseModel):
    shift_id: uuid.UUID | None = None
    pickup_point_id: uuid.UUID | None = None
    seat_number: int | None = None


class TripBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    route_id: uuid.UUID | None = None
    departure_time: datetime
    status: str
    seat_number: int | None = None
    pickup_point_id: uuid.UUID | None = None
    shift_id: uuid.UUID | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TripBookingListResponse(BaseModel):
    data: list[TripBookingResponse]
    total: int
