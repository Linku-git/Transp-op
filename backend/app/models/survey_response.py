from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SurveyResponse(BaseModel):
    __tablename__ = "survey_response"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("survey.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=True
    )
    responses: Mapped[list] = mapped_column(JSONB, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        Index("ix_survey_response_tenant_id", "tenant_id"),
        Index("ix_survey_response_survey_id", "survey_id"),
        Index("ix_survey_response_employee_id", "employee_id"),
    )
