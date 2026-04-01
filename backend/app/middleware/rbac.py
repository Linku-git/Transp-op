from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, status

from app.middleware.auth import get_current_active_user
from app.models.auth import User


def require_role(*allowed_roles: str) -> Callable[..., Any]:
    """Return a FastAPI dependency that enforces role-based access.

    Usage::

        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint(): ...

    Or as a direct dependency::

        async def handler(user: User = Depends(require_role("admin", "drh"))): ...
    """

    async def _role_checker(
        user: User = Depends(get_current_active_user),
    ) -> User:
        if user.role is None or user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _role_checker
