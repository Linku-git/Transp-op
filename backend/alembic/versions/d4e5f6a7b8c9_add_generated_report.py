"""add_generated_report

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-02 23:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('generated_report',
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('params', JSONB(), server_default='{}', nullable=True),
        sa.Column('file_url', sa.Text(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('generated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id']),
        sa.ForeignKeyConstraint(['generated_by'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_generated_report_tenant', 'generated_report', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_generated_report_tenant', table_name='generated_report')
    op.drop_table('generated_report')
