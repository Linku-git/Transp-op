"""create irve_infrastructure table

Revision ID: z3a4b5c6d7e8
Revises: y2z3a4b5c6d7
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "z3a4b5c6d7e8"
down_revision: Union[str, None] = "y2z3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "irve_infrastructure",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("charger_type", sa.String(30), nullable=False, server_default="dc_50kw"),
        sa.Column("charger_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("power_per_charger_kw", sa.Float(), nullable=False),
        sa.Column("total_installed_power_kw", sa.Float(), nullable=False),
        sa.Column("hardware_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("installation_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("transformer_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("grid_connection_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_capex_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("annual_electricity_cost_mad", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fleet_size", sa.Integer(), nullable=True),
        sa.Column("daily_km_per_vehicle", sa.Float(), nullable=True),
        sa.Column("battery_capacity_kwh", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="MAD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_irve_infrastructure_tenant_id", "irve_infrastructure", ["tenant_id"])
    op.create_index("ix_irve_infrastructure_site_id", "irve_infrastructure", ["site_id"])


def downgrade() -> None:
    op.drop_index("ix_irve_infrastructure_site_id")
    op.drop_index("ix_irve_infrastructure_tenant_id")
    op.drop_table("irve_infrastructure")
