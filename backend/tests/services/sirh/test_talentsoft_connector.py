"""Tests for Talentsoft Connector (Session 80)."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from app.services.sirh.talentsoft_connector import (
    TalentsoftConnector,
    TalentsoftAPIError,
    RATE_LIMIT_PER_HOUR,
)
from app.services.sirh.talentsoft_field_mapping import (
    TALENTSOFT_FIELD_MAP,
    TALENTSOFT_DEPARTMENT_MAP,
    TALENTSOFT_SCHEDULE_MAP,
    parse_talentsoft_date,
    map_talentsoft_employee,
)


class TestTalentsoftAuth:
    def test_authenticated_with_key(self):
        c = TalentsoftConnector({"api_key": "ts-key-123"})
        assert c.is_authenticated is True

    def test_unauthenticated_without_key(self):
        c = TalentsoftConnector({})
        assert c.is_authenticated is False


class TestTalentsoftFieldMapping:
    def test_field_map_completeness(self):
        assert "employeeId" in TALENTSOFT_FIELD_MAP
        assert "firstName" in TALENTSOFT_FIELD_MAP
        assert "lastName" in TALENTSOFT_FIELD_MAP
        assert "professionalEmail" in TALENTSOFT_FIELD_MAP

    def test_parse_date_iso(self):
        result = parse_talentsoft_date("2026-04-09T10:00:00Z")
        assert result is not None and "2026-04-09" in result

    def test_parse_date_french(self):
        result = parse_talentsoft_date("09/04/2026")
        assert result is not None and "2026" in result

    def test_parse_date_none(self):
        assert parse_talentsoft_date(None) is None

    def test_map_basic_employee(self):
        record = {
            "employeeId": "TS001",
            "firstName": "Karim",
            "lastName": "Benali",
            "professionalEmail": "karim@company.ma",
            "organizationalUnit": "IT",
        }
        result = map_talentsoft_employee(record)
        assert result["matricule"] == "TS001"
        assert result["first_name"] == "Karim"
        assert result["email"] == "karim@company.ma"

    def test_map_department_code(self):
        record = {"employeeId": "TS002", "organizationalUnit": "TS_PROD"}
        result = map_talentsoft_employee(record)
        assert result["department"] == "Production"

    def test_map_schedule(self):
        record = {"employeeId": "TS003", "workSchedule": "MATIN"}
        result = map_talentsoft_employee(record)
        assert result["shift_time"] == "Équipe Matin"

    def test_map_with_training(self):
        record = {
            "employeeId": "TS004",
            "trainingRecords": [
                {"title": "Sécurité", "completionDate": "2026-03-01", "score": 85},
            ],
        }
        result = map_talentsoft_employee(record)
        assert len(result["training_records"]) == 1
        assert result["training_records"][0]["title"] == "Sécurité"


class TestTalentsoftSync:
    @pytest.mark.asyncio
    async def test_fetch_employees(self):
        c = TalentsoftConnector({"api_key": "key"})
        result = await c.fetch_employees()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_training(self):
        c = TalentsoftConnector({"api_key": "key"})
        result = await c.fetch_training_records()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_delta_sync(self):
        c = TalentsoftConnector({"api_key": "key"})
        result = await c.run_full_sync(since=datetime.now(timezone.utc) - timedelta(hours=1))
        assert result["sync_type"] == "delta"

    @pytest.mark.asyncio
    async def test_full_sync(self):
        c = TalentsoftConnector({"api_key": "key"})
        result = await c.run_full_sync()
        assert result["sync_type"] == "full"


class TestTalentsoftRateLimit:
    def test_rate_limit_config(self):
        assert RATE_LIMIT_PER_HOUR == 1000

    def test_custom_rate_limit(self):
        c = TalentsoftConnector({"api_key": "key", "rate_limit": 500})
        assert c.rate_limit == 500

    def test_error_with_status(self):
        e = TalentsoftAPIError("Rate limited", status_code=429)
        assert e.status_code == 429
