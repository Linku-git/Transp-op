from __future__ import annotations

import uuid
from datetime import time

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Site(BaseModel):
    """Physical company site with geolocation and shift configuration."""

    __tablename__ = "site"
    __table_args__ = (
        Index("ix_site_tenant_id", "tenant_id"),
        Index("ix_site_geom", "geom", postgresql_using="gist"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    # Shift configuration
    num_shifts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    # Equipe 1 — type + quatre horaires (depart_h1/retour_h1 stored in legacy entry/exit)
    shift_1_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shift_1_entry: Mapped[time | None] = mapped_column(Time, nullable=True)   # depart_h1
    shift_1_exit: Mapped[time | None] = mapped_column(Time, nullable=True)    # retour_h1
    shift_1_depart_h2: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_1_retour_h2: Mapped[time | None] = mapped_column(Time, nullable=True)
    # Equipe 2
    shift_2_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shift_2_entry: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_2_exit: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_2_depart_h2: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_2_retour_h2: Mapped[time | None] = mapped_column(Time, nullable=True)
    # Equipe 3
    shift_3_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shift_3_entry: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_3_exit: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_3_depart_h2: Mapped[time | None] = mapped_column(Time, nullable=True)
    shift_3_retour_h2: Mapped[time | None] = mapped_column(Time, nullable=True)

    # Working schedule
    working_days: Mapped[str | None] = mapped_column(
        String(100), server_default="Lundi-Vendredi", nullable=True
    )
    days_per_week: Mapped[int | None] = mapped_column(
        Integer, server_default="5", nullable=True
    )

    # Contact & logistics
    contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    access_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    parking_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Constraints & metadata
    zfe_zone: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    security_profile: Mapped[str] = mapped_column(
        String(20), server_default="normal", nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        String(50), server_default="Europe/Paris", nullable=False
    )
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", lazy="selectin")
