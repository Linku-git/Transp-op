from __future__ import annotations

import io
import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


async def _create_site(client: AsyncClient, token: str) -> str:
    """Helper: create a site and return its ID."""
    code = f"ES-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": code, "name": "Emp Test Site", "address": "Addr", "city": "Casablanca", "lat": 33.57, "lng": -7.59},
    )
    return resp.json()["id"]


async def _create_employee(client: AsyncClient, token: str, site_id: str, **overrides: object) -> dict:
    """Helper: create an employee and return the response dict."""
    data = {
        "matricule": f"EMP-{uuid.uuid4().hex[:6]}",
        "first_name": "Test",
        "last_name": "Employee",
        "site_id": site_id,
        "shift_time": "Matin",
        "address": "10 Rue Test, Casablanca",
        "city": "Casablanca",
        "lat": 33.58,
        "lng": -7.60,
        "department": "IT",
        **overrides,
    }
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json=data,
    )
    return resp.json()


@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/employees/",
        headers=headers,
        json={
            "matricule": f"EMP-{uuid.uuid4().hex[:6]}",
            "first_name": "Alice",
            "last_name": "Dupont",
            "site_id": site_id,
            "shift_time": "Matin",
            "address": "5 Rue Test",
            "city": "Casablanca",
            "lat": 33.58,
            "lng": -7.60,
            "is_pmr": True,
            "department": "RH",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["first_name"] == "Alice"
    assert data["is_pmr"] is True
    assert data["active"] is True


@pytest.mark.asyncio
async def test_create_employee_duplicate_matricule(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    mat = f"DUP-{uuid.uuid4().hex[:4]}"

    await _create_employee(client, token, site_id, matricule=mat)
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={"matricule": mat, "first_name": "B", "last_name": "C", "site_id": site_id},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_employee_invalid_site(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={"matricule": "X", "first_name": "A", "last_name": "B", "site_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/api/v1/employees/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_filter_by_site(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(f"/api/v1/employees/?site_id={site_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(e["site_id"] == site_id for e in data["data"])


@pytest.mark.asyncio
async def test_filter_by_pmr(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    await _create_employee(client, token, site_id, is_pmr=True)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/employees/?is_pmr=true", headers=headers)
    assert resp.status_code == 200
    assert all(e["is_pmr"] is True for e in resp.json()["data"])


@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(f"/api/v1/employees/{emp['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == emp["id"]


@pytest.mark.asyncio
async def test_update_employee(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.put(
        f"/api/v1/employees/{emp['id']}",
        headers=headers,
        json={"first_name": "Updated", "department": "Finance"},
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Updated"
    assert resp.json()["department"] == "Finance"


@pytest.mark.asyncio
async def test_soft_delete_employee(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp = await _create_employee(client, token, site_id)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.delete(f"/api/v1/employees/{emp['id']}", headers=headers)
    assert resp.status_code == 200

    # Verify still in DB but inactive
    get_resp = await client.get(f"/api/v1/employees/{emp['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["active"] is False


@pytest.mark.asyncio
async def test_csv_upload(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    # Get site code for CSV
    headers = {"Authorization": f"Bearer {token}"}
    site_resp = await client.get(f"/api/v1/sites/{site_id}", headers=headers)
    site_code = site_resp.json()["code"]

    m1, m2 = f"CSV-{uuid.uuid4().hex[:6]}", f"CSV-{uuid.uuid4().hex[:6]}"
    csv_content = f"matricule,first_name,last_name,site_code,shift_time,department\n{m1},Jean,Martin,{site_code},Matin,IT\n{m2},Marie,Dupont,{site_code},Apres-midi,RH\n"
    files = {"file": ("employees.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    resp = await client.post("/api/v1/employees/upload", headers=headers, files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_rows"] == 2, f"errors: {data.get('errors')}"
    assert data["created"] == 2, f"errors: {data.get('errors')}"
    assert len(data["errors"]) == 0, f"errors: {data['errors']}"


@pytest.mark.asyncio
async def test_csv_upload_validation_errors(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    csv_content = "matricule,first_name,last_name,site_code\nBAD1,Jean,,INVALID_SITE\n"
    files = {"file": ("bad.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    resp = await client.post("/api/v1/employees/upload", headers=headers, files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["created"] == 0
    assert len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_employee_summary(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/employees/summary", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_count" in data
    assert "pmr_count" in data
    assert "by_site" in data


@pytest.mark.asyncio
async def test_postgis_geometry(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    emp = await _create_employee(client, token, site_id, lat=34.05, lng=-6.83)

    # Verify lat/lng preserved
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(f"/api/v1/employees/{emp['id']}", headers=headers)
    assert resp.json()["lat"] == pytest.approx(34.05)
    assert resp.json()["lng"] == pytest.approx(-6.83)
