from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.models.operator import Operator
from app.schemas.operator import (
    OperatorCreate,
    OperatorUpdate,
    OperatorResponse,
    OperatorListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/operators")


@router.post("", response_model=OperatorResponse)
async def create_operator(
    body: OperatorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorResponse:
    op = Operator(
        tenant_id=current_user.tenant_id,
        name=body.name,
        operator_type=body.operator_type,
        api_config=body.api_config,
        contacts=body.contacts,
    )
    db.add(op)
    await db.flush()
    await db.refresh(op)
    return OperatorResponse.model_validate(op)


@router.get("", response_model=OperatorListResponse)
async def list_operators(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorListResponse:
    conditions = [
        Operator.tenant_id == current_user.tenant_id,
        Operator.is_active.is_(True),
    ]
    total = (await db.execute(
        select(func.count()).select_from(Operator).where(*conditions)
    )).scalar() or 0

    result = await db.execute(
        select(Operator)
        .where(*conditions)
        .order_by(Operator.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(result.scalars().all())
    pages = max(1, (total + page_size - 1) // page_size)

    return OperatorListResponse(
        data=[OperatorResponse.model_validate(o) for o in items],
        total=total, page=page, pages=pages,
    )


@router.get("/{operator_id}", response_model=OperatorResponse)
async def get_operator(
    operator_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorResponse:
    result = await db.execute(
        select(Operator).where(
            Operator.id == operator_id,
            Operator.tenant_id == current_user.tenant_id,
        )
    )
    op = result.scalar_one_or_none()
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")
    return OperatorResponse.model_validate(op)


@router.put("/{operator_id}", response_model=OperatorResponse)
async def update_operator(
    operator_id: uuid.UUID,
    body: OperatorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OperatorResponse:
    result = await db.execute(
        select(Operator).where(
            Operator.id == operator_id,
            Operator.tenant_id == current_user.tenant_id,
        )
    )
    op = result.scalar_one_or_none()
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(op, field, value)

    await db.flush()
    await db.refresh(op)
    return OperatorResponse.model_validate(op)


@router.delete("/{operator_id}")
async def delete_operator(
    operator_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Operator).where(
            Operator.id == operator_id,
            Operator.tenant_id == current_user.tenant_id,
        )
    )
    op = result.scalar_one_or_none()
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")
    op.is_active = False
    await db.flush()
    return {"detail": "Operator deactivated"}
