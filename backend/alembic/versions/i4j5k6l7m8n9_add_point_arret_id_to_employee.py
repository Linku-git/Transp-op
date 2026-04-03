"""add point_arret_id to employee

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-04-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "i4j5k6l7m8n9"
down_revision = "h3i4j5k6l7m8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "employee",
        sa.Column(
            "point_arret_id",
            UUID(as_uuid=True),
            sa.ForeignKey("point_arret.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_employee_point_arret_id",
        "employee",
        ["point_arret_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_employee_point_arret_id", table_name="employee")
    op.drop_column("employee", "point_arret_id")
