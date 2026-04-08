from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ClusteringConfig(BaseModel):
    __tablename__ = "clustering_config"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    geo_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.45)
    shift_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.30)
    security_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    night_min_group_size: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    night_min_lighting_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.4)
    avoid_critical_at_night: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    priority_vehicle_night: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "site_id", name="uq_clustering_config_tenant_site"),
        Index("ix_clustering_config_site_id", "site_id"),
    )
