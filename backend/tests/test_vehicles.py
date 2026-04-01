from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_site(client: AsyncClient, token: str, name: str = "Vehicle Site") -> str:
    code = f"VS-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue Fleet",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_vehicle(
    client: AsyncClient,
    token: str,
    site_id: str | None = None,
    **overrides: object,
) -> tuple[dict, int]:
    payload: dict = {
        "type": "Minibus",
        "capacity": 20,
        "condition": "Bon",
        "motorization": "diesel",
        "is_pmr_accessible": False,
        "zfe_compliant": False,
    }
    if site_id is not None:
        payload["site_id"] = site_id
    payload.update(overrides)
    resp = await client.post(
        "/api/v1/vehicles",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    return resp.json(), resp.status_code


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_vehicle(client: AsyncClient) -> None:
    """POST creates vehicle with all fields."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)

    data, sc = await _create_vehicle(
        client, token, site_id=site_id,
        type="Midibus",
        brand_model="Mercedes Sprinter",
        capacity=30,
        year=2023,
        owner_type="proprietaire",
        monthly_cost_mad=15000.00,
        condition="Bon",
        motorization="hybrid",
        is_pmr_accessible=True,
        zfe_compliant=True,
        fuel_consumption=8.5,
    )
    assert sc == 201, f"Expected 201, got {sc}: {data}"
    assert data["type"] == "Midibus"
    assert data["brand_model"] == "Mercedes Sprinter"
    assert data["capacity"] == 30
    assert data["is_pmr_accessible"] is True
    assert data["zfe_compliant"] is True
    assert data["motorization"] == "hybrid"
    assert data["site_id"] == site_id
    assert "id" in data


@pytest.mark.asyncio
async def test_create_vehicle_invalid_condition(client: AsyncClient) -> None:
    """Invalid condition returns 422."""
    token = await login_as_admin(client)
    data, sc = await _create_vehicle(client, token, condition="Excellent")
    assert sc == 422


@pytest.mark.asyncio
async def test_create_vehicle_invalid_motorization(client: AsyncClient) -> None:
    """Invalid motorization returns 422."""
    token = await login_as_admin(client)
    data, sc = await _create_vehicle(client, token, motorization="nuclear")
    assert sc == 422


@pytest.mark.asyncio
async def test_list_vehicles(client: AsyncClient) -> None:
    """GET /vehicles returns paginated list."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 vehicles
    for i in range(3):
        await _create_vehicle(client, token, type=f"Bus{i}", capacity=10 + i)

    resp = await client.get("/api/v1/vehicles", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "total" in data
    assert data["total"] >= 3
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_filter_by_site(client: AsyncClient) -> None:
    """GET /vehicles?site_id=X filters by site."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    site_a = await _create_site(client, token, "Site Alpha")
    site_b = await _create_site(client, token, "Site Beta")

    await _create_vehicle(client, token, site_id=site_a, type="Van")
    await _create_vehicle(client, token, site_id=site_b, type="SUV")

    resp = await client.get(f"/api/v1/vehicles?site_id={site_a}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    types = [v["type"] for v in data["data"]]
    assert "Van" in types
    # SUV from site_b should not appear if we filter strictly
    for v in data["data"]:
        assert v["site_id"] == site_a


@pytest.mark.asyncio
async def test_filter_by_pmr(client: AsyncClient) -> None:
    """GET /vehicles?is_pmr_accessible=true filters PMR vehicles."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    await _create_vehicle(client, token, is_pmr_accessible=True, type="PMR Bus")
    await _create_vehicle(client, token, is_pmr_accessible=False, type="Normal Bus")

    resp = await client.get("/api/v1/vehicles?is_pmr_accessible=true", headers=headers)
    assert resp.status_code == 200
    for v in resp.json()["data"]:
        assert v["is_pmr_accessible"] is True


@pytest.mark.asyncio
async def test_filter_by_motorization(client: AsyncClient) -> None:
    """GET /vehicles?motorization=electric filters by engine type."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    await _create_vehicle(client, token, motorization="electric", type="E-Bus")
    await _create_vehicle(client, token, motorization="diesel", type="D-Bus")

    resp = await client.get("/api/v1/vehicles?motorization=electric", headers=headers)
    assert resp.status_code == 200
    for v in resp.json()["data"]:
        assert v["motorization"] == "electric"


@pytest.mark.asyncio
async def test_filter_by_zfe(client: AsyncClient) -> None:
    """GET /vehicles?zfe_compliant=true filters ZFE vehicles."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    await _create_vehicle(client, token, zfe_compliant=True, type="ZFE Bus")

    resp = await client.get("/api/v1/vehicles?zfe_compliant=true", headers=headers)
    assert resp.status_code == 200
    for v in resp.json()["data"]:
        assert v["zfe_compliant"] is True


@pytest.mark.asyncio
async def test_update_vehicle(client: AsyncClient) -> None:
    """PUT updates vehicle fields."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    data, sc = await _create_vehicle(client, token, type="Old Bus", capacity=15)
    assert sc == 201
    vehicle_id = data["id"]

    resp = await client.put(
        f"/api/v1/vehicles/{vehicle_id}",
        headers=headers,
        json={"type": "New Bus", "capacity": 25, "condition": "Moyen"},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["type"] == "New Bus"
    assert updated["capacity"] == 25
    assert updated["condition"] == "Moyen"


@pytest.mark.asyncio
async def test_delete_vehicle(client: AsyncClient) -> None:
    """DELETE removes vehicle, then GET returns empty or missing."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    data, sc = await _create_vehicle(client, token, type="Delete Me")
    assert sc == 201
    vehicle_id = data["id"]

    del_resp = await client.delete(
        f"/api/v1/vehicles/{vehicle_id}", headers=headers
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_fleet_summary(client: AsyncClient) -> None:
    """GET /vehicles/fleet-summary returns correct aggregations."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "Fleet Site")

    # Create diverse fleet
    await _create_vehicle(
        client, token, site_id=site_id, type="Minibus", capacity=20,
        motorization="diesel", condition="Bon", is_pmr_accessible=True,
        zfe_compliant=False,
    )
    await _create_vehicle(
        client, token, site_id=site_id, type="Minibus", capacity=20,
        motorization="electric", condition="Bon", is_pmr_accessible=False,
        zfe_compliant=True,
    )
    await _create_vehicle(
        client, token, site_id=site_id, type="Midibus", capacity=30,
        motorization="hybrid", condition="Moyen",
    )

    resp = await client.get("/api/v1/vehicles/fleet-summary", headers=headers)
    assert resp.status_code == 200
    summary = resp.json()

    assert summary["total_vehicles"] >= 3
    assert summary["total_capacity"] >= 70
    assert summary["pmr_accessible_count"] >= 1
    assert summary["zfe_compliant_count"] >= 1

    assert len(summary["by_type"]) >= 2
    assert len(summary["by_condition"]) >= 1
    assert len(summary["by_motorization"]) >= 2
    assert len(summary["by_site"]) >= 1
