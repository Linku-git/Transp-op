from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class FleetContext(BaseModel):
    """Snapshot of fleet diagnostics aggregated from all Ligne records."""

    __tablename__ = "fleet_context"
    __table_args__ = (Index("ix_fleet_context_tenant_id", "tenant_id"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    total_vehicles: Mapped[int] = mapped_column(Integer, nullable=False)
    total_km_annual: Mapped[float] = mapped_column(Float, nullable=False)
    total_tco2_annual: Mapped[float] = mapped_column(Float, nullable=False)
    average_age_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    pct_diesel: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    pct_electric: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="0"
    )
    pct_hybrid: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="0"
    )
    currency: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="MAD"
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
