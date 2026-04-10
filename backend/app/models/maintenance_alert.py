from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class MaintenanceAlert(BaseModel):
    """Predictive maintenance alert from Isolation Forest anomaly detection."""

    __tablename__ = "maintenance_alert"
    __table_args__ = (
        Index("ix_maintenance_alert_tenant_id", "tenant_id"),
        Index("ix_maintenance_alert_vehicle_id", "vehicle_id"),
        Index("ix_maintenance_alert_severity", "severity"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="anomaly"
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="medium"
    )
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    features: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    acknowledged: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
