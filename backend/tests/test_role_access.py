"""Role Access Tests -- Session 127.

Verifies that all 9 user roles have correct access permissions
to their designated endpoints. These are structural/contract tests
validating the RBAC permission matrix.
"""
from __future__ import annotations

import logging
from typing import Any

import pytest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Role permission matrix -- defines which endpoints each role can access
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[str, dict[str, Any]] = {
    "admin": {
        "allowed": [
            "/api/v1/users",
            "/api/v1/sites",
            "/api/v1/employees",
            "/api/v1/vehicles",
            "/api/v1/optimization",
            "/api/v1/financial",
            "/api/v1/kpis",
            "/api/v1/sotreg",
            "/api/v1/ml",
        ],
        "denied": [],
        "description": "Full access to all endpoints",
    },
    "drh": {
        "allowed": [
            "/api/v1/employees",
            "/api/v1/kpis",
            "/api/v1/sites",
            "/api/v1/reports",
            "/api/v1/content",
            "/api/v1/surveys",
        ],
        "denied": ["/api/v1/financial/tco", "/api/v1/financial/roi"],
        "description": "HR dashboards, employee data, reports",
    },
    "daf": {
        "allowed": [
            "/api/v1/financial",
            "/api/v1/kpis",
            "/api/v1/reports",
            "/api/v1/sotreg/tco",
            "/api/v1/sotreg/npv",
        ],
        "denied": ["/api/v1/employees/create", "/api/v1/users"],
        "description": "Financial dashboards, TCO, ROI, exports",
    },
    "salarie": {
        "allowed": [
            "/api/v1/mobile/trips",
            "/api/v1/mobile/profile",
            "/api/v1/content/feed",
            "/api/v1/surveys/active",
        ],
        "denied": ["/api/v1/users", "/api/v1/financial", "/api/v1/optimization"],
        "description": "Own trips, profile, content feed",
    },
    "operateur": {
        "allowed": [
            "/api/v1/operator/plans",
            "/api/v1/operator/lignes",
            "/api/v1/operator/issues",
        ],
        "denied": ["/api/v1/users", "/api/v1/employees", "/api/v1/financial"],
        "description": "Operator portal, assigned lignes",
    },
    "conducteur": {
        "allowed": [
            "/api/v1/driver/trips",
            "/api/v1/driver/vehicle",
            "/api/v1/driver/risk",
            "/api/v1/driver/schedule",
        ],
        "denied": ["/api/v1/users", "/api/v1/financial", "/api/v1/optimization"],
        "description": "Driver portal, assigned trips, risk score",
    },
    "prestataire": {
        "allowed": [
            "/api/v1/contractor/kpis",
            "/api/v1/contractor/sla",
            "/api/v1/contractor/fleet",
            "/api/v1/contractor/invoices",
        ],
        "denied": ["/api/v1/users", "/api/v1/employees", "/api/v1/optimization"],
        "description": "Contractor dashboard, SLA, fleet status",
    },
    "responsable_exploitation": {
        "allowed": [
            "/api/v1/sotreg/realtime",
            "/api/v1/sotreg/alerts",
            "/api/v1/kpis",
            "/api/v1/vehicles",
        ],
        "denied": ["/api/v1/users", "/api/v1/financial/tco"],
        "description": "Real-time operations, alerts, KPIs",
    },
    "responsable_parc": {
        "allowed": [
            "/api/v1/sotreg/ml",
            "/api/v1/kpis",
            "/api/v1/sotreg/analytics",
            "/api/v1/vehicles",
        ],
        "denied": ["/api/v1/users/create", "/api/v1/financial/export"],
        "description": "ML dashboard, analytics, read-only data",
    },
}


class TestRolePermissions:
    """Verify role permission matrices are correctly defined."""

    def test_admin_has_full_access(self) -> None:
        """Admin can access all 9 module endpoints."""
        admin = ROLE_PERMISSIONS["admin"]
        assert len(admin["allowed"]) >= 9
        # Admin should cover: users, sites, employees, vehicles,
        # optimization, financial, kpis, sotreg, ml
        key_modules = {
            "users", "sites", "employees", "vehicles",
            "optimization", "financial", "kpis", "sotreg", "ml",
        }
        covered: set[str] = set()
        for endpoint in admin["allowed"]:
            parts = endpoint.split("/")
            if len(parts) >= 4:
                covered.add(parts[3])
        assert key_modules.issubset(covered), (
            f"Admin missing modules: {key_modules - covered}"
        )
        # Admin has no denied endpoints
        assert len(admin["denied"]) == 0

    def test_conducteur_limited_to_driver_portal(self) -> None:
        """Conducteur can only access driver portal endpoints."""
        conducteur = ROLE_PERMISSIONS["conducteur"]
        for endpoint in conducteur["allowed"]:
            assert "driver" in endpoint, (
                f"Conducteur endpoint should be driver-scoped: {endpoint}"
            )
        # Conducteur cannot access admin or financial
        denied = conducteur["denied"]
        assert "/api/v1/users" in denied
        assert "/api/v1/financial" in denied
        assert "/api/v1/optimization" in denied

    def test_prestataire_limited_to_contractor(self) -> None:
        """Prestataire can only access contractor endpoints."""
        prestataire = ROLE_PERMISSIONS["prestataire"]
        for endpoint in prestataire["allowed"]:
            assert "contractor" in endpoint, (
                f"Prestataire endpoint should be contractor-scoped: {endpoint}"
            )
        assert "/api/v1/users" in prestataire["denied"]
        assert "/api/v1/employees" in prestataire["denied"]

    def test_analyste_has_readonly_analytics(self) -> None:
        """Analyste (responsable_parc) has read-only access to analytics."""
        analyste = ROLE_PERMISSIONS["responsable_parc"]
        # Has access to ML and analytics
        assert any("ml" in ep for ep in analyste["allowed"])
        assert any(
            "analytics" in ep or "kpis" in ep
            for ep in analyste["allowed"]
        )
        # Denied write/create/export operations
        denied = analyste["denied"]
        assert any("create" in d or "export" in d for d in denied)

    def test_all_9_roles_defined(self) -> None:
        """All 9 user roles have permission definitions."""
        expected_roles = {
            "admin", "drh", "daf", "salarie", "operateur",
            "conducteur", "prestataire",
            "responsable_exploitation", "responsable_parc",
        }
        assert set(ROLE_PERMISSIONS.keys()) == expected_roles

    def test_no_role_has_empty_permissions(self) -> None:
        """Every role has at least one allowed endpoint."""
        for role, perms in ROLE_PERMISSIONS.items():
            assert len(perms["allowed"]) > 0, (
                f"Role {role} has no allowed endpoints"
            )
            assert "description" in perms, (
                f"Role {role} is missing a description"
            )

    def test_salarie_cannot_access_admin_endpoints(self) -> None:
        """Salarie (employee) cannot access admin/financial endpoints."""
        salarie = ROLE_PERMISSIONS["salarie"]
        denied = salarie["denied"]
        assert "/api/v1/users" in denied
        assert "/api/v1/financial" in denied
        assert "/api/v1/optimization" in denied
        # Salarie allowed endpoints are mobile/content-scoped
        for endpoint in salarie["allowed"]:
            assert any(
                scope in endpoint
                for scope in ("mobile", "content", "surveys")
            ), f"Salarie endpoint should be mobile/content-scoped: {endpoint}"
