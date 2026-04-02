from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# OptimizationSettings schemas
# ---------------------------------------------------------------------------


class SettingsResponse(BaseModel):
    """Response for tenant optimization settings."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    meeting_radius_meters: float
    max_walking_distance_meters: float
    max_route_duration_seconds: int
    fuel_cost_per_liter: float
    fuel_consumption_l_per_100km: float
    co2_kg_per_liter: float
    rti_threshold_minutes: int
    night_mode_start: str
    night_mode_end: str
    min_night_group_size: int
    created_at: datetime
    updated_at: datetime


class SettingsUpdateRequest(BaseModel):
    """Partial update for optimization settings."""

    meeting_radius_meters: float | None = Field(default=None, ge=50, le=5000)
    max_walking_distance_meters: float | None = Field(default=None, ge=100, le=5000)
    max_route_duration_seconds: int | None = Field(default=None, ge=600, le=18000)
    fuel_cost_per_liter: float | None = Field(default=None, ge=1, le=100)
    fuel_consumption_l_per_100km: float | None = None
    co2_kg_per_liter: float | None = None
    rti_threshold_minutes: int | None = Field(default=None, ge=1, le=120)
    night_mode_start: str | None = Field(default=None, max_length=5)
    night_mode_end: str | None = Field(default=None, max_length=5)
    min_night_group_size: int | None = Field(default=None, ge=1, le=50)

    @field_validator("night_mode_start", "night_mode_end")
    @classmethod
    def validate_time_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be in HH:MM format")
        try:
            hour, minute = int(parts[0]), int(parts[1])
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time value")
        return v


# ---------------------------------------------------------------------------
# ConstraintParam schemas
# ---------------------------------------------------------------------------


class ConstraintResponse(BaseModel):
    """Response for a constraint parameter."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    key: str
    value: str
    category: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConstraintCreateRequest(BaseModel):
    """Request to create a constraint parameter."""

    key: str = Field(max_length=100)
    value: str = Field(max_length=500)
    category: str = Field(default="general", max_length=50)
    description: str | None = Field(default=None, max_length=500)


class ConstraintUpdateRequest(BaseModel):
    """Partial update for a constraint parameter."""

    value: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ConstraintBulkRequest(BaseModel):
    """Bulk import of constraint parameters."""

    constraints: list[ConstraintCreateRequest] = Field(min_length=1, max_length=100)
