from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers — create site and employee per-test for isolation
# ---------------------------------------------------------------------------


async def _create_site(
    client: AsyncClient,
    token: str,
    name: str = "Modal Test Site",
) -> str:
    """Helper: create a site and return its ID."""
    code = f"MS-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "456 Rue Modal",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201, f"Site creation failed: {resp.text}"
    return resp.json()["id"]


async def _create_employee(
    client: AsyncClient,
    token: str,
    site_id: str,
    first_name: str = "Modal",
    last_name: str = "Tester",
    shift_time: str | None = None,
) -> str:
    """Helper: create an employee and return its ID."""
    matricule = f"MD-{uuid.uuid4().hex[:8]}"
    payload: dict = {
        "matricule": matricule,
        "first_name": first_name,
        "last_name": last_name,
        "site_id": site_id,
        "city": "Casablanca",
        "lat": 33.58,
        "lng": -7.60,
    }
    if shift_time is not None:
        payload["shift_time"] = shift_time
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, f"Employee creation failed: {resp.text}"
    return resp.json()["id"]


async def _upsert_modal(
    client: AsyncClient,
    token: str,
    employee_id: str,
    primary_mode: str = "vehicule_particulier",
    distance_km: float | None = 15.5,
    **overrides: object,
) -> tuple[dict, int]:
    """Helper: upsert a modal record and return (response_json, status_code)."""
    payload: dict = {
        "employee_id": employee_id,
        "primary_mode": primary_mode,
        "distance_km": distance_km,
        "frequency": "Quotidien",
        "interest_company_transport": "Oui",
        "accepts_common_pickup": True,
        "has_private_car": False,
        "volunteer_driver": False,
    }
    payload.update(overrides)
    resp = await client.put(
        f"/api/v1/employees/{employee_id}/modal",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    return resp.json(), resp.status_code


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_modal(client: AsyncClient) -> None:
    """PUT upsert on new employee creates modal, returns 201."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    data, sc = await _upsert_modal(
        client,
        token,
        emp_id,
        primary_mode="transport_public",
        distance_km=8.0,
        volunteer_driver=True,
    )
    assert sc == 201, f"Expected 201, got {sc}: {data}"
    assert data["employee_id"] == emp_id
    assert data["primary_mode"] == "transport_public"
    assert float(data["distance_km"]) == 8.0
    assert data["volunteer_driver"] is True
    assert data["employee_name"] is not None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_modal(client: AsyncClient) -> None:
    """PUT upsert on existing modal updates, returns 200."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    # Create
    data1, sc1 = await _upsert_modal(client, token, emp_id, primary_mode="covoiturage")
    assert sc1 == 201

    # Update
    data2, sc2 = await _upsert_modal(
        client,
        token,
        emp_id,
        primary_mode="transport_public",
        distance_km=22.0,
    )
    assert sc2 == 200, f"Expected 200, got {sc2}: {data2}"
    assert data2["primary_mode"] == "transport_public"
    assert float(data2["distance_km"]) == 22.0
    # Same record ID
    assert data2["id"] == data1["id"]


@pytest.mark.asyncio
async def test_get_modal(client: AsyncClient) -> None:
    """GET returns modal with employee name populated."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id, first_name="Alice", last_name="Dupont")
    headers = {"Authorization": f"Bearer {token}"}

    await _upsert_modal(client, token, emp_id, primary_mode="navette_entreprise")

    resp = await client.get(
        f"/api/v1/employees/{emp_id}/modal",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == emp_id
    assert data["primary_mode"] == "navette_entreprise"
    assert data["employee_name"] == "Alice Dupont"


@pytest.mark.asyncio
async def test_delete_modal(client: AsyncClient) -> None:
    """DELETE returns 204, then GET returns 404."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    await _upsert_modal(client, token, emp_id)

    del_resp = await client.delete(
        f"/api/v1/employees/{emp_id}/modal",
        headers=headers,
    )
    assert del_resp.status_code == 204

    get_resp = await client.get(
        f"/api/v1/employees/{emp_id}/modal",
        headers=headers,
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_modal_stats(client: AsyncClient) -> None:
    """GET /modal/stats returns mode distribution with counts and percentages."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 employees with different modes
    emp1 = await _create_employee(client, token, site_id, first_name="S1", last_name="A")
    emp2 = await _create_employee(client, token, site_id, first_name="S2", last_name="B")
    emp3 = await _create_employee(client, token, site_id, first_name="S3", last_name="C")

    await _upsert_modal(client, token, emp1, primary_mode="vehicule_particulier")
    await _upsert_modal(client, token, emp2, primary_mode="vehicule_particulier")
    await _upsert_modal(client, token, emp3, primary_mode="transport_public")

    resp = await client.get("/api/v1/modal/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 3
    assert len(data["distribution"]) >= 2

    # Check structure of distribution items
    for item in data["distribution"]:
        assert "mode" in item
        assert "count" in item
        assert "percentage" in item

    # Percentages should sum roughly to 100
    total_pct = sum(d["percentage"] for d in data["distribution"])
    assert 99.0 <= total_pct <= 101.0


@pytest.mark.asyncio
async def test_modal_stats_per_site(client: AsyncClient) -> None:
    """GET /modal/stats?site_id=X filters by site."""
    token = await login_as_admin(client)
    site_a = await _create_site(client, token, name="Site Alpha")
    site_b = await _create_site(client, token, name="Site Beta")
    headers = {"Authorization": f"Bearer {token}"}

    emp_a = await _create_employee(client, token, site_a, first_name="SA", last_name="One")
    emp_b = await _create_employee(client, token, site_b, first_name="SB", last_name="Two")

    await _upsert_modal(client, token, emp_a, primary_mode="covoiturage")
    await _upsert_modal(client, token, emp_b, primary_mode="deux_roues_motorise")

    # Filter by site_a — should only include emp_a
    resp = await client.get(
        f"/api/v1/modal/stats?site_id={site_a}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    modes = [d["mode"] for d in data["distribution"]]
    assert "covoiturage" in modes
    # deux_roues_motorise from site_b should NOT be present
    assert "deux_roues_motorise" not in modes


@pytest.mark.asyncio
async def test_shift_analysis(client: AsyncClient) -> None:
    """GET /modal/shift-analysis returns shift-grouped modal data."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    emp1 = await _create_employee(
        client, token, site_id, first_name="Sh1", last_name="A", shift_time="06:00"
    )
    emp2 = await _create_employee(
        client, token, site_id, first_name="Sh2", last_name="B", shift_time="14:00"
    )

    await _upsert_modal(client, token, emp1, primary_mode="vehicule_particulier")
    await _upsert_modal(client, token, emp2, primary_mode="transport_public")

    resp = await client.get("/api/v1/modal/shift-analysis", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    # Should have at least two shift keys
    assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_mobility_scores(client: AsyncClient) -> None:
    """GET /modal/mobility-scores returns scores for employees with modal data."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    emp_id = await _create_employee(
        client, token, site_id, first_name="Score", last_name="Tester"
    )

    # New scoring: covoiturage(+10 sustainable) + distance<10(+15) + interest=Oui(+20)
    # + accepts_pickup(+10) + volunteer(+15) = 70
    await _upsert_modal(
        client,
        token,
        emp_id,
        primary_mode="covoiturage",
        distance_km=5.0,
        interest_company_transport="Oui",
        accepts_common_pickup=True,
        volunteer_driver=True,
    )

    resp = await client.get("/api/v1/modal/mobility-scores", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "scores" in data
    assert "group_scores" in data
    assert "timeslot_scores" in data
    scores = data["scores"]
    assert len(scores) >= 1

    # Find our employee's score
    emp_score = next((s for s in scores if s["employee_id"] == emp_id), None)
    assert emp_score is not None
    assert emp_score["employee_name"] == "Score Tester"
    assert emp_score["score"] == 70.0
    assert "factors" in emp_score
    assert emp_score["factors"]["company_transport_interest"] == 20.0


@pytest.mark.asyncio
async def test_invalid_mode(client: AsyncClient) -> None:
    """Invalid primary_mode returns 422."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    resp = await client.put(
        f"/api/v1/employees/{emp_id}/modal",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employee_id": emp_id,
            "primary_mode": "teleportation",
            "distance_km": 10.0,
        },
    )
    assert resp.status_code == 422
