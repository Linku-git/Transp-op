from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import Role, User
from app.schemas.auth import RoleCreate, RoleResponse, RoleUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles")


@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> list[Role]:
    """List all roles within the admin's tenant."""
    stmt = (
        select(Role)
        .where(Role.tenant_id == admin.tenant_id)
        .order_by(Role.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> Role:
    """Create a new role within the admin's tenant."""
    role = Role(
        tenant_id=admin.tenant_id,
        name=body.name,
        permissions=body.permissions,
    )
    db.add(role)
    await db.flush()
    await db.refresh(role)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> Role:
    """Update an existing role. Admin only."""
    stmt = select(Role).where(
        Role.id == role_id,
        Role.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    await db.flush()
    await db.refresh(role)
    return role
