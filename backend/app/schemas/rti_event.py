from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RTIEventCreate(BaseModel):
    vehicle_id: uuid.UUID
    stop_id: uuid.UUID | None = None
    event_type: str = "arrival"
    scheduled_at: datetime | None = None
    actual_at: datetime | None = None
    wait_duration_seconds: int | None = None


class RTIEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vehicle_id: uuid.UUID
    stop_id: uuid.UUID | None = None
    event_type: str
    scheduled_at: datetime | None = None
    actual_at: datetime | None = None
    wait_duration_seconds: int | None = None
    created_at: datetime


class RTIComplianceResponse(BaseModel):
    total_events: int
    compliant_events: int
    compliance_percentage: float
    threshold_seconds: int = 90
