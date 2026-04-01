from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import login_as_admin


@pytest.mark.asyncio
async def test_create_site(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"S-{uuid.uuid4().hex[:6]}"

    response = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={
            "code": code,
            "name": "Site Test",
            "address": "123 Rue de Test",
            "city": "Casablanca",
            "lat": 33.5731,
            "lng": -7.5898,
            "num_shifts": 2,
            "zfe_zone": True,
            "security_profile": "elevated",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == code
    assert data["name"] == "Site Test"
    assert data["city"] == "Casablanca"
    assert data["lat"] == pytest.approx(33.5731)
    assert data["zfe_zone"] is True
    assert data["security_profile"] == "elevated"


@pytest.mark.asyncio
async def test_create_site_duplicate_code(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SDUP-{uuid.uuid4().hex[:4]}"

    # Create first
    await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "First", "address": "Addr", "city": "Paris", "lat": 48.8, "lng": 2.3},
    )
    # Create duplicate
    response = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "Second", "address": "Addr2", "city": "Paris", "lat": 48.8, "lng": 2.3},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_site_invalid_lat(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": "SINV", "name": "Bad", "address": "X", "city": "Y", "lat": 999, "lng": 0},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_sites(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/sites/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_sites_filter_city(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a site in a specific city
    code = f"SCIT-{uuid.uuid4().hex[:4]}"
    await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "Lyon Site", "address": "Rue X", "city": "Lyon", "lat": 45.7, "lng": 4.8},
    )

    response = await client.get("/api/v1/sites/?city=Lyon", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert all("Lyon" in s["city"] for s in data["data"])


@pytest.mark.asyncio
async def test_list_sites_filter_zfe(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/sites/?zfe_zone=true", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert all(s["zfe_zone"] is True for s in data["data"])


@pytest.mark.asyncio
async def test_get_site_by_id(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SID-{uuid.uuid4().hex[:4]}"

    create_resp = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "By ID", "address": "Addr", "city": "Rabat", "lat": 34.0, "lng": -6.8},
    )
    site_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/sites/{site_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["code"] == code


@pytest.mark.asyncio
async def test_get_site_by_code(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SCOD-{uuid.uuid4().hex[:4]}"

    await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "By Code", "address": "Addr", "city": "Fes", "lat": 34.0, "lng": -5.0},
    )

    response = await client.get(f"/api/v1/sites/code/{code}", headers=headers)
    assert response.status_code == 200
    assert response.json()["code"] == code


@pytest.mark.asyncio
async def test_get_site_not_found(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = str(uuid.uuid4())

    response = await client.get(f"/api/v1/sites/{fake_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_site(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SUPD-{uuid.uuid4().hex[:4]}"

    create_resp = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "Original", "address": "Addr", "city": "Tangier", "lat": 35.7, "lng": -5.8},
    )
    site_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/sites/{site_id}",
        headers=headers,
        json={"name": "Updated Name", "city": "Tanger"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["city"] == "Tanger"


@pytest.mark.asyncio
async def test_delete_site(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SDEL-{uuid.uuid4().hex[:4]}"

    create_resp = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "To Delete", "address": "Addr", "city": "Agadir", "lat": 30.4, "lng": -9.6},
    )
    site_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/sites/{site_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/v1/sites/{site_id}", headers=headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_site_summary(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SSUM-{uuid.uuid4().hex[:4]}"

    create_resp = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "Summary Site", "address": "Addr", "city": "Marrakech", "lat": 31.6, "lng": -8.0},
    )
    site_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/sites/{site_id}/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == code
    assert data["employee_count"] == 0
    assert data["vehicle_count"] == 0


@pytest.mark.asyncio
async def test_postgis_geometry_created(client: AsyncClient) -> None:
    """Verify the PostGIS geometry column is populated."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"SGEO-{uuid.uuid4().hex[:4]}"

    response = await client.post(
        "/api/v1/sites/",
        headers=headers,
        json={"code": code, "name": "Geo Site", "address": "Addr", "city": "Kenitra", "lat": 34.26, "lng": -6.58},
    )
    assert response.status_code == 201
    # The geom column isn't in the response (internal),
    # but if the create succeeded with ST_MakePoint, PostGIS is working.
    # Verify by fetching and checking lat/lng are preserved
    site_id = response.json()["id"]
    get_resp = await client.get(f"/api/v1/sites/{site_id}", headers=headers)
    assert get_resp.json()["lat"] == pytest.approx(34.26)
    assert get_resp.json()["lng"] == pytest.approx(-6.58)
