from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DepartureSchedule(BaseModel):
    """Optimized departure schedule from LTO anti-platooning."""

    __tablename__ = "departure_schedule"
    __table_args__ = (
        Index("ix_departure_schedule_tenant_id", "tenant_id"),
        Index("ix_departure_schedule_ligne_id", "ligne_id"),
        Index("ix_departure_schedule_date", "schedule_date"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    ligne_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ligne.id"), nullable=False
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    scheduled_departure: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    optimized_departure: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    offset_seconds: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)

    is_applied: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    optimization_run_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
