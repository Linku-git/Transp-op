from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLUSTERING_ALGORITHMS = ["dbscan", "kmeans", "hierarchical"]
CONDITION_TYPES = ["normal", "rain", "strike", "peak", "night", "transit_failure"]
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


# ---------------------------------------------------------------------------
# Full pipeline schemas (Session 23)
# ---------------------------------------------------------------------------


class OptimizationRunRequest(BaseModel):
    """Request to launch a full optimization pipeline."""

    site_id: uuid.UUID
    condition_type: str = Field(default="normal", max_length=30)
    target_date: date | None = None
    algorithm: str = Field(default="dbscan", max_length=30)
    eps_meters: float = Field(default=500.0, ge=50.0, le=5000.0)
    min_samples: int = Field(default=2, ge=1, le=20)
    n_clusters: int | None = Field(default=None, ge=2, le=500)
    max_cluster_size: int | None = Field(default=None, ge=2, le=100)
    max_walking_distance_meters: float = Field(
        default=800.0, ge=100.0, le=5000.0
    )
    max_route_duration_seconds: int = Field(default=5400, ge=600, le=18000)
    include_volunteers: bool = False
    use_osrm: bool = True

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


class OptimizationMetricsResponse(BaseModel):
    """Metrics from an optimization run."""

    total_employees: int
    employees_assigned: int
    employees_excluded_leave: int = 0
    total_clusters: int
    total_vehicles_used: int
    avg_occupancy_rate: float
    total_distance_km: float
    total_duration_minutes: float
    estimated_fuel_liters: float = 0.0
    estimated_fuel_cost_mad: float = 0.0
    co2_estimate_kg: float = 0.0
    time_saved_vs_individual_hours: float = 0.0
    unassigned_clusters: int = 0


class OptimizationStatusResponse(BaseModel):
    """Progress status of an optimization run."""

    optimization_id: uuid.UUID
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 to 1.0
    step: str  # current step description
    error: str | None = None


class OptimizationFullResponse(BaseModel):
    """Full optimization result with clusters, routes, and metrics."""

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
    clusters: list[ClusterResponse] = []
    routes: list[dict] = []  # Simplified route data


class OptimizationHistoryItem(BaseModel):
    """Summary of a past optimization for the history list."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    site_id: uuid.UUID | None
    condition_type: str
    status: str
    metrics: dict
    target_date: date | None
    created_at: datetime
    completed_at: datetime | None
    site_name: str | None = None
