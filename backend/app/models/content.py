from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Content(BaseModel):
    __tablename__ = "content"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="news"
    )
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    target_sites: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    target_departments: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    target_shifts: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_content_tenant_id", "tenant_id"),
        Index("ix_content_content_type", "content_type"),
        Index("ix_content_published_at", "published_at"),
        Index("ix_content_is_active", "is_active"),
    )
