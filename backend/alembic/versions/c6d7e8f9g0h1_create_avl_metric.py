"""create avl_metric table

Revision ID: c6d7e8f9g0h1
Revises: b5c6d7e8f9g0
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


revision: str = "c6d7e8f9g0h1"
down_revision: Union[str, None] = "b5c6d7e8f9g0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "avl_metric",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("ligne_id", UUID(as_uuid=True), sa.ForeignKey("ligne.id"), nullable=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), nullable=True),
        sa.Column("metric_type", sa.String(30), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("period", sa.String(20), nullable=False, server_default="daily"),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("meets_target", sa.Boolean(), nullable=True),
        sa.Column("details", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_avl_metric_tenant_id", "avl_metric", ["tenant_id"])
    op.create_index("ix_avl_metric_ligne_id", "avl_metric", ["ligne_id"])
    op.create_index("ix_avl_metric_vehicle_id", "avl_metric", ["vehicle_id"])
    op.create_index("ix_avl_metric_metric_type", "avl_metric", ["metric_type"])
    op.create_index("ix_avl_metric_date", "avl_metric", ["metric_date"])


def downgrade() -> None:
    op.drop_index("ix_avl_metric_date")
    op.drop_index("ix_avl_metric_metric_type")
    op.drop_index("ix_avl_metric_vehicle_id")
    op.drop_index("ix_avl_metric_ligne_id")
    op.drop_index("ix_avl_metric_tenant_id")
    op.drop_table("avl_metric")
