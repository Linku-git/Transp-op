from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.site import Site
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
    FleetByCondition,
    FleetByMotorization,
    FleetBySite,
    FleetByType,
    FleetSummary,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicles")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _vehicle_to_response(vehicle: Vehicle) -> VehicleResponse:
    resp = VehicleResponse.model_validate(vehicle)
    if vehicle.site is not None:
        resp.site_name = vehicle.site.name
    return resp


# ---------------------------------------------------------------------------
# GET /vehicles — list with filters
# ---------------------------------------------------------------------------


@router.get("", response_model=dict)
async def list_vehicles(
    site_id: uuid.UUID | None = Query(default=None),
    is_pmr_accessible: bool | None = Query(default=None),
    condition: str | None = Query(default=None),
    motorization: str | None = Query(default=None),
    zfe_compliant: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List vehicles with optional filters and pagination."""
    conditions = [Vehicle.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(Vehicle.site_id == site_id)
    if is_pmr_accessible is not None:
        conditions.append(Vehicle.is_pmr_accessible == is_pmr_accessible)
    if condition is not None:
        conditions.append(Vehicle.condition == condition)
    if motorization is not None:
        conditions.append(Vehicle.motorization == motorization)
    if zfe_compliant is not None:
        conditions.append(Vehicle.zfe_compliant == zfe_compliant)

    # Count
    count_stmt = select(func.count()).select_from(Vehicle).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Paginated data
    offset = (page - 1) * page_size
    data_stmt = (
        select(Vehicle)
        .where(*conditions)
        .order_by(Vehicle.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    data_result = await db.execute(data_stmt)
    vehicles = list(data_result.scalars().all())

    pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [_vehicle_to_response(v).model_dump(mode="json") for v in vehicles],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# POST /vehicles — create vehicle
# ---------------------------------------------------------------------------


@router.post("", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    body: VehicleCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> VehicleResponse:
    """Create a new vehicle."""
    # Validate site if provided
    if body.site_id is not None:
        site_stmt = select(Site).where(
            Site.id == body.site_id,
            Site.tenant_id == current_user.tenant_id,
        )
        site_result = await db.execute(site_stmt)
        if site_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found or does not belong to your tenant",
            )

    vehicle = Vehicle(
        tenant_id=current_user.tenant_id,
        **body.model_dump(),
    )
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)

    logger.info("Vehicle %s created by user %s", vehicle.id, current_user.id)
    return _vehicle_to_response(vehicle)


# ---------------------------------------------------------------------------
# PUT /vehicles/{id} — update vehicle
# ---------------------------------------------------------------------------


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    body: VehicleUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> VehicleResponse:
    """Update an existing vehicle."""
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    await db.flush()
    await db.refresh(vehicle)

    logger.info("Vehicle %s updated by user %s", vehicle_id, current_user.id)
    return _vehicle_to_response(vehicle)


# ---------------------------------------------------------------------------
# DELETE /vehicles/{id} — delete vehicle
# ---------------------------------------------------------------------------


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a vehicle."""
    stmt = select(Vehicle).where(
        Vehicle.id == vehicle_id,
        Vehicle.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    await db.delete(vehicle)
    await db.flush()

    logger.info("Vehicle %s deleted by user %s", vehicle_id, current_user.id)


# ---------------------------------------------------------------------------
# GET /vehicles/fleet-summary — fleet overview
# ---------------------------------------------------------------------------


@router.get("/fleet-summary", response_model=FleetSummary)
async def fleet_summary(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> FleetSummary:
    """Return fleet aggregations by type, condition, motorization, and site."""
    tenant_filter = Vehicle.tenant_id == current_user.tenant_id

    # Totals
    totals_stmt = select(
        func.count().label("total"),
        func.coalesce(func.sum(Vehicle.capacity), 0).label("total_cap"),
        func.count().filter(Vehicle.is_pmr_accessible.is_(True)).label("pmr"),
        func.count().filter(Vehicle.zfe_compliant.is_(True)).label("zfe"),
    ).where(tenant_filter)
    totals = (await db.execute(totals_stmt)).one()

    # By type
    type_stmt = (
        select(
            Vehicle.type,
            func.count().label("cnt"),
            func.coalesce(func.sum(Vehicle.capacity), 0).label("cap"),
        )
        .where(tenant_filter)
        .group_by(Vehicle.type)
        .order_by(func.count().desc())
    )
    type_rows = (await db.execute(type_stmt)).all()

    # By condition
    cond_stmt = (
        select(Vehicle.condition, func.count().label("cnt"))
        .where(tenant_filter)
        .group_by(Vehicle.condition)
    )
    cond_rows = (await db.execute(cond_stmt)).all()

    # By motorization
    motor_stmt = (
        select(Vehicle.motorization, func.count().label("cnt"))
        .where(tenant_filter, Vehicle.motorization.isnot(None))
        .group_by(Vehicle.motorization)
    )
    motor_rows = (await db.execute(motor_stmt)).all()

    # By site
    site_stmt = (
        select(
            Vehicle.site_id,
            Site.name.label("site_name"),
            func.count().label("cnt"),
            func.coalesce(func.sum(Vehicle.capacity), 0).label("cap"),
            func.count().filter(Vehicle.is_pmr_accessible.is_(True)).label("pmr"),
        )
        .join(Site, Vehicle.site_id == Site.id)
        .where(tenant_filter, Vehicle.site_id.isnot(None))
        .group_by(Vehicle.site_id, Site.name)
    )
    site_rows = (await db.execute(site_stmt)).all()

    return FleetSummary(
        total_vehicles=totals.total,
        total_capacity=int(totals.total_cap),
        pmr_accessible_count=totals.pmr,
        zfe_compliant_count=totals.zfe,
        by_type=[
            FleetByType(type=r.type, count=r.cnt, total_capacity=int(r.cap))
            for r in type_rows
        ],
        by_condition=[
            FleetByCondition(condition=r.condition, count=r.cnt)
            for r in cond_rows
        ],
        by_motorization=[
            FleetByMotorization(motorization=r.motorization, count=r.cnt)
            for r in motor_rows
        ],
        by_site=[
            FleetBySite(
                site_id=r.site_id,
                site_name=r.site_name,
                count=r.cnt,
                total_capacity=int(r.cap),
                pmr_count=r.pmr,
            )
            for r in site_rows
        ],
    )
