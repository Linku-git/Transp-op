from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    body: str | None = None
    content_type: str = Field(default="news", pattern="^(news|training|safety|survey)$")
    media_url: str | None = Field(default=None, max_length=1000)
    target_sites: list[str] | None = None
    target_departments: list[str] | None = None
    target_shifts: list[str] | None = None
    expires_at: datetime | None = None


class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    body: str | None = None
    content_type: str | None = Field(default=None, pattern="^(news|training|safety|survey)$")
    media_url: str | None = None
    target_sites: list[str] | None = None
    target_departments: list[str] | None = None
    target_shifts: list[str] | None = None
    expires_at: datetime | None = None


class ContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    body: str | None = None
    content_type: str
    media_url: str | None = None
    target_sites: list | None = None
    target_departments: list | None = None
    target_shifts: list | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    created_by: uuid.UUID | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ContentListResponse(BaseModel):
    data: list[ContentResponse]
    total: int
    page: int = 1
    pages: int = 1
