from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OperatorSizingPlan(BaseModel):
    id: uuid.UUID
    version: int
    format: str
    status: str
    file_url: str | None = None
    content_summary: dict | None = None
    acknowledged: bool = False
    acknowledged_at: datetime | None = None
    created_at: datetime


class OperatorSizingPlanList(BaseModel):
    data: list[OperatorSizingPlan]
    total: int


class AcknowledgeResponse(BaseModel):
    plan_id: uuid.UUID
    acknowledged: bool = True
    acknowledged_at: datetime


class ServiceIssueCreate(BaseModel):
    issue_type: str = Field(..., pattern=r"^(delay|breakdown|safety|capacity|route|other)$")
    description: str = Field(..., min_length=10, max_length=2000)
    affected_route: str | None = None
    incident_date: str | None = None


class ServiceIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    operator_id: uuid.UUID
    issue_type: str
    description: str
    affected_route: str | None = None
    incident_date: str | None = None
    status: str = "open"
    created_at: datetime
