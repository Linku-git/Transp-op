from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.configuration_plan import ConfigurationPlan
from app.models.configuration_transport import ConfigurationTransport
from app.schemas.configuration_plan import (
    ConfigurationPlanCreate,
    ConfigurationPlanResponse,
    ConfigurationPlanUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/configuration-plans")


async def _with_count(obj: ConfigurationPlan, db: AsyncSession) -> ConfigurationPlanResponse:
    count_result = await db.execute(
        select(func.count()).where(ConfigurationTransport.plan_id == obj.id)
    )
    count = count_result.scalar_one()
    resp = ConfigurationPlanResponse.model_validate(obj)
    resp.row_count = count
    return resp


@router.get("", response_model=dict)
async def list_plans(
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(ConfigurationPlan).where(
        ConfigurationPlan.tenant_id == current_user.tenant_id
    )
    if is_active is not None:
        stmt = stmt.where(ConfigurationPlan.is_active == is_active)
    stmt = stmt.order_by(ConfigurationPlan.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = list(result.scalars().all())
    items_with_count = [await _with_count(i, db) for i in items]

    total_stmt = select(func.count()).select_from(ConfigurationPlan).where(
        ConfigurationPlan.tenant_id == current_user.tenant_id
    )
    if is_active is not None:
        total_stmt = total_stmt.where(ConfigurationPlan.is_active == is_active)
    total = (await db.execute(total_stmt)).scalar_one()

    return {
        "items": items_with_count,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=ConfigurationPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: ConfigurationPlanCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationPlanResponse:
    obj = ConfigurationPlan(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return await _with_count(obj, db)


@router.get("/{plan_id}", response_model=ConfigurationPlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationPlanResponse:
    obj = await db.get(ConfigurationPlan, plan_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Plan introuvable")
    return await _with_count(obj, db)


@router.patch("/{plan_id}", response_model=ConfigurationPlanResponse)
async def update_plan(
    plan_id: uuid.UUID,
    payload: ConfigurationPlanUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationPlanResponse:
    obj = await db.get(ConfigurationPlan, plan_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Plan introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return await _with_count(obj, db)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_plan(
    plan_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await db.get(ConfigurationPlan, plan_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Plan introuvable")
    await db.delete(obj)
    await db.commit()
