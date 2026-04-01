from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import Tenant, User
from app.schemas.auth import TenantCreate, TenantResponse, TenantUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants")


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> list[Tenant]:
    """List all tenants. Admin only."""
    stmt = select(Tenant).order_by(Tenant.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: TenantCreate,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Create a new tenant. Admin only."""
    # Check for duplicate code
    stmt = select(Tenant).where(Tenant.code == body.code)
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tenant with this code already exists",
        )

    tenant = Tenant(
        name=body.name,
        code=body.code,
    )
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    body: TenantUpdate,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """Update an existing tenant. Admin only."""
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    await db.flush()
    await db.refresh(tenant)
    return tenant
