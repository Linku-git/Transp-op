from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.optimization import Cluster, Optimization
from app.models.site import Site
from app.models.vehicle import Vehicle
from app.schemas.optimization import ClusterResponse
from app.schemas.vehicle_assignment import (
    AssignmentResultResponse,
    MergeClustersRequest,
    MergeClustersResponse,
    RecommendedVehicle,
    SplitClusterRequest,
    SplitClusterResponse,
    VehicleAssignmentRequest,
    VehicleAssignmentResponse,
)
from app.services.clustering import ClusterResult
from app.services.vehicle_assignment import (
    AssignmentSummary,
    VehicleCandidate,
    assign_vehicles_to_clusters,
    merge_clusters,
    split_cluster,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicle-assignments")


# ---------------------------------------------------------------------------
# Helper: convert DB Cluster to service ClusterResult
# ---------------------------------------------------------------------------


def _cluster_to_result(cluster: Cluster) -> ClusterResult:
    """Convert a database Cluster row into a service-layer ClusterResult."""
    return ClusterResult(
        centroid_lat=cluster.centroid_lat,
        centroid_lng=cluster.centroid_lng,
        employee_ids=list(cluster.employee_ids),
        pmr_count=cluster.pmr_count,
        employee_count=cluster.employee_count,
    )


def _vehicle_to_candidate(vehicle: Vehicle) -> VehicleCandidate:
    """Convert a database Vehicle row into a service-layer VehicleCandidate."""
    return VehicleCandidate(
        vehicle_id=vehicle.id,
        capacity=vehicle.capacity,
        is_pmr_accessible=vehicle.is_pmr_accessible,
        zfe_compliant=vehicle.zfe_compliant,
        type=vehicle.type,
        is_volunteer=False,
    )


# ---------------------------------------------------------------------------
# POST /vehicle-assignments/assign
# ---------------------------------------------------------------------------


@router.post("/assign", response_model=VehicleAssignmentResponse, status_code=201)
async def assign_vehicles(
    body: VehicleAssignmentRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> VehicleAssignmentResponse:
    """Assign fleet vehicles (and optionally volunteer drivers) to clusters."""

    # 1. Validate site
    site_stmt = select(Site).where(
        Site.id == body.site_id,
        Site.tenant_id == current_user.tenant_id,
    )
    site_result = await db.execute(site_stmt)
    site = site_result.scalar_one_or_none()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found or does not belong to your tenant",
        )

    # 2. Validate optimization
    opt_stmt = select(Optimization).where(
        Optimization.id == body.optimization_id,
        Optimization.tenant_id == current_user.tenant_id,
    )
    opt_result = await db.execute(opt_stmt)
    optimization = opt_result.scalar_one_or_none()
    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization not found or does not belong to your tenant",
        )
    if optimization.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Optimization must have status 'completed'",
        )

    # 3. Fetch clusters for the optimization
    cluster_stmt = select(Cluster).where(
        Cluster.optimization_id == body.optimization_id,
    )
    cluster_result = await db.execute(cluster_stmt)
    db_clusters = list(cluster_result.scalars().all())

    if not db_clusters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clusters found for this optimization",
        )

    # 4. Fetch available vehicles for the site (exclude condition="Mauvais")
    vehicle_stmt = select(Vehicle).where(
        Vehicle.tenant_id == current_user.tenant_id,
        Vehicle.site_id == body.site_id,
        Vehicle.condition != "Mauvais",
    )
    vehicle_result = await db.execute(vehicle_stmt)
    db_vehicles = list(vehicle_result.scalars().all())

    # 5. Convert to service-layer objects
    cluster_results = [_cluster_to_result(c) for c in db_clusters]
    vehicle_candidates = [_vehicle_to_candidate(v) for v in db_vehicles]

    # 6. Collect all employee IDs from clusters
    all_employee_ids: set[uuid.UUID] = set()
    for c in db_clusters:
        all_employee_ids.update(c.employee_ids)

    # Fetch employees for location and PMR data
    emp_stmt = select(Employee).where(Employee.id.in_(list(all_employee_ids)))
    emp_result = await db.execute(emp_stmt)
    employees = list(emp_result.scalars().all())

    employee_locations: dict[uuid.UUID, tuple[float, float]] = {}
    employee_pmr: dict[uuid.UUID, bool] = {}
    for emp in employees:
        if emp.lat is not None and emp.lng is not None:
            employee_locations[emp.id] = (emp.lat, emp.lng)
        employee_pmr[emp.id] = emp.is_pmr

    # 7. Optionally fetch volunteer drivers
    volunteer_candidates: list[VehicleCandidate] = []
    if body.include_volunteers:
        vol_stmt = select(Employee).where(
            Employee.site_id == body.site_id,
            Employee.tenant_id == current_user.tenant_id,
            Employee.volunteer_driver.is_(True),
            Employee.active.is_(True),
        )
        vol_result = await db.execute(vol_stmt)
        volunteer_employees = list(vol_result.scalars().all())

        for vol in volunteer_employees:
            volunteer_candidates.append(
                VehicleCandidate(
                    vehicle_id=vol.id,
                    capacity=vol.carpool_seats,
                    is_pmr_accessible=False,
                    zfe_compliant=False,
                    type="Voiture",
                    is_volunteer=True,
                )
            )

    # 8. Run assignment
    summary: AssignmentSummary = assign_vehicles_to_clusters(
        clusters=cluster_results,
        vehicles=vehicle_candidates,
        site_zfe=site.zfe_zone,
        volunteer_drivers=volunteer_candidates if volunteer_candidates else None,
        employee_locations=employee_locations,
        employee_pmr=employee_pmr,
    )

    # 9. Build vehicle lookup for response enrichment
    vehicle_lookup: dict[uuid.UUID, Vehicle] = {v.id: v for v in db_vehicles}

    assignment_responses: list[AssignmentResultResponse] = []
    for a in summary.assignments:
        vehicle_type: str | None = None
        vehicle_capacity: int | None = None
        if a.vehicle_id is not None and a.vehicle_id in vehicle_lookup:
            v = vehicle_lookup[a.vehicle_id]
            vehicle_type = v.type
            vehicle_capacity = v.capacity

        assignment_responses.append(
            AssignmentResultResponse(
                cluster_index=a.cluster_index,
                vehicle_id=a.vehicle_id,
                vehicle_type=vehicle_type,
                vehicle_capacity=vehicle_capacity,
                employee_ids=a.employee_ids,
                employee_count=a.employee_count,
                pmr_count=a.pmr_count,
                occupancy_rate=a.occupancy_rate,
                was_split=a.was_split,
                was_merged=a.was_merged,
            )
        )

    recommended_responses: list[RecommendedVehicle] = []
    for idx, rec in enumerate(summary.recommended_vehicles):
        recommended_responses.append(
            RecommendedVehicle(
                cluster_index=summary.unassigned_clusters[idx]
                if idx < len(summary.unassigned_clusters)
                else idx,
                needed_capacity=rec["suggested_min_capacity"],
                needs_pmr=rec["pmr_required"],
                needs_zfe=rec["zfe_required"],
                suggested_type=rec["suggested_type"],
            )
        )

    logger.info(
        "Vehicle assignment completed for optimization %s: %d vehicles used, "
        "%d employees assigned by user %s",
        body.optimization_id,
        summary.total_vehicles_used,
        summary.total_employees_assigned,
        current_user.id,
    )

    return VehicleAssignmentResponse(
        site_id=body.site_id,
        optimization_id=body.optimization_id,
        assignments=assignment_responses,
        total_vehicles_used=summary.total_vehicles_used,
        total_employees_assigned=summary.total_employees_assigned,
        avg_occupancy_rate=summary.avg_occupancy_rate,
        unassigned_clusters=summary.unassigned_clusters,
        recommended_vehicles=recommended_responses,
    )


