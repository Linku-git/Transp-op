from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, status

from app.middleware.auth import get_current_active_user
from app.models.auth import User


# ---------------------------------------------------------------------------
# Role constants
# ---------------------------------------------------------------------------

ALL_ROLES: list[str] = [
    "admin",
    "drh",
    "daf",
    "salarie",
    "operateur",
    "responsable_parc",
    "responsable_exploitation",
    "prestataire",
    "conducteur",
]

SOTREG_MODULE_ROLES: dict[str, list[str]] = {
    "m1_diagnostic": ["admin", "drh", "responsable_exploitation"],
    "m2_technologies": ["admin", "drh", "daf", "responsable_parc"],
    "m3_infrastructure": ["admin", "drh", "responsable_parc"],
    "m4_performance": ["admin", "drh", "responsable_parc", "responsable_exploitation"],
    "m5_finance": ["admin", "daf", "drh"],
    "m6_roadmap": ["admin", "drh", "daf"],
    "m7_scoring": ["admin", "drh", "daf"],
    "m8_realtime": ["admin", "responsable_exploitation", "conducteur"],
}


# ---------------------------------------------------------------------------
# require_role — existing dependency (unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# require_module — SOTREG module-level access control
# ---------------------------------------------------------------------------


def require_module(module_key: str) -> Callable[..., Any]:
    """Return a FastAPI dependency that checks SOTREG module access.

    Raises 403 if the user's role is not in ``SOTREG_MODULE_ROLES[module_key]``.

    Usage::

        @router.get("/data", dependencies=[Depends(require_module("m1_diagnostic"))])
        async def diagnostic_data(): ...
    """
    allowed_roles = SOTREG_MODULE_ROLES.get(module_key, [])

    async def _module_checker(
        user: User = Depends(get_current_active_user),
    ) -> User:
        if user.role is None or user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for module {module_key}",
            )
        return user

    return _module_checker
