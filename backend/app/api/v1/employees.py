from __future__ import annotations

import csv
import io
import logging
import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.site import Site
from app.schemas.employee import (
    CSVRowError,
    CSVUploadResult,
    DepartmentBreakdown,
    EmployeeCreate,
    EmployeeListMeta,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeSummary,
    EmployeeUpdate,
    SiteBreakdown,
)
from app.services.geocoding import batch_geocode, geocode_address

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _employee_to_response(employee: Employee) -> EmployeeResponse:
    """Build an EmployeeResponse from an ORM instance, including site_name and point_arret_nom."""
    data = EmployeeResponse.model_validate(employee)
    if employee.site is not None:
        data.site_name = employee.site.name
    if employee.point_arret is not None:
        data.point_arret_nom = employee.point_arret.nom
    return data


def _make_geom(lng: float, lat: float):
    """Return a PostGIS POINT expression for the given coordinates."""
    return func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)


# ---------------------------------------------------------------------------
# GET /employees — list with filters + pagination
# ---------------------------------------------------------------------------


@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    is_pmr: bool | None = Query(default=None, description="Filter by PMR status"),
    quartier: str | None = Query(default=None, description="Filter by quartier"),
    shift_time: str | None = Query(default=None, description="Filter by shift time"),
    department: str | None = Query(default=None, description="Filter by department"),
    active: bool = Query(default=True, description="Filter by active status"),
    q: str | None = Query(default=None, description="Search name or matricule"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=2000, description="Items per page"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> EmployeeListResponse:
    """List employees for the current tenant with optional filters and search."""
    conditions = [Employee.tenant_id == current_user.tenant_id]

    if site_id is not None:
        conditions.append(Employee.site_id == site_id)
    if is_pmr is not None:
        conditions.append(Employee.is_pmr == is_pmr)
    if quartier is not None:
        conditions.append(Employee.quartier.ilike(f"%{quartier}%"))
    if shift_time is not None:
        conditions.append(Employee.shift_time == shift_time)
    if department is not None:
        conditions.append(Employee.department.ilike(f"%{department}%"))
    conditions.append(Employee.active == active)

    if q is not None:
        search_term = f"%{q}%"
        conditions.append(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.matricule.ilike(search_term),
            )
        )

    # Total count
    count_stmt = select(func.count()).select_from(Employee).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Pagination
    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    # Fetch page with eager-loaded site and point_arret
    stmt = (
        select(Employee)
        .options(selectinload(Employee.site), selectinload(Employee.point_arret))
        .where(*conditions)
        .order_by(Employee.last_name.asc(), Employee.first_name.asc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    employees = list(result.scalars().all())

    return EmployeeListResponse(
        data=[_employee_to_response(e) for e in employees],
        meta=EmployeeListMeta(
            page=page,
            pages=pages,
            total=total,
            page_size=page_size,
        ),
    )


# ---------------------------------------------------------------------------
# GET /employees/summary — aggregate summary
# ---------------------------------------------------------------------------


@router.get("/summary", response_model=EmployeeSummary)
async def get_employee_summary(
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> EmployeeSummary:
    """Return aggregate employee statistics for the tenant."""
    tenant_filter = Employee.tenant_id == current_user.tenant_id

    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(Employee).where(tenant_filter)
    )
    total_count = total_result.scalar_one()

    # Active count
    active_result = await db.execute(
        select(func.count())
        .select_from(Employee)
        .where(tenant_filter, Employee.active.is_(True))
    )
    active_count = active_result.scalar_one()

    # PMR count
    pmr_result = await db.execute(
        select(func.count())
        .select_from(Employee)
        .where(tenant_filter, Employee.is_pmr.is_(True), Employee.active.is_(True))
    )
    pmr_count = pmr_result.scalar_one()

    # Breakdown by site
    site_stmt = (
        select(
            Employee.site_id,
            Site.name.label("site_name"),
            func.count().label("count"),
        )
        .join(Site, Employee.site_id == Site.id)
        .where(tenant_filter, Employee.active.is_(True))
        .group_by(Employee.site_id, Site.name)
        .order_by(func.count().desc())
    )
    site_rows = await db.execute(site_stmt)
    by_site = [
        SiteBreakdown(site_id=row.site_id, site_name=row.site_name, count=row.count)
        for row in site_rows.all()
    ]

    # Breakdown by department
    dept_stmt = (
        select(
            Employee.department,
            func.count().label("count"),
        )
        .where(
            tenant_filter,
            Employee.active.is_(True),
            Employee.department.isnot(None),
        )
        .group_by(Employee.department)
        .order_by(func.count().desc())
    )
    dept_rows = await db.execute(dept_stmt)
    by_department = [
        DepartmentBreakdown(department=row.department, count=row.count)
        for row in dept_rows.all()
    ]

    return EmployeeSummary(
        total_count=total_count,
        active_count=active_count,
        pmr_count=pmr_count,
        by_site=by_site,
        by_department=by_department,
    )


# ---------------------------------------------------------------------------
# GET /employees/{employee_id} — get single employee
# ---------------------------------------------------------------------------


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Get a single employee by UUID, including site name."""
    stmt = (
        select(Employee)
        .options(selectinload(Employee.site), selectinload(Employee.point_arret))
        .where(
            Employee.id == employee_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return _employee_to_response(employee)


# ---------------------------------------------------------------------------
# POST /employees — create employee
# ---------------------------------------------------------------------------


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    body: EmployeeCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Create a new employee within the current tenant."""
    # Validate that the site exists and belongs to the tenant
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

    # Check for duplicate (tenant_id, matricule)
    dup_stmt = select(Employee).where(
        Employee.tenant_id == current_user.tenant_id,
        Employee.matricule == body.matricule,
    )
    dup_result = await db.execute(dup_stmt)
    if dup_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this matricule already exists",
        )

    # Resolve coordinates: use provided lat/lng or attempt geocoding
    lat = body.lat
    lng = body.lng
    if lat is None or lng is None:
        if body.address:
            geocoded = await geocode_address(body.address)
            if geocoded is not None:
                lat, lng = geocoded
                logger.info(
                    "Geocoded address '%s' -> (%s, %s)", body.address, lat, lng
                )

    # Build PostGIS geometry if we have coordinates
    geom = _make_geom(lng, lat) if (lat is not None and lng is not None) else None

    employee = Employee(
        tenant_id=current_user.tenant_id,
        matricule=body.matricule,
        first_name=body.first_name,
        last_name=body.last_name,
        site_id=body.site_id,
        shift_time=body.shift_time,
        address=body.address,
        quartier=body.quartier,
        city=body.city,
        lat=lat,
        lng=lng,
        geom=geom,
        preferred_pickup_address=body.preferred_pickup_address,
        preferred_pickup_lat=body.preferred_pickup_lat,
        preferred_pickup_lng=body.preferred_pickup_lng,
        is_pmr=body.is_pmr,
        function_role=body.function_role,
        phone=body.phone,
        department=body.department,
        transport_required=body.transport_required,
        current_transport_mode=body.current_transport_mode,
        opt_in_company_transport=body.opt_in_company_transport,
        has_private_car=body.has_private_car,
        volunteer_driver=body.volunteer_driver,
        carpool_seats=body.carpool_seats,
        sirh_external_id=body.sirh_external_id,
        hire_date=body.hire_date,
        end_date=body.end_date,
    )
    db.add(employee)
    await db.flush()
    await db.refresh(employee, attribute_names=["site"])

    logger.info(
        "Employee %s (%s) created by user %s",
        employee.id,
        employee.matricule,
        current_user.id,
    )
    return _employee_to_response(employee)


# ---------------------------------------------------------------------------
# PUT /employees/{employee_id} — update employee
# ---------------------------------------------------------------------------


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: uuid.UUID,
    body: EmployeeUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    """Update an existing employee. Only provided fields are changed."""
    stmt = (
        select(Employee)
        .options(selectinload(Employee.site), selectinload(Employee.point_arret))
        .where(
            Employee.id == employee_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    # If site_id is being changed, validate the new site
    if "site_id" in update_data:
        site_stmt = select(Site).where(
            Site.id == update_data["site_id"],
            Site.tenant_id == current_user.tenant_id,
        )
        site_result = await db.execute(site_stmt)
        if site_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found or does not belong to your tenant",
            )

    for field, value in update_data.items():
        setattr(employee, field, value)

    # Recalculate PostGIS geom if lat or lng changed
    if "lat" in update_data or "lng" in update_data:
        new_lat = update_data.get("lat", employee.lat)
        new_lng = update_data.get("lng", employee.lng)
        if new_lat is not None and new_lng is not None:
            employee.geom = _make_geom(new_lng, new_lat)
        else:
            employee.geom = None

    await db.flush()
    await db.refresh(employee)

    logger.info("Employee %s updated by user %s", employee.id, current_user.id)
    return _employee_to_response(employee)


# ---------------------------------------------------------------------------
# DELETE /employees/{employee_id} — soft-delete (set active=false)
# ---------------------------------------------------------------------------


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft-delete an employee by setting active=false."""
    stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.tenant_id == current_user.tenant_id,
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    employee.active = False
    await db.flush()

    logger.info("Employee %s soft-deleted by user %s", employee_id, current_user.id)
    return {"detail": "Employee deactivated successfully"}


# ---------------------------------------------------------------------------
# POST /employees/upload — CSV bulk import
# ---------------------------------------------------------------------------


@router.post("/upload", response_model=CSVUploadResult)
async def upload_employees_csv(
    file: UploadFile,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> CSVUploadResult:
    """Bulk-import employees from a CSV file.

    Expected columns: matricule, first_name, last_name, site_code, shift_time,
    address, city, is_pmr, department.
    """
    if file.content_type not in (
        "text/csv",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a CSV",
        )

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    # Pre-load all sites for this tenant keyed by code for quick lookup
    site_stmt = select(Site).where(Site.tenant_id == current_user.tenant_id)
    site_result = await db.execute(site_stmt)
    sites_by_code: dict[str, Site] = {
        s.code: s for s in site_result.scalars().all()
    }

    # Pre-load existing matricules in tenant to detect duplicates
    mat_stmt = select(Employee.matricule).where(
        Employee.tenant_id == current_user.tenant_id
    )
    mat_result = await db.execute(mat_stmt)
    existing_matricules: set[str] = {row[0] for row in mat_result.all()}

    errors: list[CSVRowError] = []
    created = 0
    total_rows = 0

    for row_idx, row in enumerate(reader, start=2):  # row 1 is header
        total_rows += 1

        # --- Validate required fields ---
        matricule = (row.get("matricule") or "").strip()
        if not matricule:
            errors.append(
                CSVRowError(row=row_idx, field="matricule", message="Required field")
            )
            continue

        first_name = (row.get("first_name") or "").strip()
        if not first_name:
            errors.append(
                CSVRowError(row=row_idx, field="first_name", message="Required field")
            )
            continue

        last_name = (row.get("last_name") or "").strip()
        if not last_name:
            errors.append(
                CSVRowError(row=row_idx, field="last_name", message="Required field")
            )
            continue

        site_code = (row.get("site_code") or "").strip()
        if not site_code:
            errors.append(
                CSVRowError(row=row_idx, field="site_code", message="Required field")
            )
            continue

        # --- Validate site_code exists ---
        site = sites_by_code.get(site_code)
        if site is None:
            errors.append(
                CSVRowError(
                    row=row_idx,
                    field="site_code",
                    message=f"Site with code '{site_code}' not found",
                )
            )
            continue

        # --- Duplicate matricule check ---
        if matricule in existing_matricules:
            errors.append(
                CSVRowError(
                    row=row_idx,
                    field="matricule",
                    message=f"Matricule '{matricule}' already exists",
                )
            )
            continue

        # --- Parse optional boolean field ---
        is_pmr_raw = (row.get("is_pmr") or "").strip().lower()
        is_pmr = is_pmr_raw in ("true", "1", "oui", "yes")

        employee = Employee(
            tenant_id=current_user.tenant_id,
            matricule=matricule,
            first_name=first_name,
            last_name=last_name,
            site_id=site.id,
            shift_time=(row.get("shift_time") or "").strip() or None,
            address=(row.get("address") or "").strip() or None,
            city=(row.get("city") or "").strip() or None,
            is_pmr=is_pmr,
            department=(row.get("department") or "").strip() or None,
        )
        db.add(employee)
        existing_matricules.add(matricule)
        created += 1

    if created > 0:
        await db.flush()

    logger.info(
        "CSV upload by user %s: %d created, %d errors out of %d rows",
        current_user.id,
        created,
        len(errors),
        total_rows,
    )

    return CSVUploadResult(total_rows=total_rows, created=created, errors=errors)


# ---------------------------------------------------------------------------
# POST /employees/geocode — batch geocode employees missing coordinates
# ---------------------------------------------------------------------------


@router.post("/geocode")
async def geocode_employees(
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Find all employees with an address but no lat/lng and attempt geocoding."""
    stmt = select(Employee).where(
        Employee.tenant_id == current_user.tenant_id,
        Employee.address.isnot(None),
        Employee.address != "",
        Employee.lat.is_(None),
    )
    result = await db.execute(stmt)
    employees = list(result.scalars().all())

    if not employees:
        return {"detail": "No employees need geocoding", "geocoded": 0}

    addresses = [e.address for e in employees]
    geocoded_results = await batch_geocode(addresses)

    geocoded_count = 0
    for employee, coords in zip(employees, geocoded_results):
        if coords is not None:
            lat, lng = coords
            employee.lat = lat
            employee.lng = lng
            employee.geom = _make_geom(lng, lat)
            geocoded_count += 1

    if geocoded_count > 0:
        await db.flush()

    logger.info(
        "Batch geocoding by user %s: %d of %d employees geocoded",
        current_user.id,
        geocoded_count,
        len(employees),
    )

    return {
        "detail": f"Geocoded {geocoded_count} of {len(employees)} employees",
        "geocoded": geocoded_count,
        "total_attempted": len(employees),
    }
