from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MLModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_type: str
    version: int
    status: str
    metrics: dict | None = None
    file_path: str | None = None
    trained_at: datetime | None = None
    feature_names: list[str] | None = None
    created_at: datetime
    updated_at: datetime


class MLModelListResponse(BaseModel):
    data: list[MLModelResponse]
    total: int


class RetrainRequest(BaseModel):
    force: bool = Field(default=False, description="Force retraining even if metrics haven't improved")


class RetrainResponse(BaseModel):
    model_type: str
    status: str
    message: str
    task_id: str | None = None


class FeatureResponse(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    features: dict[str, float]
    window: str
    computed_at: datetime | None = None
