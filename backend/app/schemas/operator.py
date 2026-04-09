from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OperatorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    operator_type: str = Field(..., pattern=r"^(via|swvl|local|internal)$")
    api_config: dict | None = None
    contacts: list[dict] | None = None


class OperatorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    operator_type: str | None = Field(default=None, pattern=r"^(via|swvl|local|internal)$")
    api_config: dict | None = None
    contacts: list[dict] | None = None
    is_active: bool | None = None


class OperatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    operator_type: str
    api_config: dict | None = None
    contacts: list | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OperatorListResponse(BaseModel):
    data: list[OperatorResponse]
    total: int
    page: int = 1
    pages: int = 1
