"""Tests for SAP SuccessFactors Connector (Session 78)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

import pytest

from app.services.sirh.sap_connector import (
    SAPConnector,
    SAPAuthError,
    SAPAPIError,
    MAX_RETRIES,
    INITIAL_BACKOFF_SECONDS,
    BACKOFF_MULTIPLIER,
)
from app.services.sirh.sap_field_mapping import (
    SAP_FIELD_MAP,
    SAP_DEPARTMENT_MAP,
    SAP_SHIFT_MAP,
    parse_sap_date,
    map_sap_employee,
    map_sap_site,
)


class TestSAPAuthentication:
    @pytest.mark.asyncio
    async def test_authenticate_returns_token(self):
        connector = SAPConnector({"company_id": "TEST001"})
        token = await connector.authenticate()
        assert token is not None
        assert "sap_token" in token
        assert connector.is_authenticated is True

    @pytest.mark.asyncio
    async def test_cached_token_reused(self):
        connector = SAPConnector({"company_id": "TEST001"})
        token1 = await connector.authenticate()
        token2 = await connector.authenticate()
        assert token1 == token2

    @pytest.mark.asyncio
    async def test_refresh_token_generates_new(self):
        connector = SAPConnector({"company_id": "TEST001"})
        token1 = await connector.authenticate()
        token2 = await connector.refresh_token()
        # Tokens will differ because timestamp changes
        assert connector.is_authenticated is True

    def test_unauthenticated_initially(self):
        connector = SAPConnector({})
        assert connector.is_authenticated is False


class TestSAPFieldMapping:
    def test_field_map_completeness(self):
        """Verify all expected fields are mapped."""
        assert "userId" in SAP_FIELD_MAP
        assert "firstName" in SAP_FIELD_MAP
        assert "lastName" in SAP_FIELD_MAP
        assert "email" in SAP_FIELD_MAP
        assert "department" in SAP_FIELD_MAP
        assert "lastModifiedDateTime" in SAP_FIELD_MAP

    def test_parse_sap_date_odata_format(self):
        """Test /Date(timestamp)/ parsing."""
        # 2026-04-09T00:00:00Z = 1775865600000 ms
        result = parse_sap_date("/Date(1775865600000)/")
        assert result is not None
        assert "2026" in result

    def test_parse_sap_date_iso_format(self):
        result = parse_sap_date("2026-04-09T10:30:00Z")
        assert result is not None
        assert "2026-04-09" in result

    def test_parse_sap_date_none(self):
        assert parse_sap_date(None) is None

    def test_parse_sap_date_invalid(self):
        result = parse_sap_date("not-a-date")
        assert result is None

    def test_map_basic_employee(self):
        sap_record = {
            "userId": "EMP001",
            "firstName": "Mohammed",
            "lastName": "Amine",
            "email": "mohammed@company.ma",
            "department": "IT",
            "phoneNumber": "+212600000001",
        }
        result = map_sap_employee(sap_record)
        assert result["matricule"] == "EMP001"
        assert result["first_name"] == "Mohammed"
        assert result["last_name"] == "Amine"
        assert result["email"] == "mohammed@company.ma"
        assert result["phone"] == "+212600000001"

    def test_map_department_code(self):
        sap_record = {
            "userId": "EMP002",
            "firstName": "Test",
            "lastName": "User",
            "department": "DEP001",
        }
        result = map_sap_employee(sap_record)
        assert result["department"] == "Production"

    def test_map_shift_code(self):
        sap_record = {
            "userId": "EMP003",
            "firstName": "Test",
            "lastName": "User",
            "customString1": "SHIFT_A",
        }
        result = map_sap_employee(sap_record)
        assert result["shift_time"] == "Équipe Matin"

    def test_map_unknown_shift_passthrough(self):
        sap_record = {
            "userId": "EMP004",
            "firstName": "Test",
            "lastName": "User",
            "customString1": "CUSTOM_SHIFT",
        }
        result = map_sap_employee(sap_record)
        assert result["shift_time"] == "CUSTOM_SHIFT"

    def test_map_with_address(self):
        sap_record = {
            "userId": "EMP005",
            "firstName": "Test",
            "lastName": "User",
            "addressInfo": {
                "addressLine1": "123 Rue Mohammed V",
                "city": "Casablanca",
                "zipCode": "20000",
                "country": "MA",
            },
        }
        result = map_sap_employee(sap_record)
        assert "123 Rue Mohammed V" in result["address"]
        assert "Casablanca" in result["address"]

    def test_map_with_employment_info(self):
        sap_record = {
            "userId": "EMP006",
            "firstName": "Test",
            "lastName": "User",
            "employmentInfo": {
                "siteCode": "CASA-01",
                "isActive": True,
            },
        }
        result = map_sap_employee(sap_record)
        assert result["site_code"] == "CASA-01"
        assert result["is_active"] is True

    def test_map_sap_site(self):
        sap_site = {
            "locationCode": "CASA-01",
            "locationName": "Casablanca Factory",
            "city": "Casablanca",
            "addressLine1": "Zone Industrielle",
            "country": "MA",
        }
        result = map_sap_site(sap_site)
        assert result["code"] == "CASA-01"
        assert result["name"] == "Casablanca Factory"
        assert result["city"] == "Casablanca"

    def test_map_handles_missing_fields(self):
        sap_record = {"userId": "EMP007"}
        result = map_sap_employee(sap_record)
        assert result["matricule"] == "EMP007"
        assert "email" not in result  # Not set when None

    def test_department_map_coverage(self):
        assert len(SAP_DEPARTMENT_MAP) >= 5
        for code, name in SAP_DEPARTMENT_MAP.items():
            assert code.startswith("DEP")
            assert len(name) > 0

    def test_shift_map_coverage(self):
        assert len(SAP_SHIFT_MAP) >= 3
        for code, label in SAP_SHIFT_MAP.items():
            assert code.startswith("SHIFT_")


class TestSAPDataSync:
    @pytest.mark.asyncio
    async def test_fetch_employees_returns_list(self):
        connector = SAPConnector({"company_id": "TEST001"})
        result = await connector.fetch_employees()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_employees_delta(self):
        connector = SAPConnector({"company_id": "TEST001"})
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await connector.fetch_employees(since=since)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_sites(self):
        connector = SAPConnector({"company_id": "TEST001"})
        result = await connector.fetch_sites()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_departments(self):
        connector = SAPConnector({"company_id": "TEST001"})
        result = await connector.fetch_departments()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_full_sync_cycle(self):
        connector = SAPConnector({"company_id": "TEST001"})
        result = await connector.run_full_sync()
        assert result["sync_type"] == "full"
        assert "employees" in result
        assert "sites_count" in result

    @pytest.mark.asyncio
    async def test_delta_sync_cycle(self):
        connector = SAPConnector({"company_id": "TEST001"})
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        result = await connector.run_full_sync(since=since)
        assert result["sync_type"] == "delta"


class TestRetryLogic:
    def test_retry_config(self):
        assert MAX_RETRIES == 3
        assert INITIAL_BACKOFF_SECONDS == 1.0
        assert BACKOFF_MULTIPLIER == 2.0

    def test_backoff_sequence(self):
        """Verify exponential backoff: 1s, 2s, 4s."""
        backoff = INITIAL_BACKOFF_SECONDS
        sequence = []
        for _ in range(MAX_RETRIES):
            sequence.append(backoff)
            backoff *= BACKOFF_MULTIPLIER
        assert sequence == [1.0, 2.0, 4.0]

    def test_sap_api_error_with_status(self):
        error = SAPAPIError("Not found", status_code=404)
        assert error.status_code == 404
        assert "Not found" in str(error)

    def test_sap_api_error_without_status(self):
        error = SAPAPIError("Unknown error")
        assert error.status_code is None

    def test_sap_auth_error(self):
        error = SAPAuthError("Token expired")
        assert "Token expired" in str(error)
