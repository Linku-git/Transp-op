from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmergencyAlertTrigger(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    alert_type: str = Field(default="panic", pattern="^(panic|medical|vehicle_incident|other)$")


class EmergencyAlertResolve(BaseModel):
    resolution_notes: str | None = None


class EmergencyAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    triggered_at: datetime
    lat: float | None = None
    lng: float | None = None
    alert_type: str
    responders_notified: list | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    created_at: datetime


class EmergencyAlertListResponse(BaseModel):
    data: list[EmergencyAlertResponse]
    total: int
    page: int = 1
    pages: int = 1
