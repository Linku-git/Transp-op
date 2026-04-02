from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Vehicle(BaseModel):
    """Fleet vehicle with capacity, cost, and accessibility attributes."""

    __tablename__ = "vehicle"
    __table_args__ = (
        Index("idx_vehicle_tenant", "tenant_id"),
        Index("idx_vehicle_site", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    matricule: Mapped[str | None] = mapped_column(String(30), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    brand_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    circulation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    owner_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    prestataire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monthly_cost_mad: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    monthly_km: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    condition: Mapped[str] = mapped_column(
        String(20), server_default="Bon", nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    is_pmr_accessible: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    fuel_consumption: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    cost_per_km: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4), nullable=True
    )
    motorization: Mapped[str | None] = mapped_column(String(30), nullable=True)
    length_meters: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    zfe_compliant: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
