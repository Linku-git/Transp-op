from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.generated_stop import GeneratedStop
from app.schemas.generated_stop import (
    GeneratedStopCreate,
    GeneratedStopResponse,
    StopCapacityRequest,
    StopCapacityResponse,
    StopGenerateRequest,
    StopGenerateResponse,
    GeneratedStopResult,
)
from app.services.sotreg.stop_capacity import compute_stop_capacity, compute_los_grade
from app.services.sotreg.stop_generator import generate_stops_from_employees

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/stops")


# ---------------------------------------------------------------------------
# POST /sotreg/stops/generate — generate stops via DBSCAN
# ---------------------------------------------------------------------------


@router.post("/generate", response_model=StopGenerateResponse)
async def generate_stops(
    body: StopGenerateRequest,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> StopGenerateResponse:
    """Generate candidate stop locations from employee GPS using DBSCAN."""
    conditions = [
        Employee.tenant_id == current_user.tenant_id,
        Employee.is_active == True,  # noqa: E712
        Employee.home_lat.isnot(None),
        Employee.home_lng.isnot(None),
    ]
    if body.site_id is not None:
        conditions.append(Employee.site_id == body.site_id)

    stmt = select(Employee).where(*conditions)
    result = await db.execute(stmt)
    employees = list(result.scalars().all())

    employee_dicts = [
        {
            "employee_id": str(e.id),
            "lat": float(e.home_lat),
            "lng": float(e.home_lng),
        }
        for e in employees
        if e.home_lat is not None and e.home_lng is not None
    ]

    stops = generate_stops_from_employees(
        employees=employee_dicts,
        eps_m=body.eps_m,
        min_pts=body.min_pts,
    )

    # Persist generated stops
    for stop_data in stops:
        gs = GeneratedStop(
            tenant_id=current_user.tenant_id,
            site_id=body.site_id,
            lat=stop_data["centroid_lat"],
            lng=stop_data["centroid_lng"],
            geom=func.ST_SetSRID(
                func.ST_MakePoint(stop_data["centroid_lng"], stop_data["centroid_lat"]),
                4326,
            ),
            catchment_radius_m=stop_data["catchment_radius_m"],
            demand_passengers=stop_data["employee_count"],
            source="dbscan",
        )
        db.add(gs)

    await db.flush()

    noise_count = len(employee_dicts) - sum(s["employee_count"] for s in stops)

    logger.info(
        "Generated %d stops from %d employees (eps=%.0fm, min_pts=%d, noise=%d) by user %s",
        len(stops),
        len(employee_dicts),
        body.eps_m,
        body.min_pts,
        noise_count,
        current_user.id,
    )

    return StopGenerateResponse(
        stops_generated=len(stops),
        eps_m=body.eps_m,
        min_pts=body.min_pts,
        noise_count=noise_count,
        stops=[GeneratedStopResult(**s) for s in stops],
    )


# ---------------------------------------------------------------------------
# POST /sotreg/stops/capacity — compute HCM 2000 capacity
# ---------------------------------------------------------------------------


@router.post("/capacity", response_model=StopCapacityResponse)
async def stop_capacity(
    body: StopCapacityRequest,
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
) -> StopCapacityResponse:
    """Compute stop capacity using HCM 2000 formula."""
    cap = compute_stop_capacity(
        n_berths=body.n_berths,
        green_ratio=body.green_ratio,
        dwell_time_s=body.dwell_time_s,
        clearance_time_s=body.clearance_time_s,
        cv_dwell=body.cv_dwell,
        z_factor=body.z_factor,
    )
    los = compute_los_grade(
        demand_buses_per_hour=body.demand_buses_per_hour,
        capacity_buses_per_hour=cap["capacity_buses_per_hour"],
    )

    logger.info(
        "Stop capacity: %.1f buses/hr, LOS %s (util=%.2f) by user %s",
        cap["capacity_buses_per_hour"],
        los["los_grade"],
        los["utilization"],
        current_user.id,
    )

    return StopCapacityResponse(
        capacity_buses_per_hour=cap["capacity_buses_per_hour"],
        effective_dwell_s=cap["effective_dwell_s"],
        n_berths=cap["n_berths"],
        green_ratio=cap["green_ratio"],
        z_factor=cap["z_factor"],
        cv_dwell=cap["cv_dwell"],
        utilization=los["utilization"],
        los_grade=los["los_grade"],
        los_description=los["description"],
        avg_wait_seconds=los["avg_wait_seconds"],
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@router.post("/", response_model=GeneratedStopResponse, status_code=status.HTTP_201_CREATED)
async def create_stop(
    body: GeneratedStopCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> GeneratedStop:
    """Create a manual stop."""
    gs = GeneratedStop(
        tenant_id=current_user.tenant_id,
        site_id=body.site_id,
        ligne_id=body.ligne_id,
        lat=body.lat,
        lng=body.lng,
        geom=func.ST_SetSRID(func.ST_MakePoint(body.lng, body.lat), 4326),
        catchment_radius_m=body.catchment_radius_m,
        demand_passengers=body.demand_passengers,
        berth_count=body.berth_count,
        source=body.source,
        name=body.name,
    )
    db.add(gs)
    await db.flush()
    await db.refresh(gs)
    logger.info("Stop %s created by user %s", gs.id, current_user.id)
    return gs


@router.get("/", response_model=list[GeneratedStopResponse])
async def list_stops(
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> list[GeneratedStop]:
    """List all generated stops for the tenant."""
    stmt = (
        select(GeneratedStop)
        .where(GeneratedStop.tenant_id == current_user.tenant_id)
        .order_by(GeneratedStop.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{stop_id}", response_model=GeneratedStopResponse)
async def get_stop(
    stop_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "responsable_parc")),
    db: AsyncSession = Depends(get_db),
) -> GeneratedStop:
    """Get a single generated stop."""
    stmt = select(GeneratedStop).where(
        GeneratedStop.id == stop_id,
        GeneratedStop.tenant_id == current_user.tenant_id,
    )
    gs = (await db.execute(stmt)).scalar_one_or_none()
    if gs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    return gs


@router.delete("/{stop_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_stop(
    stop_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a generated stop."""
    stmt = select(GeneratedStop).where(
        GeneratedStop.id == stop_id,
        GeneratedStop.tenant_id == current_user.tenant_id,
    )
    gs = (await db.execute(stmt)).scalar_one_or_none()
    if gs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    await db.delete(gs)
    await db.flush()
    logger.info("Stop %s deleted by user %s", stop_id, current_user.id)
