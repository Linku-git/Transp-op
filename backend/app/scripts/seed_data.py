from __future__ import annotations

import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.models.auth import Permission, Role, RolePermission, Tenant, User
from app.utils.security import hash_password

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Seed definitions
# ---------------------------------------------------------------------------

TENANT_NAME = "Transpop Demo"
TENANT_CODE = "transpop-demo"

RESOURCES = [
    "sites",
    "employees",
    "vehicles",
    "optimization",
    "financial",
    "content",
    "security",
    "reports",
    "admin",
    "users",
]
ACTIONS = ["read", "write", "delete"]

# role_name -> { resource: [actions] }
ROLE_PERMISSIONS_MAP: dict[str, dict[str, list[str]]] = {
    "admin": {r: ACTIONS for r in RESOURCES},
    "drh": {
        "sites": ["read", "write"],
        "employees": ["read", "write"],
        "vehicles": ["read", "write"],
        "optimization": ["read", "write"],
        "reports": ["read", "write"],
        "financial": ["read"],
        "content": ["read", "write"],
        "security": ["read"],
    },
    "daf": {
        "financial": ["read", "write"],
        "reports": ["read", "write"],
        "sites": ["read"],
        "employees": ["read"],
        "optimization": ["read"],
        "vehicles": ["read"],
    },
    "salarie": {
        "employees": ["read"],  # own data only (enforced at service layer)
    },
    "operateur": {
        "optimization": ["read"],  # assigned routes only (enforced at service layer)
        "vehicles": ["read"],
    },
}

ROLE_DESCRIPTIONS: dict[str, str] = {
    "admin": "Full access to everything",
    "drh": "Read/write sites, employees, optimization, reports. Read financial.",
    "daf": "Read/write financial, reports. Read sites, employees, optimization.",
    "salarie": "Read own data only",
    "operateur": "Read assigned routes only",
}

ADMIN_EMAIL = "admin@transpop.dev"
ADMIN_PASSWORD = "admin123"
ADMIN_FIRST_NAME = "Admin"
ADMIN_LAST_NAME = "Transpop"


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------


async def seed() -> None:
    """Populate the database with initial auth data.

    This function is idempotent: it checks for existing records before
    inserting and can be safely called multiple times.
    """
    async with async_session_factory() as session:
        async with session.begin():
            # ------ 1. Tenant ------ #
            result = await session.execute(
                select(Tenant).where(Tenant.code == TENANT_CODE)
            )
            tenant = result.scalars().first()

            if tenant is None:
                tenant = Tenant(name=TENANT_NAME, code=TENANT_CODE)
                session.add(tenant)
                await session.flush()
                logger.info("Created tenant: %s", TENANT_CODE)
            else:
                logger.info("Tenant already exists: %s", TENANT_CODE)

            # ------ 2. Permissions ------ #
            existing_perms_result = await session.execute(select(Permission))
            existing_perms = {
                (p.resource, p.action) for p in existing_perms_result.scalars().all()
            }

            permission_map: dict[tuple[str, str], Permission] = {}

            for resource in RESOURCES:
                for action in ACTIONS:
                    key = (resource, action)
                    if key not in existing_perms:
                        perm = Permission(resource=resource, action=action)
                        session.add(perm)
                        permission_map[key] = perm
                    else:
                        pass  # will fetch below after flush

            await session.flush()

            # Re-fetch all permissions so we have their ids
            all_perms_result = await session.execute(select(Permission))
            for p in all_perms_result.scalars().all():
                permission_map[(p.resource, p.action)] = p

            created_perm_count = len(RESOURCES) * len(ACTIONS) - len(existing_perms)
            if created_perm_count > 0:
                logger.info("Created %d permissions", created_perm_count)
            else:
                logger.info("All permissions already exist")

            # ------ 3. Roles ------ #
            existing_roles_result = await session.execute(
                select(Role).where(Role.tenant_id == tenant.id)
            )
            existing_roles = {r.name: r for r in existing_roles_result.scalars().all()}

            role_map: dict[str, Role] = {}
            for role_name in ROLE_PERMISSIONS_MAP:
                if role_name in existing_roles:
                    role_map[role_name] = existing_roles[role_name]
                    logger.info("Role already exists: %s", role_name)
                else:
                    role = Role(
                        tenant_id=tenant.id,
                        name=role_name,
                        permissions=[],
                        is_system_role=True,
                    )
                    session.add(role)
                    role_map[role_name] = role
                    logger.info("Created role: %s", role_name)

            await session.flush()

            # ------ 4. RolePermission entries ------ #
            existing_rp_result = await session.execute(select(RolePermission))
            existing_rp = {
                (rp.role_id, rp.permission_id)
                for rp in existing_rp_result.scalars().all()
            }

            rp_created = 0
            for role_name, resource_actions in ROLE_PERMISSIONS_MAP.items():
                role = role_map[role_name]
                for resource, actions in resource_actions.items():
                    for action in actions:
                        perm = permission_map.get((resource, action))
                        if perm is None:
                            logger.warning(
                                "Permission not found: %s:%s", resource, action
                            )
                            continue
                        if (role.id, perm.id) not in existing_rp:
                            rp = RolePermission(
                                role_id=role.id,
                                permission_id=perm.id,
                            )
                            session.add(rp)
                            rp_created += 1

            if rp_created > 0:
                await session.flush()
                logger.info("Created %d role-permission links", rp_created)
            else:
                logger.info("All role-permission links already exist")

            # ------ 5. Default admin user ------ #
            admin_role = role_map["admin"]
            result = await session.execute(
                select(User).where(
                    User.tenant_id == tenant.id,
                    User.email == ADMIN_EMAIL,
                )
            )
            admin_user = result.scalars().first()

            if admin_user is None:
                admin_user = User(
                    tenant_id=tenant.id,
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    first_name=ADMIN_FIRST_NAME,
                    last_name=ADMIN_LAST_NAME,
                    role_id=admin_role.id,
                    is_active=True,
                )
                session.add(admin_user)
                await session.flush()
                logger.info("Created admin user: %s", ADMIN_EMAIL)
            else:
                logger.info("Admin user already exists: %s", ADMIN_EMAIL)

    logger.info("Seed completed successfully")
