from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Scenario(BaseModel):
    """A scenario simulation estimating transport metrics under specific conditions."""

    __tablename__ = "scenario"
    __table_args__ = (
        Index("idx_scenario_tenant", "tenant_id"),
        Index("idx_scenario_site", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    baseline_optimization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("optimization.id"), nullable=True
    )
    condition_type: Mapped[str] = mapped_column(
        String(30), server_default="normal", nullable=False
    )
    demand_multiplier: Mapped[float] = mapped_column(
        Float, server_default="1.0", nullable=False
    )
    custom_params: Mapped[dict] = mapped_column(
        JSONB, server_default="{}", nullable=False
    )
    estimated_metrics: Mapped[dict] = mapped_column(
        JSONB, server_default="{}", nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    site: Mapped["Site"] = relationship("Site", lazy="selectin")
    baseline_optimization: Mapped["Optimization | None"] = relationship(
        "Optimization", lazy="selectin"
    )
