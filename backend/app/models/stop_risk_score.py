from __future__ import annotations

import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class StopRiskScore(BaseModel):
    __tablename__ = "stop_risk_score"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=True
    )
    stop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    # Individual risk factor scores (0.0 - 1.0)
    isolation_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    lighting_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    tc_frequency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    night_risk_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    employee_perception_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Computed fields
    composite_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_critical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("ix_stop_risk_score_tenant_id", "tenant_id"),
        Index("ix_stop_risk_score_site_id", "site_id"),
        Index("ix_stop_risk_score_geom", "geom", postgresql_using="gist"),
        Index("ix_stop_risk_score_critical", "is_critical"),
    )
