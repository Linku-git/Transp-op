"""create security_questionnaire table

Revision ID: n9o0p1q2r3s4
Revises: m8n9o0p1q2r3
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "n9o0p1q2r3s4"
down_revision = "m8n9o0p1q2r3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "security_questionnaire",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("overall_safety_rating", sa.Integer(), nullable=False),
        sa.Column("responses", postgresql.JSONB(), nullable=True),
        sa.Column("vulnerable_stops", postgresql.JSONB(), nullable=True),
        sa.Column("night_concerns", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trigger_type", sa.String(30), nullable=False, server_default="periodic"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_security_questionnaire_tenant_id", "security_questionnaire", ["tenant_id"])
    op.create_index("ix_security_questionnaire_employee_id", "security_questionnaire", ["employee_id"])
    op.create_index("ix_security_questionnaire_submitted", "security_questionnaire", ["submitted_at"])


def downgrade() -> None:
    op.drop_table("security_questionnaire")
