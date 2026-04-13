from __future__ import annotations

import math
import uuid

import pytest
from httpx import AsyncClient

from app.services.sotreg.gravity_model import (
    DEFAULT_BETA,
    DEFAULT_K,
    _haversine_km,
    calibrate_beta,
    compute_gravity_flow,
    compute_od_matrix,
)
from tests.conftest import login_as_admin

# ---------------------------------------------------------------------------
# Ligne helper (reuse from test_ligne)
# ---------------------------------------------------------------------------

LIGNE_BASE = {
    "name": "Ligne OD Test",
    "origin_lat": 33.5731,
    "origin_lng": -7.5898,
    "dest_lat": 33.6,
    "dest_lng": -7.5,
    "distance_km": 25.0,
    "rotations_per_day": 4,
    "operating_days_per_year": 260,
    "service_type": "navette",
    "motorization": "diesel",
    "passenger_count_avg": 40,
}


def _ligne_payload(**overrides: object) -> dict:
    code = f"LOD-{uuid.uuid4().hex[:6]}"
    return {**LIGNE_BASE, "code": code, **overrides}


# ---------------------------------------------------------------------------
# Unit tests — gravity flow computation
# ---------------------------------------------------------------------------


def test_gravity_flow_basic() -> None:
    """T_ij = k * P_i * P_j * exp(-beta * d_ij)."""
    flow = compute_gravity_flow(100, 100, 10.0, beta=0.1, k=0.001)
    expected = 0.001 * 100 * 100 * math.exp(-0.1 * 10.0)
    assert flow == pytest.approx(expected, rel=1e-6)


def test_gravity_flow_zero_population() -> None:
    assert compute_gravity_flow(0, 100, 10.0) == 0.0
    assert compute_gravity_flow(100, 0, 10.0) == 0.0


def test_gravity_flow_zero_distance() -> None:
    flow = compute_gravity_flow(100, 100, 0.0, beta=0.1, k=0.001)
    # exp(0) = 1
    assert flow == pytest.approx(0.001 * 100 * 100, rel=1e-6)


def test_gravity_flow_large_distance() -> None:
    """Large distances produce negligible flows."""
    flow = compute_gravity_flow(100, 100, 500.0, beta=0.1, k=0.001)
    assert flow < 1e-6


def test_gravity_flow_negative_distance_raises() -> None:
    with pytest.raises(ValueError):
        compute_gravity_flow(100, 100, -5.0)


def test_gravity_flow_default_params() -> None:
    flow = compute_gravity_flow(50, 50, 12.0)
    expected = DEFAULT_K * 50 * 50 * math.exp(-DEFAULT_BETA * 12.0)
    assert flow == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# Unit tests — OD matrix computation
# ---------------------------------------------------------------------------


def test_od_matrix_basic() -> None:
    zones = [
        {"id": "A", "name": "Zone A", "lat": 33.57, "lng": -7.59, "population": 100},
        {"id": "B", "name": "Zone B", "lat": 33.60, "lng": -7.50, "population": 80},
    ]
    matrix = compute_od_matrix(zones, beta=0.08, k=0.001)
    # 2 zones → 2 OD pairs (A→B and B→A)
    assert len(matrix) == 2
    assert matrix[0]["origin_id"] == "A"
    assert matrix[0]["dest_id"] == "B"
    assert matrix[0]["flow_estimate"] > 0
    assert matrix[0]["gravity_score"] >= 0


def test_od_matrix_empty_zones() -> None:
    assert compute_od_matrix([]) == []


def test_od_matrix_single_zone() -> None:
    zones = [
        {"id": "A", "name": "Zone A", "lat": 33.57, "lng": -7.59, "population": 100},
    ]
    # Single zone → no pairs (self-flow is skipped)
    matrix = compute_od_matrix(zones)
    assert len(matrix) == 0


