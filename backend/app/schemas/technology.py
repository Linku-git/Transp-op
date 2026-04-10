from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PENTE_PROFILES = ["flat", "moderate", "hilly", "mountainous"]
SAISON_PROFILES = ["temperate", "hot", "cold", "extreme"]
VITESSE_PROFILES = ["optimal", "moderate", "city", "highway"]


# ---------------------------------------------------------------------------
# Range Correction schemas
# ---------------------------------------------------------------------------


class RangeCorrectionRequest(BaseModel):
    """Request body for battery range correction with environmental factors."""

    nominal_range_km: float = Field(
        ..., gt=0, description="Nominal battery range in km"
    )
    pente_profile: str = Field(
        default="flat",
        description="Slope profile: flat, moderate, hilly, mountainous",
    )
    saison_profile: str = Field(
        default="temperate",
        description="Season profile: temperate, hot, cold, extreme",
    )
    vitesse_profile: str = Field(
        default="moderate",
        description="Speed profile: optimal, moderate, city, highway",
    )

    @field_validator("pente_profile")
    @classmethod
    def validate_pente_profile(cls, v: str) -> str:
        if v not in PENTE_PROFILES:
            raise ValueError(
                f"pente_profile must be one of {PENTE_PROFILES}"
            )
        return v

    @field_validator("saison_profile")
    @classmethod
    def validate_saison_profile(cls, v: str) -> str:
        if v not in SAISON_PROFILES:
            raise ValueError(
                f"saison_profile must be one of {SAISON_PROFILES}"
            )
        return v

    @field_validator("vitesse_profile")
    @classmethod
    def validate_vitesse_profile(cls, v: str) -> str:
        if v not in VITESSE_PROFILES:
            raise ValueError(
                f"vitesse_profile must be one of {VITESSE_PROFILES}"
            )
        return v


class RangeCorrectionResponse(BaseModel):
    """Response with corrected range and individual correction factors."""

    nominal_range_km: float
    k_pente: float
    k_saison: float
    k_vitesse: float
    correction_factor: float
    corrected_range_km: float
    range_reduction_pct: float
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# 15-Year TCO schemas
# ---------------------------------------------------------------------------


class TCO15YearRequest(BaseModel):
    """Request body for 15-year TCO calculation with financing."""

    purchase_price: float = Field(
        ..., gt=0, description="Vehicle purchase price in MAD"
    )
    annual_maintenance_cost: float = Field(
        ..., ge=0, description="Base annual maintenance in MAD"
    )
    energy_cost_per_km: float = Field(
        ..., ge=0, description="Energy cost per km in MAD"
    )
    annual_km: float = Field(
        ..., gt=0, description="Annual kilometers driven"
    )
    residual_value_pct: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="Residual value as % of purchase price",
    )
    duration_years: int = Field(
        default=15, ge=1, le=30, description="TCO horizon in years"
    )
    loan_rate_pct: float = Field(
        default=5.0, ge=0, le=30, description="Annual loan interest rate %"
    )
    loan_duration_years: int = Field(
        default=7, ge=0, le=30, description="Loan duration in years"
    )
    energy_escalation_pct: float = Field(
        default=3.0,
        ge=0,
        le=20,
        description="Annual energy price increase %",
    )
    maintenance_escalation_pct: float = Field(
        default=2.0,
        ge=0,
        le=20,
        description="Annual maintenance cost increase %",
    )
    currency: str = Field(default="MAD", description="Currency code")


class TCO15YearYearlyBreakdown(BaseModel):
    """Single-year breakdown within the 15-year TCO timeline."""

    year: int
    depreciation: float
    maintenance: float
    energy: float
    financing: float
    year_total: float
    cumulative_tco: float


class TCO15YearResponse(BaseModel):
    """Full 15-year TCO calculation response with yearly breakdown."""

    total_tco: float
    yearly_breakdown: list[TCO15YearYearlyBreakdown]
    financing_total: float
    energy_total: float
    maintenance_total: float
    depreciation_total: float
    residual_value: float
    duration_years: int
    currency: str = "MAD"


# ---------------------------------------------------------------------------
# Breakeven schemas
# ---------------------------------------------------------------------------


class BreakevenRequest(BaseModel):
    """Request body for diesel vs electric breakeven analysis."""

    capex_diesel: float = Field(
        ..., gt=0, description="CAPEX diesel vehicle in MAD"
    )
    capex_electric: float = Field(
        ..., gt=0, description="CAPEX electric vehicle in MAD"
    )
    opex_per_km_diesel: float = Field(
        ..., ge=0, description="OPEX per km diesel in MAD"
    )
    opex_per_km_electric: float = Field(
        ..., ge=0, description="OPEX per km electric in MAD"
    )
    currency: str = Field(default="MAD")


class BreakevenResponse(BaseModel):
    """Breakeven analysis response with viability assessment."""

    km_seuil: float | None
    delta_capex: float
    delta_opex_per_km: float
    payback_years_at_reference_km: float | None
    is_electric_viable: bool
    annual_km_reference: float
    currency: str = "MAD"
