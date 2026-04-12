"""Create driver_profile table for risk scoring.

Revision ID: t3u4v5w6x7y8
Revises: s2t3u4v5w6x7
Create Date: 2026-04-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t3u4v5w6x7y8"
down_revision = "s2t3u4v5w6x7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "driver_profile",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("licence_type", sa.String(20), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("total_km_driven", sa.Float(), nullable=False, server_default="0"),
        sa.Column("risk_score", sa.Float(), nullable=False, server_default="100"),
        sa.Column("risk_category", sa.String(20), nullable=False, server_default="low"),
        sa.Column("last_scored_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_driver_profile_tenant", "driver_profile", ["tenant_id"])
    op.create_index("ix_driver_profile_driver", "driver_profile", ["driver_id"])
    op.create_index("ix_driver_profile_risk", "driver_profile", ["tenant_id", "risk_category"])


def downgrade() -> None:
    op.drop_table("driver_profile")
