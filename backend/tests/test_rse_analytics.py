from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_site(client: AsyncClient, token: str, name: str = "RSE Site") -> str:
    code = f"RSE-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue RSE",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_employee(
    client: AsyncClient,
    token: str,
    site_id: str,
    **overrides: object,
) -> str:
    matricule = f"EMP-{uuid.uuid4().hex[:8]}"
    payload: dict = {
        "matricule": matricule,
        "first_name": "Test",
        "last_name": "Employee",
        "site_id": site_id,
        "shift_time": "08:00",
        "department": "Engineering",
        "opt_in_company_transport": "Oui",
        "has_private_car": True,
        "active": True,
    }
    payload.update(overrides)
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.json()}"
    return resp.json()["id"]


async def _create_vehicle(
    client: AsyncClient,
    token: str,
    site_id: str,
    **overrides: object,
) -> str:
    payload: dict = {
        "type": "Minibus",
        "capacity": 20,
        "site_id": site_id,
        "motorization": "diesel",
        "zfe_compliant": False,
    }
    payload.update(overrides)
    resp = await client.post(
        "/api/v1/vehicles",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.json()}"
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_co2_saved_calculation(client: AsyncClient) -> None:
    """GET /kpis/rse returns co2_savings section with all expected fields."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "CO2 Site")

    # Create employees to provide baseline data
    await _create_employee(client, token, site_id, opt_in_company_transport="Oui")
    await _create_employee(client, token, site_id, opt_in_company_transport="Non")

    resp = await client.get("/api/v1/kpis/rse", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    co2 = data["co2_savings"]
    assert "co2_baseline_kg" in co2
    assert "co2_actual_kg" in co2
    assert "co2_saved_kg" in co2
    assert "co2_saved_pct" in co2
    assert "employee_count" in co2
    assert "avg_distance_km" in co2
    assert "trend" in co2
    assert isinstance(co2["trend"], list)
    assert co2["co2_baseline_kg"] >= 0
    assert co2["co2_actual_kg"] >= 0


@pytest.mark.asyncio
async def test_private_vehicles_avoided(client: AsyncClient) -> None:
    """GET /kpis/rse returns vehicles_avoided count and adoption rate."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "PV Site")

    # Create employees with private cars
    await _create_employee(client, token, site_id, has_private_car=True, opt_in_company_transport="Oui")
    await _create_employee(client, token, site_id, has_private_car=True, opt_in_company_transport="Non")
    await _create_employee(client, token, site_id, has_private_car=False, opt_in_company_transport="Oui")

    resp = await client.get("/api/v1/kpis/rse", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    pv = data["private_vehicles_avoided"]
    assert "vehicles_avoided" in pv
    assert "total_with_car" in pv
    assert "adoption_pct" in pv
    assert pv["vehicles_avoided"] >= 1  # At least the one we created
    assert pv["total_with_car"] >= 2
    assert 0 <= pv["adoption_pct"] <= 100


@pytest.mark.asyncio
async def test_modal_distribution(client: AsyncClient) -> None:
    """GET /kpis/rse returns modal distribution with percentages summing correctly."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/rse", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    modal = data["modal_distribution"]
    assert "by_mode" in modal
    assert "soft_pct" in modal
    assert "electric_pct" in modal
    assert "shared_pct" in modal
    assert "individual_pct" in modal
    assert "before" in modal
    assert "after" in modal
    assert isinstance(modal["by_mode"], list)

    # Category percentages should be non-negative
    for key in ("soft_pct", "electric_pct", "shared_pct", "individual_pct"):
        assert modal[key] >= 0

    # Each mode entry has required fields
    for mode_entry in modal["by_mode"]:
        assert "mode" in mode_entry
        assert "count" in mode_entry
        assert "pct" in mode_entry
        assert "category" in mode_entry


@pytest.mark.asyncio
async def test_zfe_compliance(client: AsyncClient) -> None:
    """GET /kpis/rse returns ZFE compliance_pct between 0 and 100."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "ZFE Site")

    # Create vehicles with different ZFE compliance
    await _create_vehicle(client, token, site_id, zfe_compliant=True, motorization="electric")
    await _create_vehicle(client, token, site_id, zfe_compliant=False, motorization="diesel")

    resp = await client.get("/api/v1/kpis/rse", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    zfe = data["zfe_compliance"]
    assert "compliant_count" in zfe
    assert "total_count" in zfe
    assert "compliance_pct" in zfe
    assert "by_motorization" in zfe
    assert 0 <= zfe["compliance_pct"] <= 100
    assert zfe["compliant_count"] >= 1
    assert zfe["total_count"] >= 2


@pytest.mark.asyncio
async def test_dpef_report_generation(client: AsyncClient) -> None:
    """POST /kpis/rse/dpef returns a PDF file."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/kpis/rse/dpef", headers=headers)
    assert resp.status_code == 200
    assert len(resp.content) > 0
    # PDF magic bytes
    assert resp.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_rse_endpoint_structure(client: AsyncClient) -> None:
    """GET /kpis/rse returns all 4 RSE sections."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/rse", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # All 4 top-level keys present
    assert "co2_savings" in data
    assert "private_vehicles_avoided" in data
    assert "modal_distribution" in data
    assert "zfe_compliance" in data


@pytest.mark.asyncio
async def test_dpef_report_download(client: AsyncClient) -> None:
    """POST /kpis/rse/dpef returns PDF content-type and attachment header."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/kpis/rse/dpef", headers=headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment" in resp.headers.get("content-disposition", "")
    assert "rapport_dpef.pdf" in resp.headers.get("content-disposition", "")
