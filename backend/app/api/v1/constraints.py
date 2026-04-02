from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.settings import ConstraintParam
from app.schemas.settings import (
    ConstraintBulkRequest,
    ConstraintCreateRequest,
    ConstraintResponse,
    ConstraintUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/constraints")


# ---------------------------------------------------------------------------
# GET /constraints — list constraints with optional category filter
# ---------------------------------------------------------------------------


@router.get("", response_model=list[ConstraintResponse])
async def list_constraints(
    category: str | None = Query(default=None),
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> list[ConstraintResponse]:
    """List constraint parameters for the current tenant."""
    stmt = select(ConstraintParam).where(
        ConstraintParam.tenant_id == current_user.tenant_id
    )

    if category is not None:
        stmt = stmt.where(ConstraintParam.category == category)

    stmt = stmt.order_by(ConstraintParam.category, ConstraintParam.key)
    result = await db.execute(stmt)
    constraints = list(result.scalars().all())
    return [ConstraintResponse.model_validate(c) for c in constraints]


# ---------------------------------------------------------------------------
# POST /constraints — create a single constraint
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=ConstraintResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_constraint(
    body: ConstraintCreateRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> ConstraintResponse:
    """Create a new constraint parameter."""
    # Check for duplicate key
    stmt = select(ConstraintParam).where(
        ConstraintParam.tenant_id == current_user.tenant_id,
        ConstraintParam.key == body.key,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Constraint with key '{body.key}' already exists",
        )

    constraint = ConstraintParam(
        tenant_id=current_user.tenant_id,
        key=body.key,
        value=body.value,
        category=body.category,
        description=body.description,
    )
    db.add(constraint)
    await db.flush()
    await db.refresh(constraint)

    logger.info(
        "Created constraint '%s' for tenant %s",
        body.key,
        current_user.tenant_id,
    )
    return ConstraintResponse.model_validate(constraint)


# ---------------------------------------------------------------------------
# PUT /constraints/{constraint_id} — update a constraint
# ---------------------------------------------------------------------------


@router.put("/{constraint_id}", response_model=ConstraintResponse)
async def update_constraint(
    constraint_id: uuid.UUID,
    body: ConstraintUpdateRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> ConstraintResponse:
    """Update an existing constraint parameter."""
    constraint = await _get_tenant_constraint(db, constraint_id, current_user.tenant_id)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(constraint, field, value)

    await db.flush()
    await db.refresh(constraint)

    logger.info(
        "Updated constraint '%s' for tenant %s",
        constraint.key,
        current_user.tenant_id,
    )
    return ConstraintResponse.model_validate(constraint)


# ---------------------------------------------------------------------------
# DELETE /constraints/{constraint_id} — delete a constraint
# ---------------------------------------------------------------------------


@router.delete("/{constraint_id}")
async def delete_constraint(
    constraint_id: uuid.UUID,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a constraint parameter."""
    constraint = await _get_tenant_constraint(db, constraint_id, current_user.tenant_id)
    await db.delete(constraint)

    logger.info(
        "Deleted constraint '%s' for tenant %s",
        constraint.key,
        current_user.tenant_id,
    )
    return {"detail": "Constraint deleted"}


# ---------------------------------------------------------------------------
# POST /constraints/bulk — bulk import constraints (upsert)
# ---------------------------------------------------------------------------


@router.post("/bulk")
async def bulk_import_constraints(
    body: ConstraintBulkRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Bulk import constraint parameters.

    Upsert semantics: existing keys are updated, new keys are created.
    """
    imported = 0

    for item in body.constraints:
        stmt = select(ConstraintParam).where(
            ConstraintParam.tenant_id == current_user.tenant_id,
            ConstraintParam.key == item.key,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.value = item.value
            existing.category = item.category
            if item.description is not None:
                existing.description = item.description
        else:
            constraint = ConstraintParam(
                tenant_id=current_user.tenant_id,
                key=item.key,
                value=item.value,
                category=item.category,
                description=item.description,
            )
            db.add(constraint)

        imported += 1

    await db.flush()

    logger.info(
        "Bulk imported %d constraints for tenant %s",
        imported,
        current_user.tenant_id,
    )
    return {"imported": imported}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_tenant_constraint(
    db: AsyncSession, constraint_id: uuid.UUID, tenant_id: uuid.UUID
) -> ConstraintParam:
    """Load a constraint and verify it belongs to the given tenant."""
    stmt = select(ConstraintParam).where(
        ConstraintParam.id == constraint_id,
        ConstraintParam.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    constraint = result.scalar_one_or_none()
    if constraint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constraint not found",
        )
    return constraint
