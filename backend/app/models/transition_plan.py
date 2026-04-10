from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class TransitionPlan(BaseModel):
    """Fleet electrification transition plan."""

    __tablename__ = "transition_plan"
    __table_args__ = (Index("ix_transition_plan_tenant_id", "tenant_id"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_budget_mad: Mapped[float] = mapped_column(Float, nullable=False)
    total_phases: Mapped[int] = mapped_column(Integer, nullable=False, server_default="3")
    fleet_size: Mapped[int] = mapped_column(Integer, nullable=False)
    scenario_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="moderate"
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=False, server_default="MAD")


class TransitionPhase(BaseModel):
    """A single phase within a transition plan."""

    __tablename__ = "transition_phase"
    __table_args__ = (
        Index("ix_transition_phase_plan_id", "plan_id"),
        Index("ix_transition_phase_tenant_id", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("transition_plan.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    technology_wave: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicles_to_convert: Mapped[int] = mapped_column(Integer, nullable=False)
    target_pct_electric: Mapped[float] = mapped_column(Float, nullable=False)
    budget_allocated_mad: Mapped[float] = mapped_column(Float, nullable=False)
    vehicle_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    infrastructure_cost_mad: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="planned"
    )
