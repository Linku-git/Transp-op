"""add_kpi_snapshot

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-02 24:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('kpi_snapshot',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('site_id', sa.UUID(), nullable=True),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('kpi_type', sa.String(length=50), nullable=False),
        sa.Column('value', JSONB(), nullable=False),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['site_id'], ['site.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_kpi_snapshot_tenant', 'kpi_snapshot', ['tenant_id'], unique=False)
    op.create_index('idx_kpi_snapshot_site', 'kpi_snapshot', ['site_id'], unique=False)
    op.create_index('idx_kpi_snapshot_type_date', 'kpi_snapshot', ['kpi_type', 'snapshot_date'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_kpi_snapshot_type_date', table_name='kpi_snapshot')
    op.drop_index('idx_kpi_snapshot_site', table_name='kpi_snapshot')
    op.drop_index('idx_kpi_snapshot_tenant', table_name='kpi_snapshot')
    op.drop_table('kpi_snapshot')
