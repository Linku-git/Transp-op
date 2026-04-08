from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ContentDelivery(BaseModel):
    __tablename__ = "content_delivery"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False
    )
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    viewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    quiz_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    time_spent_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    __table_args__ = (
        Index("ix_content_delivery_tenant_id", "tenant_id"),
        Index("ix_content_delivery_content_id", "content_id"),
        Index("ix_content_delivery_employee_id", "employee_id"),
        Index(
            "ix_content_delivery_content_employee",
            "content_id",
            "employee_id",
            unique=True,
        ),
    )
