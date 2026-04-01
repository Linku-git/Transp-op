from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VEHICLE_TYPES = [
    "Minibus",
    "Midibus",
    "Bus standard",
    "Berline",
    "SUV",
    "Van",
    "Utilitaire",
    "Autre",
]

CONDITIONS = ["Bon", "Moyen", "Mauvais"]

MOTORIZATIONS = ["diesel", "hybrid", "electric", "hydrogen", "gnv"]

OWNER_TYPES = ["proprietaire", "loueur", "sous-traitant"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class VehicleCreate(BaseModel):
    """Schema for creating a vehicle."""

    type: str = Field(..., max_length=50)
    brand_model: str | None = Field(default=None, max_length=100)
    capacity: int = Field(..., ge=1, le=100)
    year: int | None = Field(default=None, ge=1990, le=2035)
    owner_type: str | None = Field(default=None, max_length=50)
    monthly_cost_mad: Decimal | None = None
    monthly_km: Decimal | None = None
    condition: str = Field(default="Bon", max_length=20)
    site_id: uuid.UUID | None = None
    is_pmr_accessible: bool = False
    fuel_consumption: Decimal | None = None
    cost_per_km: Decimal | None = None
    motorization: str | None = Field(default=None, max_length=30)
    length_meters: Decimal | None = None
    zfe_compliant: bool = False
    observations: str | None = None

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: str) -> str:
        if v not in CONDITIONS:
            raise ValueError(f"condition must be one of {CONDITIONS}")
        return v

    @field_validator("motorization")
    @classmethod
    def validate_motorization(cls, v: str | None) -> str | None:
        if v is not None and v not in MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {MOTORIZATIONS}")
        return v

    @field_validator("owner_type")
    @classmethod
    def validate_owner_type(cls, v: str | None) -> str | None:
        if v is not None and v not in OWNER_TYPES:
            raise ValueError(f"owner_type must be one of {OWNER_TYPES}")
        return v


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle. All fields optional."""

    type: str | None = Field(default=None, max_length=50)
    brand_model: str | None = Field(default=None, max_length=100)
    capacity: int | None = Field(default=None, ge=1, le=100)
    year: int | None = Field(default=None, ge=1990, le=2035)
    owner_type: str | None = Field(default=None, max_length=50)
    monthly_cost_mad: Decimal | None = None
    monthly_km: Decimal | None = None
    condition: str | None = Field(default=None, max_length=20)
    site_id: uuid.UUID | None = None
    is_pmr_accessible: bool | None = None
    fuel_consumption: Decimal | None = None
    cost_per_km: Decimal | None = None
    motorization: str | None = Field(default=None, max_length=30)
    length_meters: Decimal | None = None
    zfe_compliant: bool | None = None
    observations: str | None = None

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: str | None) -> str | None:
        if v is not None and v not in CONDITIONS:
            raise ValueError(f"condition must be one of {CONDITIONS}")
        return v

    @field_validator("motorization")
    @classmethod
    def validate_motorization(cls, v: str | None) -> str | None:
        if v is not None and v not in MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {MOTORIZATIONS}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class VehicleResponse(BaseModel):
    """Full vehicle representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    type: str
    brand_model: str | None
    capacity: int
    year: int | None
    owner_type: str | None
    monthly_cost_mad: Decimal | None
    monthly_km: Decimal | None
    condition: str
    site_id: uuid.UUID | None
    is_pmr_accessible: bool
    fuel_consumption: Decimal | None
    cost_per_km: Decimal | None
    motorization: str | None
    length_meters: Decimal | None
    zfe_compliant: bool
    observations: str | None
    created_at: datetime
    updated_at: datetime

    # Computed / joined
    site_name: str | None = None


# ---------------------------------------------------------------------------
# Fleet summary schemas
# ---------------------------------------------------------------------------


class FleetByType(BaseModel):
    type: str
    count: int
    total_capacity: int


class FleetByCondition(BaseModel):
    condition: str
    count: int


class FleetByMotorization(BaseModel):
    motorization: str
    count: int


class FleetBySite(BaseModel):
    site_id: uuid.UUID
    site_name: str
    count: int
    total_capacity: int
    pmr_count: int


class FleetSummary(BaseModel):
    """Aggregated fleet overview."""

    total_vehicles: int
    total_capacity: int
    pmr_accessible_count: int
    zfe_compliant_count: int
    by_type: list[FleetByType]
    by_condition: list[FleetByCondition]
    by_motorization: list[FleetByMotorization]
    by_site: list[FleetBySite]
