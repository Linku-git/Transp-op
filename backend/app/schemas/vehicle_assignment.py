from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.optimization import ClusterResponse


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class VehicleAssignmentRequest(BaseModel):
    """Request to assign vehicles to clusters from an optimization run."""

    site_id: uuid.UUID
    optimization_id: uuid.UUID
    max_walking_distance: float = Field(
        default=800.0,
        ge=100.0,
        le=5000.0,
        description="Maximum walking distance in meters from employee to meeting point.",
    )
    include_volunteers: bool = Field(
        default=False,
        description="Include volunteer drivers in the assignment.",
    )


class SplitClusterRequest(BaseModel):
    """Request body for splitting an oversized cluster."""

    max_capacity: int = Field(
        ...,
        ge=2,
        le=100,
        description="Maximum number of employees per sub-cluster after split.",
    )


class MergeClustersRequest(BaseModel):
    """Request to merge multiple small clusters into one."""

    cluster_ids: list[uuid.UUID] = Field(
        ...,
        min_length=2,
        description="IDs of clusters to merge (minimum 2).",
    )
    max_capacity: int = Field(
        default=50,
        ge=2,
        le=100,
        description="Maximum capacity of the merged cluster.",
    )
    max_distance_km: float = Field(
        default=5.0,
        ge=0.5,
        le=50.0,
        description="Maximum distance in km between cluster centroids to allow merging.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class AssignmentResultResponse(BaseModel):
    """Assignment result for a single cluster."""

    model_config = ConfigDict(from_attributes=True)

    cluster_index: int
    vehicle_id: uuid.UUID | None
    vehicle_type: str | None = None
    vehicle_capacity: int | None = None
    employee_ids: list[uuid.UUID]
    employee_count: int
    pmr_count: int
    occupancy_rate: float
    was_split: bool = False
    was_merged: bool = False


class RecommendedVehicle(BaseModel):
    """Recommendation for a cluster that has no matching vehicle."""

    model_config = ConfigDict(from_attributes=True)

    cluster_index: int
    needed_capacity: int
    needs_pmr: bool
    needs_zfe: bool
    suggested_type: str


class VehicleAssignmentResponse(BaseModel):
    """Full vehicle assignment result for an optimization run."""

    model_config = ConfigDict(from_attributes=True)

    site_id: uuid.UUID
    optimization_id: uuid.UUID
    assignments: list[AssignmentResultResponse]
    total_vehicles_used: int
    total_employees_assigned: int
    avg_occupancy_rate: float
    unassigned_clusters: list[int]
    recommended_vehicles: list[RecommendedVehicle]


class SplitClusterResponse(BaseModel):
    """Result of splitting an oversized cluster."""

    model_config = ConfigDict(from_attributes=True)

    original_cluster_id: uuid.UUID
    new_clusters: list[ClusterResponse]
    total_sub_clusters: int


class MergeClustersResponse(BaseModel):
    """Result of merging multiple small clusters."""

    model_config = ConfigDict(from_attributes=True)

    merged_cluster_ids: list[uuid.UUID]
    result_cluster: ClusterResponse
    employee_count: int
