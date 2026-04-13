from __future__ import annotations

import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Ligne(BaseModel):
    """Transport line with CDC formula km_annual = D x R x J."""

    __tablename__ = "ligne"
    __table_args__ = (
        Index("ix_ligne_tenant_id", "tenant_id"),
        Index("ix_ligne_site_id", "site_id"),
        Index("ix_ligne_origin_geom", "origin_geom", postgresql_using="gist"),
        Index("ix_ligne_dest_geom", "dest_geom", postgresql_using="gist"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )

    # Origin / destination coordinates
    origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    origin_lng: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lng: Mapped[float] = mapped_column(Float, nullable=False)
    origin_geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    dest_geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    # CDC formula components: km_annual = D x R x J
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    rotations_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    operating_days_per_year: Mapped[int] = mapped_column(Integer, nullable=False)
    km_annual: Mapped[float] = mapped_column(Float, nullable=False)

    # Vehicle & service configuration
    vehicle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    motorization: Mapped[str | None] = mapped_column(String(30), nullable=True)
    passenger_count_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    service_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Terrain & status
    pente_moyenne_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )

    # Relationships
    site: Mapped["Site | None"] = relationship("Site", lazy="selectin")
