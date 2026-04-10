from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


METRIC_TYPES = ["otp", "headway_cov", "load_factor", "commercial_speed"]
PERIOD_TYPES = ["daily", "weekly", "monthly"]


# ---------------------------------------------------------------------------
# Compute request/response
# ---------------------------------------------------------------------------


class ArrivalData(BaseModel):
    """Single arrival observation for OTP computation."""

    scheduled_time: datetime
    actual_time: datetime
    stop_id: str | None = None


class LoadObservation(BaseModel):
    """Passenger count observation for load factor."""

    passenger_count: int = Field(..., ge=0)
    vehicle_capacity: int = Field(..., gt=0)


class TripData(BaseModel):
    """Trip data for commercial speed computation."""

    distance_km: float = Field(..., gt=0)
    duration_hours: float | None = Field(default=None, gt=0)
    start_time: datetime | None = None
    end_time: datetime | None = None


class KPIComputeRequest(BaseModel):
    """Request to compute all KPIs from raw data."""

    ligne_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    metric_date: date = Field(default_factory=date.today)
    period: str = Field(default="daily")
    arrivals: list[ArrivalData] | None = None
    departure_times: list[datetime] | None = None
    load_observations: list[LoadObservation] | None = None
    trips: list[TripData] | None = None

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        if v not in PERIOD_TYPES:
            raise ValueError(f"period must be one of {PERIOD_TYPES}")
        return v


class KPIResult(BaseModel):
    """A single computed KPI result."""

    metric_type: str
    value: float
    meets_target: bool
    sample_size: int
    details: dict


class KPIComputeResponse(BaseModel):
    """Response from KPI computation."""

    results: list[KPIResult]
    computed_at: str
    ligne_id: str | None = None
    vehicle_id: str | None = None
    period: str


# ---------------------------------------------------------------------------
# Query request/response
# ---------------------------------------------------------------------------


class KPIQueryParams(BaseModel):
    """Query parameters for KPI listing."""

    ligne_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    metric_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    period: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AVLMetricResponse(BaseModel):
    """AVL metric record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    ligne_id: uuid.UUID | None
    vehicle_id: uuid.UUID | None
    metric_type: str
    value: float
    metric_date: date
    period: str
    sample_size: int | None
    meets_target: bool | None
    details: str | None
    created_at: datetime
    updated_at: datetime


class AVLMetricListMeta(BaseModel):
    """Pagination metadata."""

    page: int
    pages: int
    total: int
    page_size: int


class AVLMetricListResponse(BaseModel):
    """Paginated list of AVL metrics."""

    data: list[AVLMetricResponse]
    meta: AVLMetricListMeta
