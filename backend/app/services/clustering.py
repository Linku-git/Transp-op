from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.cluster import DBSCAN, KMeans

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class EmployeePoint:
    """Lightweight employee geo-point for clustering."""

    employee_id: uuid.UUID
    lat: float
    lng: float
    is_pmr: bool = False


@dataclass
class ClusterResult:
    """A single cluster output."""

    centroid_lat: float
    centroid_lng: float
    employee_ids: list[uuid.UUID] = field(default_factory=list)
    pmr_count: int = 0
    employee_count: int = 0


# ---------------------------------------------------------------------------
# Centroid calculation
# ---------------------------------------------------------------------------


def _calculate_centroid(points: list[EmployeePoint]) -> tuple[float, float]:
    """Return the geographic center (mean lat, mean lng) of a set of points."""
    if not points:
        return 0.0, 0.0
    lats = [p.lat for p in points]
    lngs = [p.lng for p in points]
    return round(sum(lats) / len(lats), 8), round(sum(lngs) / len(lngs), 8)


# ---------------------------------------------------------------------------
# Cluster post-processing
# ---------------------------------------------------------------------------


def _build_clusters(
    employees: list[EmployeePoint],
    labels: np.ndarray,
    max_cluster_size: int | None = None,
) -> list[ClusterResult]:
    """Build ClusterResult list from clustering labels.

    Noise points (label == -1) are assigned as individual clusters.
    If ``max_cluster_size`` is set, oversized clusters are split.
    """
    label_set = set(int(l) for l in labels)
    groups: dict[int, list[EmployeePoint]] = {}
    for emp, label in zip(employees, labels):
        lbl = int(label)
        groups.setdefault(lbl, []).append(emp)

    results: list[ClusterResult] = []

    for label in sorted(label_set):
        members = groups[label]

        # Noise: each employee becomes its own cluster
        if label == -1:
            for emp in members:
                clat, clng = emp.lat, emp.lng
                results.append(
                    ClusterResult(
                        centroid_lat=clat,
                        centroid_lng=clng,
                        employee_ids=[emp.employee_id],
                        pmr_count=1 if emp.is_pmr else 0,
                        employee_count=1,
                    )
                )
            continue

        # Split oversized clusters
        if max_cluster_size and len(members) > max_cluster_size:
            chunks = _split_cluster(members, max_cluster_size)
            for chunk in chunks:
                clat, clng = _calculate_centroid(chunk)
                results.append(
                    ClusterResult(
                        centroid_lat=clat,
                        centroid_lng=clng,
                        employee_ids=[e.employee_id for e in chunk],
                        pmr_count=sum(1 for e in chunk if e.is_pmr),
                        employee_count=len(chunk),
                    )
                )
        else:
            clat, clng = _calculate_centroid(members)
            results.append(
                ClusterResult(
                    centroid_lat=clat,
                    centroid_lng=clng,
                    employee_ids=[e.employee_id for e in members],
                    pmr_count=sum(1 for e in members if e.is_pmr),
                    employee_count=len(members),
                )
            )

    return results


