from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RTIEvent(BaseModel):
    __tablename__ = "rti_event"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicle.id"), nullable=False
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    event_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="arrival"
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    wait_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    __table_args__ = (
        Index("ix_rti_event_vehicle_id", "vehicle_id"),
        Index("ix_rti_event_tenant_id", "tenant_id"),
        Index("ix_rti_event_event_type", "event_type"),
    )
