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

    # Shift configuration — up to 3 equipes, each with a type + 4 times
    num_shifts: int = Field(default=1, ge=1, le=3)

    shift_1_type: str | None = Field(default=None, max_length=50)
    shift_1_entry: time | None = None       # depart_h1
    shift_1_exit: time | None = None        # retour_h1
    shift_1_depart_h2: time | None = None
    shift_1_retour_h2: time | None = None

    shift_2_type: str | None = Field(default=None, max_length=50)
    shift_2_entry: time | None = None
    shift_2_exit: time | None = None
    shift_2_depart_h2: time | None = None
    shift_2_retour_h2: time | None = None

    shift_3_type: str | None = Field(default=None, max_length=50)
    shift_3_entry: time | None = None
    shift_3_exit: time | None = None
    shift_3_depart_h2: time | None = None
    shift_3_retour_h2: time | None = None

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
    timezone: str = Field(default="Africa/Casablanca", max_length=50)
    observations: str | None = None

    # Active shifts selected for this site (list of HoraireTravail IDs)
    active_shift_ids: list[str] = Field(default_factory=list)

    @field_validator("security_profile")
    @classmethod
    def validate_security_profile(cls, v: str) -> str:
        allowed = ("normal", "elevated", "critical")
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v

    @field_validator("shift_1_type", "shift_2_type", "shift_3_type")
    @classmethod
    def validate_shift_type(cls, v: str | None) -> str | None:
        if v is not None and v != "":
            allowed = ("Poste 1", "Poste 2", "Poste 3", "Normal", "Sirène", "Personnalisé")
            if v not in allowed:
                raise ValueError(f"Type horaire must be one of {allowed}")
        return v or None


class SiteUpdate(BaseModel):
    """Schema for updating an existing site. All fields optional (partial update).

    Note: ``code`` is not updatable after creation.
    """

    name: str | None = Field(default=None, max_length=255)
    address: str | None = None
    city: str | None = Field(default=None, max_length=100)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    num_shifts: int | None = Field(default=None, ge=1, le=3)

    shift_1_type: str | None = None
    shift_1_entry: time | None = None
    shift_1_exit: time | None = None
    shift_1_depart_h2: time | None = None
    shift_1_retour_h2: time | None = None

    shift_2_type: str | None = None
    shift_2_entry: time | None = None
    shift_2_exit: time | None = None
    shift_2_depart_h2: time | None = None
    shift_2_retour_h2: time | None = None

    shift_3_type: str | None = None
    shift_3_entry: time | None = None
    shift_3_exit: time | None = None
    shift_3_depart_h2: time | None = None
    shift_3_retour_h2: time | None = None

    working_days: str | None = Field(default=None, max_length=100)
    days_per_week: int | None = Field(default=None, ge=1, le=7)

    contact_name: str | None = Field(default=None, max_length=100)
    contact_phone: str | None = Field(default=None, max_length=50)
    access_notes: str | None = None
    parking_notes: str | None = None

    zfe_zone: bool | None = None
    security_profile: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=50)
    observations: str | None = None
    active_shift_ids: list[str] | None = None

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

    num_shifts: int

    shift_1_type: str | None
    shift_1_entry: time | None
    shift_1_exit: time | None
    shift_1_depart_h2: time | None
    shift_1_retour_h2: time | None

    shift_2_type: str | None
    shift_2_entry: time | None
    shift_2_exit: time | None
    shift_2_depart_h2: time | None
    shift_2_retour_h2: time | None

    shift_3_type: str | None
    shift_3_entry: time | None
    shift_3_exit: time | None
    shift_3_depart_h2: time | None
    shift_3_retour_h2: time | None

    working_days: str | None
    days_per_week: int | None

    contact_name: str | None
    contact_phone: str | None
    access_notes: str | None
    parking_notes: str | None

    zfe_zone: bool
    security_profile: str
    timezone: str
    observations: str | None
    active_shift_ids: list[str] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime


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
