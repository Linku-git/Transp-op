from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TrainingModule(BaseModel):
    __tablename__ = "training_module"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content.id"), nullable=False
    )
    lms_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    lms_external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    certification_name: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    lms_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    __table_args__ = (
        Index("ix_training_module_tenant_id", "tenant_id"),
        Index("ix_training_module_content_id", "content_id"),
        Index("ix_training_module_lms_provider", "lms_provider"),
        Index(
            "ix_training_module_lms_external",
            "tenant_id",
            "lms_provider",
            "lms_external_id",
            unique=True,
        ),
    )
