from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SecurityQuestionnaire(BaseModel):
    __tablename__ = "security_questionnaire"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    overall_safety_rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    responses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    vulnerable_stops: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    night_concerns: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    trigger_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="periodic"
    )

    __table_args__ = (
        Index("ix_security_questionnaire_tenant_id", "tenant_id"),
        Index("ix_security_questionnaire_employee_id", "employee_id"),
        Index("ix_security_questionnaire_submitted", "submitted_at"),
    )
