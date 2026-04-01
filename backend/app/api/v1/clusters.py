from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.optimization import Cluster, Optimization
from app.models.site import Site
from app.schemas.optimization import (
    ClusterEmployee,
    ClusteringRequest,
    ClusteringResponse,
    ClusterResponse,
    OptimizationResponse,
)
from app.services.clustering import EmployeePoint, run_clustering

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clusters")


# ---------------------------------------------------------------------------
# POST /clusters/generate — run clustering algorithm
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=ClusteringResponse, status_code=201)
async def generate_clusters(
    body: ClusteringRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ClusteringResponse:
    """Run clustering for a site and persist results."""
    # Validate site exists and belongs to tenant
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

    # Fetch active employees with coordinates for the site
    emp_stmt = select(Employee).where(
        Employee.site_id == body.site_id,
        Employee.tenant_id == current_user.tenant_id,
        Employee.active.is_(True),
        Employee.lat.isnot(None),
        Employee.lng.isnot(None),
    )
    emp_result = await db.execute(emp_stmt)
    employees = list(emp_result.scalars().all())

    if not employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employees with coordinates found for this site",
        )

    # Build employee points
    points = [
        EmployeePoint(
            employee_id=emp.id,
            lat=emp.lat,
            lng=emp.lng,
            is_pmr=emp.is_pmr,
        )
        for emp in employees
    ]

    # Run clustering
    cluster_results = run_clustering(
        employees=points,
        algorithm=body.algorithm,
        eps_meters=body.eps_meters,
        min_samples=body.min_samples,
        n_clusters=body.n_clusters,
        max_cluster_size=body.max_cluster_size,
    )

    # Create optimization record
    optimization = Optimization(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        condition_type=body.condition_type,
        status="completed",
        params={
            "algorithm": body.algorithm,
            "eps_meters": body.eps_meters,
            "min_samples": body.min_samples,
            "n_clusters": body.n_clusters,
            "max_cluster_size": body.max_cluster_size,
        },
        metrics={
            "total_employees": len(employees),
            "total_clusters": len(cluster_results),
            "avg_cluster_size": round(
                len(employees) / len(cluster_results), 2
            )
            if cluster_results
            else 0,
        },
        target_date=body.target_date,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(optimization)
    await db.flush()

    # Create cluster records
    db_clusters: list[Cluster] = []
    for cr in cluster_results:
        cluster = Cluster(
            optimization_id=optimization.id,
            site_id=body.site_id,
            centroid_lat=cr.centroid_lat,
            centroid_lng=cr.centroid_lng,
            employee_count=cr.employee_count,
            pmr_count=cr.pmr_count,
            employee_ids=cr.employee_ids,
        )
        db.add(cluster)
        db_clusters.append(cluster)

    await db.flush()
    for cluster in db_clusters:
        await db.refresh(cluster)
    await db.refresh(optimization)

    logger.info(
        "Clustering generated: %d clusters for site %s (algorithm=%s) by user %s",
        len(db_clusters),
        body.site_id,
        body.algorithm,
        current_user.id,
    )

    # Build response
    cluster_responses = [
        ClusterResponse.model_validate(c) for c in db_clusters
    ]

    return ClusteringResponse(
        optimization=OptimizationResponse.model_validate(optimization),
        clusters=cluster_responses,
        total_clusters=len(cluster_responses),
        total_employees=len(employees),
    )


# ---------------------------------------------------------------------------
# GET /clusters — list saved clusters
# ---------------------------------------------------------------------------


@router.get("", response_model=list[ClusterResponse])
async def list_clusters(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    optimization_id: uuid.UUID | None = Query(
        default=None, description="Filter by optimization run"
    ),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[ClusterResponse]:
    """List saved clusters, optionally filtered by site or optimization."""
    conditions = [
        Optimization.tenant_id == current_user.tenant_id,
    ]
    if site_id is not None:
        conditions.append(Cluster.site_id == site_id)
    if optimization_id is not None:
        conditions.append(Cluster.optimization_id == optimization_id)

    stmt = (
        select(Cluster)
        .join(Optimization, Cluster.optimization_id == Optimization.id)
        .where(*conditions)
        .order_by(Cluster.created_at.desc())
    )
    result = await db.execute(stmt)
    clusters = list(result.scalars().all())

    return [ClusterResponse.model_validate(c) for c in clusters]


# ---------------------------------------------------------------------------
# GET /clusters/{id} — single cluster with employee details
# ---------------------------------------------------------------------------


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(
    cluster_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ClusterResponse:
    """Get a single cluster with its employee details."""
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

    # Fetch employee details
    emp_stmt = select(Employee).where(Employee.id.in_(cluster.employee_ids))
    emp_result = await db.execute(emp_stmt)
    employees = list(emp_result.scalars().all())

    response = ClusterResponse.model_validate(cluster)
    response.employees = [
        ClusterEmployee(
            employee_id=emp.id,
            first_name=emp.first_name,
            last_name=emp.last_name,
            lat=emp.lat,
            lng=emp.lng,
            is_pmr=emp.is_pmr,
        )
        for emp in employees
    ]

    return response
