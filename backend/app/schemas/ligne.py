from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class LigneCreate(BaseModel):
    """Schema for creating a new transport line."""

    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=255)
    site_id: uuid.UUID | None = None

    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lng: float = Field(..., ge=-180, le=180)

    distance_km: float = Field(..., gt=0)
    rotations_per_day: int = Field(..., ge=1)
    operating_days_per_year: int = Field(..., ge=1, le=366)

    vehicle_type: str | None = Field(default=None, max_length=50)
    motorization: str | None = Field(default=None, max_length=30)
    passenger_count_avg: int | None = Field(default=None, ge=0)
    shift_type: str | None = Field(default=None, max_length=50)
    service_type: str = Field(...)
    pente_moyenne_pct: float | None = None

    @field_validator("service_type")
    @classmethod
    def validate_service_type(cls, v: str) -> str:
        allowed = ("navette", "liaison", "vip", "mixte")
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v


class LigneUpdate(BaseModel):
    """Schema for updating a transport line. All fields optional."""

    name: str | None = Field(default=None, max_length=255)
    site_id: uuid.UUID | None = None

    origin_lat: float | None = Field(default=None, ge=-90, le=90)
    origin_lng: float | None = Field(default=None, ge=-180, le=180)
    dest_lat: float | None = Field(default=None, ge=-90, le=90)
    dest_lng: float | None = Field(default=None, ge=-180, le=180)

    distance_km: float | None = Field(default=None, gt=0)
    rotations_per_day: int | None = Field(default=None, ge=1)
    operating_days_per_year: int | None = Field(default=None, ge=1, le=366)

    vehicle_type: str | None = Field(default=None, max_length=50)
    motorization: str | None = Field(default=None, max_length=30)
    passenger_count_avg: int | None = Field(default=None, ge=0)
    shift_type: str | None = Field(default=None, max_length=50)
    service_type: str | None = None
    pente_moyenne_pct: float | None = None
    is_active: bool | None = None

    @field_validator("service_type")
    @classmethod
    def validate_service_type(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = ("navette", "liaison", "vip", "mixte")
            if v not in allowed:
                raise ValueError(f"Must be one of {allowed}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class LigneResponse(BaseModel):
    """Full ligne representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    name: str
    site_id: uuid.UUID | None

    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float

    distance_km: float
    rotations_per_day: int
    operating_days_per_year: int
    km_annual: float

    vehicle_type: str | None
    motorization: str | None
    passenger_count_avg: int | None
    shift_type: str | None
    service_type: str
    pente_moyenne_pct: float | None
    is_active: bool

    created_at: datetime
    updated_at: datetime


class LigneListMeta(BaseModel):
    """Pagination metadata."""

    page: int
    pages: int
    total: int
    page_size: int


class LigneListResponse(BaseModel):
    """Paginated list response wrapper for lignes."""

    data: list[LigneResponse]
    meta: LigneListMeta
