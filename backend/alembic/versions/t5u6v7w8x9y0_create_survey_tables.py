"""create survey and survey_response tables

Revision ID: t5u6v7w8x9y0
Revises: s4t5u6v7w8x9
Create Date: 2026-04-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t5u6v7w8x9y0"
down_revision = "s4t5u6v7w8x9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Survey table
    op.create_table(
        "survey",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.String(2000), nullable=True),
        sa.Column("questions", postgresql.JSONB, nullable=False),
        sa.Column("response_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_anonymous", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_survey_tenant_id", "survey", ["tenant_id"])
    op.create_index("ix_survey_content_id", "survey", ["content_id"])
    op.create_index("ix_survey_is_active", "survey", ["is_active"])

    # Survey response table
    op.create_table(
        "survey_response",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("survey_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("survey.id"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employee.id"), nullable=True),
        sa.Column("responses", postgresql.JSONB, nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_survey_response_tenant_id", "survey_response", ["tenant_id"])
    op.create_index("ix_survey_response_survey_id", "survey_response", ["survey_id"])
    op.create_index("ix_survey_response_employee_id", "survey_response", ["employee_id"])


def downgrade() -> None:
    op.drop_index("ix_survey_response_employee_id", table_name="survey_response")
    op.drop_index("ix_survey_response_survey_id", table_name="survey_response")
    op.drop_index("ix_survey_response_tenant_id", table_name="survey_response")
    op.drop_table("survey_response")
    op.drop_index("ix_survey_is_active", table_name="survey")
    op.drop_index("ix_survey_content_id", table_name="survey")
    op.drop_index("ix_survey_tenant_id", table_name="survey")
    op.drop_table("survey")
