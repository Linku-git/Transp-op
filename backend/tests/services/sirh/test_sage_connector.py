"""Tests for Sage Connector (Session 80)."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from app.services.sirh.sage_connector import (
    SageConnector,
    SageAPIError,
    RATE_LIMIT_PER_HOUR,
)
from app.services.sirh.sage_field_mapping import (
    SAGE_FIELD_MAP,
    SAGE_DEPARTMENT_MAP,
    SAGE_SHIFT_MAP,
    parse_sage_date,
    map_sage_employee,
)


class TestSageAuth:
    def test_authenticated_with_key(self):
        c = SageConnector({"api_key": "sage-key-123"})
        assert c.is_authenticated is True

    def test_unauthenticated_without_key(self):
        c = SageConnector({})
        assert c.is_authenticated is False


class TestSageFieldMapping:
    def test_field_map_completeness(self):
        assert "matricule" in SAGE_FIELD_MAP
        assert "prenom" in SAGE_FIELD_MAP
        assert "nom" in SAGE_FIELD_MAP
        assert "email_pro" in SAGE_FIELD_MAP

    def test_parse_date_french(self):
        result = parse_sage_date("09/04/2026")
        assert result is not None and "2026" in result

    def test_parse_date_iso(self):
        result = parse_sage_date("2026-04-09")
        assert result is not None and "2026-04-09" in result

    def test_parse_date_none(self):
        assert parse_sage_date(None) is None

    def test_map_basic_employee(self):
        record = {
            "matricule": "SG001",
            "prenom": "Amina",
            "nom": "Elhilali",
            "email_pro": "amina@company.ma",
            "service": "Comptabilité",
        }
        result = map_sage_employee(record)
        assert result["matricule"] == "SG001"
        assert result["first_name"] == "Amina"
        assert result["department"] == "Comptabilité"

    def test_map_department_code(self):
        record = {"matricule": "SG002", "service": "SRV_PROD"}
        result = map_sage_employee(record)
        assert result["department"] == "Production"

    def test_map_shift(self):
        record = {"matricule": "SG003", "equipe": "EQ_NUIT"}
        result = map_sage_employee(record)
        assert result["shift_time"] == "Équipe Nuit"

    def test_map_with_payroll(self):
        record = {
            "matricule": "SG004",
            "bulletinPaie": {
                "salaire_brut": 8000,
                "salaire_net": 6200,
                "indemnite_transport": 500,
                "periode": "2026-04",
            },
        }
        result = map_sage_employee(record)
        assert result["payroll_data"]["gross_salary"] == 8000
        assert result["payroll_data"]["transport_allowance"] == 500


class TestSageSync:
    @pytest.mark.asyncio
    async def test_fetch_employees(self):
        c = SageConnector({"api_key": "key"})
        result = await c.fetch_employees()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_payroll(self):
        c = SageConnector({"api_key": "key"})
        result = await c.fetch_payroll(period="2026-04")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_delta_sync(self):
        c = SageConnector({"api_key": "key"})
        result = await c.run_full_sync(since=datetime.now(timezone.utc) - timedelta(hours=1))
        assert result["sync_type"] == "delta"

    @pytest.mark.asyncio
    async def test_full_sync(self):
        c = SageConnector({"api_key": "key"})
        result = await c.run_full_sync()
        assert result["sync_type"] == "full"


class TestSageRateLimit:
    def test_rate_limit_config(self):
        assert RATE_LIMIT_PER_HOUR == 500

    def test_custom_rate_limit(self):
        c = SageConnector({"api_key": "key", "rate_limit": 200})
        assert c.rate_limit == 200

    def test_error_with_status(self):
        e = SageAPIError("Server error", status_code=500)
        assert e.status_code == 500
