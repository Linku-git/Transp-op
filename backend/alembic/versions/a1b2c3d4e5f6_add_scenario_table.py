"""add_scenario_table

Revision ID: a1b2c3d4e5f6
Revises: dbc17ef335ab
Create Date: 2026-04-02 12:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dbc17ef335ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('scenario',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('baseline_optimization_id', sa.UUID(), nullable=True),
    sa.Column('condition_type', sa.String(length=30), server_default='normal', nullable=False),
    sa.Column('demand_multiplier', sa.Float(), server_default='1.0', nullable=False),
    sa.Column('custom_params', sa.JSON(), server_default='{}', nullable=False),
    sa.Column('estimated_metrics', sa.JSON(), server_default='{}', nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.ForeignKeyConstraint(['site_id'], ['site.id'], ),
    sa.ForeignKeyConstraint(['baseline_optimization_id'], ['optimization.id'], ),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_scenario_tenant', 'scenario', ['tenant_id'], unique=False)
    op.create_index('idx_scenario_site', 'scenario', ['site_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_scenario_site', table_name='scenario')
    op.drop_index('idx_scenario_tenant', table_name='scenario')
    op.drop_table('scenario')
