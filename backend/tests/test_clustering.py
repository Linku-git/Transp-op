from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.services.clustering import (
    ClusterResult,
    EmployeePoint,
    cluster_dbscan,
    cluster_hierarchical,
    cluster_kmeans,
    run_clustering,
)
from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_points(
    coords: list[tuple[float, float]],
    pmr_indices: set[int] | None = None,
) -> list[EmployeePoint]:
    """Create EmployeePoint list from (lat, lng) tuples."""
    pmr = pmr_indices or set()
    return [
        EmployeePoint(
            employee_id=uuid.uuid4(),
            lat=lat,
            lng=lng,
            is_pmr=i in pmr,
        )
        for i, (lat, lng) in enumerate(coords)
    ]


async def _create_site(
    client: AsyncClient, token: str, name: str = "Cluster Site"
) -> str:
    code = f"CL-{uuid.uuid4().hex[:6]}"
    resp = await client.post(
        "/api/v1/sites/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "code": code,
            "name": name,
            "address": "123 Rue Cluster",
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
    lat: float = 33.58,
    lng: float = -7.60,
    is_pmr: bool = False,
    first_name: str = "Emp",
    last_name: str = "Test",
) -> str:
    matricule = f"CL-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "matricule": matricule,
            "first_name": first_name,
            "last_name": last_name,
            "site_id": site_id,
            "city": "Casablanca",
            "lat": lat,
            "lng": lng,
            "is_pmr": is_pmr,
        },
    )
    assert resp.status_code == 201, f"Employee creation failed: {resp.text}"
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Unit tests — clustering algorithms
# ---------------------------------------------------------------------------


def test_dbscan_clustering() -> None:
    """DBSCAN produces expected clusters for known data."""
    # Two tight groups ~5km apart
    group_a = [(33.57, -7.60), (33.571, -7.601), (33.572, -7.599)]
    group_b = [(33.62, -7.55), (33.621, -7.551)]
    points = _make_points(group_a + group_b)

    clusters = cluster_dbscan(points, eps_meters=1000, min_samples=2)
    assert len(clusters) >= 2

    # All employees should be assigned
    all_ids = set()
    for c in clusters:
        all_ids.update(c.employee_ids)
    assert len(all_ids) == 5

    # Each cluster has correct employee_count
    for c in clusters:
        assert c.employee_count == len(c.employee_ids)


def test_kmeans_clustering() -> None:
    """KMeans produces expected clusters for known data."""
    coords = [(33.57, -7.60), (33.571, -7.601), (33.62, -7.55), (33.621, -7.551)]
    points = _make_points(coords)

    clusters = cluster_kmeans(points, n_clusters=2)
    assert len(clusters) == 2

    total = sum(c.employee_count for c in clusters)
    assert total == 4


def test_hierarchical_clustering() -> None:
    """Hierarchical clustering produces valid clusters."""
    coords = [(33.57, -7.60), (33.571, -7.601), (33.572, -7.599), (33.62, -7.55)]
    points = _make_points(coords)

    clusters = cluster_hierarchical(points, distance_threshold_meters=1000)
    assert len(clusters) >= 1

    total = sum(c.employee_count for c in clusters)
    assert total == 4


def test_per_site_clustering() -> None:
    """Clustering only considers employees from provided list (site isolation)."""
    site_a_coords = [(33.57, -7.60), (33.571, -7.601)]
    site_b_coords = [(34.00, -6.80), (34.001, -6.801)]

    points_a = _make_points(site_a_coords)
    points_b = _make_points(site_b_coords)

    clusters_a = cluster_dbscan(points_a, eps_meters=1000, min_samples=2)
    clusters_b = cluster_dbscan(points_b, eps_meters=1000, min_samples=2)

    # Site A employees should not appear in site B clusters
    ids_a = {eid for c in clusters_a for eid in c.employee_ids}
    ids_b = {eid for c in clusters_b for eid in c.employee_ids}
    assert ids_a.isdisjoint(ids_b)


def test_pmr_flagging() -> None:
    """PMR employees are correctly counted in clusters."""
    coords = [(33.57, -7.60), (33.571, -7.601), (33.572, -7.599)]
    points = _make_points(coords, pmr_indices={0, 2})

    clusters = cluster_dbscan(points, eps_meters=2000, min_samples=2)
    total_pmr = sum(c.pmr_count for c in clusters)
    assert total_pmr == 2


