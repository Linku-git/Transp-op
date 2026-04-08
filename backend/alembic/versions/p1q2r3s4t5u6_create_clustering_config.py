"""create clustering_config table

Revision ID: p1q2r3s4t5u6
Revises: o0p1q2r3s4t5
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "p1q2r3s4t5u6"
down_revision = "o0p1q2r3s4t5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clustering_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=False),
        sa.Column("geo_weight", sa.Float(), nullable=False, server_default="0.45"),
        sa.Column("shift_weight", sa.Float(), nullable=False, server_default="0.30"),
        sa.Column("security_weight", sa.Float(), nullable=False, server_default="0.25"),
        sa.Column("night_min_group_size", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("night_min_lighting_score", sa.Float(), nullable=False, server_default="0.4"),
        sa.Column("avoid_critical_at_night", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("priority_vehicle_night", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "site_id", name="uq_clustering_config_tenant_site"),
    )
    op.create_index("ix_clustering_config_site_id", "clustering_config", ["site_id"])


def downgrade() -> None:
    op.drop_table("clustering_config")
