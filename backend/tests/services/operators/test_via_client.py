"""Tests for Via Transportation API Client (Session 83)."""
from __future__ import annotations

import pytest

from app.services.operators.via_client import ViaClient
from app.services.operators.base_operator_client import SizingPlanPayload, OperatorResponse


SAMPLE_PAYLOAD = SizingPlanPayload(
    plan_id="plan-001",
    version=1,
    vehicles=[
        {"type": "minibus", "count": 5, "capacity": 20, "pmr_accessible": True},
        {"type": "bus", "count": 3, "capacity": 50, "pmr_accessible": False},
    ],
    routes=[
        {"name": "Route A", "stops": ["Stop 1", "Stop 2", "Stop 3"]},
    ],
    schedules=[{"shift": "morning", "departure": "07:30"}],
    passenger_counts={"total": 200, "by_site": {"CASA-01": 120, "CASA-02": 80}},
    pmr_requirements={"pmr_employees": 15, "pmr_vehicles_needed": 2},
    rti_targets={"on_time_target_pct": 95, "max_wait_minutes": 10},
)


class TestViaAuth:
    @pytest.mark.asyncio
    async def test_authenticate(self):
        client = ViaClient({"org_id": "test-org"})
        result = await client.authenticate()
        assert result is True
        assert client.is_authenticated is True

    def test_unauthenticated_initially(self):
        client = ViaClient({})
        assert client.is_authenticated is False


class TestViaSizingPlan:
    @pytest.mark.asyncio
    async def test_send_sizing_plan(self):
        client = ViaClient({"org_id": "test-org"})
        response = await client.send_sizing_plan(SAMPLE_PAYLOAD)
        assert response.success is True
        assert response.reference_id is not None
        assert "via_ref" in response.reference_id

    def test_format_sizing_plan(self):
        client = ViaClient({})
        formatted = client.format_sizing_plan(SAMPLE_PAYLOAD)
        plan = formatted["service_plan"]
        assert plan["external_id"] == "plan-001"
        assert plan["version"] == 1
        assert len(plan["fleet"]) == 2
        assert plan["fleet"][0]["vehicle_type"] == "minibus"
        assert plan["fleet"][0]["pmr_accessible"] is True
        assert plan["demand"]["total_riders"] == 200
        assert plan["accessibility"]["pmr_riders"] == 15
        assert plan["performance_targets"]["on_time_pct"] == 95

    def test_validate_format_valid(self):
        client = ViaClient({})
        formatted = client.format_sizing_plan(SAMPLE_PAYLOAD)
        errors = client.validate_format(formatted)
        assert errors == []

    def test_validate_format_missing_id(self):
        client = ViaClient({})
        errors = client.validate_format({"service_plan": {"fleet": []}})
        assert "Missing external_id" in errors

    def test_validate_format_missing_fleet(self):
        client = ViaClient({})
        errors = client.validate_format({"service_plan": {"external_id": "x"}})
        assert "Missing or invalid fleet" in errors


class TestViaDataExchange:
    @pytest.mark.asyncio
    async def test_get_schedules(self):
        client = ViaClient({"org_id": "test"})
        result = await client.get_schedules()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_capacity(self):
        client = ViaClient({"org_id": "test"})
        result = await client.get_capacity()
        assert "available_vehicles" in result
        assert "max_passengers" in result

    @pytest.mark.asyncio
    async def test_get_routes(self):
        client = ViaClient({"org_id": "test"})
        result = await client.get_routes()
        assert isinstance(result, list)
