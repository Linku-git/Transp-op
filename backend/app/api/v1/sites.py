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
from app.models.site import Site
from app.schemas.site import (
    SiteCreate,
    SiteListMeta,
    SiteListResponse,
    SiteResponse,
    SiteSummary,
    SiteUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sites")


# ---------------------------------------------------------------------------
# GET /sites — list with filters + pagination
# ---------------------------------------------------------------------------


@router.get("/", response_model=SiteListResponse)
async def list_sites(
    city: str | None = Query(default=None, description="Filter by city name"),
    zfe_zone: bool | None = Query(default=None, description="Filter by ZFE zone status"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> SiteListResponse:
    """List all sites for the current user's tenant with optional filters."""
    # Base query scoped to tenant
    base_filter = Site.tenant_id == current_user.tenant_id

    # Build WHERE conditions
    conditions = [base_filter]
    if city is not None:
        conditions.append(Site.city.ilike(f"%{city}%"))
    if zfe_zone is not None:
        conditions.append(Site.zfe_zone == zfe_zone)

    # Count total matching rows
    count_stmt = select(func.count()).select_from(Site).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Calculate pagination
    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    # Fetch the page
    stmt = (
        select(Site)
        .where(*conditions)
        .order_by(Site.name.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    sites = list(result.scalars().all())

    return SiteListResponse(
        data=[SiteResponse.model_validate(s) for s in sites],
        meta=SiteListMeta(
            page=page,
            pages=pages,
            total=total,
            page_size=page_size,
        ),
    )


# ---------------------------------------------------------------------------
# GET /sites/{site_id} — get single site by UUID
# ---------------------------------------------------------------------------


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Get a single site by its UUID."""
    stmt = select(Site).where(
        Site.id == site_id,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    return site


# ---------------------------------------------------------------------------
# GET /sites/code/{code} — get site by code string
# ---------------------------------------------------------------------------


@router.get("/code/{code}", response_model=SiteResponse)
async def get_site_by_code(
    code: str,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Get a site by its unique code."""
    stmt = select(Site).where(
        Site.code == code,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    return site


# ---------------------------------------------------------------------------
# POST /sites — create site
# ---------------------------------------------------------------------------


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    body: SiteCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Create a new site within the current user's tenant."""
    # Check for duplicate code within tenant
    stmt = select(Site).where(
        Site.code == body.code,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A site with this code already exists",
        )

    site = Site(
        tenant_id=current_user.tenant_id,
        code=body.code,
        name=body.name,
        address=body.address,
        city=body.city,
        lat=body.lat,
        lng=body.lng,
        geom=func.ST_SetSRID(func.ST_MakePoint(body.lng, body.lat), 4326),
        num_shifts=body.num_shifts,
        shift_1_entry=body.shift_1_entry,
        shift_1_exit=body.shift_1_exit,
        shift_2_entry=body.shift_2_entry,
        shift_2_exit=body.shift_2_exit,
        shift_3_entry=body.shift_3_entry,
        shift_3_exit=body.shift_3_exit,
        working_days=body.working_days,
        days_per_week=body.days_per_week,
        contact_name=body.contact_name,
        contact_phone=body.contact_phone,
        access_notes=body.access_notes,
        parking_notes=body.parking_notes,
        zfe_zone=body.zfe_zone,
        security_profile=body.security_profile,
        timezone=body.timezone,
        observations=body.observations,
    )
    db.add(site)
    await db.flush()
    await db.refresh(site)

    logger.info("Site %s (%s) created by user %s", site.id, site.code, current_user.id)
    return site


# ---------------------------------------------------------------------------
# PUT /sites/{site_id} — update site
# ---------------------------------------------------------------------------


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: uuid.UUID,
    body: SiteUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Update an existing site. Only provided fields are changed."""
    stmt = select(Site).where(
        Site.id == site_id,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(site, field, value)

    # Recalculate PostGIS geom if lat or lng changed
    new_lat = update_data.get("lat", site.lat)
    new_lng = update_data.get("lng", site.lng)
    if "lat" in update_data or "lng" in update_data:
        site.geom = func.ST_SetSRID(func.ST_MakePoint(new_lng, new_lat), 4326)

    await db.flush()
    await db.refresh(site)

    logger.info("Site %s updated by user %s", site.id, current_user.id)
    return site


# ---------------------------------------------------------------------------
# DELETE /sites/{site_id} — delete site
# ---------------------------------------------------------------------------


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_site(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a site. Returns 204 on success.

    NOTE: Employee/vehicle relationship checks will be added when those
    models exist.
    """
    stmt = select(Site).where(
        Site.id == site_id,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    await db.delete(site)
    await db.flush()

    logger.info("Site %s deleted by user %s", site_id, current_user.id)


# ---------------------------------------------------------------------------
# GET /sites/{site_id}/summary — site summary with aggregate counts
# ---------------------------------------------------------------------------


@router.get("/{site_id}/summary", response_model=SiteSummary)
async def get_site_summary(
    site_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> SiteSummary:
    """Return a summary for a site including employee, vehicle, and PMR counts.

    NOTE: Counts are hardcoded to 0 until the Employee and Vehicle models
    are implemented in later sessions.
    """
    stmt = select(Site).where(
        Site.id == site_id,
        Site.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    site = result.scalar_one_or_none()

    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # TODO: Replace with real aggregate queries once Employee and Vehicle
    # models exist (sessions 09 and 20).
    return SiteSummary(
        id=site.id,
        code=site.code,
        name=site.name,
        city=site.city,
        employee_count=0,
        vehicle_count=0,
        pmr_count=0,
    )
