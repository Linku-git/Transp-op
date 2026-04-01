from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RouteStopResponse(BaseModel):
    """A single stop along a route."""

    model_config = ConfigDict(from_attributes=True)

    employee_id: uuid.UUID | None
    lat: float
    lng: float
    is_pickup: bool
    eta_seconds: float
    cumulative_distance_meters: float


class RouteResponse(BaseModel):
    """Full route with ordered stops, polyline, and metrics."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    optimization_id: uuid.UUID
    vehicle_id: uuid.UUID | None
    site_id: uuid.UUID
    ordered_stops: list[RouteStopResponse]
    total_distance_km: Decimal | None
    total_time_minutes: Decimal | None
    polyline: str | None
    rti_compliance_pct: Decimal | None
    created_at: datetime

    # Joined fields
    vehicle_type: str | None = None
    vehicle_capacity: int | None = None
    site_name: str | None = None


class TwoLegResponse(BaseModel):
    """Two-leg route: walking access + driving main."""

    access_leg: dict
    main_leg: dict
    total_duration_seconds: float
    total_distance_meters: float
