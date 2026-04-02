"""add horaire_travail and update point_arret

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-04-02

"""
from __future__ import annotations

import uuid
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "c2d3e4f5a6b7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- horaire_travail table --------------------------------------------------
    op.create_table(
        "horaire_travail",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        # Shift type e.g. "Journalier", "2x8", "3x8", "VSD", "Nuit"
        sa.Column("type_horaire", sa.String(100), nullable=False),
        # Premier Horaire
        sa.Column("depart_h1", sa.String(10), nullable=True),   # "06:00"
        sa.Column("retour_h1", sa.String(10), nullable=True),   # "14:00"
        # Deuxième Horaire
        sa.Column("depart_h2", sa.String(10), nullable=True),   # "14:00"
        sa.Column("retour_h2", sa.String(10), nullable=True),   # "22:00"
        sa.Column("observations", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_horaire_travail_tenant", "horaire_travail", ["tenant_id"])
    op.create_index("ix_horaire_travail_site", "horaire_travail", ["site_id"])

    # -- point_arret: add correspondance_tb column ----------------------------
    op.add_column("point_arret", sa.Column("correspondance_tb", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("point_arret", "correspondance_tb")
    op.drop_index("ix_horaire_travail_site", table_name="horaire_travail")
    op.drop_index("ix_horaire_travail_tenant", table_name="horaire_travail")
    op.drop_table("horaire_travail")
