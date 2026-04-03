from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class EmployeeCreate(BaseModel):
    """Schema for creating a new employee."""

    matricule: str = Field(..., max_length=50)
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    site_id: uuid.UUID

    # Shift & stop
    shift_time: str | None = Field(default=None, max_length=50)
    point_arret_id: uuid.UUID | None = None

    # Home address & geolocation
    address: str | None = None
    quartier: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    # Preferred pickup point
    preferred_pickup_address: str | None = None
    preferred_pickup_lat: float | None = Field(default=None, ge=-90, le=90)
    preferred_pickup_lng: float | None = Field(default=None, ge=-180, le=180)

    # Accessibility
    is_pmr: bool = False

    # Professional info
    function_role: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=100)

    # Transport preferences
    transport_required: bool = True
    current_transport_mode: str | None = Field(default=None, max_length=50)
    opt_in_company_transport: str = Field(default="Non", max_length=20)
    has_private_car: bool = False
    volunteer_driver: bool = False
    carpool_seats: int = Field(default=0, ge=0)

    # SIRH & dates
    sirh_external_id: str | None = Field(default=None, max_length=100)
    hire_date: date | None = None
    end_date: date | None = None

    @field_validator("opt_in_company_transport")
    @classmethod
    def validate_opt_in(cls, v: str) -> str:
        allowed = ("Oui", "Non", "Sous conditions")
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v


class EmployeeUpdate(BaseModel):
    """Schema for updating an existing employee. All fields optional.

    Note: ``matricule`` is not updatable after creation.
    """

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    site_id: uuid.UUID | None = None

    # Shift & stop
    shift_time: str | None = Field(default=None, max_length=50)
    point_arret_id: uuid.UUID | None = None

    # Home address & geolocation
    address: str | None = None
    quartier: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)

    # Preferred pickup point
    preferred_pickup_address: str | None = None
    preferred_pickup_lat: float | None = Field(default=None, ge=-90, le=90)
    preferred_pickup_lng: float | None = Field(default=None, ge=-180, le=180)

    # Accessibility
    is_pmr: bool | None = None

    # Professional info
    function_role: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=100)

    # Transport preferences
    transport_required: bool | None = None
    current_transport_mode: str | None = Field(default=None, max_length=50)
    opt_in_company_transport: str | None = Field(default=None, max_length=20)
    has_private_car: bool | None = None
    volunteer_driver: bool | None = None
    carpool_seats: int | None = Field(default=None, ge=0)

    # Status & SIRH
    active: bool | None = None
    sirh_external_id: str | None = Field(default=None, max_length=100)
    hire_date: date | None = None
    end_date: date | None = None

    @field_validator("opt_in_company_transport")
    @classmethod
    def validate_opt_in(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = ("Oui", "Non", "Sous conditions")
            if v not in allowed:
                raise ValueError(f"Must be one of {allowed}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class EmployeeResponse(BaseModel):
    """Full employee representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    matricule: str
    first_name: str
    last_name: str
    site_id: uuid.UUID
    shift_time: str | None
    point_arret_id: uuid.UUID | None

    # Home address & geolocation
    address: str | None
    quartier: str | None
    city: str | None
    lat: float | None
    lng: float | None

    # Preferred pickup point
    preferred_pickup_address: str | None
    preferred_pickup_lat: float | None
    preferred_pickup_lng: float | None

    # Accessibility
    is_pmr: bool

    # Professional info
    function_role: str | None
    phone: str | None
    department: str | None

    # Transport preferences
    transport_required: bool
    current_transport_mode: str | None
    opt_in_company_transport: str
    has_private_car: bool
    volunteer_driver: bool
    carpool_seats: int

    # Status & SIRH
    active: bool
    sirh_external_id: str | None
    hire_date: date | None
    end_date: date | None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Computed / joined fields
    site_name: str | None = None
    point_arret_nom: str | None = None

    # Note: geom (PostGIS internal column) is intentionally excluded.


# ---------------------------------------------------------------------------
# Summary / aggregate schemas
# ---------------------------------------------------------------------------


class SiteBreakdown(BaseModel):
    """Employee count grouped by site."""

    site_id: uuid.UUID
    site_name: str
    count: int


class DepartmentBreakdown(BaseModel):
    """Employee count grouped by department."""

    department: str
    count: int


class EmployeeSummary(BaseModel):
    """Aggregate summary of employees for a tenant."""

    total_count: int
    active_count: int
    pmr_count: int
    by_site: list[SiteBreakdown]
    by_department: list[DepartmentBreakdown]


# ---------------------------------------------------------------------------
# List / pagination schemas
# ---------------------------------------------------------------------------


class EmployeeListMeta(BaseModel):
    """Pagination metadata."""

    page: int
    pages: int
    total: int
    page_size: int


class EmployeeListResponse(BaseModel):
    """Paginated list response wrapper for employees."""

    data: list[EmployeeResponse]
    meta: EmployeeListMeta


# ---------------------------------------------------------------------------
# CSV upload result
# ---------------------------------------------------------------------------


class CSVRowError(BaseModel):
    """A single row-level error during CSV import."""

    row: int
    field: str
    message: str


class CSVUploadResult(BaseModel):
    """Result of a bulk CSV employee upload."""

    total_rows: int
    created: int
    errors: list[CSVRowError]
