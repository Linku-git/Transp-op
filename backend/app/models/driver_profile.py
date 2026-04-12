"""DriverProfile model for ML-based driver risk scoring.

Session 120 — CDC SOTREG v5.0 Module M8/ML.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DriverProfile(BaseModel):
    """Driver risk profile with telematics-based scoring."""

    __tablename__ = "driver_profile"
    __table_args__ = (
        Index("ix_driver_profile_tenant", "tenant_id"),
        Index("ix_driver_profile_driver", "driver_id"),
        Index("ix_driver_profile_risk", "tenant_id", "risk_category"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False,
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False,
    )
    licence_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_km_driven: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    risk_category: Mapped[str] = mapped_column(
        String(20), default="low", nullable=False,
    )  # low, medium, high, critical
    last_scored_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
