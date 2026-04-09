"""Tests for Workday Connector (Session 79)."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from app.services.sirh.workday_connector import (
    WorkdayConnector,
    WorkdayAuthError,
    WorkdayAPIError,
    MAX_RETRIES,
    DEFAULT_PAGE_SIZE,
)
from app.services.sirh.workday_field_mapping import (
    WORKDAY_FIELD_MAP,
    WORKDAY_DEPARTMENT_MAP,
    WORKDAY_SCHEDULE_MAP,
    WORKDAY_STATUS_MAP,
    parse_workday_date,
    resolve_wid_reference,
    get_effective_record,
    map_workday_employee,
    map_workday_position,
    map_workday_schedule,
)


class TestWorkdayAuthentication:
    @pytest.mark.asyncio
    async def test_authenticate_returns_token(self):
        connector = WorkdayConnector({"tenant_name": "test_tenant"})
        token = await connector.authenticate()
        assert token is not None
        assert "wd_token" in token
        assert connector.is_authenticated is True

    @pytest.mark.asyncio
    async def test_cached_token_reused(self):
        connector = WorkdayConnector({"tenant_name": "test_tenant"})
        t1 = await connector.authenticate()
        t2 = await connector.authenticate()
        assert t1 == t2

    @pytest.mark.asyncio
    async def test_refresh_token(self):
        connector = WorkdayConnector({"tenant_name": "test_tenant"})
        await connector.authenticate()
        await connector.refresh_token()
        assert connector.is_authenticated is True

    def test_unauthenticated_initially(self):
        connector = WorkdayConnector({})
        assert connector.is_authenticated is False


class TestWorkdayFieldMapping:
    def test_field_map_completeness(self):
        assert "Worker_ID" in WORKDAY_FIELD_MAP
        assert "First_Name" in WORKDAY_FIELD_MAP
        assert "Last_Name" in WORKDAY_FIELD_MAP
        assert "Email_Address" in WORKDAY_FIELD_MAP
        assert "Department_Name" in WORKDAY_FIELD_MAP
        assert "Schedule_Name" in WORKDAY_FIELD_MAP
        assert "Last_Modified" in WORKDAY_FIELD_MAP

    def test_parse_date_iso(self):
        result = parse_workday_date("2026-04-09T10:30:00Z")
        assert result is not None
        assert "2026-04-09" in result

    def test_parse_date_with_offset(self):
        result = parse_workday_date("2026-04-09T10:30:00.000-07:00")
        assert result is not None

    def test_parse_date_only(self):
        result = parse_workday_date("2026-04-09")
        assert result is not None
        assert "2026-04-09" in result

    def test_parse_date_none(self):
        assert parse_workday_date(None) is None

    def test_parse_date_invalid(self):
        assert parse_workday_date("not-a-date") is None


class TestWIDReferences:
    def test_resolve_descriptor(self):
        ref = {"WID": "abc123", "Descriptor": "Human Resources"}
        assert resolve_wid_reference(ref) == "Human Resources"

    def test_resolve_wid_only(self):
        ref = {"WID": "abc123"}
        assert resolve_wid_reference(ref) == "abc123"

    def test_resolve_string(self):
        assert resolve_wid_reference("direct_value") == "direct_value"

    def test_resolve_none(self):
        assert resolve_wid_reference(None) is None

    def test_resolve_id_fallback(self):
        ref = {"ID": "id123"}
        assert resolve_wid_reference(ref) == "id123"


class TestEffectiveDating:
    def test_get_most_recent_record(self):
        records = [
            {"Effective_Date": "2026-01-01T00:00:00Z", "Department": "Old"},
            {"Effective_Date": "2026-04-01T00:00:00Z", "Department": "Current"},
            {"Effective_Date": "2026-07-01T00:00:00Z", "Department": "Future"},
        ]
        as_of = datetime(2026, 5, 1, tzinfo=timezone.utc)
        result = get_effective_record(records, as_of)
        assert result is not None
        assert result["Department"] == "Current"

    def test_empty_records(self):
        assert get_effective_record([]) is None

    def test_no_effective_date(self):
        records = [{"Department": "Only"}]
        result = get_effective_record(records)
        assert result is not None
        assert result["Department"] == "Only"

    def test_all_future(self):
        records = [
            {"Effective_Date": "2099-01-01T00:00:00Z", "Department": "Future"},
        ]
        result = get_effective_record(records)
        # Should return first record as fallback when none are valid
        assert result is not None


class TestEmployeeMapping:
    def test_map_basic_employee(self):
        wd_record = {
            "Worker_ID": "WD001",
            "First_Name": "Fatima",
            "Last_Name": "Zahra",
            "Email_Address": "fatima@company.ma",
            "Phone_Number": "+212600000001",
            "Department_Name": "IT",
            "Worker_Status": "Active",
        }
        result = map_workday_employee(wd_record)
        assert result["matricule"] == "WD001"
        assert result["first_name"] == "Fatima"
        assert result["last_name"] == "Zahra"
        assert result["email"] == "fatima@company.ma"
        assert result["is_active"] is True

    def test_map_department_wid(self):
        wd_record = {
            "Worker_ID": "WD002",
            "First_Name": "Test",
            "Last_Name": "User",
            "Department_Name": "WD_DEP_PROD",
        }
        result = map_workday_employee(wd_record)
        assert result["department"] == "Production"

    def test_map_schedule_wid(self):
        wd_record = {
            "Worker_ID": "WD003",
            "First_Name": "Test",
            "Last_Name": "User",
            "Schedule_Name": "WD_SCH_MORNING",
        }
        result = map_workday_employee(wd_record)
        assert result["shift_time"] == "Équipe Matin"

    def test_map_wid_reference_object(self):
        wd_record = {
            "Worker_ID": "WD004",
            "First_Name": "Test",
            "Last_Name": "User",
            "Department_Name": {"WID": "dep123", "Descriptor": "Quality Control"},
        }
        result = map_workday_employee(wd_record)
        assert result["department"] == "Quality Control"

    def test_map_with_position_data(self):
        wd_record = {
            "Worker_ID": "WD005",
            "First_Name": "Test",
            "Last_Name": "User",
            "Position_Data": {
                "Job_Title": {"Descriptor": "Senior Engineer"},
                "Location": {"Descriptor": "Casablanca Factory"},
            },
        }
        result = map_workday_employee(wd_record)
        assert result["job_title"] == "Senior Engineer"
        assert result["site_name"] == "Casablanca Factory"

    def test_map_with_contact_data(self):
        wd_record = {
            "Worker_ID": "WD006",
            "First_Name": "Test",
            "Last_Name": "User",
            "Contact_Data": {
                "Email_Address": "contact@company.ma",
                "Phone_Number": "+212611111111",
            },
        }
        result = map_workday_employee(wd_record)
        assert result["email"] == "contact@company.ma"
        assert result["phone"] == "+212611111111"

    def test_map_terminated_status(self):
        wd_record = {
            "Worker_ID": "WD007",
            "First_Name": "Test",
            "Last_Name": "User",
            "Worker_Status": "Terminated",
        }
        result = map_workday_employee(wd_record)
        assert result["is_active"] is False

    def test_map_handles_missing_fields(self):
        wd_record = {"Worker_ID": "WD008"}
        result = map_workday_employee(wd_record)
        assert result["matricule"] == "WD008"
        assert "email" not in result


class TestPositionAndScheduleMapping:
    def test_map_position(self):
        wd_record = {
            "Job_Title": {"Descriptor": "Plant Manager"},
            "Department": {"Descriptor": "Production"},
            "Location": {"Descriptor": "Casablanca"},
            "Worker_Reference": {"WID": "WD001"},
        }
        result = map_workday_position(wd_record)
        assert result["title"] == "Plant Manager"
        assert result["department"] == "Production"
        assert result["worker_id"] == "WD001"

    def test_map_schedule(self):
        wd_record = {
            "Schedule_Name": "WD_SCH_NIGHT",
            "Worker_Reference": {"WID": "WD001"},
        }
        result = map_workday_schedule(wd_record)
        assert result["name"] == "Équipe Nuit"
        assert result["code"] == "WD_SCH_NIGHT"


class TestWorkdayDataSync:
    @pytest.mark.asyncio
    async def test_fetch_employees(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        result = await connector.fetch_employees()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_employees_delta(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        result = await connector.fetch_employees(since=since)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_positions(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        result = await connector.fetch_positions()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_schedules(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        result = await connector.fetch_schedules()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_full_sync(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        result = await connector.run_full_sync()
        assert result["sync_type"] == "full"

    @pytest.mark.asyncio
    async def test_delta_sync(self):
        connector = WorkdayConnector({"tenant_name": "test"})
        result = await connector.run_full_sync(
            since=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        assert result["sync_type"] == "delta"


class TestPaginationAndRetry:
    def test_default_page_size(self):
        assert DEFAULT_PAGE_SIZE == 100

    def test_custom_page_size(self):
        connector = WorkdayConnector({"page_size": 50})
        assert connector.page_size == 50

    def test_retry_config(self):
        assert MAX_RETRIES == 3

    def test_workday_api_error(self):
        error = WorkdayAPIError("Rate limited", status_code=429)
        assert error.status_code == 429

    def test_workday_auth_error(self):
        error = WorkdayAuthError("Invalid credentials")
        assert "Invalid credentials" in str(error)
