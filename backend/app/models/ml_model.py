from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class MLModel(BaseModel):
    """Machine Learning model version in the registry."""

    __tablename__ = "ml_model"
    __table_args__ = (
        Index("ix_ml_model_tenant_type", "tenant_id", "model_type"),
        Index("ix_ml_model_tenant_status", "tenant_id", "status"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False,
    )
    model_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )  # isolation_forest, random_forest, lstm
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="training",
    )  # training, ready, promoted, retired
    metrics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    trained_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    feature_names: Mapped[list | None] = mapped_column(JSONB, nullable=True)
