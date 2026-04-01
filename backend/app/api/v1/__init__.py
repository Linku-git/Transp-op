from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.roles import router as roles_router
from app.api.v1.sites import router as sites_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(roles_router, tags=["roles"])
api_router.include_router(tenants_router, tags=["tenants"])
api_router.include_router(sites_router, tags=["sites"])
