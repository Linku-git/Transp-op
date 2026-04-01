from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.auth import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate user with email/password and return JWT tokens."""
    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(User.email == body.email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)

    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role": user.role.name if user.role else "",
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.post("/logout")
async def logout() -> dict:
    """Log out the current user.

    This is a placeholder. A real implementation would blacklist the token
    in Redis so it cannot be reused before its natural expiry.
    """
    return {"detail": "Logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Issue a new access token using a valid refresh token."""
    try:
        payload = decode_token(body.refresh_token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    sub: str | None = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    stmt = (
        select(User)
        .options(selectinload(User.role))
        .where(User.id == sub)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role": user.role.name if user.role else "",
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_active_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return user
