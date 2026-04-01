from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLUSTERING_ALGORITHMS = ["dbscan", "kmeans", "hierarchical"]
CONDITION_TYPES = ["normal", "rain", "strike", "peak", "night"]
OPTIMIZATION_STATUSES = ["pending", "running", "completed", "failed"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ClusteringRequest(BaseModel):
    """Request to run clustering for a site."""

    site_id: uuid.UUID
    algorithm: str = Field(default="dbscan", max_length=30)
    eps_meters: float = Field(default=500.0, ge=50.0, le=5000.0)
    min_samples: int = Field(default=2, ge=1, le=20)
    n_clusters: int | None = Field(default=None, ge=2, le=500)
    max_cluster_size: int | None = Field(default=None, ge=2, le=100)
    condition_type: str = Field(default="normal", max_length=30)
    target_date: date | None = None

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        if v not in CLUSTERING_ALGORITHMS:
            raise ValueError(f"algorithm must be one of {CLUSTERING_ALGORITHMS}")
        return v

    @field_validator("condition_type")
    @classmethod
    def validate_condition(cls, v: str) -> str:
        if v not in CONDITION_TYPES:
            raise ValueError(f"condition_type must be one of {CONDITION_TYPES}")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ClusterEmployee(BaseModel):
    """Employee info within a cluster response."""

    employee_id: uuid.UUID
    first_name: str
    last_name: str
    lat: float | None
    lng: float | None
    is_pmr: bool


class ClusterResponse(BaseModel):
    """A single cluster with employees."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    optimization_id: uuid.UUID
    site_id: uuid.UUID
    centroid_lat: float
    centroid_lng: float
    employee_count: int
    pmr_count: int
    employee_ids: list[uuid.UUID]
    created_at: datetime

    # Optionally populated
    employees: list[ClusterEmployee] | None = None


class OptimizationResponse(BaseModel):
    """Optimization run summary."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None
    condition_type: str
    status: str
    params: dict
    metrics: dict
    target_date: date | None
    created_at: datetime
    completed_at: datetime | None


class ClusteringResponse(BaseModel):
    """Full clustering result: optimization info + clusters."""

    optimization: OptimizationResponse
    clusters: list[ClusterResponse]
    total_clusters: int
    total_employees: int


# ---------------------------------------------------------------------------
# Meeting zone schemas (Session 19)
# ---------------------------------------------------------------------------


class AccessLegResponse(BaseModel):
    """Walking path from employee to meeting zone."""

    employee_id: uuid.UUID
    meeting_zone_lat: float
    meeting_zone_lng: float
    walking_distance_meters: float
    walking_time_seconds: float
    within_constraint: bool


class MeetingZoneResponse(BaseModel):
    """Optimized meeting/gathering point for a cluster."""

    cluster_index: int
    lat: float
    lng: float
    road_name: str | None
    snap_distance_meters: float
    pmr_accessible: bool
    employee_count: int
    pmr_count: int
    employee_ids: list[uuid.UUID]
    access_legs: list[AccessLegResponse]
    all_within_constraint: bool


class MeetingZonesResult(BaseModel):
    """Full meeting zones optimization result."""

    optimization_id: uuid.UUID
    site_id: uuid.UUID
    zones: list[MeetingZoneResponse]
    total_zones: int
    total_employees: int
    zones_within_constraint: int
    max_walking_distance_meters: float
