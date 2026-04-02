from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.point_arret import PointArret
from app.schemas.point_arret import (
    PointArretCreate,
    PointArretResponse,
    PointArretUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/points-arret")


def _to_resp(obj: PointArret) -> PointArretResponse:
    resp = PointArretResponse.model_validate(obj)
    if obj.site is not None:
        resp.site_name = obj.site.name
    return resp


@router.get("", response_model=dict)
async def list_points_arret(
    prestataire: str | None = Query(default=None),
    site_id: uuid.UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(PointArret).where(PointArret.tenant_id == current_user.tenant_id)
    if prestataire:
        stmt = stmt.where(PointArret.prestataire.ilike(f"%{prestataire}%"))
    if site_id:
        stmt = stmt.where(PointArret.site_id == site_id)
    if is_active is not None:
        stmt = stmt.where(PointArret.is_active == is_active)

    stmt = stmt.order_by(PointArret.nom)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return {
        "items": [_to_resp(i) for i in items],
        "total": len(items),
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=PointArretResponse, status_code=status.HTTP_201_CREATED)
async def create_point_arret(
    payload: PointArretCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> PointArretResponse:
    obj = PointArret(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.get("/{item_id}", response_model=PointArretResponse)
async def get_point_arret(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> PointArretResponse:
    obj = await db.get(PointArret, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Point d'arrêt introuvable")
    return _to_resp(obj)


@router.patch("/{item_id}", response_model=PointArretResponse)
async def update_point_arret(
    item_id: uuid.UUID,
    payload: PointArretUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> PointArretResponse:
    obj = await db.get(PointArret, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Point d'arrêt introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_point_arret(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await db.get(PointArret, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Point d'arrêt introuvable")
    await db.delete(obj)
    await db.commit()
