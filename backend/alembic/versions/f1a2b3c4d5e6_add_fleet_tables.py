"""add_fleet_tables

Adds matricule/circulation_date/prestataire to vehicle,
and creates km_consommation, point_arret, configuration_transport tables.

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-04-02 22:30:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------------------
    # 1. Extend vehicle table
    # ---------------------------------------------------------------------------
    op.add_column("vehicle", sa.Column("matricule", sa.String(length=30), nullable=True))
    op.add_column("vehicle", sa.Column("circulation_date", sa.Date(), nullable=True))
    op.add_column("vehicle", sa.Column("prestataire", sa.String(length=100), nullable=True))

    # ---------------------------------------------------------------------------
    # 2. km_consommation — aggregate stats by provider × vehicle-type
    # ---------------------------------------------------------------------------
    op.create_table(
        "km_consommation",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("prestataire", sa.String(100), nullable=False),
        sa.Column("vehicle_type", sa.String(50), nullable=False),
        sa.Column("vehicle_count_peak", sa.Integer(), nullable=True),
        sa.Column("km_avg", sa.Numeric(10, 2), nullable=True),
        sa.Column("km_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("km_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("seat_count", sa.Integer(), nullable=True),
        sa.Column("fuel_consumption_l100km", sa.Numeric(6, 2), nullable=True),
        sa.Column("monthly_cost_per_vehicle_mad", sa.Numeric(12, 2), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_km_consommation_tenant", "km_consommation", ["tenant_id"])

    # ---------------------------------------------------------------------------
    # 3. point_arret — SOTREG / provider bus stops
    # ---------------------------------------------------------------------------
    op.create_table(
        "point_arret",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("nom", sa.String(200), nullable=False),
        sa.Column("adresse", sa.Text(), nullable=True),
        sa.Column("ville", sa.String(100), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("prestataire", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_point_arret_tenant", "point_arret", ["tenant_id"])
    op.create_index("ix_point_arret_site", "point_arret", ["site_id"])

    # ---------------------------------------------------------------------------
    # 4. configuration_transport — line/vehicle/stop assignments
    # ---------------------------------------------------------------------------
    op.create_table(
        "configuration_transport",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("ligne", sa.String(100), nullable=False),
        sa.Column("prestataire", sa.String(100), nullable=False),
        sa.Column("vehicle_type", sa.String(50), nullable=True),
        sa.Column("vehicle_count", sa.Integer(), nullable=True),
        sa.Column("shift", sa.String(20), nullable=True),
        sa.Column("point_depart_id", UUID(as_uuid=True), sa.ForeignKey("point_arret.id"), nullable=True),
        sa.Column("point_arrivee_id", UUID(as_uuid=True), sa.ForeignKey("point_arret.id"), nullable=True),
        sa.Column("circuit", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_configuration_transport_tenant", "configuration_transport", ["tenant_id"])
    op.create_index("ix_configuration_transport_site", "configuration_transport", ["site_id"])


def downgrade() -> None:
    op.drop_table("configuration_transport")
    op.drop_table("point_arret")
    op.drop_table("km_consommation")
    op.drop_column("vehicle", "prestataire")
    op.drop_column("vehicle", "circulation_date")
    op.drop_column("vehicle", "matricule")
