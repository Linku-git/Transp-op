from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers — reuse patterns from test_modal.py
# ---------------------------------------------------------------------------


async def _create_site(
    client: AsyncClient,
    token: str,
    name: str = "Scoring Test Site",
) -> str:
    """Helper: create a site and return its ID."""
    code = f"SC-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "789 Rue Scoring",
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
    first_name: str = "Test",
    last_name: str = "Employee",
    shift_time: str | None = None,
    department: str | None = None,
) -> str:
    """Helper: create an employee and return its ID."""
    matricule = f"SC-{uuid.uuid4().hex[:8]}"
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
    if department is not None:
        payload["department"] = department
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
    """Helper: upsert a modal record."""
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
async def test_employee_score_calculation(client: AsyncClient) -> None:
    """Mobility score calculation matches expected values for known input.

    Employee with: transport_public (+10 sustainable), distance 5km (+15 short),
    interest=Oui (+20), accepts_pickup (+10), volunteer=True (+15),
    alternative_mode set (+5) => 0 + 10 + 15 + 20 + 10 + 15 + 5 = 75.
    """
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id, first_name="Score", last_name="Test")
    headers = {"Authorization": f"Bearer {token}"}

    await _upsert_modal(
        client,
        token,
        emp_id,
        primary_mode="transport_public",
        distance_km=5.0,
        interest_company_transport="Oui",
        accepts_common_pickup=True,
        volunteer_driver=True,
        has_private_car=False,
        alternative_mode="covoiturage",
    )

    resp = await client.get("/api/v1/modal/mobility-scores", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # Find our employee
    emp_score = next(
        (s for s in data["scores"] if s["employee_id"] == emp_id), None
    )
    assert emp_score is not None
    assert emp_score["employee_name"] == "Score Test"
    # 10 (sustainable) + 15 (short dist) + 20 (interest) + 10 (pickup) + 15 (volunteer) + 5 (alt mode) = 75
    assert emp_score["score"] == 75.0
    assert "sustainable_mode" in emp_score["factors"]
    assert "distance_short" in emp_score["factors"]
    assert "company_transport_interest" in emp_score["factors"]

    # Verify response structure includes group and timeslot scores
    assert "group_scores" in data
    assert "timeslot_scores" in data


@pytest.mark.asyncio
async def test_group_score_aggregation(client: AsyncClient) -> None:
    """Group scores aggregate correctly by site."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Group Site")
    headers = {"Authorization": f"Bearer {token}"}

    # Two employees in the same site with different scores
    emp1 = await _create_employee(
        client, token, site_id, first_name="G1", last_name="A", department="IT"
    )
    emp2 = await _create_employee(
        client, token, site_id, first_name="G2", last_name="B", department="IT"
    )

    # emp1: transport_public(+10) + distance<10(+15) + interest=Oui(+20) + pickup(+10) = 55
    await _upsert_modal(
        client, token, emp1,
        primary_mode="transport_public",
        distance_km=5.0,
        interest_company_transport="Oui",
        accepts_common_pickup=True,
        volunteer_driver=False,
    )
    # emp2: vehicule_particulier(0) + distance<10(+15) + interest=Non(0) + pickup(+10) = 25
    await _upsert_modal(
        client, token, emp2,
        primary_mode="vehicule_particulier",
        distance_km=8.0,
        interest_company_transport="Non",
        accepts_common_pickup=True,
        volunteer_driver=False,
    )

    resp = await client.get(
        f"/api/v1/modal/mobility-scores?site_id={site_id}", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()

    # Find site group score
    site_groups = [
        g for g in data["group_scores"]
        if g["group_type"] == "site" and g["group_key"] == site_id
    ]
    assert len(site_groups) == 1
    assert site_groups[0]["employee_count"] == 2
    # Average of 55 and 25 = 40
    assert site_groups[0]["avg_score"] == 40.0


@pytest.mark.asyncio
async def test_shadow_zone_identification(client: AsyncClient) -> None:
    """Shadow zone correctly identifies car-dependent employees far from site."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Shadow Site")
    headers = {"Authorization": f"Bearer {token}"}

    # Shadow zone employee: far, car-dependent, no interest
    shadow_emp = await _create_employee(
        client, token, site_id, first_name="Shadow", last_name="Employee"
    )
    await _upsert_modal(
        client, token, shadow_emp,
        primary_mode="vehicule_particulier",
        distance_km=45.0,
        interest_company_transport="Non",
        accepts_common_pickup=False,
        volunteer_driver=False,
    )

    # Non-shadow employee: close, interested
    normal_emp = await _create_employee(
        client, token, site_id, first_name="Normal", last_name="Employee"
    )
    await _upsert_modal(
        client, token, normal_emp,
        primary_mode="transport_public",
        distance_km=5.0,
        interest_company_transport="Oui",
    )

    resp = await client.get("/api/v1/modal/shadow-zones", headers=headers)
    assert resp.status_code == 200
    zones = resp.json()

    shadow_ids = [z["employee_id"] for z in zones]
    assert shadow_emp in shadow_ids
    assert normal_emp not in shadow_ids

    # Check structure
    shadow = next(z for z in zones if z["employee_id"] == shadow_emp)
    assert shadow["employee_name"] == "Shadow Employee"
    assert shadow["distance_km"] == 45.0
    assert "reason" in shadow


