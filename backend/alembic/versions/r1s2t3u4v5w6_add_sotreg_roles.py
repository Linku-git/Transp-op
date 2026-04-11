"""Add SOTREG extended roles (9 roles)

Revision ID: r1s2t3u4v5w6
Revises: g0h1i2j3k4l5
Create Date: 2026-04-11
"""
from alembic import op

revision = "r1s2t3u4v5w6"
down_revision = "g0h1i2j3k4l5"
branch_labels = None
depends_on = None

TENANT_ID = "0cea9745-6aa2-4105-9bdc-341d95999048"

NEW_ROLES = [
    (
        "responsable_parc",
        '["vehicles:read","vehicles:write","sotreg:m2","sotreg:m3","sotreg:m4","reports:read"]',
    ),
    (
        "responsable_exploitation",
        '["sotreg:m1","sotreg:m4","sotreg:m8","optimization:read","reports:read"]',
    ),
    (
        "prestataire",
        '["operator:read","sizing_plans:read"]',
    ),
    (
        "conducteur",
        '["trips:read","routes:read","sotreg:m8:read"]',
    ),
]


def upgrade() -> None:
    for name, perms in NEW_ROLES:
        op.execute(
            f"""
            INSERT INTO role (id, tenant_id, name, permissions, is_system_role, created_at, updated_at)
            VALUES (gen_random_uuid(), '{TENANT_ID}', '{name}', '{perms}'::jsonb, true, now(), now())
            ON CONFLICT DO NOTHING
            """
        )


def downgrade() -> None:
    for name, _ in NEW_ROLES:
        op.execute(
            f"DELETE FROM role WHERE tenant_id = '{TENANT_ID}' AND name = '{name}'"
        )
