from __future__ import annotations

import uuid
from datetime import datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRANSPORT_MODES = [
    "vehicule_particulier",
    "covoiturage",
    "deux_roues_motorise",
    "deux_roues_non_motorise",
    "transport_public",
    "auto_stop",
    "navette_entreprise",
    "autre",
]

FREQUENCIES = [
    "Quotidien",
    "3-4 fois/semaine",
    "2-3 fois/semaine",
    "Occasionnel",
]

INTEREST_VALUES = ["Oui", "Non", "Sous conditions"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ModalCreate(BaseModel):
    """Schema for creating / upserting an employee modal record."""

    employee_id: uuid.UUID
    primary_mode: str = Field(..., max_length=50)
    alternative_mode: str | None = Field(default=None, max_length=50)
    distance_km: Decimal | None = None
    travel_time_min: int | None = None
    frequency: str | None = Field(default=None, max_length=50)
    interest_company_transport: str | None = Field(default=None, max_length=30)
    reason_current_mode: str | None = None
    departure_time: time | None = None
    accepts_common_pickup: bool = True
    max_pickup_distance_meters: int = 500
    has_private_car: bool = False
    volunteer_driver: bool = False
    carpool_seats_available: int = 0
    max_detour_minutes: int | None = None
    bonus_opt_in: bool = False
    observations: str | None = None

    @field_validator("primary_mode")
    @classmethod
    def validate_primary_mode(cls, v: str) -> str:
        if v not in TRANSPORT_MODES:
            raise ValueError(f"primary_mode must be one of {TRANSPORT_MODES}")
        return v

    @field_validator("alternative_mode")
    @classmethod
    def validate_alternative_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in TRANSPORT_MODES:
            raise ValueError(f"alternative_mode must be one of {TRANSPORT_MODES}")
        return v

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str | None) -> str | None:
        if v is not None and v not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}")
        return v

    @field_validator("interest_company_transport")
    @classmethod
    def validate_interest(cls, v: str | None) -> str | None:
        if v is not None and v not in INTEREST_VALUES:
            raise ValueError(f"interest_company_transport must be one of {INTEREST_VALUES}")
        return v


class ModalUpdate(BaseModel):
    """Schema for updating an existing modal. All fields optional.

    Note: ``employee_id`` is not updatable after creation.
    """

    primary_mode: str | None = Field(default=None, max_length=50)
    alternative_mode: str | None = Field(default=None, max_length=50)
    distance_km: Decimal | None = None
    travel_time_min: int | None = None
    frequency: str | None = Field(default=None, max_length=50)
    interest_company_transport: str | None = Field(default=None, max_length=30)
    reason_current_mode: str | None = None
    departure_time: time | None = None
    accepts_common_pickup: bool | None = None
    max_pickup_distance_meters: int | None = None
    has_private_car: bool | None = None
    volunteer_driver: bool | None = None
    carpool_seats_available: int | None = None
    max_detour_minutes: int | None = None
    bonus_opt_in: bool | None = None
    observations: str | None = None

    @field_validator("primary_mode")
    @classmethod
    def validate_primary_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in TRANSPORT_MODES:
            raise ValueError(f"primary_mode must be one of {TRANSPORT_MODES}")
        return v

    @field_validator("alternative_mode")
    @classmethod
    def validate_alternative_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in TRANSPORT_MODES:
            raise ValueError(f"alternative_mode must be one of {TRANSPORT_MODES}")
        return v

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str | None) -> str | None:
        if v is not None and v not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}")
        return v

    @field_validator("interest_company_transport")
    @classmethod
    def validate_interest(cls, v: str | None) -> str | None:
        if v is not None and v not in INTEREST_VALUES:
            raise ValueError(f"interest_company_transport must be one of {INTEREST_VALUES}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ModalResponse(BaseModel):
    """Full modal representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    primary_mode: str
    alternative_mode: str | None
    distance_km: Decimal | None
    travel_time_min: int | None
    frequency: str | None
    interest_company_transport: str | None
    reason_current_mode: str | None
    departure_time: time | None
    accepts_common_pickup: bool
    max_pickup_distance_meters: int
    has_private_car: bool
    volunteer_driver: bool
    carpool_seats_available: int
    max_detour_minutes: int | None
    bonus_opt_in: bool
    observations: str | None

    # Timestamps (from BaseModel / TimestampMixin)
    created_at: datetime
    updated_at: datetime

    # Computed / joined field
    employee_name: str | None = None


# ---------------------------------------------------------------------------
# Analytics schemas
# ---------------------------------------------------------------------------


class ModalDistribution(BaseModel):
    """Single row in a mode distribution result."""

    mode: str
    count: int
    percentage: float


class ModalStats(BaseModel):
    """Aggregated modal statistics."""

    total: int
    distribution: list[ModalDistribution]
    by_site: list[dict] | None = None


class MobilityScore(BaseModel):
    """Mobility score for a single employee."""

    employee_id: uuid.UUID
    employee_name: str
    score: float
    factors: dict


# ---------------------------------------------------------------------------
# Session 17 — Extended analytics schemas
# ---------------------------------------------------------------------------


class GroupScore(BaseModel):
    """Average mobility score for a group (site, department, shift)."""

    group_type: str
    group_key: str
    group_label: str
    avg_score: float
    employee_count: int


class TimeSlotScore(BaseModel):
    """Employee count per departure time bucket."""

    slot: str
    count: int


class ShadowZoneEmployee(BaseModel):
    """Employee identified as being in a shadow zone (no viable transport)."""

    employee_id: uuid.UUID
    employee_name: str
    lat: float | None
    lng: float | None
    site_id: uuid.UUID
    distance_km: float
    reason: str


class MobilityScoresResponse(BaseModel):
    """Full mobility scores response with individual + group + timeslot data."""

    scores: list[MobilityScore]
    group_scores: list[GroupScore]
    timeslot_scores: list[TimeSlotScore]


class WeatherImpact(BaseModel):
    """Weather-dependent modal shift analysis per mode."""

    mode: str
    employee_count: int
    switch_probability: float
    likely_alternative: str


class DisruptionVulnerability(BaseModel):
    """Disruption vulnerability analysis per mode."""

    mode: str
    employee_count: int
    vulnerability_score: float
    disruption_types: list[str]


class CarpoolPotential(BaseModel):
    """Carpool supply vs demand per site."""

    site_id: uuid.UUID
    site_name: str
    supply_seats: int
    demand_count: int
    coverage_ratio: float


class ShiftAnalysisResponse(BaseModel):
    """Enhanced shift analysis with disruption and weather data."""

    data: dict[str, list[dict]]
    disruptions: list[DisruptionVulnerability]
    weather_impact: list[WeatherImpact]
