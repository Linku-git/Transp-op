from __future__ import annotations

import csv
import io
import logging
import math
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
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
# CSV column definitions — single source of truth for export + import
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "code", "name", "address", "city", "lat", "lng",
    "num_shifts",
    # Equipe 1
    "shift_1_type", "shift_1_depart_h1", "shift_1_retour_h1", "shift_1_depart_h2", "shift_1_retour_h2",
    # Equipe 2
    "shift_2_type", "shift_2_depart_h1", "shift_2_retour_h1", "shift_2_depart_h2", "shift_2_retour_h2",
    # Equipe 3
    "shift_3_type", "shift_3_depart_h1", "shift_3_retour_h1", "shift_3_depart_h2", "shift_3_retour_h2",
    "working_days", "days_per_week",
    "contact_name", "contact_phone",
    "zfe_zone", "security_profile", "timezone", "observations",
]


def _site_to_row(site: Site) -> dict:
    def fmt_time(t):
        return t.strftime("%H:%M") if t else ""

    return {
        "code": site.code,
        "name": site.name,
        "address": site.address or "",
        "city": site.city,
        "lat": str(site.lat),
        "lng": str(site.lng),
        "num_shifts": str(site.num_shifts),
        # Equipe 1
        "shift_1_type": site.shift_1_type or "",
        "shift_1_depart_h1": fmt_time(site.shift_1_entry),
        "shift_1_retour_h1": fmt_time(site.shift_1_exit),
        "shift_1_depart_h2": fmt_time(site.shift_1_depart_h2),
        "shift_1_retour_h2": fmt_time(site.shift_1_retour_h2),
        # Equipe 2
        "shift_2_type": site.shift_2_type or "",
        "shift_2_depart_h1": fmt_time(site.shift_2_entry),
        "shift_2_retour_h1": fmt_time(site.shift_2_exit),
        "shift_2_depart_h2": fmt_time(site.shift_2_depart_h2),
        "shift_2_retour_h2": fmt_time(site.shift_2_retour_h2),
        # Equipe 3
        "shift_3_type": site.shift_3_type or "",
        "shift_3_depart_h1": fmt_time(site.shift_3_entry),
        "shift_3_retour_h1": fmt_time(site.shift_3_exit),
        "shift_3_depart_h2": fmt_time(site.shift_3_depart_h2),
        "shift_3_retour_h2": fmt_time(site.shift_3_retour_h2),
        "working_days": site.working_days or "",
        "days_per_week": str(site.days_per_week),
        "contact_name": site.contact_name or "",
        "contact_phone": site.contact_phone or "",
        "zfe_zone": "true" if site.zfe_zone else "false",
        "security_profile": site.security_profile,
        "timezone": site.timezone,
        "observations": site.observations or "",
    }


# ---------------------------------------------------------------------------
# GET /sites/export/csv — download all sites as CSV (headers-only if empty)
# ---------------------------------------------------------------------------


