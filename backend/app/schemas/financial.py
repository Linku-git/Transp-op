from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INVESTMENT_MODELS = ["capex", "mise_a_disposition", "opex"]

FINANCIAL_VEHICLE_TYPES = [
    "minibus",
    "midibus",
    "bus_standard",
    "grand_bus",
    "vehicule_leger",
]

MOTORIZATIONS = ["diesel", "hybrid", "electric", "hydrogen", "gnv"]


# ---------------------------------------------------------------------------
# FinancialScenario schemas
# ---------------------------------------------------------------------------


class FinancialScenarioCreate(BaseModel):
    """Schema for creating a financial scenario."""

    name: str = Field(..., max_length=255)
    investment_model: str = Field(..., max_length=30)
    duration_years: int = Field(default=5, ge=1, le=30)
    fleet_composition: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)

    @field_validator("investment_model")
    @classmethod
    def validate_investment_model(cls, v: str) -> str:
        if v not in INVESTMENT_MODELS:
            raise ValueError(f"investment_model must be one of {INVESTMENT_MODELS}")
        return v


class FinancialScenarioUpdate(BaseModel):
    """Schema for updating a financial scenario. All fields optional."""

    name: str | None = Field(default=None, max_length=255)
    investment_model: str | None = Field(default=None, max_length=30)
    duration_years: int | None = Field(default=None, ge=1, le=30)
    fleet_composition: dict | None = None
    params: dict | None = None

    @field_validator("investment_model")
    @classmethod
    def validate_investment_model(cls, v: str | None) -> str | None:
        if v is not None and v not in INVESTMENT_MODELS:
            raise ValueError(f"investment_model must be one of {INVESTMENT_MODELS}")
        return v


class FinancialScenarioResponse(BaseModel):
    """Full financial scenario representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    investment_model: str
    duration_years: int
    fleet_composition: dict
    params: dict
    results: dict
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# TCOEntry schemas
# ---------------------------------------------------------------------------


class TCOEntryCreate(BaseModel):
    """Schema for creating a TCO entry."""

    vehicle_type: str = Field(..., max_length=50)
    motorization: str | None = Field(default=None, max_length=30)
    quantity: int = Field(default=1, ge=1)
    purchase_price: Decimal | None = Field(default=None, ge=0)
    annual_maintenance_cost: Decimal | None = Field(default=None, ge=0)
    energy_cost_per_km: Decimal | None = Field(default=None, ge=0)
    annual_km: Decimal | None = Field(default=None, ge=0)
    residual_value: Decimal | None = Field(default=None, ge=0)
    infrastructure_cost: Decimal | None = Field(default=None, ge=0)

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle_type(cls, v: str) -> str:
        if v not in FINANCIAL_VEHICLE_TYPES:
            raise ValueError(f"vehicle_type must be one of {FINANCIAL_VEHICLE_TYPES}")
        return v

    @field_validator("motorization")
    @classmethod
    def validate_motorization(cls, v: str | None) -> str | None:
        if v is not None and v not in MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {MOTORIZATIONS}")
        return v


class TCOEntryResponse(BaseModel):
    """Full TCO entry representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    financial_scenario_id: uuid.UUID
    vehicle_type: str
    motorization: str | None
    quantity: int
    purchase_price: Decimal | None
    annual_maintenance_cost: Decimal | None
    energy_cost_per_km: Decimal | None
    annual_km: Decimal | None
    residual_value: Decimal | None
    infrastructure_cost: Decimal | None
    tco_per_vehicle: Decimal | None
    tco_total: Decimal | None


# ---------------------------------------------------------------------------
# ROICalculation schemas
# ---------------------------------------------------------------------------


class ROICalculationCreate(BaseModel):
    """Schema for creating an ROI calculation."""

    baseline_absence_rate: Decimal | None = Field(default=None, ge=0, le=1)
    target_absence_rate: Decimal | None = Field(default=None, ge=0, le=1)
    headcount: int | None = Field(default=None, ge=0)
    daily_cost: Decimal | None = Field(default=None, ge=0)
    replacement_cost: Decimal | None = Field(default=None, ge=0)
    turnover_rate_before: Decimal | None = Field(default=None, ge=0, le=1)
    turnover_rate_after: Decimal | None = Field(default=None, ge=0, le=1)
    training_hour_cost: Decimal | None = Field(default=None, ge=0)
    engagement_rate: Decimal | None = Field(default=None, ge=0, le=1)
    annual_travel_hours: Decimal | None = Field(default=None, ge=0)


