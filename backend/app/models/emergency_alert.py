from __future__ import annotations

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class EmergencyAlert(BaseModel):
    __tablename__ = "emergency_alert"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    location: Mapped[object | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    lat: Mapped[float | None] = mapped_column(nullable=True)
    lng: Mapped[float | None] = mapped_column(nullable=True)
    alert_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="panic"
    )
    responders_notified: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_emergency_alert_tenant_id", "tenant_id"),
        Index("ix_emergency_alert_employee_id", "employee_id"),
        Index("ix_emergency_alert_triggered_at", "triggered_at"),
        Index("ix_emergency_alert_location", "location", postgresql_using="gist"),
    )