@router.get("/export/csv")
async def export_sites_csv(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Export all sites for the tenant as a UTF-8 CSV file.

    Returns only the header row when there are no sites, so the user can
    fill in data manually and re-import the file.
    """
    stmt = (
        select(Site)
        .where(Site.tenant_id == current_user.tenant_id)
        .order_by(Site.name.asc())
    )
    result = await db.execute(stmt)
    sites = list(result.scalars().all())

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for site in sites:
        writer.writerow(_site_to_row(site))

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sites.csv"},
    )


# ---------------------------------------------------------------------------
# POST /sites/import/csv — upsert sites from a CSV file (no duplicates)
# ---------------------------------------------------------------------------


@router.post("/import/csv")
async def import_sites_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import sites from a CSV file using upsert logic.

    - Rows whose ``code`` already exists for this tenant are **updated**.
    - Rows with a new ``code`` are **inserted**.
    - Returns a summary: created, updated, skipped (bad rows), errors list.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a .csv file",
        )

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None or "code" not in reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSV must contain at least a 'code' column",
        )

    created = 0
    updated = 0
    skipped = 0
    errors: list[str] = []

    for i, row in enumerate(reader, start=2):
        code = (row.get("code") or "").strip()
        if not code:
            skipped += 1
            errors.append(f"Row {i}: missing code — skipped")
            continue

        try:
            lat = float(row.get("lat") or 0)
            lng = float(row.get("lng") or 0)
            num_shifts = int(row.get("num_shifts") or 1)
            days_per_week = int(row.get("days_per_week") or 5)
        except ValueError as exc:
            skipped += 1
            errors.append(f"Row {i} ({code}): invalid numeric value — {exc}")
            continue

        def parse_time(val: str):
            val = (val or "").strip()
            if not val:
                return None
            try:
                from datetime import time as dt_time
                parts = val.split(":")
                return dt_time(int(parts[0]), int(parts[1]))
            except Exception:
                return None

        zfe_raw = (row.get("zfe_zone") or "").strip().lower()
        zfe_zone = zfe_raw in ("true", "1", "yes", "oui")

        security_profile = (row.get("security_profile") or "normal").strip()
        if security_profile not in ("normal", "elevated", "critical"):
            security_profile = "normal"

        stmt = select(Site).where(
            Site.code == code,
            Site.tenant_id == current_user.tenant_id,
        )
        result = await db.execute(stmt)
        site = result.scalar_one_or_none()

        if site is None:
            site = Site(tenant_id=current_user.tenant_id, code=code)
            db.add(site)
            created += 1
        else:
            updated += 1

        def valid_type(val: str | None) -> str | None:
            allowed = ("Poste 1", "Poste 2", "Poste 3", "Normal", "Sirène", "Personnalisé")
            v = (val or "").strip()
            return v if v in allowed else None

        site.name = (row.get("name") or code).strip()
        site.address = (row.get("address") or "").strip()
        site.city = (row.get("city") or "").strip()
        site.lat = lat
        site.lng = lng
        site.geom = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        site.num_shifts = max(1, min(3, num_shifts))
        # Equipe 1
        site.shift_1_type = valid_type(row.get("shift_1_type"))
        site.shift_1_entry = parse_time(row.get("shift_1_depart_h1") or row.get("shift_1_entry"))
        site.shift_1_exit = parse_time(row.get("shift_1_retour_h1") or row.get("shift_1_exit"))
        site.shift_1_depart_h2 = parse_time(row.get("shift_1_depart_h2"))
        site.shift_1_retour_h2 = parse_time(row.get("shift_1_retour_h2"))
        # Equipe 2
        site.shift_2_type = valid_type(row.get("shift_2_type"))
        site.shift_2_entry = parse_time(row.get("shift_2_depart_h1") or row.get("shift_2_entry"))
        site.shift_2_exit = parse_time(row.get("shift_2_retour_h1") or row.get("shift_2_exit"))
        site.shift_2_depart_h2 = parse_time(row.get("shift_2_depart_h2"))
        site.shift_2_retour_h2 = parse_time(row.get("shift_2_retour_h2"))
        # Equipe 3
        site.shift_3_type = valid_type(row.get("shift_3_type"))
        site.shift_3_entry = parse_time(row.get("shift_3_depart_h1") or row.get("shift_3_entry"))
        site.shift_3_exit = parse_time(row.get("shift_3_retour_h1") or row.get("shift_3_exit"))
        site.shift_3_depart_h2 = parse_time(row.get("shift_3_depart_h2"))
        site.shift_3_retour_h2 = parse_time(row.get("shift_3_retour_h2"))
        site.working_days = (row.get("working_days") or "Lundi-Vendredi").strip()
        site.days_per_week = max(1, min(7, days_per_week))
        site.contact_name = (row.get("contact_name") or "").strip() or None
        site.contact_phone = (row.get("contact_phone") or "").strip() or None
        site.zfe_zone = zfe_zone
        site.security_profile = security_profile
        site.timezone = (row.get("timezone") or "Africa/Casablanca").strip()
        site.observations = (row.get("observations") or "").strip() or None

    await db.flush()

    logger.info(
        "CSV import by user %s: %d created, %d updated, %d skipped",
        current_user.id, created, updated, skipped,
    )

    return {
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }


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
        shift_1_type=body.shift_1_type,
        shift_1_entry=body.shift_1_entry,
        shift_1_exit=body.shift_1_exit,
        shift_1_depart_h2=body.shift_1_depart_h2,
        shift_1_retour_h2=body.shift_1_retour_h2,
        shift_2_type=body.shift_2_type,
        shift_2_entry=body.shift_2_entry,
        shift_2_exit=body.shift_2_exit,
        shift_2_depart_h2=body.shift_2_depart_h2,
        shift_2_retour_h2=body.shift_2_retour_h2,
        shift_3_type=body.shift_3_type,
        shift_3_entry=body.shift_3_entry,
        shift_3_exit=body.shift_3_exit,
        shift_3_depart_h2=body.shift_3_depart_h2,
        shift_3_retour_h2=body.shift_3_retour_h2,
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
        active_shift_ids=body.active_shift_ids,
    )
    db.add(site)
    await db.flush()
    await db.refresh(site)

    logger.info("Site %s (%s) created by user %s", site.id, site.code, current_user.id)
    return site


# ---------------------------------------------------------------------------
# PUT /sites/{site_id} and PATCH /sites/{site_id} — update site
# ---------------------------------------------------------------------------


async def _apply_site_update(
    site_id: uuid.UUID,
    body: SiteUpdate,
    current_user: User,
    db: AsyncSession,
) -> Site:
    """Shared logic for PUT and PATCH: partial-update a site."""
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

    new_lat = update_data.get("lat", site.lat)
    new_lng = update_data.get("lng", site.lng)
    if "lat" in update_data or "lng" in update_data:
        site.geom = func.ST_SetSRID(func.ST_MakePoint(new_lng, new_lat), 4326)

    await db.flush()
    await db.refresh(site)

    logger.info("Site %s updated by user %s", site.id, current_user.id)
    return site


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: uuid.UUID,
    body: SiteUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Update an existing site (PUT). Only provided fields are changed."""
    return await _apply_site_update(site_id, body, current_user, db)


@router.patch("/{site_id}", response_model=SiteResponse)
async def patch_site(
    site_id: uuid.UUID,
    body: SiteUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> Site:
    """Partially update an existing site (PATCH). Only provided fields are changed."""
    return await _apply_site_update(site_id, body, current_user, db)


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
