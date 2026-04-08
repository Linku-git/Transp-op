from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StopRiskScoreCreate(BaseModel):
    site_id: uuid.UUID | None = None
    stop_name: str = Field(..., min_length=1, max_length=255)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    isolation_score: float = Field(default=0.5, ge=0, le=1)
    lighting_score: float = Field(default=0.5, ge=0, le=1)
    tc_frequency_score: float = Field(default=0.5, ge=0, le=1)
    night_risk_multiplier: float = Field(default=1.0, ge=0, le=2)
    employee_perception_avg: float = Field(default=0.5, ge=0, le=1)


class StopRiskScoreUpdate(BaseModel):
    stop_name: str | None = Field(default=None, min_length=1, max_length=255)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    isolation_score: float | None = Field(default=None, ge=0, le=1)
    lighting_score: float | None = Field(default=None, ge=0, le=1)
    tc_frequency_score: float | None = Field(default=None, ge=0, le=1)
    night_risk_multiplier: float | None = Field(default=None, ge=0, le=2)
    employee_perception_avg: float | None = Field(default=None, ge=0, le=1)


class StopRiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    site_id: uuid.UUID | None = None
    stop_name: str
    lat: float
    lng: float
    isolation_score: float
    lighting_score: float
    tc_frequency_score: float
    night_risk_multiplier: float
    employee_perception_avg: float
    composite_risk_score: float
    is_critical: bool
    created_at: datetime
    updated_at: datetime


class StopRiskScoreListResponse(BaseModel):
    data: list[StopRiskScoreResponse]
    total: int
