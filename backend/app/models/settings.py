from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class OptimizationSettings(BaseModel):
    """Tenant-scoped settings for the optimization engine."""

    __tablename__ = "optimization_settings"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_optimization_settings_tenant"),
        Index("idx_optimization_settings_tenant", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    meeting_radius_meters: Mapped[float] = mapped_column(
        Float, server_default="500.0", nullable=False
    )
    max_walking_distance_meters: Mapped[float] = mapped_column(
        Float, server_default="800.0", nullable=False
    )
    max_route_duration_seconds: Mapped[int] = mapped_column(
        Integer, server_default="5400", nullable=False
    )
    fuel_cost_per_liter: Mapped[float] = mapped_column(
        Float, server_default="12.0", nullable=False
    )
    fuel_consumption_l_per_100km: Mapped[float] = mapped_column(
        Float, server_default="15.0", nullable=False
    )
    co2_kg_per_liter: Mapped[float] = mapped_column(
        Float, server_default="2.68", nullable=False
    )
    rti_threshold_minutes: Mapped[int] = mapped_column(
        Integer, server_default="15", nullable=False
    )
    night_mode_start: Mapped[str] = mapped_column(
        String(5), server_default="22:00", nullable=False
    )
    night_mode_end: Mapped[str] = mapped_column(
        String(5), server_default="06:00", nullable=False
    )
    min_night_group_size: Mapped[int] = mapped_column(
        Integer, server_default="3", nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")


class ConstraintParam(BaseModel):
    """Configurable constraint parameter for the optimization engine."""

    __tablename__ = "constraint_param"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_constraint_param_tenant_key"),
        Index("idx_constraint_param_tenant", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), server_default="general", nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", lazy="selectin")
