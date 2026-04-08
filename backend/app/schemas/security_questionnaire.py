from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SecurityQuestionnaireSubmit(BaseModel):
    overall_safety_rating: int = Field(..., ge=1, le=5)
    responses: dict | None = None
    vulnerable_stops: list[str] | None = None
    night_concerns: str | None = None
    trigger_type: str = Field(default="periodic", pattern="^(periodic|incident|initial)$")


class SecurityQuestionnaireResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    employee_id: uuid.UUID
    version: int
    overall_safety_rating: int
    responses: dict | None = None
    vulnerable_stops: list | None = None
    night_concerns: str | None = None
    submitted_at: datetime
    trigger_type: str
    created_at: datetime


class SecurityQuestionnaireHistory(BaseModel):
    latest: SecurityQuestionnaireResponse | None = None
    history: list[SecurityQuestionnaireSummary] = []
    total_submissions: int = 0


class SecurityQuestionnaireSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    overall_safety_rating: int
    submitted_at: datetime
    trigger_type: str


class ReassessmentStatus(BaseModel):
    employee_id: uuid.UUID
    last_submitted_at: datetime | None = None
    is_due: bool
    next_due_at: datetime | None = None
    trigger_type: str = "periodic"
