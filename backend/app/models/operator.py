from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Operator(BaseModel):
    __tablename__ = "operator"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    operator_type: Mapped[str] = mapped_column(String(20), nullable=False)
    api_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    contacts: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("ix_operator_tenant_id", "tenant_id"),
        Index("ix_operator_type", "operator_type"),
    )
