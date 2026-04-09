"""Tests for RGPD Audit & Compliance (Session 90)."""
from __future__ import annotations

import json

import pytest

from app.services.gdpr import (
    RETENTION_POLICIES,
    PERSONAL_DATA_FIELDS,
    RGPD_CHECKLIST,
    get_retention_policy,
    _dict_to_csv,
)
from app.tasks.cleanup_tasks import CLEANUP_SCHEDULE


class TestRetentionPolicies:
    def test_location_data_30_days(self):
        assert RETENTION_POLICIES["location_data"] == 30

    def test_trip_history_365_days(self):
        assert RETENTION_POLICIES["trip_history"] == 365

    def test_content_delivery_180_days(self):
        assert RETENTION_POLICIES["content_delivery"] == 180

    def test_audit_logs_730_days(self):
        assert RETENTION_POLICIES["audit_logs"] == 730

    def test_all_policies_positive(self):
        for key, days in RETENTION_POLICIES.items():
            assert days > 0, f"{key} has non-positive retention"


class TestPersonalDataFields:
    def test_includes_name(self):
        assert "first_name" in PERSONAL_DATA_FIELDS
        assert "last_name" in PERSONAL_DATA_FIELDS

    def test_includes_contact(self):
        assert "email" in PERSONAL_DATA_FIELDS
        assert "phone" in PERSONAL_DATA_FIELDS

    def test_includes_location(self):
        assert "latitude" in PERSONAL_DATA_FIELDS
        assert "longitude" in PERSONAL_DATA_FIELDS

    def test_includes_address(self):
        assert "address" in PERSONAL_DATA_FIELDS


class TestRGPDChecklist:
    def test_all_articles_covered(self):
        assert len(RGPD_CHECKLIST) >= 10

    def test_art_7_consent(self):
        entry = RGPD_CHECKLIST["art_7_consent"]
        assert entry["status"] == "COMPLIANT"
        assert "consent" in entry["notes"].lower() or "opt-in" in entry["notes"].lower()

    def test_art_15_access(self):
        entry = RGPD_CHECKLIST["art_15_access"]
        assert entry["status"] == "COMPLIANT"
        assert "export" in entry["notes"].lower()

    def test_art_17_erasure(self):
        entry = RGPD_CHECKLIST["art_17_erasure"]
        assert entry["status"] == "COMPLIANT"
        assert "delete" in entry["notes"].lower() or "gdpr" in entry["notes"].lower()

    def test_art_20_portability(self):
        entry = RGPD_CHECKLIST["art_20_portability"]
        assert entry["status"] == "COMPLIANT"
        assert "JSON" in entry["notes"] or "CSV" in entry["notes"]

    def test_art_25_by_design(self):
        entry = RGPD_CHECKLIST["art_25_by_design"]
        assert entry["status"] == "COMPLIANT"
        assert "active-only" in entry["notes"].lower() or "geolocation" in entry["notes"].lower()

    def test_art_32_security(self):
        entry = RGPD_CHECKLIST["art_32_security"]
        assert entry["status"] == "COMPLIANT"
        assert "TLS" in entry["notes"] or "encryption" in entry["notes"]

    def test_no_non_compliant(self):
        for key, entry in RGPD_CHECKLIST.items():
            assert entry["status"] in ("COMPLIANT", "PREPARED", "IN_PROGRESS"), (
                f"{key} has status {entry['status']}"
            )


class TestRetentionPolicy:
    def test_get_retention_policy(self):
        policy = get_retention_policy()
        assert "policies" in policy
        assert "personal_data_fields" in policy
        assert "geolocation" in policy

    def test_geolocation_active_only(self):
        policy = get_retention_policy()
        geo = policy["geolocation"]
        assert geo["mode"] == "active_only"
        assert geo["background_tracking"] is False

    def test_location_retention(self):
        policy = get_retention_policy()
        assert policy["geolocation"]["retention_days"] == 30


class TestDataExport:
    def test_dict_to_csv(self):
        data = {"name": "Test", "email": "test@example.com"}
        csv_str = _dict_to_csv(data)
        assert "name" in csv_str
        assert "email" in csv_str
        assert "test@example.com" in csv_str


class TestCleanupSchedule:
    def test_three_cleanup_tasks(self):
        assert len(CLEANUP_SCHEDULE) == 3

    def test_location_cleanup_daily(self):
        task = CLEANUP_SCHEDULE["cleanup-location-data"]
        assert task["retention_days"] == 30
        assert "daily" in task["schedule"]

    def test_content_cleanup_weekly(self):
        task = CLEANUP_SCHEDULE["cleanup-content-delivery"]
        assert task["retention_days"] == 180
        assert "weekly" in task["schedule"]

    def test_trip_cleanup_monthly(self):
        task = CLEANUP_SCHEDULE["cleanup-trip-data"]
        assert task["retention_days"] == 365
        assert "monthly" in task["schedule"]
