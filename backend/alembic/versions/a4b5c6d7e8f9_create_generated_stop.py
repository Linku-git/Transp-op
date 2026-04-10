"""create generated_stop table

Revision ID: a4b5c6d7e8f9
Revises: z3a4b5c6d7e8
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID


revision: str = "a4b5c6d7e8f9"
down_revision: Union[str, None] = "z3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "generated_stop",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("ligne_id", UUID(as_uuid=True), sa.ForeignKey("ligne.id"), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("catchment_radius_m", sa.Float(), nullable=False, server_default="500"),
        sa.Column("demand_passengers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("berth_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("capacity_buses_per_hour", sa.Float(), nullable=True),
        sa.Column("capacity_los", sa.String(1), nullable=True),
        sa.Column("avg_wait_seconds", sa.Float(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="dbscan"),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_generated_stop_tenant_id", "generated_stop", ["tenant_id"])
    op.create_index("ix_generated_stop_site_id", "generated_stop", ["site_id"])
    op.create_index("ix_generated_stop_geom", "generated_stop", ["geom"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_generated_stop_geom")
    op.drop_index("ix_generated_stop_site_id")
    op.drop_index("ix_generated_stop_tenant_id")
    op.drop_table("generated_stop")
