from __future__ import annotations

import uuid
from datetime import date

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_site(client: AsyncClient, token: str, name: str = "KPI Site") -> str:
    code = f"KPI-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue KPI",
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
        "last_name": "KPIEmployee",
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
async def test_kpi_snapshot_creation(client: AsyncClient) -> None:
    """POST /kpis/snapshot creates snapshots for a specific site."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "Snapshot Site")
    await _create_employee(client, token, site_id)

    resp = await client.post(
        f"/api/v1/kpis/snapshot?site_id={site_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] == 6
    assert data["site_id"] == site_id


@pytest.mark.asyncio
async def test_kpi_snapshot_all_sites(client: AsyncClient) -> None:
    """POST /kpis/snapshot without site_id captures all sites."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    await _create_site(client, token, "All-sites Snap")

    resp = await client.post(
        "/api/v1/kpis/snapshot",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    # Should have at least 6 (tenant-wide) + 6 per site
    assert data["count"] >= 6
    assert data["site_id"] is None


@pytest.mark.asyncio
async def test_all_kpi_types_captured(client: AsyncClient) -> None:
    """All 6 KPI types are captured in a snapshot."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "Types Site")

    resp = await client.post(
        f"/api/v1/kpis/snapshot?site_id={site_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    expected_types = [
        "mobility_coverage",
        "modal_distribution",
        "occupancy_rate",
        "co2_saved",
        "rti_compliance",
        "security_score",
    ]
    assert sorted(data["kpi_types"]) == sorted(expected_types)


@pytest.mark.asyncio
async def test_trend_query(client: AsyncClient) -> None:
    """GET /kpis/trend returns time-series data after a snapshot is created."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "Trend Site")

    # Create a snapshot first
    await client.post(
        f"/api/v1/kpis/snapshot?site_id={site_id}",
        headers=headers,
    )

    resp = await client.get(
        f"/api/v1/kpis/trend?kpi_type=mobility_coverage&site_id={site_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "snapshot_date" in data[0]
    assert "value" in data[0]
    assert data[0]["site_id"] == site_id


@pytest.mark.asyncio
async def test_trend_date_range(client: AsyncClient) -> None:
    """GET /kpis/trend supports date range filtering."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    site_id = await _create_site(client, token, "DateRange Site")

    # Create a snapshot
    await client.post(
        f"/api/v1/kpis/snapshot?site_id={site_id}",
        headers=headers,
    )

    today = date.today().isoformat()

    # Query with valid date range including today
    resp = await client.get(
        f"/api/v1/kpis/trend?kpi_type=co2_saved&site_id={site_id}&start_date={today}&end_date={today}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1

    # Query with a future date range should return empty
    resp2 = await client.get(
        "/api/v1/kpis/trend?kpi_type=co2_saved&start_date=2099-01-01&end_date=2099-12-31",
        headers=headers,
    )
    assert resp2.status_code == 200
    assert resp2.json()["data"] == []


@pytest.mark.asyncio
async def test_trend_invalid_kpi_type(client: AsyncClient) -> None:
    """GET /kpis/trend rejects invalid kpi_type with 422."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(
        "/api/v1/kpis/trend?kpi_type=nonexistent_metric",
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_celery_task_function(client: AsyncClient) -> None:
    """Celery task function is importable and callable."""
    from app.tasks.kpi_tasks import daily_kpi_snapshot

    assert callable(daily_kpi_snapshot)
