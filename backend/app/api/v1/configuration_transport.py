from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.configuration_transport import ConfigurationTransport
from app.schemas.configuration_transport import (
    ConfigurationTransportCreate,
    ConfigurationTransportResponse,
    ConfigurationTransportUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/configuration-transport")


def _to_resp(obj: ConfigurationTransport) -> ConfigurationTransportResponse:
    resp = ConfigurationTransportResponse.model_validate(obj)
    if obj.site is not None:
        resp.site_name = obj.site.name
    return resp


@router.get("", response_model=dict)
async def list_configuration_transport(
    plan_id: uuid.UUID | None = Query(default=None),
    prestataire: str | None = Query(default=None),
    site_id: uuid.UUID | None = Query(default=None),
    secteur: str | None = Query(default=None),
    poste: str | None = Query(default=None),
    shift: str | None = Query(default=None),
    aller_retour: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=600),
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from sqlalchemy import func
    stmt = select(ConfigurationTransport).where(
        ConfigurationTransport.tenant_id == current_user.tenant_id
    )
    if plan_id:
        stmt = stmt.where(ConfigurationTransport.plan_id == plan_id)
    if prestataire:
        stmt = stmt.where(ConfigurationTransport.prestataire.ilike(f"%{prestataire}%"))
    if site_id:
        stmt = stmt.where(ConfigurationTransport.site_id == site_id)
    if secteur:
        stmt = stmt.where(ConfigurationTransport.secteur.ilike(f"%{secteur}%"))
    if poste:
        stmt = stmt.where(ConfigurationTransport.poste == poste)
    if shift:
        stmt = stmt.where(ConfigurationTransport.shift == shift)
    if aller_retour:
        stmt = stmt.where(ConfigurationTransport.aller_retour == aller_retour)
    if is_active is not None:
        stmt = stmt.where(ConfigurationTransport.is_active == is_active)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(ConfigurationTransport.poste, ConfigurationTransport.shift)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return {
        "items": [_to_resp(i) for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", response_model=ConfigurationTransportResponse, status_code=status.HTTP_201_CREATED)
async def create_configuration_transport(
    payload: ConfigurationTransportCreate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationTransportResponse:
    obj = ConfigurationTransport(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.get("/{item_id}", response_model=ConfigurationTransportResponse)
async def get_configuration_transport(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationTransportResponse:
    obj = await db.get(ConfigurationTransport, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Configuration introuvable")
    return _to_resp(obj)


@router.patch("/{item_id}", response_model=ConfigurationTransportResponse)
async def update_configuration_transport(
    item_id: uuid.UUID,
    payload: ConfigurationTransportUpdate,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> ConfigurationTransportResponse:
    obj = await db.get(ConfigurationTransport, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Configuration introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return _to_resp(obj)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_configuration_transport(
    item_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "daf")),
    db: AsyncSession = Depends(get_db),
) -> None:
    obj = await db.get(ConfigurationTransport, item_id)
    if not obj or obj.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Configuration introuvable")
    await db.delete(obj)
    await db.commit()
