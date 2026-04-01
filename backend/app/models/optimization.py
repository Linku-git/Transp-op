from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Optimization(BaseModel):
    """An optimization run (clustering, routing, or full pipeline)."""

    __tablename__ = "optimization"
    __table_args__ = (Index("idx_optimization_tenant", "tenant_id"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    condition_type: Mapped[str] = mapped_column(
        String(30), server_default="normal", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending", nullable=False
    )
    params: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    site: Mapped[Site | None] = relationship("Site", lazy="selectin")
    clusters: Mapped[list[Cluster]] = relationship(
        "Cluster", back_populates="optimization", cascade="all, delete-orphan"
    )
    routes: Mapped[list[Route]] = relationship(
        "Route", back_populates="optimization", cascade="all, delete-orphan"
    )


class Cluster(BaseModel):
    """A geographic cluster of employees for transport optimization."""

    __tablename__ = "cluster"
    __table_args__ = (Index("idx_cluster_optimization", "optimization_id"),)

    optimization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("optimization.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    centroid_lat: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_lng: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    employee_count: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    pmr_count: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    security_risk_level: Mapped[str] = mapped_column(
        String(20), server_default="low", nullable=False
    )
    employee_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), server_default="{}", nullable=False
    )

    # Relationships
    optimization: Mapped[Optimization] = relationship(
        "Optimization", back_populates="clusters"
    )
    site: Mapped[Site] = relationship("Site", lazy="selectin")


class Route(BaseModel):
    """An optimized transport route within an optimization run."""

    __tablename__ = "route"
    __table_args__ = (Index("idx_route_optimization", "optimization_id"),)

    optimization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("optimization.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicle.id"), nullable=True
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    ordered_stops: Mapped[dict] = mapped_column(
        JSONB, server_default="[]", nullable=False
    )
    total_distance_km: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    total_time_minutes: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    polyline: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326), nullable=True
    )
    rti_compliance_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    # Relationships
    optimization: Mapped[Optimization] = relationship(
        "Optimization", back_populates="routes"
    )
    vehicle: Mapped[Vehicle | None] = relationship("Vehicle", lazy="selectin")
    site: Mapped[Site] = relationship("Site", lazy="selectin")
