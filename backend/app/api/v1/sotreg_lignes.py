from __future__ import annotations

import logging
import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.ligne import Ligne
from app.schemas.ligne import (
    LigneCreate,
    LigneListMeta,
    LigneListResponse,
    LigneResponse,
    LigneUpdate,
)
from app.services.sotreg.context_service import compute_line_km_annual

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sotreg/lignes")


# ---------------------------------------------------------------------------
# GET /sotreg/lignes — list with pagination & filters
# ---------------------------------------------------------------------------


@router.get("/", response_model=LigneListResponse)
async def list_lignes(
    service_type: str | None = Query(default=None, description="Filter by service type"),
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> LigneListResponse:
    """List all transport lines for the current tenant."""
    conditions = [Ligne.tenant_id == current_user.tenant_id]
    if service_type is not None:
        conditions.append(Ligne.service_type == service_type)
    if site_id is not None:
        conditions.append(Ligne.site_id == site_id)
    if is_active is not None:
        conditions.append(Ligne.is_active == is_active)

    count_stmt = select(func.count()).select_from(Ligne).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    stmt = (
        select(Ligne)
        .where(*conditions)
        .order_by(Ligne.code.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    lignes = list(result.scalars().all())

    return LigneListResponse(
        data=[LigneResponse.model_validate(l) for l in lignes],
        meta=LigneListMeta(page=page, pages=pages, total=total, page_size=page_size),
    )


# ---------------------------------------------------------------------------
# GET /sotreg/lignes/{ligne_id} — single ligne
# ---------------------------------------------------------------------------


@router.get("/{ligne_id}", response_model=LigneResponse)
async def get_ligne(
    ligne_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "responsable_exploitation")),
    db: AsyncSession = Depends(get_db),
) -> Ligne:
    """Get a single transport line by UUID."""
    stmt = select(Ligne).where(
        Ligne.id == ligne_id,
        Ligne.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    ligne = result.scalar_one_or_none()

    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne not found",
        )
    return ligne


# ---------------------------------------------------------------------------
# POST /sotreg/lignes — create
# ---------------------------------------------------------------------------


@router.post("/", response_model=LigneResponse, status_code=status.HTTP_201_CREATED)
async def create_ligne(
    body: LigneCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Ligne:
    """Create a new transport line."""
    # Duplicate code check
    dup_stmt = select(Ligne).where(
        Ligne.code == body.code,
        Ligne.tenant_id == current_user.tenant_id,
    )
    if (await db.execute(dup_stmt)).scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A ligne with this code already exists",
        )

    km_annual = compute_line_km_annual(
        body.distance_km, body.rotations_per_day, body.operating_days_per_year
    )

    ligne = Ligne(
        tenant_id=current_user.tenant_id,
        code=body.code,
        name=body.name,
        site_id=body.site_id,
        origin_lat=body.origin_lat,
        origin_lng=body.origin_lng,
        dest_lat=body.dest_lat,
        dest_lng=body.dest_lng,
        origin_geom=func.ST_SetSRID(
            func.ST_MakePoint(body.origin_lng, body.origin_lat), 4326
        ),
        dest_geom=func.ST_SetSRID(
            func.ST_MakePoint(body.dest_lng, body.dest_lat), 4326
        ),
        distance_km=body.distance_km,
        rotations_per_day=body.rotations_per_day,
        operating_days_per_year=body.operating_days_per_year,
        km_annual=km_annual,
        vehicle_type=body.vehicle_type,
        motorization=body.motorization,
        passenger_count_avg=body.passenger_count_avg,
        shift_type=body.shift_type,
        service_type=body.service_type,
        pente_moyenne_pct=body.pente_moyenne_pct,
    )
    db.add(ligne)
    await db.flush()
    await db.refresh(ligne)

    logger.info("Ligne %s (%s) created by user %s", ligne.id, ligne.code, current_user.id)
    return ligne


# ---------------------------------------------------------------------------
# PUT /sotreg/lignes/{ligne_id} — update
# ---------------------------------------------------------------------------


@router.put("/{ligne_id}", response_model=LigneResponse)
async def update_ligne(
    ligne_id: uuid.UUID,
    body: LigneUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Ligne:
    """Update an existing transport line."""
    stmt = select(Ligne).where(
        Ligne.id == ligne_id,
        Ligne.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    ligne = result.scalar_one_or_none()

    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ligne, field, value)

    # Recompute km_annual if any formula input changed
    if any(k in update_data for k in ("distance_km", "rotations_per_day", "operating_days_per_year")):
        ligne.km_annual = compute_line_km_annual(
            ligne.distance_km, ligne.rotations_per_day, ligne.operating_days_per_year
        )

    # Recompute geometry if coordinates changed
    if "origin_lat" in update_data or "origin_lng" in update_data:
        ligne.origin_geom = func.ST_SetSRID(
            func.ST_MakePoint(ligne.origin_lng, ligne.origin_lat), 4326
        )
    if "dest_lat" in update_data or "dest_lng" in update_data:
        ligne.dest_geom = func.ST_SetSRID(
            func.ST_MakePoint(ligne.dest_lng, ligne.dest_lat), 4326
        )

    await db.flush()
    await db.refresh(ligne)

    logger.info("Ligne %s updated by user %s", ligne.id, current_user.id)
    return ligne


# ---------------------------------------------------------------------------
# DELETE /sotreg/lignes/{ligne_id} — hard delete
# ---------------------------------------------------------------------------


@router.delete("/{ligne_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_ligne(
    ligne_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a transport line."""
    stmt = select(Ligne).where(
        Ligne.id == ligne_id,
        Ligne.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    ligne = result.scalar_one_or_none()

    if ligne is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ligne not found",
        )

    await db.delete(ligne)
    await db.flush()
    logger.info("Ligne %s deleted by user %s", ligne_id, current_user.id)
