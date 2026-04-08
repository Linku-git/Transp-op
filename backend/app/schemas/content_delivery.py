from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeliveryEventCreate(BaseModel):
    """Record a delivery event (content served to employee)."""
    content_id: uuid.UUID
    employee_id: uuid.UUID


class ViewEventCreate(BaseModel):
    """Record a view event (content opened)."""
    pass


class CompletionEventCreate(BaseModel):
    """Record a completion event with optional quiz score and time spent."""
    quiz_score: float | None = Field(default=None, ge=0.0, le=100.0)
    time_spent_seconds: int | None = Field(default=None, ge=0)


class ContentDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    content_id: uuid.UUID
    employee_id: uuid.UUID
    delivered_at: datetime
    viewed_at: datetime | None = None
    completed_at: datetime | None = None
    quiz_score: float | None = None
    time_spent_seconds: int | None = None
    created_at: datetime
    updated_at: datetime


class EngagementMetrics(BaseModel):
    """Aggregated engagement metrics for a content item."""
    content_id: uuid.UUID
    total_deliveries: int = 0
    total_views: int = 0
    total_completions: int = 0
    view_rate: float = 0.0
    completion_rate: float = 0.0
    avg_quiz_score: float | None = None
    avg_time_spent_seconds: float | None = None


class FeedContentResponse(BaseModel):
    """Content item in the personalized feed."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    body: str | None = None
    content_type: str
    media_url: str | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    # Delivery status for the requesting employee
    delivered: bool = False
    viewed: bool = False
    completed: bool = False


class FeedResponse(BaseModel):
    data: list[FeedContentResponse]
    total: int
    page: int = 1
    pages: int = 1
