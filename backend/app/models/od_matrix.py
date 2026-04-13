from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ODMatrix(BaseModel):
    """Origin-Destination matrix entry computed via gravity model."""

    __tablename__ = "od_matrix"
    __table_args__ = (
        Index("ix_od_matrix_tenant_id", "tenant_id"),
        Index("ix_od_matrix_ligne_id", "ligne_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    ligne_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ligne.id", ondelete="CASCADE"), nullable=True
    )
    origin_zone: Mapped[str] = mapped_column(String(255), nullable=False)
    destination_zone: Mapped[str] = mapped_column(String(255), nullable=False)
    flow_estimate: Mapped[float] = mapped_column(Float, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    gravity_score: Mapped[float] = mapped_column(Float, nullable=False)
    beta_used: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.08")
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    ligne: Mapped["Ligne | None"] = relationship("Ligne", lazy="selectin")
