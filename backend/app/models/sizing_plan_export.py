from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SizingPlanExport(BaseModel):
    __tablename__ = "sizing_plan_export"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    optimization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.id"), nullable=True
    )
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changes_from_previous: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_sizing_plan_export_tenant_id", "tenant_id"),
        Index("ix_sizing_plan_export_operator_id", "operator_id"),
        Index("ix_sizing_plan_export_status", "status"),
    )
