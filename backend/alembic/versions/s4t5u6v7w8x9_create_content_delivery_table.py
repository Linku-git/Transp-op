"""create content_delivery table

Revision ID: s4t5u6v7w8x9
Revises: r3s4t5u6v7w8
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s4t5u6v7w8x9"
down_revision = "r3s4t5u6v7w8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_delivery",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenant.id"),
            nullable=False,
        ),
        sa.Column(
            "content_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content.id"),
            nullable=False,
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employee.id"),
            nullable=False,
        ),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "viewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "quiz_score",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "time_spent_seconds",
            sa.Integer,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_delivery_tenant_id", "content_delivery", ["tenant_id"])
    op.create_index("ix_content_delivery_content_id", "content_delivery", ["content_id"])
    op.create_index("ix_content_delivery_employee_id", "content_delivery", ["employee_id"])
    op.create_index(
        "ix_content_delivery_content_employee",
        "content_delivery",
        ["content_id", "employee_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_content_delivery_content_employee", table_name="content_delivery")
    op.drop_index("ix_content_delivery_employee_id", table_name="content_delivery")
    op.drop_index("ix_content_delivery_content_id", table_name="content_delivery")
    op.drop_index("ix_content_delivery_tenant_id", table_name="content_delivery")
    op.drop_table("content_delivery")
