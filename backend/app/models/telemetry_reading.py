from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TelemetryReading(BaseModel):
    """IoT telemetry reading from vehicle sensors."""

    __tablename__ = "telemetry_reading"
    __table_args__ = (
        Index("ix_telemetry_reading_tenant_id", "tenant_id"),
        Index("ix_telemetry_reading_vehicle_id", "vehicle_id"),
        Index("ix_telemetry_reading_sensor_type", "sensor_type"),
        Index("ix_telemetry_reading_timestamp", "reading_timestamp"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    reading_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sensor_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reading_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
