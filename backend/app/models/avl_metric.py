from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class AVLMetric(BaseModel):
    """AVL-based operational KPI metric record."""

    __tablename__ = "avl_metric"
    __table_args__ = (
        Index("ix_avl_metric_tenant_id", "tenant_id"),
        Index("ix_avl_metric_ligne_id", "ligne_id"),
        Index("ix_avl_metric_vehicle_id", "vehicle_id"),
        Index("ix_avl_metric_metric_type", "metric_type"),
        Index("ix_avl_metric_date", "metric_date"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    ligne_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ligne.id"), nullable=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    metric_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    period: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="daily"
    )

    sample_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meets_target: Mapped[bool | None] = mapped_column(nullable=True)
    details: Mapped[str | None] = mapped_column(String(500), nullable=True)