def test_meeting_radius_effect() -> None:
    """Different radii produce different cluster counts (larger radius = fewer clusters)."""
    # Points spread across ~2km
    coords = [
        (33.570, -7.600),
        (33.575, -7.595),
        (33.580, -7.590),
        (33.585, -7.585),
        (33.590, -7.580),
    ]
    points = _make_points(coords)

    clusters_small = cluster_dbscan(points, eps_meters=200, min_samples=2)
    clusters_large = cluster_dbscan(points, eps_meters=2000, min_samples=2)

    # Larger radius should produce fewer or equal clusters
    assert len(clusters_large) <= len(clusters_small)


def test_max_cluster_size() -> None:
    """No cluster exceeds max_cluster_size."""
    # 10 tightly grouped points
    coords = [(33.57 + i * 0.0001, -7.60 + i * 0.0001) for i in range(10)]
    points = _make_points(coords)

    clusters = cluster_dbscan(
        points, eps_meters=5000, min_samples=2, max_cluster_size=4
    )
    for c in clusters:
        assert c.employee_count <= 4


def test_centroid_calculation() -> None:
    """Centroid is the geographic center of cluster members."""
    coords = [(33.57, -7.60), (33.58, -7.60), (33.57, -7.61), (33.58, -7.61)]
    points = _make_points(coords)

    # Force single cluster with KMeans k=1
    clusters = cluster_kmeans(points, n_clusters=1)
    assert len(clusters) == 1

    c = clusters[0]
    expected_lat = round(sum(lat for lat, _ in coords) / 4, 8)
    expected_lng = round(sum(lng for _, lng in coords) / 4, 8)

    assert abs(c.centroid_lat - expected_lat) < 0.001
    assert abs(c.centroid_lng - expected_lng) < 0.001


def test_empty_site_clustering() -> None:
    """Empty employee list returns empty clusters."""
    clusters = cluster_dbscan([], eps_meters=500, min_samples=2)
    assert clusters == []

    clusters = cluster_kmeans([], n_clusters=3)
    assert clusters == []

    clusters = cluster_hierarchical([], distance_threshold_meters=500)
    assert clusters == []


# ---------------------------------------------------------------------------
# Integration tests — API endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_endpoint(client: AsyncClient) -> None:
    """POST /clusters/generate creates clusters and returns them."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    # Create 5 employees with coordinates
    for i in range(5):
        await _create_employee(
            client, token, site_id,
            lat=33.57 + i * 0.001,
            lng=-7.60 + i * 0.001,
            first_name=f"Cl{i}",
            last_name=f"E{i}",
        )

    resp = await client.post(
        "/api/v1/clusters/generate",
        headers=headers,
        json={
            "site_id": site_id,
            "algorithm": "dbscan",
            "eps_meters": 1000,
            "min_samples": 2,
        },
    )
    assert resp.status_code == 201, f"Generate failed: {resp.text}"
    data = resp.json()

    assert "optimization" in data
    assert data["optimization"]["status"] == "completed"
    assert data["total_employees"] == 5
    assert data["total_clusters"] >= 1

    for cluster in data["clusters"]:
        assert "centroid_lat" in cluster
        assert "centroid_lng" in cluster
        assert "employee_ids" in cluster
        assert cluster["employee_count"] == len(cluster["employee_ids"])


@pytest.mark.asyncio
async def test_get_clusters(client: AsyncClient) -> None:
    """GET /clusters returns saved clusters after generation."""
    token = await login_as_admin(client)
    site_id = await _create_site(client, token, name="Get Cluster Site")
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(3):
        await _create_employee(
            client, token, site_id,
            lat=33.57 + i * 0.0005,
            lng=-7.60 + i * 0.0005,
            first_name=f"G{i}",
            last_name=f"T{i}",
        )

    # Generate
    gen_resp = await client.post(
        "/api/v1/clusters/generate",
        headers=headers,
        json={
            "site_id": site_id,
            "algorithm": "kmeans",
            "n_clusters": 2,
        },
    )
    assert gen_resp.status_code == 201

    # List clusters for site
    list_resp = await client.get(
        f"/api/v1/clusters?site_id={site_id}",
        headers=headers,
    )
    assert list_resp.status_code == 200
    clusters = list_resp.json()
    assert len(clusters) >= 1

    # Get single cluster detail
    cluster_id = clusters[0]["id"]
    detail_resp = await client.get(
        f"/api/v1/clusters/{cluster_id}",
        headers=headers,
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == cluster_id
    assert "employees" in detail
    assert len(detail["employees"]) > 0
    assert "first_name" in detail["employees"][0]
