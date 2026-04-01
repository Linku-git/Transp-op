from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.rbac import require_role
from app.models.auth import User
from app.models.optimization import Optimization, Route
from app.schemas.route import RouteResponse, RouteStopResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _route_to_response(route: Route) -> RouteResponse:
    """Convert a Route ORM object to a RouteResponse schema.

    Parses the ``ordered_stops`` JSONB column into a list of
    :class:`RouteStopResponse` objects and enriches the response
    with joined vehicle and site information when available.
    """
    raw_stops = route.ordered_stops if route.ordered_stops else []
    stops = [
        RouteStopResponse(
            employee_id=s.get("employee_id"),
            lat=s.get("lat", 0.0),
            lng=s.get("lng", 0.0),
            is_pickup=s.get("is_pickup", True),
            eta_seconds=s.get("eta_seconds", 0.0),
            cumulative_distance_meters=s.get("cumulative_distance_meters", 0.0),
        )
        for s in raw_stops
    ]

    vehicle_type: str | None = None
    vehicle_capacity: int | None = None
    if route.vehicle is not None:
        vehicle_type = route.vehicle.type
        vehicle_capacity = route.vehicle.capacity

    site_name: str | None = None
    if route.site is not None:
        site_name = route.site.name

    return RouteResponse(
        id=route.id,
        optimization_id=route.optimization_id,
        vehicle_id=route.vehicle_id,
        site_id=route.site_id,
        ordered_stops=stops,
        total_distance_km=route.total_distance_km,
        total_time_minutes=route.total_time_minutes,
        polyline=route.polyline,
        rti_compliance_pct=route.rti_compliance_pct,
        created_at=route.created_at,
        vehicle_type=vehicle_type,
        vehicle_capacity=vehicle_capacity,
        site_name=site_name,
    )


# ---------------------------------------------------------------------------
# GET /routes — list routes with optional filters
# ---------------------------------------------------------------------------


@router.get("", response_model=list[RouteResponse])
async def list_routes(
    site_id: uuid.UUID | None = Query(default=None, description="Filter by site"),
    optimization_id: uuid.UUID | None = Query(
        default=None, description="Filter by optimization run"
    ),
    vehicle_id: uuid.UUID | None = Query(
        default=None, description="Filter by vehicle"
    ),
    current_user: User = Depends(require_role("admin", "drh", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> list[RouteResponse]:
    """List routes, optionally filtered by site, optimization, or vehicle."""
    conditions = [
        Optimization.tenant_id == current_user.tenant_id,
    ]
    if site_id is not None:
        conditions.append(Route.site_id == site_id)
    if optimization_id is not None:
        conditions.append(Route.optimization_id == optimization_id)
    if vehicle_id is not None:
        conditions.append(Route.vehicle_id == vehicle_id)

    stmt = (
        select(Route)
        .join(Optimization, Route.optimization_id == Optimization.id)
        .where(*conditions)
        .order_by(Route.created_at.desc())
    )
    result = await db.execute(stmt)
    routes = list(result.scalars().all())

    return [_route_to_response(r) for r in routes]


# ---------------------------------------------------------------------------
# GET /routes/{route_id} — single route detail
# ---------------------------------------------------------------------------


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: uuid.UUID,
    current_user: User = Depends(require_role("admin", "drh", "operateur")),
    db: AsyncSession = Depends(get_db),
) -> RouteResponse:
    """Get a single route by ID with tenant check."""
    stmt = (
        select(Route)
        .join(Optimization, Route.optimization_id == Optimization.id)
        .where(
            Route.id == route_id,
            Optimization.tenant_id == current_user.tenant_id,
        )
    )
    result = await db.execute(stmt)
    route = result.scalar_one_or_none()

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return _route_to_response(route)
