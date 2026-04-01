from __future__ import annotations

import logging
import math
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.employee import Employee
from app.models.leave import EmployeeLeave
from app.schemas.leave import (
    LeaveCreate,
    LeaveListMeta,
    LeaveListResponse,
    LeaveResponse,
    LeaveUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leaves")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _leave_to_response(leave: EmployeeLeave) -> LeaveResponse:
    """Build a LeaveResponse from an ORM instance, including employee_name."""
    data = LeaveResponse.model_validate(leave)
    if leave.employee is not None:
        data.employee_name = f"{leave.employee.first_name} {leave.employee.last_name}"
    return data


async def _check_overlap(
    db: AsyncSession,
    employee_id: uuid.UUID,
    start_date: date,
    end_date: date,
    exclude_leave_id: uuid.UUID | None = None,
) -> bool:
    """Return True if an overlapping leave exists for the same employee."""
    conditions = [
        EmployeeLeave.employee_id == employee_id,
        EmployeeLeave.start_date <= end_date,
        EmployeeLeave.end_date >= start_date,
    ]
    if exclude_leave_id is not None:
        conditions.append(EmployeeLeave.id != exclude_leave_id)

    stmt = select(func.count()).select_from(EmployeeLeave).where(*conditions)
    result = await db.execute(stmt)
    return result.scalar_one() > 0


# ---------------------------------------------------------------------------
# POST /leaves — create leave
# ---------------------------------------------------------------------------


@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
async def create_leave(
    body: LeaveCreate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> LeaveResponse:
    """Create a new employee leave record."""
    # Validate that the employee exists and belongs to the tenant
    emp_stmt = select(Employee).where(
        Employee.id == body.employee_id,
        Employee.tenant_id == current_user.tenant_id,
    )
    emp_result = await db.execute(emp_stmt)
    employee = emp_result.scalar_one_or_none()
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found or does not belong to your tenant",
        )

    # Check for overlapping leave
    if await _check_overlap(db, body.employee_id, body.start_date, body.end_date):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Leave period overlaps with an existing leave for this employee",
        )

    leave = EmployeeLeave(
        employee_id=body.employee_id,
        leave_type=body.leave_type,
        start_date=body.start_date,
        end_date=body.end_date,
        notes=body.notes,
    )
    db.add(leave)
    await db.flush()
    await db.refresh(leave, attribute_names=["employee"])

    logger.info(
        "Leave %s created for employee %s by user %s",
        leave.id,
        leave.employee_id,
        current_user.id,
    )
    return _leave_to_response(leave)


# ---------------------------------------------------------------------------
# GET /leaves — list with filters + pagination
# ---------------------------------------------------------------------------


@router.get("/", response_model=LeaveListResponse)
async def list_leaves(
    employee_id: uuid.UUID | None = Query(default=None, description="Filter by employee"),
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site (via employee)"),
    date_from: date | None = Query(default=None, description="Leaves ending on or after this date"),
    date_to: date | None = Query(default=None, description="Leaves starting on or before this date"),
    leave_type: str | None = Query(default=None, description="Filter by leave type"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> LeaveListResponse:
    """List leaves for the current tenant with optional filters and pagination."""
    # Base condition: tenant-scoped via employee relationship
    conditions = [Employee.tenant_id == current_user.tenant_id]

    if employee_id is not None:
        conditions.append(EmployeeLeave.employee_id == employee_id)
    if site_id is not None:
        conditions.append(Employee.site_id == site_id)
    if date_from is not None:
        conditions.append(EmployeeLeave.end_date >= date_from)
    if date_to is not None:
        conditions.append(EmployeeLeave.start_date <= date_to)
    if leave_type is not None:
        conditions.append(EmployeeLeave.leave_type == leave_type)

    # Total count (join to Employee for tenant scoping)
    count_stmt = (
        select(func.count())
        .select_from(EmployeeLeave)
        .join(Employee, EmployeeLeave.employee_id == Employee.id)
        .where(*conditions)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Pagination
    pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    # Fetch page with eager-loaded employee for employee_name
    stmt = (
        select(EmployeeLeave)
        .join(Employee, EmployeeLeave.employee_id == Employee.id)
        .options(selectinload(EmployeeLeave.employee))
        .where(*conditions)
        .order_by(EmployeeLeave.start_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    leaves = list(result.scalars().all())

    return LeaveListResponse(
        data=[_leave_to_response(lv) for lv in leaves],
        meta=LeaveListMeta(
            page=page,
            pages=pages,
            total=total,
            page_size=page_size,
        ),
    )


# ---------------------------------------------------------------------------
# GET /leaves/{leave_id} — get single leave
# ---------------------------------------------------------------------------


@router.get("/{leave_id}", response_model=LeaveResponse)
async def get_leave(
    leave_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> LeaveResponse:
    """Get a single leave by UUID, including employee name."""
    stmt = (
        select(EmployeeLeave)
        .join(Employee, EmployeeLeave.employee_id == Employee.id)
        .options(selectinload(EmployeeLeave.employee))
        .where(
            EmployeeLeave.id == leave_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    leave = result.scalar_one_or_none()

    if leave is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )

    return _leave_to_response(leave)


# ---------------------------------------------------------------------------
# PUT /leaves/{leave_id} — update leave
# ---------------------------------------------------------------------------


@router.put("/{leave_id}", response_model=LeaveResponse)
async def update_leave(
    leave_id: uuid.UUID,
    body: LeaveUpdate,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> LeaveResponse:
    """Update an existing leave. Only provided fields are changed."""
    stmt = (
        select(EmployeeLeave)
        .join(Employee, EmployeeLeave.employee_id == Employee.id)
        .options(selectinload(EmployeeLeave.employee))
        .where(
            EmployeeLeave.id == leave_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    leave = result.scalar_one_or_none()

    if leave is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    # Determine effective dates for overlap check
    new_start = update_data.get("start_date", leave.start_date)
    new_end = update_data.get("end_date", leave.end_date)

    # Validate end >= start with effective values
    if new_end < new_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be >= start_date",
        )

    # Check overlap if dates changed
    if "start_date" in update_data or "end_date" in update_data:
        if await _check_overlap(
            db, leave.employee_id, new_start, new_end, exclude_leave_id=leave.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Leave period overlaps with an existing leave for this employee",
            )

    for field, value in update_data.items():
        setattr(leave, field, value)

    await db.flush()
    await db.refresh(leave)

    logger.info("Leave %s updated by user %s", leave.id, current_user.id)
    return _leave_to_response(leave)


# ---------------------------------------------------------------------------
# DELETE /leaves/{leave_id} — hard delete
# ---------------------------------------------------------------------------


@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_leave(
    leave_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Hard-delete a leave record."""
    stmt = (
        select(EmployeeLeave)
        .join(Employee, EmployeeLeave.employee_id == Employee.id)
        .where(
            EmployeeLeave.id == leave_id,
            Employee.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    leave = result.scalar_one_or_none()

    if leave is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found",
        )

    await db.delete(leave)
    await db.flush()

    logger.info("Leave %s deleted by user %s", leave_id, current_user.id)
