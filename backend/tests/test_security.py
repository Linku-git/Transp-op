"""Tests for Security Hardening (Session 89)."""
from __future__ import annotations

import pytest

from app.middleware.security_headers import SECURITY_HEADERS, get_security_headers
from app.middleware.audit_log import (
    OWASP_CHECKLIST,
    FILE_UPLOAD_CONFIG,
    RATE_LIMITS,
    WRITE_METHODS,
    SKIP_PATHS,
)


class TestSecurityHeaders:
    def test_x_content_type_options(self):
        assert SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options(self):
        assert SECURITY_HEADERS["X-Frame-Options"] == "DENY"

    def test_hsts(self):
        hsts = SECURITY_HEADERS["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_csp(self):
        csp = SECURITY_HEADERS["Content-Security-Policy"]
        assert "default-src 'self'" in csp

    def test_referrer_policy(self):
        assert SECURITY_HEADERS["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy(self):
        pp = SECURITY_HEADERS["Permissions-Policy"]
        assert "geolocation=(self)" in pp
        assert "camera=()" in pp

    def test_cache_control(self):
        assert "no-store" in SECURITY_HEADERS["Cache-Control"]

    def test_get_security_headers_returns_copy(self):
        headers = get_security_headers()
        assert headers == SECURITY_HEADERS
        headers["Custom"] = "test"
        assert "Custom" not in SECURITY_HEADERS


class TestOWASPChecklist:
    def test_all_10_categories_covered(self):
        assert len(OWASP_CHECKLIST) == 10

    def test_a01_broken_access_control(self):
        entry = OWASP_CHECKLIST["A01_broken_access_control"]
        assert entry["status"] in ("MITIGATED", "CHECKED")
        assert len(entry["measures"]) >= 2

    def test_a02_cryptographic_failures(self):
        entry = OWASP_CHECKLIST["A02_cryptographic_failures"]
        measures_text = " ".join(entry["measures"])
        assert "TLS" in measures_text or "bcrypt" in measures_text

    def test_a03_injection(self):
        entry = OWASP_CHECKLIST["A03_injection"]
        measures_text = " ".join(entry["measures"])
        assert "ORM" in measures_text or "Pydantic" in measures_text

    def test_a05_security_misconfiguration(self):
        entry = OWASP_CHECKLIST["A05_security_misconfiguration"]
        measures_text = " ".join(entry["measures"])
        assert "header" in measures_text.lower() or "CORS" in measures_text

    def test_a07_auth_failures(self):
        entry = OWASP_CHECKLIST["A07_auth_failures"]
        measures_text = " ".join(entry["measures"])
        assert "JWT" in measures_text
        assert "MFA" in measures_text

    def test_a09_logging(self):
        entry = OWASP_CHECKLIST["A09_logging_failures"]
        measures_text = " ".join(entry["measures"])
        assert "audit" in measures_text.lower()

    def test_a10_ssrf(self):
        entry = OWASP_CHECKLIST["A10_ssrf"]
        measures_text = " ".join(entry["measures"])
        assert "user-controlled" in measures_text.lower() or "env" in measures_text.lower()

    def test_no_unmitigated_critical(self):
        for key, entry in OWASP_CHECKLIST.items():
            assert entry["status"] in ("MITIGATED", "CHECKED", "IN_PROGRESS"), (
                f"{key} has status {entry['status']}"
            )


class TestFileUploadSecurity:
    def test_max_size_10mb(self):
        assert FILE_UPLOAD_CONFIG["max_size_bytes"] == 10 * 1024 * 1024

    def test_blocked_executables(self):
        blocked = FILE_UPLOAD_CONFIG["blocked_extensions"]
        assert ".exe" in blocked
        assert ".bat" in blocked
        assert ".sh" in blocked
        assert ".js" in blocked

    def test_allowed_mime_types(self):
        allowed = FILE_UPLOAD_CONFIG["allowed_mime_types"]
        assert "text/csv" in allowed
        assert "application/pdf" in allowed
        assert "image/jpeg" in allowed

    def test_no_executable_in_allowed(self):
        allowed = FILE_UPLOAD_CONFIG["allowed_mime_types"]
        for mime in allowed:
            assert "executable" not in mime
            assert "javascript" not in mime


class TestRateLimiting:
    def test_admin_highest_limit(self):
        assert RATE_LIMITS["admin"] == 2000

    def test_operateur_lowest_limit(self):
        assert RATE_LIMITS["operateur"] == 100

    def test_all_roles_have_limits(self):
        for role in ["admin", "drh", "daf", "salarie", "operateur"]:
            assert role in RATE_LIMITS
            assert RATE_LIMITS[role] > 0

    def test_limits_descending_order(self):
        assert RATE_LIMITS["admin"] >= RATE_LIMITS["drh"]
        assert RATE_LIMITS["drh"] >= RATE_LIMITS["salarie"]
        assert RATE_LIMITS["salarie"] >= RATE_LIMITS["operateur"]


class TestAuditLogConfig:
    def test_write_methods(self):
        assert "POST" in WRITE_METHODS
        assert "PUT" in WRITE_METHODS
        assert "PATCH" in WRITE_METHODS
        assert "DELETE" in WRITE_METHODS
        assert "GET" not in WRITE_METHODS

    def test_skip_paths(self):
        assert "/health" in SKIP_PATHS
        assert "/docs" in SKIP_PATHS
