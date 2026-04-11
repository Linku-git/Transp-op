from __future__ import annotations

import pytest

from app.middleware.rbac import ALL_ROLES, SOTREG_MODULE_ROLES


class TestSOTREGRoles:
    """Unit tests for the extended 9-role RBAC configuration."""

    def test_all_roles_count(self) -> None:
        assert len(ALL_ROLES) == 9

    def test_responsable_parc_access_m2_m3_m4(self) -> None:
        for module in ["m2_technologies", "m3_infrastructure", "m4_performance"]:
            assert "responsable_parc" in SOTREG_MODULE_ROLES[module]

    def test_responsable_parc_no_access_m5_m6_m7(self) -> None:
        for module in ["m5_finance", "m6_roadmap", "m7_scoring"]:
            assert "responsable_parc" not in SOTREG_MODULE_ROLES[module]

    def test_responsable_exploitation_access_m4_m8(self) -> None:
        for module in ["m4_performance", "m8_realtime"]:
            assert "responsable_exploitation" in SOTREG_MODULE_ROLES[module]

    def test_responsable_exploitation_no_m5(self) -> None:
        assert "responsable_exploitation" not in SOTREG_MODULE_ROLES["m5_finance"]

    def test_prestataire_not_in_any_sotreg_module(self) -> None:
        for roles in SOTREG_MODULE_ROLES.values():
            assert "prestataire" not in roles

    def test_conducteur_m8_only(self) -> None:
        assert "conducteur" in SOTREG_MODULE_ROLES["m8_realtime"]
        for key, roles in SOTREG_MODULE_ROLES.items():
            if key != "m8_realtime":
                assert "conducteur" not in roles

    def test_admin_full_access(self) -> None:
        for roles in SOTREG_MODULE_ROLES.values():
            assert "admin" in roles

    def test_drh_retains_m1_through_m7(self) -> None:
        for key, roles in SOTREG_MODULE_ROLES.items():
            if not key.startswith("m8"):
                assert "drh" in roles

    def test_daf_in_m2_m5_m6_m7(self) -> None:
        for module in ["m2_technologies", "m5_finance", "m6_roadmap", "m7_scoring"]:
            assert "daf" in SOTREG_MODULE_ROLES[module]

    def test_require_module_function_exists(self) -> None:
        from app.middleware.rbac import require_module

        assert callable(require_module)

    def test_role_permissions_config_exists(self) -> None:
        from app.services.rbac_config import ROLE_PERMISSIONS

        assert len(ROLE_PERMISSIONS) == 9

    def test_role_permissions_admin_has_wildcard(self) -> None:
        from app.services.rbac_config import ROLE_PERMISSIONS

        assert "*" in ROLE_PERMISSIONS["admin"]

    def test_salarie_role_unchanged(self) -> None:
        assert "salarie" in ALL_ROLES
        for roles in SOTREG_MODULE_ROLES.values():
            assert "salarie" not in roles

    def test_operateur_role_unchanged(self) -> None:
        assert "operateur" in ALL_ROLES
        for roles in SOTREG_MODULE_ROLES.values():
            assert "operateur" not in roles

    def test_require_role_returns_callable(self) -> None:
        from app.middleware.rbac import require_role

        dep = require_role("admin")
        assert callable(dep)
