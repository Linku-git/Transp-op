"""create rti_config table

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "m8n9o0p1q2r3"
down_revision = "l7m8n9o0p1q2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rti_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("site.id"), nullable=False),
        sa.Column("max_wait_seconds", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("compliance_target_pct", sa.Float(), nullable=False, server_default="95.0"),
        sa.Column("buffer_vehicle_count", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("night_mode_start", sa.Time(), nullable=True),
        sa.Column("night_mode_end", sa.Time(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "site_id", name="uq_rti_config_tenant_site"),
    )
    op.create_index("ix_rti_config_site_id", "rti_config", ["site_id"])


def downgrade() -> None:
    op.drop_table("rti_config")
