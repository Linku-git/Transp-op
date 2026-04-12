"""Pydantic schemas for driver risk scoring (Session 120)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DriverRiskProfileResponse(BaseModel):
    """Response for a single driver's risk profile."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    driver_id: uuid.UUID
    licence_type: str | None = None
    experience_years: int | None = None
    total_km_driven: float
    risk_score: float
    risk_category: str
    last_scored_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DriverRiskScoreRequest(BaseModel):
    """Request to trigger batch driver risk scoring."""

    force: bool = Field(default=False, description="Force re-score all drivers even if recently scored")


class DriverRiskScoreResponse(BaseModel):
    """Response from batch scoring trigger."""

    status: str
    message: str
    drivers_scored: int = 0
    task_id: str | None = None


class FeatureImportanceResponse(BaseModel):
    """Feature importance from the trained model."""

    features: dict[str, float] = Field(..., description="Feature name to importance mapping")
    model_version: int | None = None
