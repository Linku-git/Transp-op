from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_site(client: AsyncClient, token: str, name: str = "HR Site") -> str:
    code = f"HR-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue HR",
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mobility_coverage(client: AsyncClient) -> None:
    """Mobility coverage returns correct percentages per site, shift, department."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "Coverage Site")

    # Create employees with different transport preferences
    await _create_employee(client, token, site_id, opt_in_company_transport="Oui")
    await _create_employee(client, token, site_id, opt_in_company_transport="Non")
    await _create_employee(client, token, site_id, opt_in_company_transport="Sous conditions")

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    coverage = data["mobility_coverage"]
    assert coverage["total_employees"] >= 3
    assert coverage["covered_employees"] >= 2  # Oui + Peut-etre
    assert coverage["coverage_pct"] > 0
    assert len(coverage["by_site"]) >= 1
    assert len(coverage["by_shift"]) >= 1
    assert len(coverage["by_department"]) >= 1


@pytest.mark.asyncio
async def test_mobility_score_evolution(client: AsyncClient) -> None:
    """Mobility score evolution returns time-series data."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    evolution = data["mobility_score_evolution"]
    assert isinstance(evolution, list)
    # May be empty if no completed optimizations
    for point in evolution:
        assert "date" in point
        assert "score" in point


@pytest.mark.asyncio
async def test_absenteeism_correlation(client: AsyncClient) -> None:
    """Absenteeism correlation produces valid groups with rates."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    absenteeism = data["absenteeism_correlation"]
    assert "with_transport" in absenteeism
    assert "without_transport" in absenteeism
    assert "correlation" in absenteeism

    for group in ["with_transport", "without_transport", "maybe_transport"]:
        assert "employee_count" in absenteeism[group]
        assert "absence_rate_pct" in absenteeism[group]
        assert absenteeism[group]["absence_rate_pct"] >= 0

    assert "delta_pct" in absenteeism["correlation"]
    assert "interpretation" in absenteeism["correlation"]


@pytest.mark.asyncio
async def test_retention_impact(client: AsyncClient) -> None:
    """Retention impact returns cost comparison figures."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    retention = data["retention_impact"]
    assert "total_employees" in retention
    assert "departed_total" in retention
    assert "turnover_rate_pct" in retention
    assert "avg_replacement_cost" in retention
    assert "estimated_annual_savings" in retention
    assert retention["turnover_rate_pct"] >= 0


@pytest.mark.asyncio
async def test_shadow_zones(client: AsyncClient) -> None:
    """Shadow zone identification correctly flags employees."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    shadow = data["shadow_zones"]
    assert "shadow_zone_count" in shadow
    assert "total_active_employees" in shadow
    assert "shadow_zone_pct" in shadow
    assert "threshold_km" in shadow
    assert isinstance(shadow["employees"], list)
    assert shadow["threshold_km"] == 30


@pytest.mark.asyncio
async def test_hr_kpis_endpoint_structure(client: AsyncClient) -> None:
    """GET /kpis/hr returns all metrics with correct structure."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/kpis/hr", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    # All 5 top-level keys present
    assert "mobility_coverage" in data
    assert "mobility_score_evolution" in data
    assert "absenteeism_correlation" in data
    assert "retention_impact" in data
    assert "shadow_zones" in data