def test_od_matrix_three_zones() -> None:
    zones = [
        {"id": "A", "name": "Zone A", "lat": 33.57, "lng": -7.59, "population": 100},
        {"id": "B", "name": "Zone B", "lat": 33.60, "lng": -7.50, "population": 80},
        {"id": "C", "name": "Zone C", "lat": 34.00, "lng": -6.85, "population": 50},
    ]
    matrix = compute_od_matrix(zones, beta=0.08, k=0.001)
    # 3 zones → 6 OD pairs
    assert len(matrix) == 6

    # Verify gravity scores are normalized (max = 100)
    scores = [p["gravity_score"] for p in matrix]
    assert max(scores) == pytest.approx(100.0)


def test_od_matrix_missing_key_raises() -> None:
    zones = [{"id": "A", "name": "Zone A"}]  # missing lat, lng, population
    with pytest.raises(ValueError, match="missing required key"):
        compute_od_matrix(zones)


# ---------------------------------------------------------------------------
# Unit tests — beta calibration
# ---------------------------------------------------------------------------


def test_calibrate_beta_default_on_insufficient_data() -> None:
    assert calibrate_beta([10.0], [5.0]) == DEFAULT_BETA


def test_calibrate_beta_valid_data() -> None:
    # Synthetic data: flow = exp(-0.1 * distance) * constant
    distances = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
    flows = [math.exp(-0.1 * d) * 100 for d in distances]
    beta = calibrate_beta(distances, flows)
    assert 0.05 < beta < 0.15  # Should be close to 0.1


def test_calibrate_beta_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="equal length"):
        calibrate_beta([1.0, 2.0], [1.0])


# ---------------------------------------------------------------------------
# Unit tests — haversine
# ---------------------------------------------------------------------------


def test_haversine_km_known() -> None:
    # Casablanca to Rabat
    dist = _haversine_km(33.5731, -7.5898, 33.9911, -6.8498)
    assert 80 < dist < 95


# ---------------------------------------------------------------------------
# Integration tests — OD matrix compute endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_compute_od_matrix_endpoint(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create two lignes first
    await client.post("/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload())
    await client.post("/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload(
        name="Ligne B", dest_lat=34.0, dest_lng=-6.85, passenger_count_avg=60,
    ))

    response = await client.post(
        "/api/v1/sotreg/od-matrix/compute",
        headers=headers,
        json={"beta": 0.08, "k": 0.001},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entries_computed"] >= 2
    assert data["beta_used"] == pytest.approx(0.08)
    assert len(data["entries"]) >= 2


@pytest.mark.asyncio
async def test_get_od_matrix_for_ligne(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a ligne
    create_resp = await client.post(
        "/api/v1/sotreg/lignes/", headers=headers, json=_ligne_payload()
    )
    ligne_id = create_resp.json()["id"]

    # Compute OD matrix
    await client.post(
        "/api/v1/sotreg/od-matrix/compute",
        headers=headers,
        json={"beta": 0.08},
    )

    # Get OD matrix for the ligne
    response = await client.get(
        f"/api/v1/sotreg/od-matrix/{ligne_id}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_od_matrix_ligne_not_found(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/v1/sotreg/od-matrix/{fake_id}", headers=headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_od_matrix(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/sotreg/od-matrix", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data


# ---------------------------------------------------------------------------
# Integration tests — ZFE endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_zfe_point_check_in_zfe(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/sotreg/zfe/check",
        headers=headers,
        json={"lat": 33.5731, "lng": -7.5898},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_in_zfe"] is True
    assert data["zone_name"] == "Casablanca Centre"


@pytest.mark.asyncio
async def test_zfe_point_check_outside_zfe(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/sotreg/zfe/check",
        headers=headers,
        json={"lat": 31.6295, "lng": -7.9811},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_in_zfe"] is False


@pytest.mark.asyncio
async def test_zfe_lignes_compliance(client: AsyncClient) -> None:
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a ligne in Casablanca (should be in ZFE)
    await client.post(
        "/api/v1/sotreg/lignes/",
        headers=headers,
        json=_ligne_payload(origin_lat=33.5731, origin_lng=-7.5898),
    )

    response = await client.get("/api/v1/sotreg/zfe/lignes", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_lignes" in data
    assert "lignes_in_zfe" in data
    assert "results" in data
