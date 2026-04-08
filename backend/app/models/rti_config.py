from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class RTIConfig(BaseModel):
    __tablename__ = "rti_config"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("site.id"), nullable=False
    )
    max_wait_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=90
    )
    compliance_target_pct: Mapped[float] = mapped_column(
        Float, nullable=False, default=95.0
    )
    buffer_vehicle_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2
    )
    night_mode_start: Mapped[object | None] = mapped_column(
        Time, nullable=True
    )
    night_mode_end: Mapped[object | None] = mapped_column(
        Time, nullable=True
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "site_id", name="uq_rti_config_tenant_site"),
        Index("ix_rti_config_site_id", "site_id"),
    )
