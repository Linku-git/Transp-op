"""create ligne and fleet_context tables

Revision ID: x1y2z3a4b5c6
Revises: w8x9y0z1a2b3
Create Date: 2026-04-09
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


revision: str = "x1y2z3a4b5c6"
down_revision: Union[str, None] = "w8x9y0z1a2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ligne",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("site_id", sa.UUID(), nullable=True),
        sa.Column("origin_lat", sa.Float(), nullable=False),
        sa.Column("origin_lng", sa.Float(), nullable=False),
        sa.Column("dest_lat", sa.Float(), nullable=False),
        sa.Column("dest_lng", sa.Float(), nullable=False),
        sa.Column(
            "origin_geom",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column(
            "dest_geom",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("rotations_per_day", sa.Integer(), nullable=False),
        sa.Column("operating_days_per_year", sa.Integer(), nullable=False),
        sa.Column("km_annual", sa.Float(), nullable=False),
        sa.Column("vehicle_type", sa.String(length=50), nullable=True),
        sa.Column("motorization", sa.String(length=30), nullable=True),
        sa.Column("passenger_count_avg", sa.Integer(), nullable=True),
        sa.Column("shift_type", sa.String(length=50), nullable=True),
        sa.Column("service_type", sa.String(length=20), nullable=False),
        sa.Column("pente_moyenne_pct", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
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
        sa.ForeignKeyConstraint(["site_id"], ["site.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_ligne_tenant_id", "ligne", ["tenant_id"], unique=False)
    op.create_index("ix_ligne_site_id", "ligne", ["site_id"], unique=False)
    op.create_index(
        "ix_ligne_origin_geom",
        "ligne",
        ["origin_geom"],
        unique=False,
        postgresql_using="gist",
    )
    op.create_index(
        "ix_ligne_dest_geom",
        "ligne",
        ["dest_geom"],
        unique=False,
        postgresql_using="gist",
    )

    op.create_table(
        "fleet_context",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("total_vehicles", sa.Integer(), nullable=False),
        sa.Column("total_km_annual", sa.Float(), nullable=False),
        sa.Column("total_tco2_annual", sa.Float(), nullable=False),
        sa.Column("average_age_years", sa.Float(), nullable=True),
        sa.Column("pct_diesel", sa.Float(), server_default="0", nullable=False),
        sa.Column("pct_electric", sa.Float(), server_default="0", nullable=False),
        sa.Column("pct_hybrid", sa.Float(), server_default="0", nullable=False),
        sa.Column(
            "currency", sa.String(length=10), server_default="MAD", nullable=False
        ),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_fleet_context_tenant_id", "fleet_context", ["tenant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_fleet_context_tenant_id", table_name="fleet_context")
    op.drop_table("fleet_context")
    op.drop_index(
        "ix_ligne_dest_geom", table_name="ligne", postgresql_using="gist"
    )
    op.drop_index(
        "ix_ligne_origin_geom", table_name="ligne", postgresql_using="gist"
    )
    op.drop_index("ix_ligne_site_id", table_name="ligne")
    op.drop_index("ix_ligne_tenant_id", table_name="ligne")
    op.drop_table("ligne")
