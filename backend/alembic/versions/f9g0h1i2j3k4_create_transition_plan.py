"""create transition_plan and transition_phase tables

Revision ID: f9g0h1i2j3k4
Revises: e8f9g0h1i2j3
Create Date: 2026-04-10
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "f9g0h1i2j3k4"
down_revision: Union[str, None] = "e8f9g0h1i2j3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "transition_plan",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("total_budget_mad", sa.Float(), nullable=False),
        sa.Column("total_phases", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("fleet_size", sa.Integer(), nullable=False),
        sa.Column("scenario_type", sa.String(20), nullable=False, server_default="moderate"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="MAD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_transition_plan_tenant_id", "transition_plan", ["tenant_id"])

    op.create_table(
        "transition_phase",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("transition_plan.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("technology_wave", sa.String(20), nullable=False),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=False),
        sa.Column("vehicles_to_convert", sa.Integer(), nullable=False),
        sa.Column("target_pct_electric", sa.Float(), nullable=False),
        sa.Column("budget_allocated_mad", sa.Float(), nullable=False),
        sa.Column("vehicle_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("infrastructure_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_transition_phase_plan_id", "transition_phase", ["plan_id"])
    op.create_index("ix_transition_phase_tenant_id", "transition_phase", ["tenant_id"])

def downgrade() -> None:
    op.drop_index("ix_transition_phase_tenant_id")
    op.drop_index("ix_transition_phase_plan_id")
    op.drop_table("transition_phase")
    op.drop_index("ix_transition_plan_tenant_id")
    op.drop_table("transition_plan")
