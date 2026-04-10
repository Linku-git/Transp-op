from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# LTO Optimize request/response
# ---------------------------------------------------------------------------


class LigneDeparture(BaseModel):
    """A single departure for LTO input."""

    vehicle_id: str | None = None
    scheduled_departure: datetime
    actual_departure: datetime | None = None


class LTOOptimizeRequest(BaseModel):
    """Request to run LTO optimization for a ligne."""

    ligne_id: uuid.UUID
    departures: list[LigneDeparture]
    target_headway_seconds: float = Field(default=600.0, gt=0)
    min_headway_seconds: float = Field(default=120.0, gt=0)
    max_offset_seconds: float = Field(default=300.0, gt=0)


class OptimizedDeparture(BaseModel):
    """A single optimized departure in the result."""

    vehicle_id: str | None
    scheduled_departure: str
    optimized_departure: str
    offset_seconds: float


class PlatooningCheck(BaseModel):
    """Platooning detection result."""

    is_platooning: bool
    cov_headway: float
    avg_deviation_seconds: float
    max_deviation_seconds: float
    vehicle_count: int
    recommendation: str


class OptimizationResult(BaseModel):
    """Optimization algorithm result."""

    original_cov: float
    optimized_cov: float
    improvement_pct: float
    converged: bool
    iterations: int
    target_headway_seconds: float


class LTOOptimizeResponse(BaseModel):
    """Response from LTO optimization."""

    needs_optimization: bool
    platooning_check: PlatooningCheck
    schedule: list[OptimizedDeparture]
    optimization_result: OptimizationResult | None = None


# ---------------------------------------------------------------------------
# Schedule query response
# ---------------------------------------------------------------------------


class DepartureScheduleResponse(BaseModel):
    """Departure schedule record response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    ligne_id: uuid.UUID
    vehicle_id: uuid.UUID | None
    scheduled_departure: datetime
    optimized_departure: datetime
    offset_seconds: float
    schedule_date: date
    is_applied: bool
    optimization_run_id: str | None
    created_at: datetime
    updated_at: datetime


class LTOApplyRequest(BaseModel):
    """Request to apply an optimized schedule."""

    ligne_id: uuid.UUID
    schedule_date: date = Field(default_factory=date.today)
