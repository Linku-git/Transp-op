"""add_financial_tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-02 22:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- financial_scenario --
    op.create_table('financial_scenario',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('investment_model', sa.String(length=30), nullable=False),
        sa.Column('duration_years', sa.Integer(), server_default='5', nullable=False),
        sa.Column('fleet_composition', JSONB(), server_default='{}', nullable=True),
        sa.Column('params', JSONB(), server_default='{}', nullable=True),
        sa.Column('results', JSONB(), server_default='{}', nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['created_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_financial_scenario_tenant', 'financial_scenario', ['tenant_id'], unique=False)
    op.create_index('idx_financial_scenario_created_by', 'financial_scenario', ['created_by'], unique=False)

    # -- tco_entry --
    op.create_table('tco_entry',
        sa.Column('financial_scenario_id', sa.UUID(), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=False),
        sa.Column('motorization', sa.String(length=30), nullable=True),
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=False),
        sa.Column('purchase_price', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('annual_maintenance_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('energy_cost_per_km', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('annual_km', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('residual_value', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('infrastructure_cost', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('tco_per_vehicle', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('tco_total', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['financial_scenario_id'], ['financial_scenario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_tco_entry_financial_scenario', 'tco_entry', ['financial_scenario_id'], unique=False)

    # -- roi_calculation --
    op.create_table('roi_calculation',
        sa.Column('financial_scenario_id', sa.UUID(), nullable=False),
        sa.Column('baseline_absence_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('target_absence_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('headcount', sa.Integer(), nullable=True),
        sa.Column('daily_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('replacement_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('turnover_rate_before', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('turnover_rate_after', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('training_hour_cost', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('engagement_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('annual_travel_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('roi_absenteeism', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('roi_retention', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('roi_journey', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('roi_fleet_optimization', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('roi_total', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('payback_months', sa.Numeric(precision=6, scale=1), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['financial_scenario_id'], ['financial_scenario.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_roi_calculation_financial_scenario', 'roi_calculation', ['financial_scenario_id'], unique=False)

    # -- vehicle_reference --
    op.create_table('vehicle_reference',
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('capacity_min', sa.Integer(), nullable=True),
        sa.Column('capacity_max', sa.Integer(), nullable=True),
        sa.Column('motorizations_available', JSONB(), server_default='[]', nullable=True),
        sa.Column('recommended_use', sa.Text(), nullable=True),
        sa.Column('reference_tco_5y', JSONB(), server_default='{}', nullable=True),
        sa.Column('length_meters', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('zfe_compliant', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('vehicle_reference')
    op.drop_index('idx_roi_calculation_financial_scenario', table_name='roi_calculation')
    op.drop_table('roi_calculation')
    op.drop_index('idx_tco_entry_financial_scenario', table_name='tco_entry')
    op.drop_table('tco_entry')
    op.drop_index('idx_financial_scenario_created_by', table_name='financial_scenario')
    op.drop_index('idx_financial_scenario_tenant', table_name='financial_scenario')
    op.drop_table('financial_scenario')
