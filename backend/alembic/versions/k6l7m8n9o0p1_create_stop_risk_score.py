"""create stop_risk_score table

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

revision = "k6l7m8n9o0p1"
down_revision = "j5k6l7m8n9o0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stop_risk_score",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=True),
        sa.Column("stop_name", sa.String(255), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("isolation_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("lighting_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("tc_frequency_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("night_risk_multiplier", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("employee_perception_avg", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("composite_risk_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stop_risk_score_tenant_id", "stop_risk_score", ["tenant_id"])
    op.create_index("ix_stop_risk_score_site_id", "stop_risk_score", ["site_id"])
    op.create_index("ix_stop_risk_score_geom", "stop_risk_score", ["geom"], postgresql_using="gist")
    op.create_index("ix_stop_risk_score_critical", "stop_risk_score", ["is_critical"])


def downgrade() -> None:
    op.drop_table("stop_risk_score")
