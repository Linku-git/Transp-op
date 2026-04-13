from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.services.sotreg.context_service import compute_line_km_annual
from tests.conftest import login_as_admin

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

LIGNE_BASE = {
    "name": "Ligne Test",
    "origin_lat": 33.5731,
    "origin_lng": -7.5898,
    "dest_lat": 33.6,
    "dest_lng": -7.5,
    "distance_km": 25.0,
    "rotations_per_day": 4,
    "operating_days_per_year": 260,
    "service_type": "navette",
}


def _ligne_payload(**overrides: object) -> dict:
    code = f"L-{uuid.uuid4().hex[:6]}"
    return {**LIGNE_BASE, "code": code, **overrides}


# ---------------------------------------------------------------------------
# Unit tests — compute_line_km_annual
# ---------------------------------------------------------------------------


def test_compute_line_km_annual_basic() -> None:
    assert compute_line_km_annual(25.0, 4, 260) == 26000.0


def test_compute_line_km_annual_single_rotation() -> None:
    assert compute_line_km_annual(10.0, 1, 365) == 3650.0


def test_compute_line_km_annual_zero_distance() -> None:
    assert compute_line_km_annual(0.0, 4, 260) == 0.0


def test_compute_line_km_annual_zero_rotations() -> None:
    assert compute_line_km_annual(25.0, 0, 260) == 0.0


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


def test_schema_rejects_invalid_service_type() -> None:
    from app.schemas.ligne import LigneCreate

    with pytest.raises(Exception):
        LigneCreate(**{**LIGNE_BASE, "code": "X1", "service_type": "invalid"})


def test_schema_accepts_valid_service_types() -> None:
    from app.schemas.ligne import LigneCreate

    for st in ("navette", "liaison", "vip", "mixte"):
        obj = LigneCreate(**{**LIGNE_BASE, "code": "X1", "service_type": st})
        assert obj.service_type == st


def test_schema_rejects_negative_distance() -> None:
    from app.schemas.ligne import LigneCreate

    with pytest.raises(Exception):
        LigneCreate(**{**LIGNE_BASE, "code": "X2", "distance_km": -5})


def test_schema_rejects_zero_distance() -> None:
    from app.schemas.ligne import LigneCreate

    with pytest.raises(Exception):
        LigneCreate(**{**LIGNE_BASE, "code": "X3", "distance_km": 0})


def test_update_schema_partial() -> None:
    from app.schemas.ligne import LigneUpdate

    obj = LigneUpdate(name="New Name")
    dumped = obj.model_dump(exclude_unset=True)
    assert dumped == {"name": "New Name"}


# ---------------------------------------------------------------------------
# Integration tests — CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_ligne(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = _ligne_payload()

    response = await client.post("/api/v1/sotreg/lignes/", headers=headers, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == payload["code"]
    assert data["name"] == "Ligne Test"
    assert data["service_type"] == "navette"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_km_annual_auto_computes(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = _ligne_payload(distance_km=25.0, rotations_per_day=4, operating_days_per_year=260)

    response = await client.post("/api/v1/sotreg/lignes/", headers=headers, json=payload)
    assert response.status_code == 201
    assert response.json()["km_annual"] == pytest.approx(26000.0)


@pytest.mark.asyncio
async def test_create_ligne_duplicate_code(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    code = f"LDUP-{uuid.uuid4().hex[:4]}"

    await client.post("/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload(code=code))
    response = await client.post(
        "/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload(code=code)
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_lignes(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create one to ensure list is non-empty
    await client.post("/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload())

    response = await client.get("/api/v1/sotreg/lignes/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)
    assert data["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_get_ligne_by_id(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload()
    )
    ligne_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/sotreg/lignes/{ligne_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == ligne_id


@pytest.mark.asyncio
async def test_get_ligne_not_found(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = str(uuid.uuid4())

    response = await client.get(f"/api/v1/sotreg/lignes/{fake_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_ligne(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload()
    )
    ligne_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/sotreg/lignes/{ligne_id}",
        headers=headers,
        json={"name": "Updated Ligne", "distance_km": 50.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Ligne"
    assert data["distance_km"] == pytest.approx(50.0)
    # km_annual recomputed: 50 * 4 * 260 = 52000
    assert data["km_annual"] == pytest.approx(52000.0)


@pytest.mark.asyncio
async def test_delete_ligne(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload()
    )
    ligne_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/sotreg/lignes/{ligne_id}", headers=headers)
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/api/v1/sotreg/lignes/{ligne_id}", headers=headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_invalid_service_type_api(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/sotreg/lignes/",
        headers=headers,
        json=_ligne_payload(service_type="invalid"),
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Integration tests — Context snapshot
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_context_snapshot(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a ligne with known values
    await client.post(
        "/api/v1/sotreg/lignes/",
        headers=headers,
        json=_ligne_payload(motorization="diesel"),
    )

    response = await client.get("/api/v1/sotreg/context/snapshot", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_vehicles"] >= 1
    assert data["total_km_annual"] > 0
    assert data["currency"] == "MAD"
    assert "snapshot_date" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_context_snapshot_empty(client: AsyncClient) -> None:
    """Snapshot with no lignes should return zeroed values (or reflect existing)."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/sotreg/context/snapshot", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "MAD"
    assert isinstance(data["total_vehicles"], int)
    assert isinstance(data["total_km_annual"], float)
