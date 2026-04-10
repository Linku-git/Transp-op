from __future__ import annotations

import json
import logging
import math
import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.avl_metric import AVLMetric
from app.schemas.avl_metric import (
    AVLMetricListMeta,
    AVLMetricListResponse,
    AVLMetricResponse,
    KPIComputeRequest,
    KPIComputeResponse,
    KPIResult,
)
from app.services.sotreg.avl_kpi_service import (
    compute_all_kpis,
    compute_commercial_speed,
    compute_headway_cov,
    compute_load_factor,
    compute_otp,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/performance")


# ---------------------------------------------------------------------------
# POST /sotreg/performance/compute — trigger KPI computation
# ---------------------------------------------------------------------------


@router.post("/compute", response_model=KPIComputeResponse)
async def compute_kpis(
    body: KPIComputeRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> KPIComputeResponse:
    """Compute and store AVL-based operational KPIs."""
    arrivals_data = None
    if body.arrivals:
        arrivals_data = [
            {
                "scheduled_time": a.scheduled_time,
                "actual_time": a.actual_time,
                "stop_id": a.stop_id,
            }
            for a in body.arrivals
        ]

    departure_times = body.departure_times
    load_obs = None
    if body.load_observations:
        load_obs = [
            {"passenger_count": o.passenger_count, "vehicle_capacity": o.vehicle_capacity}
            for o in body.load_observations
        ]

    trips_data = None
    if body.trips:
        trips_data = []
        for t in body.trips:
            trip = {"distance_km": t.distance_km}
            if t.duration_hours is not None:
                trip["duration_hours"] = t.duration_hours
            elif t.start_time and t.end_time:
                delta = (t.end_time - t.start_time).total_seconds() / 3600
                trip["duration_hours"] = delta
            trips_data.append(trip)

    all_results = compute_all_kpis(
        arrivals=arrivals_data,
        departure_times=departure_times,
        load_observations=load_obs,
        trips=trips_data,
    )

    results: list[KPIResult] = []
    for key in ["otp", "headway_cov", "load_factor", "commercial_speed"]:
        if key not in all_results:
            continue
        kpi = all_results[key]
        value = _extract_value(key, kpi)
        meets = kpi.get("meets_target", False)
        sample = _extract_sample(key, kpi)

        metric = AVLMetric(
            tenant_id=current_user.tenant_id,
            ligne_id=body.ligne_id,
            vehicle_id=body.vehicle_id,
            metric_type=key,
            value=value,
            metric_date=body.metric_date,
            period=body.period,
            sample_size=sample,
            meets_target=meets,
            details=json.dumps({k: _safe_val(v) for k, v in kpi.items()}),
        )
        db.add(metric)

        results.append(KPIResult(
            metric_type=key,
            value=value,
            meets_target=meets,
            sample_size=sample,
            details=kpi,
        ))

    await db.flush()

    logger.info(
        "KPIs computed: %d metrics for ligne=%s, vehicle=%s by user %s",
        len(results),
        body.ligne_id,
        body.vehicle_id,
        current_user.id,
    )

    return KPIComputeResponse(
        results=results,
        computed_at=datetime.utcnow().isoformat(),
        ligne_id=str(body.ligne_id) if body.ligne_id else None,
        vehicle_id=str(body.vehicle_id) if body.vehicle_id else None,
        period=body.period,
    )


def _extract_value(metric_type: str, kpi: dict) -> float:
    """Extract the primary value for a metric type."""
    key_map = {
        "otp": "otp_pct",
        "headway_cov": "cov",
        "load_factor": "load_factor",
        "commercial_speed": "commercial_speed_kmh",
    }
    return float(kpi.get(key_map.get(metric_type, "value"), 0))


def _extract_sample(metric_type: str, kpi: dict) -> int:
    """Extract sample size for a metric type."""
    key_map = {
        "otp": "total_arrivals",
        "headway_cov": "headway_count",
        "load_factor": "observation_count",
        "commercial_speed": "trip_count",
    }
    return int(kpi.get(key_map.get(metric_type, "sample_size"), 0))


def _safe_val(v: object) -> object:
    """Make a value JSON-serializable."""
    if isinstance(v, datetime):
        return v.isoformat()
    return v


# ---------------------------------------------------------------------------
# GET /sotreg/performance/kpis — list KPIs with filters
# ---------------------------------------------------------------------------


@router.get("/kpis", response_model=AVLMetricListResponse)
async def list_kpis(
    ligne_id: uuid.UUID | None = Query(default=None),
    vehicle_id: uuid.UUID | None = Query(default=None),
    metric_type: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    period: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> AVLMetricListResponse:
    """List AVL KPI metrics with optional filters and pagination."""
    conditions = [AVLMetric.tenant_id == current_user.tenant_id]

    if ligne_id is not None:
        conditions.append(AVLMetric.ligne_id == ligne_id)
    if vehicle_id is not None:
        conditions.append(AVLMetric.vehicle_id == vehicle_id)
    if metric_type is not None:
        conditions.append(AVLMetric.metric_type == metric_type)
    if date_from is not None:
        conditions.append(AVLMetric.metric_date >= date_from)
    if date_to is not None:
        conditions.append(AVLMetric.metric_date <= date_to)
    if period is not None:
        conditions.append(AVLMetric.period == period)

    count_stmt = select(func.count()).select_from(AVLMetric).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    stmt = (
        select(AVLMetric)
        .where(*conditions)
        .order_by(AVLMetric.metric_date.desc(), AVLMetric.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    metrics = list(result.scalars().all())

    return AVLMetricListResponse(
        data=[AVLMetricResponse.model_validate(m) for m in metrics],
        meta=AVLMetricListMeta(page=page, pages=pages, total=total, page_size=page_size),
    )


# ---------------------------------------------------------------------------
# GET /sotreg/performance/kpis/{ligne_id} — KPIs for specific ligne
# ---------------------------------------------------------------------------


@router.get("/kpis/{ligne_id}", response_model=AVLMetricListResponse)
async def get_ligne_kpis(
    ligne_id: uuid.UUID,
    metric_type: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> AVLMetricListResponse:
    """Get KPIs for a specific transport line."""
    conditions = [
        AVLMetric.tenant_id == current_user.tenant_id,
        AVLMetric.ligne_id == ligne_id,
    ]
    if metric_type is not None:
        conditions.append(AVLMetric.metric_type == metric_type)
    if date_from is not None:
        conditions.append(AVLMetric.metric_date >= date_from)
    if date_to is not None:
        conditions.append(AVLMetric.metric_date <= date_to)

    count_stmt = select(func.count()).select_from(AVLMetric).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    stmt = (
        select(AVLMetric)
        .where(*conditions)
        .order_by(AVLMetric.metric_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    metrics = list(result.scalars().all())

    return AVLMetricListResponse(
        data=[AVLMetricResponse.model_validate(m) for m in metrics],
        meta=AVLMetricListMeta(page=page, pages=pages, total=total, page_size=page_size),
    )
