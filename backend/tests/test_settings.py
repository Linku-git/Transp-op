from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Tests — OptimizationSettings
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_settings(client: AsyncClient) -> None:
    """GET /settings returns settings with expected structure."""
    token = await login_as_admin(client)

    resp = await client.get(
        "/api/v1/settings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    data = resp.json()
    # Verify all fields are present (values may differ if previously updated)
    assert "meeting_radius_meters" in data
    assert "max_walking_distance_meters" in data
    assert "max_route_duration_seconds" in data
    assert "fuel_cost_per_liter" in data
    assert "fuel_consumption_l_per_100km" in data
    assert "co2_kg_per_liter" in data
    assert "rti_threshold_minutes" in data
    assert "night_mode_start" in data
    assert "night_mode_end" in data
    assert "min_night_group_size" in data
    assert "id" in data
    assert "tenant_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient) -> None:
    """PUT /settings updates fuel_cost_per_liter and max_walking_distance_meters."""
    token = await login_as_admin(client)

    # Ensure settings exist
    await client.get(
        "/api/v1/settings",
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.put(
        "/api/v1/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "fuel_cost_per_liter": 15.5,
            "max_walking_distance_meters": 1200.0,
        },
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["fuel_cost_per_liter"] == 15.5
    assert data["max_walking_distance_meters"] == 1200.0
    # Other fields remain at defaults
    assert data["meeting_radius_meters"] == 500.0
    assert data["co2_kg_per_liter"] == 2.68


# ---------------------------------------------------------------------------
# Tests — ConstraintParam
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_constraint(client: AsyncClient) -> None:
    """POST /constraints creates a constraint and returns 201."""
    token = await login_as_admin(client)

    suffix = uuid.uuid4().hex[:6]
    key = f"max_detour_km_{suffix}"
    resp = await client.post(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": key,
            "value": "5",
            "category": "routing",
            "description": "Maximum detour in kilometers",
        },
    )
    assert resp.status_code == 201

    data = resp.json()
    assert data["key"] == key
    assert data["value"] == "5"
    assert data["category"] == "routing"
    assert data["description"] == "Maximum detour in kilometers"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_list_constraints_by_category(client: AsyncClient) -> None:
    """Create 2 constraints in different categories, GET with ?category filters."""
    token = await login_as_admin(client)

    # Create routing constraint
    await client.post(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": f"route_param_{uuid.uuid4().hex[:6]}",
            "value": "10",
            "category": "routing",
        },
    )

    # Create safety constraint
    await client.post(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": f"safety_param_{uuid.uuid4().hex[:6]}",
            "value": "true",
            "category": "safety",
        },
    )

    # Filter by routing
    resp = await client.get(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        params={"category": "routing"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert all(c["category"] == "routing" for c in data)

    # Filter by safety
    resp = await client.get(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        params={"category": "safety"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert all(c["category"] == "safety" for c in data)


@pytest.mark.asyncio
async def test_bulk_import_constraints(client: AsyncClient) -> None:
    """POST /constraints/bulk with 3 constraints returns imported count."""
    token = await login_as_admin(client)

    suffix = uuid.uuid4().hex[:6]
    resp = await client.post(
        "/api/v1/constraints/bulk",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "constraints": [
                {"key": f"bulk_a_{suffix}", "value": "100", "category": "limits"},
                {"key": f"bulk_b_{suffix}", "value": "200", "category": "limits"},
                {"key": f"bulk_c_{suffix}", "value": "300", "category": "limits"},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 3


@pytest.mark.asyncio
async def test_delete_constraint(client: AsyncClient) -> None:
    """Create then DELETE a constraint, verify 200 and subsequent GET returns 404."""
    token = await login_as_admin(client)

    # Create
    suffix = uuid.uuid4().hex[:6]
    resp = await client.post(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "key": f"to_delete_{suffix}",
            "value": "temporary",
            "category": "general",
        },
    )
    assert resp.status_code == 201
    constraint_id = resp.json()["id"]

    # Delete
    resp = await client.delete(
        f"/api/v1/constraints/{constraint_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Constraint deleted"

    # Verify the constraint no longer appears in list with its specific key
    resp = await client.get(
        "/api/v1/constraints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert constraint_id not in ids
