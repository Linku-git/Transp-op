from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_financial_scenario(
    client: AsyncClient,
    token: str,
    **overrides: object,
) -> tuple[dict, int]:
    """Create a financial scenario and return (json, status_code)."""
    payload: dict = {
        "name": "Test Scenario",
        "investment_model": "capex",
        "duration_years": 5,
        "fleet_composition": {},
        "params": {},
    }
    payload.update(overrides)
    resp = await client.post(
        "/api/v1/financial/scenarios",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    return resp.json(), resp.status_code


async def _create_tco_entry(
    client: AsyncClient,
    token: str,
    scenario_id: str,
    **overrides: object,
) -> tuple[dict, int]:
    """Create a TCO entry under a financial scenario."""
    payload: dict = {
        "vehicle_type": "minibus",
        "motorization": "diesel",
        "quantity": 3,
        "purchase_price": 150000.00,
        "annual_maintenance_cost": 5000.00,
        "energy_cost_per_km": 0.12,
        "annual_km": 50000.00,
    }
    payload.update(overrides)
    resp = await client.post(
        f"/api/v1/financial/scenarios/{scenario_id}/tco-entries",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    return resp.json(), resp.status_code


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_financial_scenario(client: AsyncClient) -> None:
    """POST /financial/scenarios creates a scenario with all fields."""
    token = await login_as_admin(client)

    data, sc = await _create_financial_scenario(
        client,
        token,
        name="Test Scenario",
        investment_model="capex",
        duration_years=5,
    )
    assert sc == 201, f"Expected 201, got {sc}: {data}"
    assert data["name"] == "Test Scenario"
    assert data["investment_model"] == "capex"
    assert data["duration_years"] == 5
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_update_financial_scenario(client: AsyncClient) -> None:
    """PUT /financial/scenarios/{id} updates name and duration."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    data, sc = await _create_financial_scenario(client, token)
    assert sc == 201
    scenario_id = data["id"]

    resp = await client.put(
        f"/api/v1/financial/scenarios/{scenario_id}",
        headers=headers,
        json={"name": "Updated Scenario", "duration_years": 7},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["name"] == "Updated Scenario"
    assert updated["duration_years"] == 7
    assert updated["id"] == scenario_id


@pytest.mark.asyncio
async def test_delete_financial_scenario(client: AsyncClient) -> None:
    """DELETE /financial/scenarios/{id} removes scenario and cascades to TCO entries."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create scenario
    data, sc = await _create_financial_scenario(client, token)
    assert sc == 201
    scenario_id = data["id"]

    # Create a TCO entry under it
    tco_data, tco_sc = await _create_tco_entry(client, token, scenario_id)
    assert tco_sc == 201

    # Delete scenario
    del_resp = await client.delete(
        f"/api/v1/financial/scenarios/{scenario_id}",
        headers=headers,
    )
    assert del_resp.status_code == 204

    # GET deleted scenario should return 404
    get_resp = await client.get(
        f"/api/v1/financial/scenarios/{scenario_id}",
        headers=headers,
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_tco_entry(client: AsyncClient) -> None:
    """POST /financial/scenarios/{id}/tco-entries creates a TCO entry."""
    token = await login_as_admin(client)

    # Create scenario first
    scenario_data, sc = await _create_financial_scenario(client, token)
    assert sc == 201
    scenario_id = scenario_data["id"]

    # Create TCO entry
    data, tco_sc = await _create_tco_entry(
        client,
        token,
        scenario_id,
        vehicle_type="minibus",
        motorization="diesel",
        quantity=3,
        purchase_price=150000.00,
        annual_maintenance_cost=5000.00,
        energy_cost_per_km=0.12,
        annual_km=50000.00,
    )
    assert tco_sc == 201, f"Expected 201, got {tco_sc}: {data}"
    assert data["financial_scenario_id"] == scenario_id
    assert data["vehicle_type"] == "minibus"
    assert data["motorization"] == "diesel"
    assert data["quantity"] == 3
    assert float(data["purchase_price"]) == 150000.00
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tco_entries(client: AsyncClient) -> None:
    """GET /financial/scenarios/{id}/tco-entries returns entries for the scenario."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create scenario
    scenario_data, sc = await _create_financial_scenario(client, token)
    assert sc == 201
    scenario_id = scenario_data["id"]

    # Create 2 TCO entries
    await _create_tco_entry(client, token, scenario_id, vehicle_type="minibus")
    await _create_tco_entry(client, token, scenario_id, vehicle_type="midibus")

    resp = await client.get(
        f"/api/v1/financial/scenarios/{scenario_id}/tco-entries",
        headers=headers,
    )
    assert resp.status_code == 200
    entries = resp.json()
    assert isinstance(entries, list)
    assert len(entries) >= 2
    vehicle_types = [e["vehicle_type"] for e in entries]
    assert "minibus" in vehicle_types
    assert "midibus" in vehicle_types


@pytest.mark.asyncio
async def test_schema_validation(client: AsyncClient) -> None:
    """Validation rejects invalid investment_model, vehicle_type, and negative prices."""
    token = await login_as_admin(client)

    # Invalid investment_model
    data, sc = await _create_financial_scenario(
        client, token, investment_model="invalid",
    )
    assert sc == 422, f"Expected 422 for invalid investment_model, got {sc}: {data}"

    # Create valid scenario for TCO validation tests
    scenario_data, scenario_sc = await _create_financial_scenario(client, token)
    assert scenario_sc == 201
    scenario_id = scenario_data["id"]

    # Invalid vehicle_type
    data, sc = await _create_tco_entry(
        client, token, scenario_id, vehicle_type="invalid_type",
    )
    assert sc == 422, f"Expected 422 for invalid vehicle_type, got {sc}: {data}"

    # Negative purchase_price
    data, sc = await _create_tco_entry(
        client, token, scenario_id, purchase_price=-5000.00,
    )
    assert sc == 422, f"Expected 422 for negative purchase_price, got {sc}: {data}"


@pytest.mark.asyncio
async def test_vehicle_catalog_endpoint(client: AsyncClient) -> None:
    """GET /financial/vehicles returns 200 with a list."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/financial/vehicles", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
