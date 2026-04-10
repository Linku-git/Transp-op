from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


CHARGER_TYPES = ["ac_7kw", "ac_22kw", "dc_50kw", "dc_150kw"]


# ---------------------------------------------------------------------------
# Cost estimate request/response
# ---------------------------------------------------------------------------


class DepotCostEstimateRequest(BaseModel):
    """Request for depot electrification cost estimate."""

    charger_count: int = Field(..., ge=0, description="Number of chargers")
    charger_type: str = Field(default="dc_50kw")
    contingency_pct: float = Field(default=10.0, ge=0, le=50, description="Contingency %")
    currency: str = Field(default="MAD")

    @field_validator("charger_type")
    @classmethod
    def validate_charger_type(cls, v: str) -> str:
        if v not in CHARGER_TYPES:
            raise ValueError(f"charger_type must be one of {CHARGER_TYPES}")
        return v


class DepotCostEstimateResponse(BaseModel):
    """Depot electrification cost breakdown."""

    charger_hardware_mad: float
    installation_mad: float
    electrical_upgrade_mad: float
    transformer_mad: float
    grid_connection_mad: float
    civil_works_mad: float
    contingency_mad: float
    subtotal_mad: float
    total_cost_mad: float
    cost_per_charger_mad: float
    charger_type: str
    charger_count: int
    total_power_kw: float
    contingency_pct: float
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# Layout plan request/response
# ---------------------------------------------------------------------------


class DepotLayoutRequest(BaseModel):
    """Request for depot layout planning."""

    charger_count: int = Field(..., ge=0)
    fleet_size: int = Field(..., ge=0)
    charger_type: str = Field(default="dc_50kw")
    include_maintenance: bool = Field(default=True)
    currency: str = Field(default="MAD")

    @field_validator("charger_type")
    @classmethod
    def validate_charger_type(cls, v: str) -> str:
        if v not in CHARGER_TYPES:
            raise ValueError(f"charger_type must be one of {CHARGER_TYPES}")
        return v


class ChargerPosition(BaseModel):
    """Position of a charger bay in the depot layout."""

    bay_id: int
    x: float
    y: float
    bay_width: float
    bay_depth: float


class DepotLayoutResponse(BaseModel):
    """Depot layout plan response."""

    total_area_m2: float
    charging_area_m2: float
    parking_area_m2: float
    maintenance_area_m2: float
    circulation_area_m2: float
    charger_positions: list[ChargerPosition]
    parking_bays: int
    charger_count: int
    charger_type: str
    dimensions: dict
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# CRUD schemas
# ---------------------------------------------------------------------------


class DepotPlanCreate(BaseModel):
    """Create a depot plan record."""

    site_id: uuid.UUID | None = None
    name: str | None = None
    total_area_m2: float = Field(..., gt=0)
    charging_area_m2: float = Field(default=0, ge=0)
    parking_area_m2: float = Field(default=0, ge=0)
    maintenance_area_m2: float = Field(default=0, ge=0)
    charger_count: int = Field(default=0, ge=0)
    charger_type: str = Field(default="dc_50kw")
    parking_bays: int = Field(default=0, ge=0)
    fleet_size: int = Field(default=0, ge=0)
    total_cost_mad: float = Field(default=0, ge=0)
    cost_breakdown: dict | None = None


class DepotPlanResponse(BaseModel):
    """Depot plan record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    name: str | None
    total_area_m2: float
    charging_area_m2: float
    parking_area_m2: float
    maintenance_area_m2: float
    charger_count: int
    charger_type: str
    parking_bays: int
    fleet_size: int
    total_cost_mad: float
    cost_breakdown: dict | None
    is_active: bool
    currency: str
    created_at: datetime
    updated_at: datetime
