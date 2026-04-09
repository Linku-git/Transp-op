from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SIRHConnection(BaseModel):
    __tablename__ = "sirh_connection"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sync_frequency: Mapped[str] = mapped_column(
        String(20), nullable=False, default="daily"
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    conflict_strategy: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sirh_wins"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    __table_args__ = (
        Index("ix_sirh_connection_tenant_id", "tenant_id"),
        Index("ix_sirh_connection_provider", "provider"),
        Index("ix_sirh_connection_status", "status"),
    )
