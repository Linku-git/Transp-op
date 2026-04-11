from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class FeatureRecord(BaseModel):
    """Feature store record for ML feature caching."""

    __tablename__ = "feature_store"
    __table_args__ = (
        Index("ix_feature_store_entity", "tenant_id", "entity_type", "entity_id"),
        Index("ix_feature_store_lookup", "tenant_id", "entity_type", "entity_id", "feature_name", "window"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
    )  # vehicle, driver, route, stop
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_value: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    window: Mapped[str] = mapped_column(
        String(10), nullable=False, default="24h",
    )  # 1h, 24h, 7d, 30d
