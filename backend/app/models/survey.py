from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Survey(BaseModel):
    __tablename__ = "survey"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    questions: Mapped[list] = mapped_column(JSONB, nullable=False)
    response_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_survey_tenant_id", "tenant_id"),
        Index("ix_survey_content_id", "content_id"),
        Index("ix_survey_is_active", "is_active"),
    )