# ---------------------------------------------------------------------------
# POST /vehicle-assignments/split-cluster/{cluster_id}
# ---------------------------------------------------------------------------


@router.post(
    "/split-cluster/{cluster_id}",
    response_model=SplitClusterResponse,
    status_code=200,
)
async def split_cluster_endpoint(
    cluster_id: uuid.UUID,
    body: SplitClusterRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> SplitClusterResponse:
    """Split an oversized cluster into smaller sub-clusters."""

    # 1. Fetch cluster and verify tenant ownership via Optimization join
    stmt = (
        select(Cluster)
        .join(Optimization, Cluster.optimization_id == Optimization.id)
        .where(
            Cluster.id == cluster_id,
            Optimization.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    cluster = result.scalar_one_or_none()

    if cluster is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    # 2. Check if split is needed
    if cluster.employee_count <= body.max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cluster does not exceed max_capacity",
        )

    # 3. Fetch employee locations for the cluster
    emp_stmt = select(Employee).where(Employee.id.in_(list(cluster.employee_ids)))
    emp_result = await db.execute(emp_stmt)
    employees = list(emp_result.scalars().all())

    employee_locations: dict[uuid.UUID, tuple[float, float]] = {}
    employee_pmr: dict[uuid.UUID, bool] = {}
    for emp in employees:
        if emp.lat is not None and emp.lng is not None:
            employee_locations[emp.id] = (emp.lat, emp.lng)
        employee_pmr[emp.id] = emp.is_pmr

    # 4. Convert and split
    cluster_result = _cluster_to_result(cluster)
    sub_clusters = split_cluster(
        cluster=cluster_result,
        max_capacity=body.max_capacity,
        employee_locations=employee_locations,
        employee_pmr=employee_pmr,
    )

    # 5. Delete the original cluster
    original_optimization_id = cluster.optimization_id
    original_site_id = cluster.site_id
    original_cluster_id = cluster.id
    await db.delete(cluster)
    await db.flush()

    # 6. Create new Cluster DB records for each sub-cluster
    new_db_clusters: list[Cluster] = []
    for sc in sub_clusters:
        new_cluster = Cluster(
            optimization_id=original_optimization_id,
            site_id=original_site_id,
            centroid_lat=sc.centroid_lat,
            centroid_lng=sc.centroid_lng,
            employee_count=sc.employee_count,
            pmr_count=sc.pmr_count,
            employee_ids=sc.employee_ids,
        )
        db.add(new_cluster)
        new_db_clusters.append(new_cluster)

    await db.flush()
    for nc in new_db_clusters:
        await db.refresh(nc)

    logger.info(
        "Split cluster %s into %d sub-clusters (max_capacity=%d) by user %s",
        original_cluster_id,
        len(new_db_clusters),
        body.max_capacity,
        current_user.id,
    )

    return SplitClusterResponse(
        original_cluster_id=original_cluster_id,
        new_clusters=[ClusterResponse.model_validate(c) for c in new_db_clusters],
        total_sub_clusters=len(new_db_clusters),
    )


# ---------------------------------------------------------------------------
# POST /vehicle-assignments/merge-clusters
# ---------------------------------------------------------------------------


@router.post(
    "/merge-clusters",
    response_model=MergeClustersResponse,
    status_code=200,
)
async def merge_clusters_endpoint(
    body: MergeClustersRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> MergeClustersResponse:
    """Merge multiple small clusters into fewer, larger clusters."""

    # 1. Fetch all clusters and verify tenant ownership
    stmt = (
        select(Cluster)
        .join(Optimization, Cluster.optimization_id == Optimization.id)
        .where(
            Cluster.id.in_(body.cluster_ids),
            Optimization.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    db_clusters = list(result.scalars().all())

    # 2. Check all clusters were found
    found_ids = {c.id for c in db_clusters}
    missing_ids = set(body.cluster_ids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clusters not found: {[str(mid) for mid in missing_ids]}",
        )

    # 3. Verify all clusters belong to the same optimization
    optimization_ids = {c.optimization_id for c in db_clusters}
    if len(optimization_ids) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All clusters must belong to the same optimization",
        )

    common_optimization_id = db_clusters[0].optimization_id
    common_site_id = db_clusters[0].site_id

    # 4. Convert to ClusterResult objects and run merge
    cluster_results = [_cluster_to_result(c) for c in db_clusters]
    merged_results = merge_clusters(
        clusters=cluster_results,
        max_capacity=body.max_capacity,
        max_distance_km=body.max_distance_km,
    )

    # 5. Check if merge actually reduced the count
    if len(merged_results) >= len(db_clusters):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clusters are too far apart or exceed capacity to merge",
        )

    # 6. Delete original clusters
    for c in db_clusters:
        await db.delete(c)
    await db.flush()

    # 7. Create merged cluster record(s)
    new_db_clusters: list[Cluster] = []
    for mr in merged_results:
        new_cluster = Cluster(
            optimization_id=common_optimization_id,
            site_id=common_site_id,
            centroid_lat=mr.centroid_lat,
            centroid_lng=mr.centroid_lng,
            employee_count=mr.employee_count,
            pmr_count=mr.pmr_count,
            employee_ids=mr.employee_ids,
        )
        db.add(new_cluster)
        new_db_clusters.append(new_cluster)

    await db.flush()
    for nc in new_db_clusters:
        await db.refresh(nc)

    logger.info(
        "Merged %d clusters into %d cluster(s) for optimization %s by user %s",
        len(db_clusters),
        len(new_db_clusters),
        common_optimization_id,
        current_user.id,
    )

    # The schema expects a single result_cluster; use the first merged cluster
    # (in practice merging 2+ clusters into 1 is the common case)
    result_cluster = new_db_clusters[0]

    return MergeClustersResponse(
        merged_cluster_ids=list(body.cluster_ids),
        result_cluster=ClusterResponse.model_validate(result_cluster),
        employee_count=result_cluster.employee_count,
    )
