from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class IRVEInfrastructure(BaseModel):
    """IRVE (Infrastructure de Recharge pour Vehicules Electriques) record."""

    __tablename__ = "irve_infrastructure"
    __table_args__ = (
        Index("ix_irve_infrastructure_tenant_id", "tenant_id"),
        Index("ix_irve_infrastructure_site_id", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )

    charger_type: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="dc_50kw"
    )
    charger_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    power_per_charger_kw: Mapped[float] = mapped_column(Float, nullable=False)
    total_installed_power_kw: Mapped[float] = mapped_column(Float, nullable=False)

    hardware_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    installation_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    transformer_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    grid_connection_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    total_capex_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    annual_electricity_cost_mad: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="0"
    )

    fleet_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_km_per_vehicle: Mapped[float | None] = mapped_column(Float, nullable=True)
    battery_capacity_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default="MAD")
