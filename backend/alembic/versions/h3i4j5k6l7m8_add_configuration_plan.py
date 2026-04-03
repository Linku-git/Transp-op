"""add configuration_plan and redesign configuration_transport

Revision ID: h3i4j5k6l7m8
Revises: d1e2f3a4b5c6, g2h3i4j5k6l7
Create Date: 2026-04-03
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "h3i4j5k6l7m8"
down_revision = ("d1e2f3a4b5c6", "g2h3i4j5k6l7")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Create configuration_plan ──────────────────────────────────────
    op.create_table(
        "configuration_plan",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True),
                  sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_current", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_configuration_plan_tenant", "configuration_plan", ["tenant_id"])

    # ── 2. Drop old columns from configuration_transport ──────────────────
    with op.batch_alter_table("configuration_transport") as batch_op:
        batch_op.drop_column("ligne")
        batch_op.drop_column("vehicle_type")
        batch_op.drop_column("vehicle_count")
        batch_op.drop_column("point_depart_id")
        batch_op.drop_column("point_arrivee_id")
        batch_op.drop_column("circuit")
        batch_op.drop_column("observations")

    # ── 3. Add new columns to configuration_transport ─────────────────────
    op.add_column("configuration_transport",
        sa.Column("plan_id", UUID(as_uuid=True),
                  sa.ForeignKey("configuration_plan.id", ondelete="CASCADE"),
                  nullable=True))
    op.add_column("configuration_transport",
        sa.Column("conducteur", sa.String(200), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("poste", sa.String(20), nullable=True))
    # prestataire column already exists — keep it
    op.add_column("configuration_transport",
        sa.Column("mle_vehicule", sa.String(50), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("type_vehicule", sa.String(50), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("type_moteur", sa.String(50), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("secteur", sa.String(100), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("entite", sa.String(200), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("aller_retour", sa.String(10), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("heure_depart", sa.String(10), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("point_depart", sa.String(200), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("point_arrivee", sa.String(200), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("heure_arrivee", sa.String(10), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("arrets_circuit", sa.String(500), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("duree_trajet_min", sa.Integer(), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("km", sa.Numeric(8, 2), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("rot", sa.Numeric(6, 2), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("t_km", sa.Numeric(8, 2), nullable=True))

    # ── 4. Now make plan_id NOT NULL (table is empty at this point) ────────
    op.alter_column("configuration_transport", "plan_id", nullable=False)

    # ── 5. Rename old shift column — it already exists, keep it ───────────
    # shift column is kept as-is, just changing length
    op.alter_column("configuration_transport", "shift",
                    existing_type=sa.String(20),
                    type_=sa.String(10),
                    existing_nullable=True)

    # ── 6. Indexes ─────────────────────────────────────────────────────────
    op.create_index("ix_configuration_transport_plan", "configuration_transport", ["plan_id"])
    op.create_index("ix_configuration_transport_poste", "configuration_transport", ["poste"])
    # drop old index that no longer matches
    op.drop_index("ix_configuration_transport_site", table_name="configuration_transport")


def downgrade() -> None:
    op.drop_index("ix_configuration_transport_poste", table_name="configuration_transport")
    op.drop_index("ix_configuration_transport_plan", table_name="configuration_transport")

    for col in ["plan_id", "conducteur", "poste", "prestataire", "mle_vehicule",
                "type_vehicule", "type_moteur", "secteur", "entite", "aller_retour",
                "heure_depart", "point_depart", "point_arrivee", "heure_arrivee",
                "arrets_circuit", "duree_trajet_min", "km", "rot", "t_km"]:
        op.drop_column("configuration_transport", col)

    op.add_column("configuration_transport",
        sa.Column("ligne", sa.String(100), nullable=False, server_default=""))
    op.add_column("configuration_transport",
        sa.Column("vehicle_type", sa.String(50), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("vehicle_count", sa.Integer(), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("point_depart_id", UUID(as_uuid=True), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("point_arrivee_id", UUID(as_uuid=True), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("circuit", sa.String(200), nullable=True))
    op.add_column("configuration_transport",
        sa.Column("observations", sa.Text(), nullable=True))

    op.create_index("ix_configuration_transport_site", "configuration_transport", ["site_id"])

    op.drop_index("ix_configuration_plan_tenant", table_name="configuration_plan")
    op.drop_table("configuration_plan")
