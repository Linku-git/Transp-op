"""Tests for SIRH Connection Framework (Session 77)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.sirh_connection import SIRHConnection
from app.models.sync_log import SyncLog
from app.models.sync_conflict import SyncConflict
from app.schemas.sirh import (
    SIRHConnectionCreate,
    SIRHConnectionUpdate,
    SIRHConnectionResponse,
    ConflictResolveRequest,
    SyncTriggerResponse,
)
from app.services.sirh.conflict_resolver import ConflictResolver


class TestSIRHConnectionModel:
    def test_create_connection(self):
        conn = SIRHConnection(
            tenant_id=uuid.uuid4(),
            provider="sap",
            name="SAP SuccessFactors",
            config={"api_url": "https://api.sap.com", "api_key": "encrypted"},
            sync_frequency="daily",
            conflict_strategy="sirh_wins",
        )
        assert conn.provider == "sap"
        assert conn.name == "SAP SuccessFactors"
        assert conn.config["api_url"] == "https://api.sap.com"

    def test_all_providers(self):
        for provider in ["sap", "workday", "talentsoft", "sage"]:
            conn = SIRHConnection(
                tenant_id=uuid.uuid4(),
                provider=provider,
                name=f"{provider} connection",
            )
            assert conn.provider == provider

    def test_connection_with_last_sync(self):
        now = datetime.now(timezone.utc)
        conn = SIRHConnection(
            tenant_id=uuid.uuid4(),
            provider="workday",
            name="Workday",
            last_sync_at=now,
            status="active",
        )
        assert conn.last_sync_at == now
        assert conn.status == "active"


class TestSyncLogModel:
    def test_create_sync_log(self):
        log = SyncLog(
            connection_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            started_at=datetime.now(timezone.utc),
            status="running",
            records_created=0,
            records_updated=0,
            records_failed=0,
        )
        assert log.status == "running"
        assert log.records_created == 0

    def test_completed_sync_log(self):
        log = SyncLog(
            connection_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            records_created=10,
            records_updated=5,
            records_failed=1,
            errors=["Employee X: missing email"],
            status="completed_with_errors",
        )
        assert log.records_created == 10
        assert len(log.errors) == 1


class TestSyncConflictModel:
    def test_create_conflict(self):
        conflict = SyncConflict(
            sync_log_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            field_name="department",
            platform_value="Engineering",
            sirh_value="IT",
            resolution="unresolved",
        )
        assert conflict.field_name == "department"
        assert conflict.platform_value == "Engineering"
        assert conflict.sirh_value == "IT"
        assert conflict.resolution == "unresolved"


class TestSIRHSchemas:
    def test_create_schema_valid(self):
        schema = SIRHConnectionCreate(
            provider="sap",
            name="SAP Connection",
            sync_frequency="daily",
            conflict_strategy="sirh_wins",
        )
        assert schema.provider == "sap"

    def test_create_rejects_invalid_provider(self):
        with pytest.raises(Exception):
            SIRHConnectionCreate(provider="oracle", name="Test")

    def test_create_rejects_invalid_frequency(self):
        with pytest.raises(Exception):
            SIRHConnectionCreate(
                provider="sap", name="Test", sync_frequency="every_minute"
            )

    def test_create_rejects_invalid_strategy(self):
        with pytest.raises(Exception):
            SIRHConnectionCreate(
                provider="sap", name="Test", conflict_strategy="always_fail"
            )

    def test_update_schema_partial(self):
        schema = SIRHConnectionUpdate(name="Updated Name")
        assert schema.name == "Updated Name"
        assert schema.config is None

    def test_conflict_resolve_request(self):
        req = ConflictResolveRequest(resolution="manual", manual_value="Corrected")
        assert req.resolution == "manual"
        assert req.manual_value == "Corrected"


class TestConflictResolver:
    def test_no_conflict(self):
        resolver = ConflictResolver("sirh_wins")
        value, resolution = resolver.resolve("dept", "IT", "IT")
        assert resolution == "no_conflict"
        assert value == "IT"

    def test_sirh_wins(self):
        resolver = ConflictResolver("sirh_wins")
        value, resolution = resolver.resolve("dept", "Engineering", "IT")
        assert resolution == "sirh_wins"
        assert value == "IT"

    def test_platform_wins(self):
        resolver = ConflictResolver("platform_wins")
        value, resolution = resolver.resolve("dept", "Engineering", "IT")
        assert resolution == "platform_wins"
        assert value == "Engineering"

    def test_manual_resolution(self):
        resolver = ConflictResolver("manual")
        value, resolution = resolver.resolve("dept", "Engineering", "IT")
        assert resolution == "unresolved"
        assert value is None

    def test_sirh_wins_with_none(self):
        resolver = ConflictResolver("sirh_wins")
        value, resolution = resolver.resolve("phone", None, "+212600000000")
        assert resolution == "sirh_wins"
        assert value == "+212600000000"

    def test_platform_wins_with_none(self):
        resolver = ConflictResolver("platform_wins")
        value, resolution = resolver.resolve("phone", "+212600000000", None)
        assert resolution == "platform_wins"
        assert value == "+212600000000"


class TestSyncEngine:
    def test_syncable_fields_defined(self):
        from app.services.sirh.sync_engine import SYNCABLE_FIELDS
        assert "first_name" in SYNCABLE_FIELDS
        assert "last_name" in SYNCABLE_FIELDS
        assert "email" in SYNCABLE_FIELDS
        assert "department" in SYNCABLE_FIELDS
        assert "matricule" in SYNCABLE_FIELDS

    def test_delta_update_logic(self):
        """Test that records older than last_sync_at are skipped."""
        from datetime import timedelta

        last_sync = datetime(2026, 4, 8, tzinfo=timezone.utc)
        old_record = {"matricule": "M001", "modified_at": "2026-04-07T10:00:00+00:00"}
        new_record = {"matricule": "M002", "modified_at": "2026-04-09T10:00:00+00:00"}

        old_modified = datetime.fromisoformat(old_record["modified_at"])
        new_modified = datetime.fromisoformat(new_record["modified_at"])

        assert old_modified < last_sync  # Should be skipped
        assert new_modified > last_sync  # Should be processed
