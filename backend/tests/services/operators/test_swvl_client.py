"""Tests for SWVL API Client (Session 83)."""
from __future__ import annotations

import pytest

from app.services.operators.swvl_client import SWVLClient
from app.services.operators.base_operator_client import SizingPlanPayload, OperatorResponse


SAMPLE_PAYLOAD = SizingPlanPayload(
    plan_id="plan-002",
    version=2,
    vehicles=[
        {"type": "standard", "count": 8, "capacity": 40, "pmr_accessible": True},
    ],
    routes=[
        {"name": "Route B", "stops": ["Campus", "Station", "Factory"], "distance_km": 15},
    ],
    schedules=[{"shift": "afternoon", "departure": "14:00"}],
    passenger_counts={"total": 300, "by_site": {"SITE-A": 200, "SITE-B": 100}},
    pmr_requirements={"pmr_employees": 10, "pmr_vehicles_needed": 1},
    rti_targets={"on_time_target_pct": 90, "max_wait_minutes": 15, "real_time_tracking": True},
)


class TestSWVLAuth:
    @pytest.mark.asyncio
    async def test_authenticate(self):
        client = SWVLClient({"client_id": "test-client"})
        result = await client.authenticate()
        assert result is True
        assert client.is_authenticated is True

    def test_unauthenticated_initially(self):
        client = SWVLClient({})
        assert client.is_authenticated is False


class TestSWVLSizingPlan:
    @pytest.mark.asyncio
    async def test_send_sizing_plan(self):
        client = SWVLClient({"client_id": "test"})
        response = await client.send_sizing_plan(SAMPLE_PAYLOAD)
        assert response.success is True
        assert response.reference_id is not None
        assert "swvl_ref" in response.reference_id

    def test_format_sizing_plan(self):
        client = SWVLClient({})
        formatted = client.format_sizing_plan(SAMPLE_PAYLOAD)
        plan = formatted["corporate_plan"]
        assert plan["plan_reference"] == "plan-002"
        assert plan["plan_version"] == 2
        assert len(plan["fleet_requirements"]) == 1
        assert plan["fleet_requirements"][0]["bus_type"] == "standard"
        assert plan["fleet_requirements"][0]["wheelchair_accessible"] is True
        assert plan["ridership"]["total_commuters"] == 300
        assert plan["accessibility"]["wheelchair_users"] == 10
        assert plan["sla"]["punctuality_target"] == 90
        assert plan["sla"]["real_time_tracking"] is True

    def test_validate_format_valid(self):
        client = SWVLClient({})
        formatted = client.format_sizing_plan(SAMPLE_PAYLOAD)
        errors = client.validate_format(formatted)
        assert errors == []

    def test_validate_format_missing_reference(self):
        client = SWVLClient({})
        errors = client.validate_format({"corporate_plan": {"fleet_requirements": []}})
        assert "Missing plan_reference" in errors

    def test_validate_format_missing_fleet(self):
        client = SWVLClient({})
        errors = client.validate_format({"corporate_plan": {"plan_reference": "x"}})
        assert "Missing or invalid fleet_requirements" in errors


class TestSWVLDataExchange:
    @pytest.mark.asyncio
    async def test_get_schedules(self):
        client = SWVLClient({"client_id": "test"})
        result = await client.get_schedules()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_capacity(self):
        client = SWVLClient({"client_id": "test"})
        result = await client.get_capacity()
        assert "available_buses" in result

    @pytest.mark.asyncio
    async def test_get_routes(self):
        client = SWVLClient({"client_id": "test"})
        result = await client.get_routes()
        assert isinstance(result, list)


class TestBaseClient:
    def test_sizing_plan_payload(self):
        payload = SizingPlanPayload(plan_id="p1", version=1)
        assert payload.plan_id == "p1"
        assert payload.vehicles == []
        assert payload.routes == []

    def test_operator_response(self):
        resp = OperatorResponse(success=True, reference_id="ref1", message="OK")
        assert resp.success is True
        assert resp.reference_id == "ref1"
