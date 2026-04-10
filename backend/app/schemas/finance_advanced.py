from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# NPV schemas
# ---------------------------------------------------------------------------


class NPVRequest(BaseModel):
    """Request for NPV computation."""

    cash_flows: list[float] = Field(..., min_length=1, description="Cash flows by year (CF[0]=initial investment)")
    discount_rate: float = Field(default=0.08, ge=0, le=1.0, description="Discount rate (0-1)")
    currency: str = Field(default="MAD")


class PresentValueEntry(BaseModel):
    """Present value for a single year."""

    year: int
    cash_flow: float
    present_value: float


class NPVResponse(BaseModel):
    """NPV computation response."""

    npv: float
    discount_rate: float
    cash_flow_count: int
    present_values: list[PresentValueEntry]
    is_viable: bool
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# IRR schemas
# ---------------------------------------------------------------------------


class IRRRequest(BaseModel):
    """Request for IRR computation."""

    cash_flows: list[float] = Field(..., min_length=2, description="Cash flows (need 2+ for IRR)")


class IRRResponse(BaseModel):
    """IRR computation response."""

    irr: float | None
    irr_pct: float | None
    converged: bool
    npv_at_irr: float | None


# ---------------------------------------------------------------------------
# Payback period schemas
# ---------------------------------------------------------------------------


class PaybackRequest(BaseModel):
    """Request for payback period."""

    cash_flows: list[float] = Field(..., min_length=1)
    currency: str = Field(default="MAD")


class PaybackResponse(BaseModel):
    """Payback period response."""

    payback_years: float | None
    cumulative_flows: list[float]
    total_investment: float
    total_return: float
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# Full investment analysis
# ---------------------------------------------------------------------------


class InvestmentAnalysisRequest(BaseModel):
    """Request for full investment analysis."""

    cash_flows: list[float] = Field(..., min_length=2)
    discount_rate: float = Field(default=0.08, ge=0, le=1.0)
    currency: str = Field(default="MAD")


class InvestmentAnalysisResponse(BaseModel):
    """Combined NPV + IRR + payback response."""

    npv: dict
    irr: dict
    payback: dict


# ---------------------------------------------------------------------------
# CO2 Valorization schemas
# ---------------------------------------------------------------------------


VALID_MOTORIZATIONS = ["diesel", "essence", "gnv", "hybride", "electrique", "hydrogen"]


class CO2ValorizationRequest(BaseModel):
    """Request for CO2 emissions monetization."""

    fleet_annual_km: float = Field(..., gt=0, description="Annual km per vehicle")
    current_motorization: str = Field(default="diesel")
    target_motorization: str = Field(default="electrique")
    carbon_price_mad_tco2: float = Field(default=200.0, gt=0, description="Carbon price MAD/tCO2")
    vehicle_count: int = Field(default=1, ge=1)
    energy_consumption_kwh_per_km: float = Field(default=0.25, gt=0)
    currency: str = Field(default="MAD")

    @field_validator("current_motorization", "target_motorization")
    @classmethod
    def validate_motorization(cls, v: str) -> str:
        if v not in VALID_MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {VALID_MOTORIZATIONS}")
        return v


class CO2ValorizationResponse(BaseModel):
    """CO2 valorization response."""

    current_emissions_tco2: float
    target_emissions_tco2: float
    avoided_emissions_tco2: float
    carbon_price_mad_tco2: float
    valorization_mad: float
    valorization_15year_mad: float
    fleet_annual_km: float
    vehicle_count: int
    current_motorization: str
    target_motorization: str
    currency: str = "MAD"


class CO2SavingsNPVRequest(BaseModel):
    """Request for NPV of CO2 savings over time."""

    fleet_annual_km: float = Field(..., gt=0)
    current_motorization: str = Field(default="diesel")
    target_motorization: str = Field(default="electrique")
    carbon_price_mad_tco2: float = Field(default=200.0, gt=0)
    carbon_price_escalation_pct: float = Field(default=3.0, ge=0, le=20)
    discount_rate: float = Field(default=0.08, ge=0, le=1.0)
    horizon_years: int = Field(default=15, ge=1, le=30)
    vehicle_count: int = Field(default=1, ge=1)
    energy_consumption_kwh_per_km: float = Field(default=0.25, gt=0)
    currency: str = Field(default="MAD")

    @field_validator("current_motorization", "target_motorization")
    @classmethod
    def validate_motorization(cls, v: str) -> str:
        if v not in VALID_MOTORIZATIONS:
            raise ValueError(f"motorization must be one of {VALID_MOTORIZATIONS}")
        return v


class YearlyCO2Saving(BaseModel):
    """Single year CO2 savings entry."""

    year: int
    carbon_price: float
    avoided_tco2: float
    savings_mad: float
    pv_mad: float


class CO2SavingsNPVResponse(BaseModel):
    """NPV of CO2 savings response."""

    npv_co2_savings_mad: float
    yearly_savings: list[YearlyCO2Saving]
    total_avoided_tco2: float
    horizon_years: int
    discount_rate: float
    currency: str = "MAD"
