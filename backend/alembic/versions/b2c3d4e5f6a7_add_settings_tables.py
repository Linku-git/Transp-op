"""add_settings_tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-02 18:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- optimization_settings --
    op.create_table('optimization_settings',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('meeting_radius_meters', sa.Float(), server_default='500.0', nullable=False),
        sa.Column('max_walking_distance_meters', sa.Float(), server_default='800.0', nullable=False),
        sa.Column('max_route_duration_seconds', sa.Integer(), server_default='5400', nullable=False),
        sa.Column('fuel_cost_per_liter', sa.Float(), server_default='12.0', nullable=False),
        sa.Column('fuel_consumption_l_per_100km', sa.Float(), server_default='15.0', nullable=False),
        sa.Column('co2_kg_per_liter', sa.Float(), server_default='2.68', nullable=False),
        sa.Column('rti_threshold_minutes', sa.Integer(), server_default='15', nullable=False),
        sa.Column('night_mode_start', sa.String(length=5), server_default='22:00', nullable=False),
        sa.Column('night_mode_end', sa.String(length=5), server_default='06:00', nullable=False),
        sa.Column('min_night_group_size', sa.Integer(), server_default='3', nullable=False),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', name='uq_optimization_settings_tenant'),
    )
    op.create_index('idx_optimization_settings_tenant', 'optimization_settings', ['tenant_id'], unique=False)

    # -- constraint_param --
    op.create_table('constraint_param',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=False),
        sa.Column('category', sa.String(length=50), server_default='general', nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'key', name='uq_constraint_param_tenant_key'),
    )
    op.create_index('idx_constraint_param_tenant', 'constraint_param', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_constraint_param_tenant', table_name='constraint_param')
    op.drop_table('constraint_param')
    op.drop_index('idx_optimization_settings_tenant', table_name='optimization_settings')
    op.drop_table('optimization_settings')
