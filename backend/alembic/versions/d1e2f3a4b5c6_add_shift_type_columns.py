"""add shift type and h2 columns to site

Revision ID: d1e2f3a4b5c6
Revises: c2d3e4f5a6b7
Create Date: 2026-04-02
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "d1e2f3a4b5c6"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for i in (1, 2, 3):
        op.add_column("site", sa.Column(f"shift_{i}_type", sa.String(50), nullable=True))
        op.add_column("site", sa.Column(f"shift_{i}_depart_h2", sa.Time(), nullable=True))
        op.add_column("site", sa.Column(f"shift_{i}_retour_h2", sa.Time(), nullable=True))


def downgrade() -> None:
    for i in (1, 2, 3):
        op.drop_column("site", f"shift_{i}_type")
        op.drop_column("site", f"shift_{i}_depart_h2")
        op.drop_column("site", f"shift_{i}_retour_h2")
