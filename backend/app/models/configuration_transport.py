from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ConfigurationTransport(BaseModel):
    """Transport line ↔ vehicle type ↔ stop assignment."""

    __tablename__ = "configuration_transport"
    __table_args__ = (
        Index("ix_configuration_transport_tenant", "tenant_id"),
        Index("ix_configuration_transport_site", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    ligne: Mapped[str] = mapped_column(String(100), nullable=False)
    prestataire: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vehicle_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift: Mapped[str | None] = mapped_column(String(20), nullable=True)
    point_depart_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("point_arret.id"), nullable=True
    )
    point_arrivee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("point_arret.id"), nullable=True
    )
    circuit: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
    point_depart: Mapped[PointArret | None] = relationship(
        "PointArret", foreign_keys=[point_depart_id], lazy="selectin"
    )
    point_arrivee: Mapped[PointArret | None] = relationship(
        "PointArret", foreign_keys=[point_arrivee_id], lazy="selectin"
    )
