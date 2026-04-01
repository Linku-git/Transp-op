from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.middleware.rbac import require_role
from app.models.auth import User
from app.schemas.auth import UserCreate, UserResponse, UserUpdate
from app.utils.security import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")


@router.get("/", response_model=list[UserResponse])
async def list_users(
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    """List all users within the admin's tenant."""
    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(User.tenant_id == admin.tenant_id)
        .order_by(User.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user within the admin's tenant."""
    # Check for duplicate email within tenant
    stmt = select(User).where(
        User.tenant_id == admin.tenant_id,
        User.email == body.email,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        tenant_id=admin.tenant_id,
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        role_id=body.role_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user, attribute_names=["role"])
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update a user. Admins can update any user in their tenant; others can only update themselves."""
    is_admin = current_user.role is not None and current_user.role.name == "admin"
    is_self = current_user.id == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id, User.tenant_id == current_user.tenant_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    # Non-admins cannot change role or active status
    if not is_admin:
        update_data.pop("role_id", None)
        update_data.pop("is_active", None)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user, attribute_names=["role"])
    return user


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: uuid.UUID,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Deactivate a user (soft delete). Admin only."""
    stmt = select(User).where(
        User.id == user_id,
        User.tenant_id == admin.tenant_id,
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = False
    await db.flush()
    return {"detail": "User deactivated"}
