from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PointArret(BaseModel):
    """Bus / transport stop (SOTREG, STCR, CTM…)."""

    __tablename__ = "point_arret"
    __table_args__ = (
        Index("ix_point_arret_tenant", "tenant_id"),
        Index("ix_point_arret_site", "site_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    prestataire: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
