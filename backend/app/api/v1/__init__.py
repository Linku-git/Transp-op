from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.clusters import router as clusters_router
from app.api.v1.employees import router as employees_router
from app.api.v1.excel_import import router as excel_import_router
from app.api.v1.health import router as health_router
from app.api.v1.leaves import router as leaves_router
from app.api.v1.modal import employee_modal_router, modal_stats_router
from app.api.v1.roles import router as roles_router
from app.api.v1.sites import router as sites_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.users import router as users_router
from app.api.v1.routes import router as routes_router
from app.api.v1.vehicle_assignments import router as vehicle_assignments_router
from app.api.v1.optimization import router as optimization_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.scenarios import router as scenarios_router
from app.api.v1.settings import router as settings_router
from app.api.v1.constraints import router as constraints_router
from app.api.v1.weather import router as weather_router
from app.api.v1.exports import router as exports_router
from app.api.v1.financial import router as financial_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(roles_router, tags=["roles"])
api_router.include_router(tenants_router, tags=["tenants"])
api_router.include_router(sites_router, tags=["sites"])
api_router.include_router(employees_router, tags=["employees"])
api_router.include_router(leaves_router, tags=["leaves"])
api_router.include_router(employee_modal_router, tags=["modal"])
api_router.include_router(modal_stats_router, tags=["modal"])
api_router.include_router(excel_import_router, tags=["import"])
api_router.include_router(clusters_router, tags=["clusters"])
api_router.include_router(optimization_router, tags=["optimization"])
api_router.include_router(vehicles_router, tags=["vehicles"])
api_router.include_router(vehicle_assignments_router, tags=["vehicle-assignments"])
api_router.include_router(routes_router, tags=["routes"])
api_router.include_router(scenarios_router, tags=["scenarios"])
api_router.include_router(settings_router, tags=["settings"])
api_router.include_router(constraints_router, tags=["constraints"])
api_router.include_router(weather_router, tags=["weather"])
api_router.include_router(exports_router, tags=["exports"])
api_router.include_router(financial_router, tags=["financial"])
