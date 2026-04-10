from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel

class MCDAScenario(BaseModel):
    __tablename__ = "mcda_scenario"
    __table_args__ = (Index("ix_mcda_scenario_tenant_id", "tenant_id"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alternatives: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    weights: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
