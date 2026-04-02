from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.km_consommation import KmConsommation
from app.schemas.km_consommation import (
    KmConsommationCreate,
    KmConsommationResponse,
    KmConsommationUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/km-consommation")


def _to_resp(obj: KmConsommation) -> KmConsommationResponse:
    resp = KmConsommationResponse.model_validate(obj)
    if obj.site is not None:
        resp.site_name = obj.site.name
    return resp


@router.get("", response_model=dict)
async def list_km_consommation(
    prestataire: str | None = Query(default=None),
    vehicle_type: str | None = Query(default=None),
    site_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    stmt = select(KmConsommation).where(
        KmConsommation.tenant_id == current_user.tenant_id
    )
    if prestataire:
        stmt = stmt.where(KmConsommation.prestataire.ilike(f"%{prestataire}%"))
    if vehicle_type:
        stmt = stmt.where(KmConsommation.vehicle_type == vehicle_type)
    if site_id:
        stmt = stmt.where(KmConsommation.site_id == site_id)

    stmt = stmt.order_by(KmConsommation.prestataire, KmConsommation.vehicle_type)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return {
        "items": [_to_resp(i) for i in items],
        "total": len(items),
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=KmConsommationResponse, status_code=status.HTTP_201_CREATED)
async def create_km_consommation(
    payload: KmConsommationCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> KmConsommationResponse:
    obj = KmConsommation(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.get("/{item_id}", response_model=KmConsommationResponse)
async def get_km_consommation(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> KmConsommationResponse:
    obj = await db.get(KmConsommation, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    return _to_resp(obj)


@router.patch("/{item_id}", response_model=KmConsommationResponse)
async def update_km_consommation(
    item_id: uuid.UUID,
    payload: KmConsommationUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> KmConsommationResponse:
    obj = await db.get(KmConsommation, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_km_consommation(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await db.get(KmConsommation, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable")
    await db.delete(obj)
    await db.commit()
