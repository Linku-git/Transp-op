from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHARGER_TYPES = ["ac_7kw", "ac_22kw", "dc_50kw", "dc_150kw"]


# ---------------------------------------------------------------------------
# Charging Optimization schemas
# ---------------------------------------------------------------------------


class ChargingOptimizationRequest(BaseModel):
    """Request for SOC-based charging schedule optimization."""

    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    current_soc_pct: float = Field(..., ge=0, le=100, description="Current state of charge %")
    target_soc_pct: float = Field(default=62.0, ge=0, le=100, description="Target SOC at departure (Qin 2016: 62%)")
    charger_power_kw: float = Field(default=50.0, gt=0, description="Charger power in kW")
    departure_hour: int = Field(default=6, ge=0, le=23, description="Departure hour (0-23)")
    arrival_hour: int = Field(default=18, ge=0, le=23, description="Arrival hour (0-23)")
    currency: str = Field(default="MAD")


class ChargingWindowSchedule(BaseModel):
    """A single charging window within the schedule."""

    window_name: str
    start_hour: int
    end_hour: int
    duration_hours: float
    energy_kwh: float
    cost_mad: float


class ChargingOptimizationResponse(BaseModel):
    """Optimal charging schedule response."""

    target_soc_pct: float
    energy_needed_kwh: float
    charging_duration_hours: float
    schedule: list[ChargingWindowSchedule]
    total_energy_cost_mad: float
    peak_demand_kw: float
    monthly_demand_charge_mad: float
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# IRVE Sizing schemas
# ---------------------------------------------------------------------------


class IRVESizingRequest(BaseModel):
    """Request for IRVE infrastructure sizing."""

    fleet_size: int = Field(..., ge=1, description="Number of electric vehicles")
    daily_km_per_vehicle: float = Field(..., gt=0, description="Average daily km per vehicle")
    battery_capacity_kwh: float = Field(..., gt=0, description="Battery capacity in kWh")
    energy_consumption_kwh_per_km: float = Field(default=0.25, gt=0, description="Energy consumption kWh/km")
    charging_window_hours: float = Field(default=8.0, gt=0, description="Available charging window in hours")
    charger_utilization_target: float = Field(default=0.75, gt=0, le=1.0, description="Target charger utilization 0-1")
    preferred_charger_type: str = Field(default="dc_50kw", description="Charger type: ac_7kw, ac_22kw, dc_50kw, dc_150kw")
    currency: str = Field(default="MAD")

    @field_validator("preferred_charger_type")
    @classmethod
    def validate_charger_type(cls, v: str) -> str:
        if v not in CHARGER_TYPES:
            raise ValueError(f"charger_type must be one of {CHARGER_TYPES}")
        return v


class IRVESizingResponse(BaseModel):
    """IRVE infrastructure sizing response with cost breakdown."""

    charger_type: str
    charger_count: int
    power_per_charger_kw: float
    total_installed_power_kw: float
    daily_energy_demand_kwh: float
    daily_energy_per_vehicle_kwh: float
    vehicles_per_charger: float
    hardware_cost_mad: float
    installation_cost_mad: float
    transformer_cost_mad: float
    grid_connection_cost_mad: float
    annual_electricity_cost_mad: float
    total_capex_mad: float
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# IRVE Infrastructure CRUD schemas
# ---------------------------------------------------------------------------


class IRVEInfrastructureCreate(BaseModel):
    """Create a new IRVE infrastructure record."""

    site_id: uuid.UUID | None = None
    charger_type: str = Field(default="dc_50kw")
    charger_count: int = Field(default=1, ge=1)
    power_per_charger_kw: float = Field(..., gt=0)
    total_installed_power_kw: float = Field(..., gt=0)
    hardware_cost_mad: float = Field(default=0, ge=0)
    installation_cost_mad: float = Field(default=0, ge=0)
    transformer_cost_mad: float = Field(default=0, ge=0)
    grid_connection_cost_mad: float = Field(default=0, ge=0)
    total_capex_mad: float = Field(default=0, ge=0)
    annual_electricity_cost_mad: float = Field(default=0, ge=0)
    fleet_size: int | None = None
    daily_km_per_vehicle: float | None = None
    battery_capacity_kwh: float | None = None

    @field_validator("charger_type")
    @classmethod
    def validate_charger_type(cls, v: str) -> str:
        if v not in CHARGER_TYPES:
            raise ValueError(f"charger_type must be one of {CHARGER_TYPES}")
        return v


class IRVEInfrastructureResponse(BaseModel):
    """IRVE infrastructure record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    charger_type: str
    charger_count: int
    power_per_charger_kw: float
    total_installed_power_kw: float
    hardware_cost_mad: float
    installation_cost_mad: float
    transformer_cost_mad: float
    grid_connection_cost_mad: float
    total_capex_mad: float
    annual_electricity_cost_mad: float
    fleet_size: int | None
    daily_km_per_vehicle: float | None
    battery_capacity_kwh: float | None
    is_active: bool
    currency: str
    created_at: datetime
    updated_at: datetime
