"""create training_module table

Revision ID: u6v7w8x9y0z1
Revises: t5u6v7w8x9y0
Create Date: 2026-04-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "u6v7w8x9y0z1"
down_revision = "t5u6v7w8x9y0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "training_module",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content.id"), nullable=False),
        sa.Column("lms_provider", sa.String(50), nullable=False),
        sa.Column("lms_external_id", sa.String(255), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("is_mandatory", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("certification_name", sa.String(500), nullable=True),
        sa.Column("lms_metadata", postgresql.JSONB, nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_module_tenant_id", "training_module", ["tenant_id"])
    op.create_index("ix_training_module_content_id", "training_module", ["content_id"])
    op.create_index("ix_training_module_lms_provider", "training_module", ["lms_provider"])
    op.create_index(
        "ix_training_module_lms_external",
        "training_module",
        ["tenant_id", "lms_provider", "lms_external_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_training_module_lms_external", table_name="training_module")
    op.drop_index("ix_training_module_lms_provider", table_name="training_module")
    op.drop_index("ix_training_module_content_id", table_name="training_module")
    op.drop_index("ix_training_module_tenant_id", table_name="training_module")
    op.drop_table("training_module")
