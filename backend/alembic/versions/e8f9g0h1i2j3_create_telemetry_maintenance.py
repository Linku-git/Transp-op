"""create telemetry_reading and maintenance_alert tables

Revision ID: e8f9g0h1i2j3
Revises: d7e8f9g0h1i2
Create Date: 2026-04-10
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision: str = "e8f9g0h1i2j3"
down_revision: Union[str, None] = "d7e8f9g0h1i2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telemetry_reading",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), nullable=False),
        sa.Column("reading_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sensor_type", sa.String(30), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("reading_metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_telemetry_reading_tenant_id", "telemetry_reading", ["tenant_id"])
    op.create_index("ix_telemetry_reading_vehicle_id", "telemetry_reading", ["vehicle_id"])
    op.create_index("ix_telemetry_reading_sensor_type", "telemetry_reading", ["sensor_type"])
    op.create_index("ix_telemetry_reading_timestamp", "telemetry_reading", ["reading_timestamp"])

    op.create_table(
        "maintenance_alert",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), nullable=False),
        sa.Column("alert_type", sa.String(50), nullable=False, server_default="anomaly"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("anomaly_score", sa.Float(), nullable=False),
        sa.Column("features", JSONB, nullable=True),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_maintenance_alert_tenant_id", "maintenance_alert", ["tenant_id"])
    op.create_index("ix_maintenance_alert_vehicle_id", "maintenance_alert", ["vehicle_id"])
    op.create_index("ix_maintenance_alert_severity", "maintenance_alert", ["severity"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_alert_severity")
    op.drop_index("ix_maintenance_alert_vehicle_id")
    op.drop_index("ix_maintenance_alert_tenant_id")
    op.drop_table("maintenance_alert")
    op.drop_index("ix_telemetry_reading_timestamp")
    op.drop_index("ix_telemetry_reading_sensor_type")
    op.drop_index("ix_telemetry_reading_vehicle_id")
    op.drop_index("ix_telemetry_reading_tenant_id")
    op.drop_table("telemetry_reading")
