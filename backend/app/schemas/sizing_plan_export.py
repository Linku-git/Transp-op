from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SizingPlanExportRequest(BaseModel):
    optimization_id: uuid.UUID | None = None
    operator_id: uuid.UUID | None = None
    format: str = Field(default="json", pattern=r"^(json|xml|pdf)$")


class SizingPlanExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    optimization_id: uuid.UUID | None = None
    operator_id: uuid.UUID | None = None
    format: str
    file_url: str | None = None
    status: str
    version: int
    content_summary: dict | None = None
    changes_from_previous: dict | None = None
    created_at: datetime
    updated_at: datetime


class SizingPlanExportListResponse(BaseModel):
    data: list[SizingPlanExportResponse]
    total: int
    page: int = 1
    pages: int = 1
