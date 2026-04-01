from __future__ import annotations

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class SiteCreate(BaseModel):
    """Schema for creating a new site."""

    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=255)
    address: str
    city: str = Field(..., max_length=100)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

    # Shift configuration
    num_shifts: int = Field(default=1, ge=1, le=3)
    shift_1_entry: time | None = None
    shift_1_exit: time | None = None
    shift_2_entry: time | None = None
    shift_2_exit: time | None = None
    shift_3_entry: time | None = None
    shift_3_exit: time | None = None

    # Working schedule
    working_days: str = Field(default="Lundi-Vendredi", max_length=100)
    days_per_week: int = Field(default=5, ge=1, le=7)

    # Contact & logistics
    contact_name: str | None = Field(default=None, max_length=100)
    contact_phone: str | None = Field(default=None, max_length=50)
    access_notes: str | None = None
    parking_notes: str | None = None

    # Constraints & metadata
    zfe_zone: bool = False
    security_profile: str = Field(default="normal", max_length=20)
    timezone: str = Field(default="Europe/Paris", max_length=50)
    observations: str | None = None

    @field_validator("security_profile")
    @classmethod
    def validate_security_profile(cls, v: str) -> str:
        allowed = ("normal", "elevated", "critical")
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v


class SiteUpdate(BaseModel):
    """Schema for updating an existing site. All fields optional (partial update).

    Note: ``code`` is not updatable after creation.
    """

    name: str | None = Field(default=None, max_length=255)
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    # Shift configuration
    num_shifts: int | None = Field(default=None, ge=1, le=3)
    shift_1_entry: time | None = None
    shift_1_exit: time | None = None
    shift_2_entry: time | None = None
    shift_2_exit: time | None = None
    shift_3_entry: time | None = None
    shift_3_exit: time | None = None

    # Working schedule
    working_days: str | None = Field(default=None, max_length=100)
    days_per_week: int | None = Field(default=None, ge=1, le=7)

    # Contact & logistics
    contact_name: str | None = Field(default=None, max_length=100)
    contact_phone: str | None = Field(default=None, max_length=50)
    access_notes: str | None = None
    parking_notes: str | None = None

    # Constraints & metadata
    zfe_zone: bool | None = None
    security_profile: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=50)
    observations: str | None = None

    @field_validator("security_profile")
    @classmethod
    def validate_security_profile(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = ("normal", "elevated", "critical")
            if v not in allowed:
                raise ValueError(f"Must be one of {allowed}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class SiteResponse(BaseModel):
    """Full site representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    name: str
    address: str
    city: str
    lat: float
    lng: float

    # Shift configuration
    num_shifts: int
    shift_1_entry: time | None
    shift_1_exit: time | None
    shift_2_entry: time | None
    shift_2_exit: time | None
    shift_3_entry: time | None
    shift_3_exit: time | None

    # Working schedule
    working_days: str | None
    days_per_week: int | None

    # Contact & logistics
    contact_name: str | None
    contact_phone: str | None
    access_notes: str | None
    parking_notes: str | None

    # Constraints & metadata
    zfe_zone: bool
    security_profile: str
    timezone: str
    observations: str | None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Note: geom (PostGIS internal column) is intentionally excluded.


class SiteSummary(BaseModel):
    """Lightweight summary with aggregate counts."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    city: str
    employee_count: int = 0
    vehicle_count: int = 0
    pmr_count: int = 0


class SiteListMeta(BaseModel):
    """Pagination metadata."""

    page: int
    pages: int
    total: int
    page_size: int


class SiteListResponse(BaseModel):
    """Paginated list response wrapper for sites."""

    data: list[SiteResponse]
    meta: SiteListMeta
