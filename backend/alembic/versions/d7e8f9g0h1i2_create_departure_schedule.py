"""create departure_schedule table

Revision ID: d7e8f9g0h1i2
Revises: c6d7e8f9g0h1
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


revision: str = "d7e8f9g0h1i2"
down_revision: Union[str, None] = "c6d7e8f9g0h1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departure_schedule",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("ligne_id", UUID(as_uuid=True), sa.ForeignKey("ligne.id"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), nullable=True),
        sa.Column("scheduled_departure", sa.DateTime(timezone=True), nullable=False),
        sa.Column("optimized_departure", sa.DateTime(timezone=True), nullable=False),
        sa.Column("offset_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("is_applied", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("optimization_run_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_departure_schedule_tenant_id", "departure_schedule", ["tenant_id"])
    op.create_index("ix_departure_schedule_ligne_id", "departure_schedule", ["ligne_id"])
    op.create_index("ix_departure_schedule_date", "departure_schedule", ["schedule_date"])


def downgrade() -> None:
    op.drop_index("ix_departure_schedule_date")
    op.drop_index("ix_departure_schedule_ligne_id")
    op.drop_index("ix_departure_schedule_tenant_id")
    op.drop_table("departure_schedule")
