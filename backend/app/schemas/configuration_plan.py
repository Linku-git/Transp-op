from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConfigurationPlanCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None
    is_active: bool = True
    is_current: bool = False
    source: str | None = Field(default=None, max_length=50)


class ConfigurationPlanUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_active: bool | None = None
    is_current: bool | None = None
    source: str | None = Field(default=None, max_length=50)


class ConfigurationPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None
    is_active: bool
    is_current: bool
    source: str | None
    row_count: int = 0
    created_at: datetime
    updated_at: datetime
