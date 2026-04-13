"""create od_matrix table

Revision ID: y2z3a4b5c6d7
Revises: x1y2z3a4b5c6
Create Date: 2026-04-09
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "y2z3a4b5c6d7"
down_revision: Union[str, None] = "x1y2z3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "od_matrix",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("ligne_id", sa.UUID(), nullable=True),
        sa.Column("origin_zone", sa.String(length=255), nullable=False),
        sa.Column("destination_zone", sa.String(length=255), nullable=False),
        sa.Column("flow_estimate", sa.Float(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("gravity_score", sa.Float(), nullable=False),
        sa.Column(
            "beta_used", sa.Float(), server_default="0.08", nullable=False
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(
            ["ligne_id"], ["ligne.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_od_matrix_tenant_id", "od_matrix", ["tenant_id"], unique=False)
    op.create_index("ix_od_matrix_ligne_id", "od_matrix", ["ligne_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_od_matrix_ligne_id", table_name="od_matrix")
    op.drop_index("ix_od_matrix_tenant_id", table_name="od_matrix")
    op.drop_table("od_matrix")
