from __future__ import annotations

"""Role-based permission configuration for all 9 Transpop roles.

Each role maps to a list of permission strings following the pattern
``resource:action`` or ``resource:*`` for full CRUD access.
The admin role uses ``"*"`` for unrestricted access.
"""

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["*"],
    "drh": [
        "employees:*",
        "sites:*",
        "optimization:*",
        "financial:read",
        "sotreg:m1",
        "sotreg:m2",
        "sotreg:m3",
        "sotreg:m4",
        "sotreg:m6",
        "sotreg:m7",
        "reports:*",
        "content:*",
    ],
    "daf": [
        "financial:*",
        "sotreg:m2",
        "sotreg:m5",
        "sotreg:m6",
        "sotreg:m7",
        "reports:read",
    ],
    "salarie": [
        "profile:read",
        "profile:write",
        "trips:read",
        "trips:write",
    ],
    "operateur": [
        "operator:read",
        "sotreg:m8:read",
    ],
    "responsable_parc": [
        "vehicles:*",
        "sotreg:m2",
        "sotreg:m3",
        "sotreg:m4",
        "reports:read",
    ],
    "responsable_exploitation": [
        "sotreg:m1",
        "sotreg:m4",
        "sotreg:m8",
        "optimization:read",
        "reports:read",
    ],
    "prestataire": [
        "operator:read",
        "sizing_plans:read",
    ],
    "conducteur": [
        "trips:read",
        "routes:read",
        "sotreg:m8:read",
    ],
}
