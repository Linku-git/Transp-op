from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


SOURCE_OPTIONS = ["dbscan", "manual", "imported"]


# ---------------------------------------------------------------------------
# Stop Generation request/response
# ---------------------------------------------------------------------------


class StopGenerateRequest(BaseModel):
    """Request to generate stops from employee coordinates."""

    site_id: uuid.UUID | None = Field(default=None, description="Filter employees by site")
    eps_m: float = Field(default=500.0, gt=0, description="DBSCAN epsilon in meters")
    min_pts: int = Field(default=5, ge=1, description="DBSCAN min_samples")


class GeneratedStopResult(BaseModel):
    """A single generated stop from DBSCAN."""

    cluster_id: int
    centroid_lat: float
    centroid_lng: float
    employee_count: int
    employee_ids: list[str]
    catchment_radius_m: float
    source: str = "dbscan"


class StopGenerateResponse(BaseModel):
    """Response from stop generation."""

    stops_generated: int
    eps_m: float
    min_pts: int
    noise_count: int
    stops: list[GeneratedStopResult]


# ---------------------------------------------------------------------------
# Stop Capacity request/response
# ---------------------------------------------------------------------------


class StopCapacityRequest(BaseModel):
    """Request for HCM 2000 stop capacity calculation."""

    n_berths: int = Field(default=1, ge=1, description="Number of loading berths")
    green_ratio: float = Field(default=0.5, gt=0, le=1.0, description="Signal g/C ratio")
    dwell_time_s: float = Field(default=30.0, gt=0, description="Average dwell time seconds")
    clearance_time_s: float = Field(default=15.0, ge=0, description="Clearance time seconds")
    cv_dwell: float = Field(default=0.6, gt=0, description="CV of dwell time")
    z_factor: float = Field(default=1.96, gt=0, description="Z-factor for confidence")
    demand_buses_per_hour: float = Field(default=6.0, ge=0, description="Current demand buses/hour")


class StopCapacityResponse(BaseModel):
    """HCM 2000 stop capacity analysis response."""

    capacity_buses_per_hour: float
    effective_dwell_s: float
    n_berths: int
    green_ratio: float
    z_factor: float
    cv_dwell: float
    utilization: float
    los_grade: str
    los_description: str
    avg_wait_seconds: float


# ---------------------------------------------------------------------------
# CRUD schemas
# ---------------------------------------------------------------------------


class GeneratedStopCreate(BaseModel):
    """Create a generated stop record."""

    site_id: uuid.UUID | None = None
    ligne_id: uuid.UUID | None = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    catchment_radius_m: float = Field(default=500.0, gt=0)
    demand_passengers: int = Field(default=0, ge=0)
    berth_count: int = Field(default=1, ge=1)
    source: str = Field(default="manual")
    name: str | None = None

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in SOURCE_OPTIONS:
            raise ValueError(f"source must be one of {SOURCE_OPTIONS}")
        return v


class GeneratedStopResponse(BaseModel):
    """Generated stop record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    ligne_id: uuid.UUID | None
    lat: float
    lng: float
    catchment_radius_m: float
    demand_passengers: int
    berth_count: int
    capacity_buses_per_hour: float | None
    capacity_los: str | None
    avg_wait_seconds: float | None
    source: str
    name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
