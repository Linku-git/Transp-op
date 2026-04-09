from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SyncConflict(BaseModel):
    __tablename__ = "sync_conflict"

    sync_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sync_log.id"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employee.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    sirh_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unresolved"
    )

    __table_args__ = (
        Index("ix_sync_conflict_sync_log_id", "sync_log_id"),
        Index("ix_sync_conflict_tenant_id", "tenant_id"),
        Index("ix_sync_conflict_employee_id", "employee_id"),
        Index("ix_sync_conflict_resolution", "resolution"),
    )
