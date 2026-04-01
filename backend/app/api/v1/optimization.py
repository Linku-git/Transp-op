from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.optimization import Cluster, Optimization, Route
from app.models.site import Site
from app.schemas.optimization import (
    ClusterResponse,
    OptimizationFullResponse,
    OptimizationHistoryItem,
    OptimizationRunRequest,
    OptimizationStatusResponse,
)
from app.tasks.optimization_tasks import (
    HAS_CELERY,
    get_optimization_status,
    run_optimization_task,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/optimize")


# ---------------------------------------------------------------------------
# Helper: build an OptimizationFullResponse from an Optimization ORM instance
# ---------------------------------------------------------------------------


def _build_full_response(
    optimization: Optimization,
    clusters: list[Cluster],
    routes: list[Route],
) -> OptimizationFullResponse:
    """Construct a full optimization response from ORM objects."""
    cluster_responses = [ClusterResponse.model_validate(c) for c in clusters]

    route_dicts: list[dict] = []
    for r in routes:
        route_dicts.append(
            {
                "id": str(r.id),
                "vehicle_id": str(r.vehicle_id) if r.vehicle_id else None,
                "site_id": str(r.site_id),
                "ordered_stops": r.ordered_stops,
                "total_distance_km": (
                    float(r.total_distance_km) if r.total_distance_km is not None else None
                ),
                "total_time_minutes": (
                    float(r.total_time_minutes) if r.total_time_minutes is not None else None
                ),
                "polyline": r.polyline,
                "rti_compliance_pct": (
                    float(r.rti_compliance_pct) if r.rti_compliance_pct is not None else None
                ),
            }
        )

    return OptimizationFullResponse(
        id=optimization.id,
        tenant_id=optimization.tenant_id,
        site_id=optimization.site_id,
        condition_type=optimization.condition_type,
        status=optimization.status,
        params=optimization.params,
        metrics=optimization.metrics,
        target_date=optimization.target_date,
        created_at=optimization.created_at,
        completed_at=optimization.completed_at,
        clusters=cluster_responses,
        routes=route_dicts,
    )


# ---------------------------------------------------------------------------
# POST /optimize  --  launch a full optimization pipeline
# ---------------------------------------------------------------------------


@router.post("", status_code=202)
async def launch_optimization(
    body: OptimizationRunRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Launch an asynchronous optimization pipeline for a site.

    Creates an Optimization record in ``pending`` state and dispatches the
    heavy computation to Celery (or runs it directly when Celery is
    unavailable).  Returns immediately with the ``optimization_id`` so the
    caller can poll for progress via ``GET /optimize/{id}/status``.
    """
    # 1. Validate site exists and belongs to tenant
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

    # 2. Create Optimization record (pending)
    optimization = Optimization(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        condition_type=body.condition_type,
        status="pending",
        params={
            "algorithm": body.algorithm,
            "eps_meters": body.eps_meters,
            "min_samples": body.min_samples,
            "n_clusters": body.n_clusters,
            "max_cluster_size": body.max_cluster_size,
            "max_walking_distance_meters": body.max_walking_distance_meters,
            "max_route_duration_seconds": body.max_route_duration_seconds,
            "include_volunteers": body.include_volunteers,
            "use_osrm": body.use_osrm,
        },
        metrics={},
        target_date=body.target_date,
    )
    db.add(optimization)
    await db.flush()
    await db.refresh(optimization)

    opt_id = optimization.id
    task_kwargs = {
        "optimization_id": str(opt_id),
        "site_id": str(body.site_id),
        "tenant_id": str(current_user.tenant_id),
        "condition_type": body.condition_type,
        "target_date": body.target_date.isoformat() if body.target_date else None,
        "algorithm": body.algorithm,
        "eps_meters": body.eps_meters,
        "min_samples": body.min_samples,
        "n_clusters": body.n_clusters,
        "max_cluster_size": body.max_cluster_size,
        "max_walking_distance_meters": body.max_walking_distance_meters,
        "max_route_duration_seconds": body.max_route_duration_seconds,
        "include_volunteers": body.include_volunteers,
        "use_osrm": body.use_osrm,
    }

    # 3. Dispatch to Celery or run directly
    if HAS_CELERY:
        from app.tasks.optimization_tasks import optimize_pipeline_task

        task = optimize_pipeline_task.delay(**task_kwargs)
        logger.info(
            "Optimization %s dispatched to Celery (task_id=%s) by user %s",
            opt_id,
            task.id,
            current_user.id,
        )
        return {
            "optimization_id": str(opt_id),
            "status": "pending",
            "message": "Optimization dispatched to background worker",
            "task_id": task.id,
        }

    # No Celery -- run synchronously
    logger.info(
        "Optimization %s running synchronously (no Celery) by user %s",
        opt_id,
        current_user.id,
    )
    result = await run_optimization_task(**task_kwargs)
    return {
        "optimization_id": str(opt_id),
        "status": result.get("status", "completed"),
        "message": "Optimization completed synchronously",
    }


# ---------------------------------------------------------------------------
# GET /optimize/latest/result  --  most recent completed optimization
# ---------------------------------------------------------------------------
# NOTE: Static paths (/latest/result, /history/list) MUST be registered
# before the parameterised /{optimization_id} routes so that FastAPI does
# not try to parse "latest" or "history" as a UUID path parameter.


@router.get("/latest/result", response_model=OptimizationFullResponse)
async def get_latest_optimization(
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> OptimizationFullResponse:
    """Retrieve the most recently completed optimization for the tenant.

    Returns the latest optimization whose status is ``completed``, ordered
    by ``created_at`` descending.
    """
    stmt = (
        select(Optimization)
        .options(
            selectinload(Optimization.clusters),
            selectinload(Optimization.routes),
        )
        .where(
            Optimization.tenant_id == current_user.tenant_id,
            Optimization.status == "completed",
        )
        .order_by(Optimization.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    optimization = result.scalar_one_or_none()

    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed optimization found for this tenant",
        )

    return _build_full_response(
        optimization,
        list(optimization.clusters),
        list(optimization.routes),
    )


# ---------------------------------------------------------------------------
# GET /optimize/history/list  --  paginated optimization history
# ---------------------------------------------------------------------------


@router.get("/history/list", response_model=list[OptimizationHistoryItem])
async def list_optimization_history(
    site_id: uuid.UUID | None = Query(
        default=None, description="Filter by site UUID"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Items per page"
    ),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[OptimizationHistoryItem]:
    """List past optimization runs for the tenant.

    Supports optional site filter and pagination. Returns a summary of
    each run including the site name.
    """
    conditions = [Optimization.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(Optimization.site_id == site_id)

    stmt = (
        select(Optimization)
        .options(selectinload(Optimization.site))
        .where(*conditions)
        .order_by(Optimization.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    optimizations = list(result.scalars().all())

    items: list[OptimizationHistoryItem] = []
    for opt in optimizations:
        item = OptimizationHistoryItem.model_validate(opt)
        item.site_name = opt.site.name if opt.site else None
        items.append(item)

    return items


# ---------------------------------------------------------------------------
# GET /optimize/{optimization_id}  --  full result
# ---------------------------------------------------------------------------


@router.get("/{optimization_id}", response_model=OptimizationFullResponse)
async def get_optimization(
    optimization_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> OptimizationFullResponse:
    """Retrieve the full result of an optimization run.

    Returns the optimization record together with its clusters and routes.
    """
    stmt = (
        select(Optimization)
        .options(
            selectinload(Optimization.clusters),
            selectinload(Optimization.routes),
        )
        .where(
            Optimization.id == optimization_id,
            Optimization.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    optimization = result.scalar_one_or_none()

    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization not found",
        )

    return _build_full_response(
        optimization,
        list(optimization.clusters),
        list(optimization.routes),
    )


# ---------------------------------------------------------------------------
# GET /optimize/{optimization_id}/status  --  progress polling
# ---------------------------------------------------------------------------


@router.get(
    "/{optimization_id}/status",
    response_model=OptimizationStatusResponse,
)
async def get_optimization_status_endpoint(
    optimization_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> OptimizationStatusResponse:
    """Poll the current status of an optimization run.

    First checks Redis for real-time progress set by the worker, then
    falls back to the database record.
    """
    # 1. Try Redis for live progress
    try:
        redis_status = get_optimization_status(optimization_id)
    except Exception:
        logger.warning(
            "Redis unavailable when fetching status for optimization %s",
            optimization_id,
        )
        redis_status = None

    if redis_status is not None:
        return OptimizationStatusResponse(
            optimization_id=optimization_id,
            status=redis_status["status"],
            progress=float(redis_status.get("progress", 0.0)),
            step=redis_status.get("step", ""),
            error=redis_status.get("error") or None,
        )

    # 2. Fallback to DB
    stmt = select(Optimization).where(
        Optimization.id == optimization_id,
        Optimization.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    optimization = result.scalar_one_or_none()

    if optimization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization not found",
        )

    # Map DB status to progress values
    progress_map = {
        "pending": 0.0,
        "running": 0.5,
        "completed": 1.0,
        "failed": 0.0,
    }

    return OptimizationStatusResponse(
        optimization_id=optimization_id,
        status=optimization.status,
        progress=progress_map.get(optimization.status, 0.0),
        step=optimization.status,
        error=optimization.metrics.get("error") if optimization.status == "failed" else None,
    )
