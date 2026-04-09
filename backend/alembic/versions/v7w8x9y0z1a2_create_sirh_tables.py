"""create sirh_connection, sync_log, sync_conflict tables

Revision ID: v7w8x9y0z1a2
Revises: u6v7w8x9y0z1
Create Date: 2026-04-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "v7w8x9y0z1a2"
down_revision = "u6v7w8x9y0z1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SIRHConnection
    op.create_table(
        "sirh_connection",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column("sync_frequency", sa.String(20), nullable=False, server_default="daily"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("conflict_strategy", sa.String(20), nullable=False, server_default="sirh_wins"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sirh_connection_tenant_id", "sirh_connection", ["tenant_id"])
    op.create_index("ix_sirh_connection_provider", "sirh_connection", ["provider"])
    op.create_index("ix_sirh_connection_status", "sirh_connection", ["status"])

    # SyncLog
    op.create_table(
        "sync_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sirh_connection.id"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("records_failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("errors", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_log_connection_id", "sync_log", ["connection_id"])
    op.create_index("ix_sync_log_tenant_id", "sync_log", ["tenant_id"])
    op.create_index("ix_sync_log_status", "sync_log", ["status"])

    # SyncConflict
    op.create_table(
        "sync_conflict",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sync_log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sync_log.id"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("platform_value", sa.Text, nullable=True),
        sa.Column("sirh_value", sa.Text, nullable=True),
        sa.Column("resolution", sa.String(20), nullable=False, server_default="unresolved"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sync_conflict_sync_log_id", "sync_conflict", ["sync_log_id"])
    op.create_index("ix_sync_conflict_tenant_id", "sync_conflict", ["tenant_id"])
    op.create_index("ix_sync_conflict_employee_id", "sync_conflict", ["employee_id"])
    op.create_index("ix_sync_conflict_resolution", "sync_conflict", ["resolution"])


def downgrade() -> None:
    op.drop_index("ix_sync_conflict_resolution", table_name="sync_conflict")
    op.drop_index("ix_sync_conflict_employee_id", table_name="sync_conflict")
    op.drop_index("ix_sync_conflict_tenant_id", table_name="sync_conflict")
    op.drop_index("ix_sync_conflict_sync_log_id", table_name="sync_conflict")
    op.drop_table("sync_conflict")
    op.drop_index("ix_sync_log_status", table_name="sync_log")
    op.drop_index("ix_sync_log_tenant_id", table_name="sync_log")
    op.drop_index("ix_sync_log_connection_id", table_name="sync_log")
    op.drop_table("sync_log")
    op.drop_index("ix_sirh_connection_status", table_name="sirh_connection")
    op.drop_index("ix_sirh_connection_provider", table_name="sirh_connection")
    op.drop_index("ix_sirh_connection_tenant_id", table_name="sirh_connection")
    op.drop_table("sirh_connection")