@pytest.mark.asyncio
async def test_weather_modal_shift(client: AsyncClient) -> None:
    """Shift analysis includes weather impact data for vulnerable modes."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Weather Site")
    headers = {"Authorization": f"Bearer {token}"}

    emp1 = await _create_employee(
        client, token, site_id, first_name="W1", last_name="Cyclist",
        shift_time="08:00"
    )
    emp2 = await _create_employee(
        client, token, site_id, first_name="W2", last_name="Driver",
        shift_time="08:00"
    )

    await _upsert_modal(
        client, token, emp1, primary_mode="deux_roues_non_motorise", distance_km=8.0
    )
    await _upsert_modal(
        client, token, emp2, primary_mode="vehicule_particulier", distance_km=12.0
    )

    resp = await client.get("/api/v1/modal/shift-analysis", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "weather_impact" in data
    assert "disruptions" in data

    # Find bicycle mode — should have high switch probability
    bike_impact = next(
        (w for w in data["weather_impact"] if w["mode"] == "deux_roues_non_motorise"),
        None,
    )
    assert bike_impact is not None
    assert bike_impact["switch_probability"] == 0.85
    assert bike_impact["likely_alternative"] == "transport_public"


@pytest.mark.asyncio
async def test_carpool_potential(client: AsyncClient) -> None:
    """Carpool potential correctly calculates supply vs demand per site."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Carpool Site")
    headers = {"Authorization": f"Bearer {token}"}

    # Supply: 1 volunteer driver with 3 seats
    driver = await _create_employee(
        client, token, site_id, first_name="Driver", last_name="Vol"
    )
    await _upsert_modal(
        client, token, driver,
        primary_mode="vehicule_particulier",
        distance_km=15.0,
        volunteer_driver=True,
        has_private_car=True,
        carpool_seats_available=3,
        interest_company_transport="Oui",
    )

    # Demand: 2 employees interested without cars
    for i in range(2):
        emp = await _create_employee(
            client, token, site_id, first_name=f"Rider{i}", last_name="Need"
        )
        await _upsert_modal(
            client, token, emp,
            primary_mode="transport_public",
            distance_km=10.0,
            interest_company_transport="Oui",
            has_private_car=False,
            volunteer_driver=False,
        )

    resp = await client.get("/api/v1/modal/carpool-potential", headers=headers)
    assert resp.status_code == 200
    potentials = resp.json()
    assert len(potentials) >= 1

    # Find our site
    site_potential = next(
        (p for p in potentials if p["site_id"] == site_id), None
    )
    assert site_potential is not None
    assert site_potential["supply_seats"] >= 3
    assert site_potential["demand_count"] >= 2
    assert site_potential["coverage_ratio"] > 0


@pytest.mark.asyncio
async def test_zero_mobility_score(client: AsyncClient) -> None:
    """Employee with worst factors gets a score clamped to 0."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Zero Site")
    headers = {"Authorization": f"Bearer {token}"}

    emp_id = await _create_employee(
        client, token, site_id, first_name="Zero", last_name="Scorer"
    )

    # Worst case: very long distance (-15), no interest (0), no pickup, no volunteer,
    # car-only mode (0), no alternative — total = -15, clamped to 0
    await _upsert_modal(
        client, token, emp_id,
        primary_mode="vehicule_particulier",
        distance_km=50.0,
        interest_company_transport="Non",
        accepts_common_pickup=False,
        volunteer_driver=False,
        has_private_car=False,
    )

    resp = await client.get("/api/v1/modal/mobility-scores", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    emp_score = next(
        (s for s in data["scores"] if s["employee_id"] == emp_id), None
    )
    assert emp_score is not None
    assert emp_score["score"] == 0.0
    assert emp_score["employee_name"] == "Zero Scorer"
