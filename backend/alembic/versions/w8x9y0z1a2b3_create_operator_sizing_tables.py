"""create operator and sizing_plan_export tables

Revision ID: w8x9y0z1a2b3
Revises: v7w8x9y0z1a2
Create Date: 2026-04-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "w8x9y0z1a2b3"
down_revision = "v7w8x9y0z1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operator",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("operator_type", sa.String(20), nullable=False),
        sa.Column("api_config", postgresql.JSONB, nullable=True),
        sa.Column("contacts", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operator_tenant_id", "operator", ["tenant_id"])
    op.create_index("ix_operator_type", "operator", ["operator_type"])

    op.create_table(
        "sizing_plan_export",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("optimization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("operator.id"), nullable=True),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("file_url", sa.String(1000), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("content_summary", postgresql.JSONB, nullable=True),
        sa.Column("changes_from_previous", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sizing_plan_export_tenant_id", "sizing_plan_export", ["tenant_id"])
    op.create_index("ix_sizing_plan_export_operator_id", "sizing_plan_export", ["operator_id"])
    op.create_index("ix_sizing_plan_export_status", "sizing_plan_export", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sizing_plan_export_status", table_name="sizing_plan_export")
    op.drop_index("ix_sizing_plan_export_operator_id", table_name="sizing_plan_export")
    op.drop_index("ix_sizing_plan_export_tenant_id", table_name="sizing_plan_export")
    op.drop_table("sizing_plan_export")
    op.drop_index("ix_operator_type", table_name="operator")
    op.drop_index("ix_operator_tenant_id", table_name="operator")
    op.drop_table("operator")