class ROICalculationResponse(BaseModel):
    """Full ROI calculation representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    financial_scenario_id: uuid.UUID
    baseline_absence_rate: Decimal | None
    target_absence_rate: Decimal | None
    headcount: int | None
    daily_cost: Decimal | None
    replacement_cost: Decimal | None
    turnover_rate_before: Decimal | None
    turnover_rate_after: Decimal | None
    training_hour_cost: Decimal | None
    engagement_rate: Decimal | None
    annual_travel_hours: Decimal | None
    roi_absenteeism: Decimal | None
    roi_retention: Decimal | None
    roi_journey: Decimal | None
    roi_fleet_optimization: Decimal | None
    roi_total: Decimal | None
    payback_months: Decimal | None


# ---------------------------------------------------------------------------
# VehicleReference schemas
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# TCO Calculation schemas
# ---------------------------------------------------------------------------


class TCOFleetItem(BaseModel):
    """A single vehicle spec within a fleet for TCO calculation."""

    vehicle_type: str = Field(..., max_length=50)
    motorization: str = Field(default="diesel", max_length=30)
    quantity: int = Field(default=1, ge=1)
    purchase_price: Decimal | None = Field(default=None, ge=0)
    annual_maintenance_cost: Decimal | None = Field(default=None, ge=0)
    energy_cost_per_km: Decimal | None = Field(default=None, ge=0)
    annual_km: Decimal | None = Field(default=None, ge=0)
    residual_value: Decimal | None = Field(default=None, ge=0)

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle_type(cls, v: str) -> str:
        if v not in FINANCIAL_VEHICLE_TYPES:
            raise ValueError(f"vehicle_type must be one of {FINANCIAL_VEHICLE_TYPES}")
        return v

    @field_validator("motorization")
    @classmethod
    def validate_motorization(cls, v: str) -> str:
        if v not in MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {MOTORIZATIONS}")
        return v


class TCOCalculateRequest(BaseModel):
    """Request body for TCO calculation."""

    fleet: list[TCOFleetItem] = Field(..., min_length=1)
    duration_years: int = Field(default=5, ge=1, le=10)
    include_evolution: bool = Field(default=True)
    include_comparison: bool = Field(default=True)


class TCOVehicleResult(BaseModel):
    """TCO result for a single vehicle specification."""

    vehicle_type: str
    motorization: str
    purchase_price: float
    annual_maintenance_cost: float
    energy_cost_per_km: float
    annual_km: float
    residual_value: float
    duration_years: int
    quantity: int
    maintenance_total: float
    energy_total: float
    tco_per_vehicle: float
    tco_total: float


class TCOFleetResult(BaseModel):
    """Aggregate fleet TCO breakdown."""

    duration_years: int
    vehicles: list[TCOVehicleResult]
    fleet_tco_total: float
    vehicle_count: int


class TCOYearlyPoint(BaseModel):
    """Single year in the TCO evolution series."""

    year: int
    fleet_tco_total: float


class TCOMotorizationItem(BaseModel):
    """TCO for one motorization in a comparison."""

    motorization: str
    purchase_price: float
    annual_maintenance_cost: float
    energy_cost_per_km: float
    annual_km: float
    residual_value: float
    duration_years: int
    quantity: int
    maintenance_total: float
    energy_total: float
    tco_per_vehicle: float
    tco_total: float


class TCOMotorizationComparison(BaseModel):
    """Motorization comparison for a vehicle type."""

    vehicle_type: str
    motorizations: list[TCOMotorizationItem]


class TCOCalculateResponse(BaseModel):
    """Full TCO calculation response."""

    fleet_tco: TCOFleetResult
    evolution: list[TCOYearlyPoint] | None = None
    motorization_comparisons: list[TCOMotorizationComparison] | None = None


# ---------------------------------------------------------------------------
# VehicleReference schemas
# ---------------------------------------------------------------------------


class VehicleReferenceResponse(BaseModel):
    """Vehicle reference catalog entry returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    capacity_min: int | None
    capacity_max: int | None
    motorizations_available: list
    recommended_use: str | None
    reference_tco_5y: dict
    length_meters: Decimal | None
    zfe_compliant: bool
    created_at: datetime
    updated_at: datetime
