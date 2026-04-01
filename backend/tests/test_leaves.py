from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers — create site and employee per-test for isolation
# ---------------------------------------------------------------------------


async def _create_site(client: AsyncClient, token: str) -> str:
    """Helper: create a site and return its ID."""
    code = f"LS-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": "Leave Test Site",
            "address": "123 Rue Test",
            "city": "Casablanca",
            "lat": 33.57,
            "lng": -7.59,
        },
    )
    assert resp.status_code == 201, f"Site creation failed: {resp.text}"
    return resp.json()["id"]


async def _create_employee(client: AsyncClient, token: str, site_id: str) -> str:
    """Helper: create an employee and return its ID."""
    matricule = f"LV-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "matricule": matricule,
            "first_name": "Leave",
            "last_name": "Tester",
            "site_id": site_id,
            "city": "Casablanca",
            "lat": 33.58,
            "lng": -7.60,
        },
    )
    assert resp.status_code == 201, f"Employee creation failed: {resp.text}"
    return resp.json()["id"]


async def _create_leave(
    client: AsyncClient,
    token: str,
    employee_id: str,
    start_date: str = "2026-06-01",
    end_date: str = "2026-06-10",
    leave_type: str = "vacation",
    notes: str | None = None,
) -> dict:
    """Helper: create a leave and return the response dict."""
    payload: dict = {
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
    }
    if notes is not None:
        payload["notes"] = notes
    resp = await client.post(
        "/api/v1/leaves/",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    return resp.json(), resp.status_code


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_leave(client: AsyncClient) -> None:
    """Valid leave creation returns 201 with correct fields."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    data, status_code = await _create_leave(
        client,
        token,
        emp_id,
        start_date="2026-07-01",
        end_date="2026-07-15",
        leave_type="vacation",
        notes="Summer holiday",
    )
    assert status_code == 201, f"Unexpected response: {data}"
    assert data["employee_id"] == emp_id
    assert data["leave_type"] == "vacation"
    assert data["start_date"] == "2026-07-01"
    assert data["end_date"] == "2026-07-15"
    assert data["notes"] == "Summer holiday"
    assert data["employee_name"] is not None
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_leave_invalid_dates(client: AsyncClient) -> None:
    """end_date < start_date returns 422."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    resp = await client.post(
        "/api/v1/leaves/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employee_id": emp_id,
            "leave_type": "sick",
            "start_date": "2026-08-15",
            "end_date": "2026-08-10",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_leave_invalid_type(client: AsyncClient) -> None:
    """Unknown leave_type returns 422."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    resp = await client.post(
        "/api/v1/leaves/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "employee_id": emp_id,
            "leave_type": "spa_day",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_leaves_filter_employee(client: AsyncClient) -> None:
    """Filtering by employee_id returns only that employee's leaves."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id_a = await _create_employee(client, token, site_id)
    emp_id_b = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create leaves for both employees (non-overlapping dates within each employee)
    await _create_leave(client, token, emp_id_a, "2026-03-01", "2026-03-05", "vacation")
    await _create_leave(client, token, emp_id_b, "2026-03-01", "2026-03-05", "sick")

    resp = await client.get(
        f"/api/v1/leaves/?employee_id={emp_id_a}",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "meta" in data
    assert all(lv["employee_id"] == emp_id_a for lv in data["data"])
    assert data["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_list_leaves_filter_date_range(client: AsyncClient) -> None:
    """Filtering by date_from / date_to narrows results correctly."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    # Create two non-overlapping leaves
    await _create_leave(client, token, emp_id, "2026-01-10", "2026-01-20", "vacation")
    await _create_leave(client, token, emp_id, "2026-04-01", "2026-04-10", "formation")

    # Query a range that covers only the first leave
    resp = await client.get(
        f"/api/v1/leaves/?employee_id={emp_id}&date_from=2026-01-01&date_to=2026-02-01",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["leave_type"] == "vacation"


@pytest.mark.asyncio
async def test_update_leave(client: AsyncClient) -> None:
    """Updating a leave changes fields and returns 200."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    leave_data, sc = await _create_leave(
        client, token, emp_id, "2026-05-01", "2026-05-10", "sick"
    )
    assert sc == 201
    leave_id = leave_data["id"]

    resp = await client.put(
        f"/api/v1/leaves/{leave_id}",
        headers=headers,
        json={"leave_type": "unpaid", "notes": "Changed to unpaid"},
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["leave_type"] == "unpaid"
    assert updated["notes"] == "Changed to unpaid"
    # Dates remain unchanged
    assert updated["start_date"] == "2026-05-01"
    assert updated["end_date"] == "2026-05-10"


@pytest.mark.asyncio
async def test_delete_leave(client: AsyncClient) -> None:
    """Deleting a leave returns 204 and it is no longer retrievable."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    leave_data, sc = await _create_leave(
        client, token, emp_id, "2026-11-01", "2026-11-05", "other"
    )
    assert sc == 201
    leave_id = leave_data["id"]

    del_resp = await client.delete(
        f"/api/v1/leaves/{leave_id}",
        headers=headers,
    )
    assert del_resp.status_code == 204

    # Confirm it's gone
    get_resp = await client.get(
        f"/api/v1/leaves/{leave_id}",
        headers=headers,
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_overlapping_leave_check(client: AsyncClient) -> None:
    """Creating a leave that overlaps with an existing one returns 409."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp_id = await _create_employee(client, token, site_id)

    # First leave: June 1-10
    data, sc = await _create_leave(
        client, token, emp_id, "2026-06-01", "2026-06-10", "vacation"
    )
    assert sc == 201, f"First leave failed: {data}"

    # Overlapping leave: June 5-15 (overlaps June 5-10)
    data2, sc2 = await _create_leave(
        client, token, emp_id, "2026-06-05", "2026-06-15", "sick"
    )
    assert sc2 == 409, f"Expected 409, got {sc2}: {data2}"

    # Non-overlapping leave: June 11-20 should succeed
    data3, sc3 = await _create_leave(
        client, token, emp_id, "2026-06-11", "2026-06-20", "formation"
    )
    assert sc3 == 201, f"Non-overlapping leave should succeed: {data3}"
