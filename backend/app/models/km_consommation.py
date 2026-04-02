from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Float, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class KmConsommation(BaseModel):
    """Aggregate fuel/km consumption statistics per provider × vehicle-type."""

    __tablename__ = "km_consommation"
    __table_args__ = (Index("ix_km_consommation_tenant", "tenant_id"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    prestataire: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_count_peak: Mapped[int | None] = mapped_column(Integer, nullable=True)
    km_avg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    km_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    km_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_consumption_l100km: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    monthly_cost_per_vehicle_mad: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