def _split_cluster(
    members: list[EmployeePoint], max_size: int
) -> list[list[EmployeePoint]]:
    """Split an oversized cluster using KMeans sub-clustering."""
    n_sub = max(2, (len(members) + max_size - 1) // max_size)
    coords = np.array([[e.lat, e.lng] for e in members])
    km = KMeans(n_clusters=n_sub, n_init=5, random_state=42)
    sub_labels = km.fit_predict(coords)
    chunks: dict[int, list[EmployeePoint]] = {}
    for emp, lbl in zip(members, sub_labels):
        chunks.setdefault(int(lbl), []).append(emp)
    return list(chunks.values())


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------


def _to_radians_array(employees: list[EmployeePoint]) -> np.ndarray:
    """Convert lat/lng to radians for haversine-based algorithms."""
    return np.radians(np.array([[e.lat, e.lng] for e in employees]))


# ---------------------------------------------------------------------------
# DBSCAN clustering
# ---------------------------------------------------------------------------


def cluster_dbscan(
    employees: list[EmployeePoint],
    eps_meters: float = 500.0,
    min_samples: int = 2,
    max_cluster_size: int | None = None,
) -> list[ClusterResult]:
    """Cluster employees using DBSCAN with haversine distance.

    Args:
        employees: List of employee geo-points.
        eps_meters: Neighbourhood radius in meters.
        min_samples: Minimum points to form a cluster.
        max_cluster_size: Optional max employees per cluster.

    Returns:
        List of ClusterResult.
    """
    if not employees:
        return []

    coords_rad = _to_radians_array(employees)
    earth_radius_m = 6_371_000.0
    eps_rad = eps_meters / earth_radius_m

    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine")
    labels = db.fit_predict(coords_rad)

    clusters = _build_clusters(employees, labels, max_cluster_size)
    logger.info(
        "DBSCAN: %d employees -> %d clusters (eps=%dm, min_samples=%d)",
        len(employees),
        len(clusters),
        int(eps_meters),
        min_samples,
    )
    return clusters


# ---------------------------------------------------------------------------
# KMeans clustering
# ---------------------------------------------------------------------------


def cluster_kmeans(
    employees: list[EmployeePoint],
    n_clusters: int | None = None,
    max_cluster_size: int | None = None,
) -> list[ClusterResult]:
    """Cluster employees using KMeans.

    If ``n_clusters`` is not provided, auto-determine from employee count.
    """
    if not employees:
        return []

    coords = np.array([[e.lat, e.lng] for e in employees])

    if n_clusters is None:
        # Heuristic: sqrt(n/2), at least 2, at most n
        n_clusters = max(2, min(len(employees), int(np.sqrt(len(employees) / 2))))
    n_clusters = min(n_clusters, len(employees))

    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = km.fit_predict(coords)

    clusters = _build_clusters(employees, labels, max_cluster_size)
    logger.info(
        "KMeans: %d employees -> %d clusters (k=%d)",
        len(employees),
        len(clusters),
        n_clusters,
    )
    return clusters


# ---------------------------------------------------------------------------
# Hierarchical clustering
# ---------------------------------------------------------------------------


def cluster_hierarchical(
    employees: list[EmployeePoint],
    distance_threshold_meters: float = 500.0,
    max_cluster_size: int | None = None,
) -> list[ClusterResult]:
    """Cluster employees using agglomerative hierarchical clustering.

    Uses Ward linkage with a distance threshold converted from meters.
    """
    if not employees:
        return []

    if len(employees) == 1:
        e = employees[0]
        return [
            ClusterResult(
                centroid_lat=e.lat,
                centroid_lng=e.lng,
                employee_ids=[e.employee_id],
                pmr_count=1 if e.is_pmr else 0,
                employee_count=1,
            )
        ]

    coords = np.array([[e.lat, e.lng] for e in employees])

    # Convert meters to approximate degree distance for threshold
    # 1 degree lat ~ 111,320 meters
    threshold_deg = distance_threshold_meters / 111_320.0

    Z = linkage(coords, method="ward")
    labels = fcluster(Z, t=threshold_deg, criterion="distance") - 1  # 0-indexed

    clusters = _build_clusters(employees, labels, max_cluster_size)
    logger.info(
        "Hierarchical: %d employees -> %d clusters (threshold=%dm)",
        len(employees),
        len(clusters),
        int(distance_threshold_meters),
    )
    return clusters


# ---------------------------------------------------------------------------
# Unified clustering entry point
# ---------------------------------------------------------------------------


def run_clustering(
    employees: list[EmployeePoint],
    algorithm: str = "dbscan",
    eps_meters: float = 500.0,
    min_samples: int = 2,
    n_clusters: int | None = None,
    max_cluster_size: int | None = None,
) -> list[ClusterResult]:
    """Run clustering with the specified algorithm.

    Args:
        employees: List of employee geo-points.
        algorithm: One of 'dbscan', 'kmeans', 'hierarchical'.
        eps_meters: Radius for DBSCAN / hierarchical (in meters).
        min_samples: Min points for DBSCAN.
        n_clusters: Number of clusters for KMeans (auto if None).
        max_cluster_size: Optional max employees per cluster.

    Returns:
        List of ClusterResult.
    """
    if algorithm == "dbscan":
        return cluster_dbscan(employees, eps_meters, min_samples, max_cluster_size)
    elif algorithm == "kmeans":
        return cluster_kmeans(employees, n_clusters, max_cluster_size)
    elif algorithm == "hierarchical":
        return cluster_hierarchical(employees, eps_meters, max_cluster_size)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use dbscan, kmeans, or hierarchical.")
