from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASELINE_METRICS = {
    "total_employees": 100,
    "employees_assigned": 80,
    "total_clusters": 10,
    "total_vehicles_used": 8,
    "avg_occupancy_rate": 0.75,
    "total_distance_km": 200.0,
    "total_duration_minutes": 150.0,
    "estimated_fuel_liters": 30.0,
    "estimated_fuel_cost_mad": 360.0,
    "co2_estimate_kg": 80.4,
    "time_saved_vs_individual_hours": 25.0,
    "unassigned_clusters": 0,
}


async def _create_site(
    client: AsyncClient, token: str, name: str = "Scenario Site"
) -> str:
    code = f"SC-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue Scenario",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_baseline_optimization(
    client: AsyncClient,
    token: str,
    site_id: str,
) -> str:
    """Create a completed optimization record by mocking the pipeline.

    We insert via the optimize endpoint with mocked Celery task, then
    directly patch the DB record to 'completed' with metrics.
    """
    from app.database import async_session_factory
    from app.models.optimization import Optimization

    # Get tenant_id from site
    resp = await client.get(
        f"/api/v1/sites/{site_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    tenant_id = resp.json()["tenant_id"]

    # Insert optimization record directly
    async with async_session_factory() as session:
        async with session.begin():
            opt = Optimization(
                tenant_id=uuid.UUID(tenant_id),
                site_id=uuid.UUID(site_id),
                condition_type="normal",
                status="completed",
                params={"algorithm": "dbscan", "eps_meters": 500},
                metrics=BASELINE_METRICS,
                completed_at=datetime.now(timezone.utc),
            )
            session.add(opt)
            await session.flush()
            opt_id = str(opt.id)
    return opt_id


async def _simulate(
    client: AsyncClient,
    token: str,
    site_id: str,
    condition_type: str,
    demand_multiplier: float | None = None,
    name: str | None = None,
) -> dict:
    """Helper to POST /scenarios/simulate."""
    body: dict = {
        "site_id": site_id,
        "condition_type": condition_type,
    }
    if demand_multiplier is not None:
        body["demand_multiplier"] = demand_multiplier
    if name is not None:
        body["name"] = name

    resp = await client.post(
        "/api/v1/scenarios/simulate",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )
    return {"status_code": resp.status_code, "data": resp.json()}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_simulate_rain(client: AsyncClient) -> None:
    """Rain scenario increases vehicle demand with 1.15x multiplier."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    result = await _simulate(client, token, site_id, "rain")
    assert result["status_code"] == 201

    data = result["data"]
    assert data["condition_type"] == "rain"
    assert data["demand_multiplier"] == 1.15
    metrics = data["estimated_metrics"]
    assert metrics["total_vehicles_used"] > BASELINE_METRICS["total_vehicles_used"]
    assert metrics["total_distance_km"] > BASELINE_METRICS["total_distance_km"]
    assert metrics["co2_estimate_kg"] > BASELINE_METRICS["co2_estimate_kg"]


@pytest.mark.asyncio
async def test_simulate_strike(client: AsyncClient) -> None:
    """Strike scenario increases demand significantly with 1.5x multiplier."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    result = await _simulate(client, token, site_id, "strike")
    assert result["status_code"] == 201

    data = result["data"]
    assert data["condition_type"] == "strike"
    assert data["demand_multiplier"] == 1.5
    metrics = data["estimated_metrics"]
    # Strike should increase more than rain
    assert metrics["total_vehicles_used"] >= 12  # ceil(8 * 1.5) = 12
    assert metrics["estimated_fuel_cost_mad"] > BASELINE_METRICS["estimated_fuel_cost_mad"]


@pytest.mark.asyncio
async def test_simulate_peak(client: AsyncClient) -> None:
    """Peak scenario handles extra headcount with 1.3x multiplier."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    result = await _simulate(client, token, site_id, "peak")
    assert result["status_code"] == 201

    data = result["data"]
    assert data["condition_type"] == "peak"
    assert data["demand_multiplier"] == 1.3
    metrics = data["estimated_metrics"]
    assert metrics["total_vehicles_used"] > BASELINE_METRICS["total_vehicles_used"]
    assert metrics["employees_assigned"] <= BASELINE_METRICS["total_employees"]


@pytest.mark.asyncio
async def test_compare_scenarios(client: AsyncClient) -> None:
    """Comparison of two scenarios returns meaningful delta metrics."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    # Create two scenarios
    rain = await _simulate(client, token, site_id, "rain", name="Rain")
    strike = await _simulate(client, token, site_id, "strike", name="Strike")
    assert rain["status_code"] == 201
    assert strike["status_code"] == 201

    rain_id = rain["data"]["id"]
    strike_id = strike["data"]["id"]

    resp = await client.post(
        "/api/v1/scenarios/compare",
        headers={"Authorization": f"Bearer {token}"},
        json={"scenario_ids": [rain_id, strike_id]},
    )
    assert resp.status_code == 200

    data = resp.json()
    assert len(data["scenarios"]) == 2
    assert len(data["deltas"]) == 1

    delta = data["deltas"][0]
    # Strike uses more vehicles than rain
    assert delta["vehicles_delta"] > 0
    assert delta["cost_delta_mad"] > 0
    assert delta["co2_delta_kg"] > 0


@pytest.mark.asyncio
async def test_list_scenarios(client: AsyncClient) -> None:
    """Listing returns saved scenarios ordered by created_at desc."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    await _simulate(client, token, site_id, "rain", name="Rain Test")
    await _simulate(client, token, site_id, "peak", name="Peak Test")

    resp = await client.get(
        "/api/v1/scenarios",
        headers={"Authorization": f"Bearer {token}"},
        params={"site_id": site_id},
    )
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) >= 2
    # Most recent first
    assert data[0]["created_at"] >= data[1]["created_at"]


@pytest.mark.asyncio
async def test_delete_scenario(client: AsyncClient) -> None:
    """Deleting a scenario removes it, subsequent GET returns 404."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_baseline_optimization(client, token, site_id)

    result = await _simulate(client, token, site_id, "night")
    assert result["status_code"] == 201
    scenario_id = result["data"]["id"]

    # Delete
    resp = await client.delete(
        f"/api/v1/scenarios/{scenario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Scenario deleted"

    # Verify 404
    resp = await client.get(
        f"/api/v1/scenarios/{scenario_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
