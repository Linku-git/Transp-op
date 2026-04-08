from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehiclePositionCreate(BaseModel):
    vehicle_id: uuid.UUID
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    heading: float | None = Field(default=None, ge=0, le=360)
    speed: float | None = Field(default=None, ge=0)
    recorded_at: datetime


class VehiclePositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vehicle_id: uuid.UUID
    lat: float
    lng: float
    heading: float | None = None
    speed: float | None = None
    recorded_at: datetime
    created_at: datetime


class VehiclePositionCurrent(BaseModel):
    vehicle_id: str
    lat: float
    lng: float
    heading: float | None = None
    speed: float | None = None
    recorded_at: str
    eta_seconds: int | None = None
