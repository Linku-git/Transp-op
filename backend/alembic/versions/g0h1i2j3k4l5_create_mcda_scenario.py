"""create mcda_scenario table
Revision ID: g0h1i2j3k4l5
Revises: f9g0h1i2j3k4
Create Date: 2026-04-10
"""
from __future__ import annotations
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "g0h1i2j3k4l5"
down_revision: Union[str, None] = "f9g0h1i2j3k4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "mcda_scenario",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("alternatives", JSONB, nullable=True),
        sa.Column("weights", JSONB, nullable=True),
        sa.Column("results", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_mcda_scenario_tenant_id", "mcda_scenario", ["tenant_id"])

def downgrade() -> None:
    op.drop_index("ix_mcda_scenario_tenant_id")
    op.drop_table("mcda_scenario")
