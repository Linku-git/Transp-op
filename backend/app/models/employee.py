from __future__ import annotations

import uuid
from datetime import date

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Employee(BaseModel):
    """Employee with home geolocation, transport preferences, and site assignment."""

    __tablename__ = "employee"
    __table_args__ = (
        UniqueConstraint("tenant_id", "matricule", name="uq_employee_tenant_matricule"),
        Index("ix_employee_tenant_id", "tenant_id"),
        Index("ix_employee_site_id", "site_id"),
        Index("ix_employee_geom", "geom", postgresql_using="gist"),
        Index("ix_employee_active", "active"),
    )

    # Tenant & identification
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    matricule: Mapped[str] = mapped_column(String(50), nullable=False)

    # Personal information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Site & shift
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    shift_time: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Home address & geolocation
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    quartier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    # Preferred pickup point
    preferred_pickup_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_pickup_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_pickup_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Accessibility
    is_pmr: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )

    # Professional info
    function_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Transport preferences
    transport_required: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    current_transport_mode: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    opt_in_company_transport: Mapped[str] = mapped_column(
        String(20), server_default="Non", nullable=False
    )
    has_private_car: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    volunteer_driver: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    carpool_seats: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )

    # Status & SIRH
    active: Mapped[bool] = mapped_column(
        Boolean, server_default="true", nullable=False
    )
    sirh_external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    tenant: Mapped[Tenant] = relationship("Tenant", lazy="selectin")
    site: Mapped[Site] = relationship("Site", lazy="selectin")
