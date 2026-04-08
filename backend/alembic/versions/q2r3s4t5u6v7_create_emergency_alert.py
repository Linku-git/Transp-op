"""create emergency_alert table

Revision ID: q2r3s4t5u6v7
Revises: p1q2r3s4t5u6
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

revision = "q2r3s4t5u6v7"
down_revision = "p1q2r3s4t5u6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "emergency_alert",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("alert_type", sa.String(30), nullable=False, server_default="panic"),
        sa.Column("responders_notified", postgresql.JSONB(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_emergency_alert_tenant_id", "emergency_alert", ["tenant_id"])
    op.create_index("ix_emergency_alert_employee_id", "emergency_alert", ["employee_id"])
    op.create_index("ix_emergency_alert_triggered_at", "emergency_alert", ["triggered_at"])
    op.create_index("ix_emergency_alert_location", "emergency_alert", ["location"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_table("emergency_alert")
