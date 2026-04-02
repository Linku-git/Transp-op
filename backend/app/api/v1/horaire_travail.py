from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.horaire_travail import HoraireTravail
from app.schemas.horaire_travail import (
    HoraireTravailCreate,
    HoraireTravailResponse,
    HoraireTravailUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/horaires-travail")


def _to_resp(obj: HoraireTravail) -> HoraireTravailResponse:
    resp = HoraireTravailResponse.model_validate(obj)
    if obj.site is not None:
        resp.site_name = obj.site.name
    return resp


@router.get("", response_model=dict)
async def list_horaires(
    site_id: uuid.UUID | None = Query(default=None),
    type_horaire: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=200),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(HoraireTravail).where(HoraireTravail.tenant_id == current_user.tenant_id)
    if site_id:
        stmt = stmt.where(HoraireTravail.site_id == site_id)
    if type_horaire:
        stmt = stmt.where(HoraireTravail.type_horaire.ilike(f"%{type_horaire}%"))

    stmt = stmt.order_by(HoraireTravail.type_horaire)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return {
        "items": [_to_resp(i) for i in items],
        "total": len(items),
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=HoraireTravailResponse, status_code=status.HTTP_201_CREATED)
async def create_horaire(
    payload: HoraireTravailCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> HoraireTravailResponse:
    obj = HoraireTravail(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.get("/{item_id}", response_model=HoraireTravailResponse)
async def get_horaire(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> HoraireTravailResponse:
    obj = await db.get(HoraireTravail, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Horaire introuvable")
    return _to_resp(obj)


@router.patch("/{item_id}", response_model=HoraireTravailResponse)
async def update_horaire(
    item_id: uuid.UUID,
    payload: HoraireTravailUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> HoraireTravailResponse:
    obj = await db.get(HoraireTravail, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Horaire introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_horaire(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh")),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await db.get(HoraireTravail, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Horaire introuvable")
    await db.delete(obj)
    await db.commit()
