from __future__ import annotations

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field


class RTIConfigCreate(BaseModel):
    site_id: uuid.UUID
    max_wait_seconds: int = Field(default=90, ge=30, le=600)
    compliance_target_pct: float = Field(default=95.0, ge=50, le=100)
    buffer_vehicle_count: int = Field(default=2, ge=0, le=20)
    night_mode_start: time | None = None
    night_mode_end: time | None = None


class RTIConfigUpdate(BaseModel):
    max_wait_seconds: int | None = Field(default=None, ge=30, le=600)
    compliance_target_pct: float | None = Field(default=None, ge=50, le=100)
    buffer_vehicle_count: int | None = Field(default=None, ge=0, le=20)
    night_mode_start: time | None = None
    night_mode_end: time | None = None


class RTIConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID
    max_wait_seconds: int
    compliance_target_pct: float
    buffer_vehicle_count: int
    night_mode_start: time | None = None
    night_mode_end: time | None = None
    created_at: datetime
    updated_at: datetime


class AdaptiveSizingResult(BaseModel):
    site_id: uuid.UUID
    required_buffer: int
    recommended_buffer: int
    current_compliance_pct: float
    is_degraded: bool
    buffer_activated: bool
    tad_requested: bool


class FallbackEvent(BaseModel):
    site_id: uuid.UUID
    event_type: str
    reason: str
    timestamp: datetime
