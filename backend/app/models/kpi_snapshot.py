from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class KPISnapshot(BaseModel):
    """Point-in-time capture of a KPI value for trend tracking."""

    __tablename__ = "kpi_snapshot"
    __table_args__ = (
        Index("idx_kpi_snapshot_tenant", "tenant_id"),
        Index("idx_kpi_snapshot_site", "site_id"),
        Index("idx_kpi_snapshot_type_date", "kpi_type", "snapshot_date"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    kpi_type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
