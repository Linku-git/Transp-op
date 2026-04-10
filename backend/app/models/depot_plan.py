from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DepotPlan(BaseModel):
    """Depot electrification plan with layout and cost breakdown."""

    __tablename__ = "depot_plan"
    __table_args__ = (
        Index("ix_depot_plan_tenant_id", "tenant_id"),
        Index("ix_depot_plan_site_id", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    total_area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    charging_area_m2: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    parking_area_m2: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    maintenance_area_m2: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")

    charger_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    charger_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="dc_50kw")
    parking_bays: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    fleet_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    total_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    cost_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default="MAD")
