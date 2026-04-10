"""create depot_plan table

Revision ID: b5c6d7e8f9g0
Revises: a4b5c6d7e8f9
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "b5c6d7e8f9g0"
down_revision: Union[str, None] = "a4b5c6d7e8f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "depot_plan",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("total_area_m2", sa.Float(), nullable=False),
        sa.Column("charging_area_m2", sa.Float(), nullable=False, server_default="0"),
        sa.Column("parking_area_m2", sa.Float(), nullable=False, server_default="0"),
        sa.Column("maintenance_area_m2", sa.Float(), nullable=False, server_default="0"),
        sa.Column("charger_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("charger_type", sa.String(30), nullable=False, server_default="dc_50kw"),
        sa.Column("parking_bays", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fleet_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cost_breakdown", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="MAD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_depot_plan_tenant_id", "depot_plan", ["tenant_id"])
    op.create_index("ix_depot_plan_site_id", "depot_plan", ["site_id"])


def downgrade() -> None:
    op.drop_index("ix_depot_plan_site_id")
    op.drop_index("ix_depot_plan_tenant_id")
    op.drop_table("depot_plan")
