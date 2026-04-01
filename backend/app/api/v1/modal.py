from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.modal import EmployeeModal
from app.schemas.modal import (
    CarpoolPotential,
    ModalCreate,
    ModalDistribution,
    ModalResponse,
    ModalStats,
    ModalUpdate,
    MobilityScore,
    MobilityScoresResponse,
    ShadowZoneEmployee,
    ShiftAnalysisResponse,
)
from app.services.mobility_scoring import (
    calculate_employee_score,
    calculate_group_scores,
    calculate_timeslot_scores,
    identify_shadow_zones,
)
from app.services.modal_analytics import (
    analyze_carpool_potential,
    analyze_disruption_vulnerability,
    analyze_weather_impact,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Employee-scoped routes: /employees/{employee_id}/modal
employee_modal_router = APIRouter(prefix="/employees")

# Stats routes: /modal/stats, /modal/shift-analysis, /modal/mobility-scores
modal_stats_router = APIRouter(prefix="/modal")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _modal_to_response(modal: EmployeeModal) -> ModalResponse:
    """Build a ModalResponse from an ORM instance, including employee_name."""
    data = ModalResponse.model_validate(modal)
    if modal.employee is not None:
        data.employee_name = f"{modal.employee.first_name} {modal.employee.last_name}"
    return data



# ---------------------------------------------------------------------------
# GET /employees/{employee_id}/modal — get modal for employee
# ---------------------------------------------------------------------------


@employee_modal_router.get(
    "/{employee_id}/modal",
    response_model=ModalResponse,
)
async def get_employee_modal(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ModalResponse:
    """Get the modal analysis record for a specific employee."""
    stmt = (
        select(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .options(selectinload(EmployeeModal.employee))
        .where(
            EmployeeModal.employee_id == employee_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    modal = result.scalar_one_or_none()

    if modal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modal analysis not found for this employee",
        )

    return _modal_to_response(modal)


# ---------------------------------------------------------------------------
# PUT /employees/{employee_id}/modal — upsert modal
# ---------------------------------------------------------------------------


@employee_modal_router.put(
    "/{employee_id}/modal",
    response_model=ModalResponse,
)
async def upsert_employee_modal(
    employee_id: uuid.UUID,
    body: ModalCreate,
    response: Response,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ModalResponse:
    """Create or update the modal analysis for an employee.

    Returns 201 if created, 200 if updated.
    """
    # Validate that the employee exists and belongs to the tenant
    emp_stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.tenant_id == current_user.tenant_id,
    )
    emp_result = await db.execute(emp_stmt)
    employee = emp_result.scalar_one_or_none()
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found or does not belong to your tenant",
        )

    # Check if modal already exists
    existing_stmt = select(EmployeeModal).where(
        EmployeeModal.employee_id == employee_id,
    )
    existing_result = await db.execute(existing_stmt)
    existing_modal = existing_result.scalar_one_or_none()

    # Build field dict from body, excluding employee_id (we use the path param)
    update_data = body.model_dump(exclude={"employee_id"})

    if existing_modal is not None:
        # Update existing
        for field, value in update_data.items():
            setattr(existing_modal, field, value)
        await db.flush()
        await db.refresh(existing_modal)
        response.status_code = status.HTTP_200_OK
        logger.info(
            "Modal for employee %s updated by user %s",
            employee_id,
            current_user.id,
        )
        return _modal_to_response(existing_modal)
    else:
        # Create new
        modal = EmployeeModal(
            employee_id=employee_id,
            **update_data,
        )
        db.add(modal)
        await db.flush()
        await db.refresh(modal, attribute_names=["employee"])
        response.status_code = status.HTTP_201_CREATED
        logger.info(
            "Modal for employee %s created by user %s",
            employee_id,
            current_user.id,
        )
        return _modal_to_response(modal)


# ---------------------------------------------------------------------------
# DELETE /employees/{employee_id}/modal — delete modal
# ---------------------------------------------------------------------------


@employee_modal_router.delete(
    "/{employee_id}/modal",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_employee_modal(
    employee_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete the modal analysis record for an employee."""
    stmt = (
        select(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(
            EmployeeModal.employee_id == employee_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    modal = result.scalar_one_or_none()

    if modal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modal analysis not found for this employee",
        )

    await db.delete(modal)
    await db.flush()

    logger.info(
        "Modal for employee %s deleted by user %s",
        employee_id,
        current_user.id,
    )


# ---------------------------------------------------------------------------
# GET /modal/stats — modal distribution statistics
# ---------------------------------------------------------------------------


@modal_stats_router.get("/stats", response_model=ModalStats)
async def get_modal_stats(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ModalStats:
    """Return modal distribution stats: count per mode with percentage.

    Optionally filtered by ``site_id``.
    """
    conditions = [Employee.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    # Total count
    count_stmt = (
        select(func.count())
        .select_from(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Distribution by primary_mode
    dist_stmt = (
        select(
            EmployeeModal.primary_mode,
            func.count().label("cnt"),
        )
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
        .group_by(EmployeeModal.primary_mode)
        .order_by(func.count().desc())
    )
    dist_result = await db.execute(dist_stmt)
    rows = dist_result.all()

    distribution = [
        ModalDistribution(
            mode=row.primary_mode,
            count=row.cnt,
            percentage=round((row.cnt / total) * 100, 2) if total > 0 else 0.0,
        )
        for row in rows
    ]

    return ModalStats(
        total=total,
        distribution=distribution,
    )


# ---------------------------------------------------------------------------
# GET /modal/shift-analysis — distribution grouped by shift
# ---------------------------------------------------------------------------


@modal_stats_router.get("/shift-analysis", response_model=ShiftAnalysisResponse)
async def get_shift_analysis(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> ShiftAnalysisResponse:
    """Return modal distribution grouped by shift, with disruption and weather data."""
    conditions = [Employee.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(
            Employee.shift_time,
            EmployeeModal.primary_mode,
            func.count().label("cnt"),
        )
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .where(*conditions)
        .group_by(Employee.shift_time, EmployeeModal.primary_mode)
        .order_by(Employee.shift_time, func.count().desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    # Group by shift
    shifts: dict[str, list[dict]] = {}
    for row in rows:
        shift_key = row.shift_time or "unassigned"
        if shift_key not in shifts:
            shifts[shift_key] = []
        shifts[shift_key].append({"mode": row.primary_mode, "count": row.cnt})

    # Enhanced analytics
    disruptions = await analyze_disruption_vulnerability(
        db, current_user.tenant_id, site_id
    )
    weather = await analyze_weather_impact(db, current_user.tenant_id, site_id)

    return ShiftAnalysisResponse(
        data=shifts,
        disruptions=disruptions,
        weather_impact=weather,
    )


# ---------------------------------------------------------------------------
# GET /modal/mobility-scores — calculate mobility scores
# ---------------------------------------------------------------------------


@modal_stats_router.get("/mobility-scores", response_model=MobilityScoresResponse)
async def get_mobility_scores(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> MobilityScoresResponse:
    """Calculate mobility scores with group aggregation and timeslot data."""
    conditions = [Employee.tenant_id == current_user.tenant_id]
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)

    stmt = (
        select(EmployeeModal)
        .join(Employee, EmployeeModal.employee_id == Employee.id)
        .options(selectinload(EmployeeModal.employee))
        .where(*conditions)
        .order_by(Employee.last_name, Employee.first_name)
    )
    result = await db.execute(stmt)
    modals = list(result.scalars().all())

    # Per-employee scores
    scores: list[MobilityScore] = []
    for modal in modals:
        score, factors = calculate_employee_score(modal)
        emp_name = (
            f"{modal.employee.first_name} {modal.employee.last_name}"
            if modal.employee is not None
            else "Unknown"
        )
        scores.append(
            MobilityScore(
                employee_id=modal.employee_id,
                employee_name=emp_name,
                score=score,
                factors=factors,
            )
        )

    # Group and timeslot aggregations
    group_scores = await calculate_group_scores(
        db, current_user.tenant_id, site_id
    )
    timeslot_scores = await calculate_timeslot_scores(
        db, current_user.tenant_id, site_id
    )

    return MobilityScoresResponse(
        scores=scores,
        group_scores=group_scores,
        timeslot_scores=timeslot_scores,
    )


# ---------------------------------------------------------------------------
# GET /modal/shadow-zones — identify employees without transport solutions
# ---------------------------------------------------------------------------


@modal_stats_router.get("/shadow-zones", response_model=list[ShadowZoneEmployee])
async def get_shadow_zones(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    distance_threshold: float = Query(
        default=30.0, description="Distance threshold in km"
    ),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[ShadowZoneEmployee]:
    """Find employees in shadow zones — no satisfactory transport solution."""
    results = await identify_shadow_zones(
        db, current_user.tenant_id, distance_threshold, site_id
    )
    return results


# ---------------------------------------------------------------------------
# GET /modal/carpool-potential — carpool supply vs demand per site
# ---------------------------------------------------------------------------


@modal_stats_router.get("/carpool-potential", response_model=list[CarpoolPotential])
async def get_carpool_potential(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[CarpoolPotential]:
    """Calculate carpool supply vs demand by site."""
    results = await analyze_carpool_potential(
        db, current_user.tenant_id, site_id
    )
    return results
