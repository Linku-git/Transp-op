from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TrainingModuleCreate(BaseModel):
    content_id: uuid.UUID
    lms_provider: str = Field(..., pattern=r"^(cornerstone|360learning|talentlms)$")
    lms_external_id: str = Field(..., min_length=1, max_length=255)
    duration_minutes: int | None = None
    is_mandatory: bool = False
    certification_name: str | None = None
    lms_metadata: dict | None = None


class TrainingModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    content_id: uuid.UUID
    lms_provider: str
    lms_external_id: str
    duration_minutes: int | None = None
    is_mandatory: bool = False
    certification_name: str | None = None
    lms_metadata: dict | None = None
    last_synced_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class TrainingModuleListResponse(BaseModel):
    data: list[TrainingModuleResponse]
    total: int
    page: int = 1
    pages: int = 1


class CompletionRecord(BaseModel):
    employee_id: uuid.UUID
    content_id: uuid.UUID
    training_module_id: uuid.UUID | None = None
    lms_provider: str | None = None
    lms_external_id: str | None = None
    completed_at: datetime | None = None
    quiz_score: float | None = None
    time_spent_seconds: int | None = None
    certification_name: str | None = None


class CompletionListResponse(BaseModel):
    data: list[CompletionRecord]
    total: int
    page: int = 1
    pages: int = 1


class SyncRequest(BaseModel):
    provider: str = Field(..., pattern=r"^(cornerstone|360learning|talentlms)$")


class SyncResult(BaseModel):
    provider: str
    imported: int = 0
    exported: int = 0
    errors: list[str] = []


class WebhookPayload(BaseModel):
    provider: str
    event_type: str
    lms_external_id: str
    employee_external_id: str | None = None
    completed_at: str | None = None
    score: float | None = None
    metadata: dict | None = None
