from __future__ import annotations

import logging
import math

import numpy as np
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — CDC SOTREG v5.0
# ---------------------------------------------------------------------------

DEFAULT_EPS_METERS: float = 500.0
DEFAULT_MIN_PTS: int = 5
EARTH_RADIUS_KM: float = 6371.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _haversine_distance(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float,
) -> float:
    """Compute haversine distance in meters between two GPS points.

    Uses the standard haversine formula:

    .. math::

        a = \\sin^2(\\Delta\\phi/2)
            + \\cos(\\phi_1) \\cos(\\phi_2) \\sin^2(\\Delta\\lambda/2)

        d = 2 R \\arcsin(\\sqrt{a})

    Args:
        lat1: Latitude of point 1 in degrees.
        lng1: Longitude of point 1 in degrees.
        lat2: Latitude of point 2 in degrees.
        lng2: Longitude of point 2 in degrees.

    Returns:
        Distance in meters.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * 1000.0 * c


def _compute_catchment_radius(
    centroid_lat: float,
    centroid_lng: float,
    members: list[dict],
) -> float:
    """Compute the maximum distance (meters) from centroid to any member.

    Args:
        centroid_lat: Centroid latitude in degrees.
        centroid_lng: Centroid longitude in degrees.
        members: List of employee dicts with ``lat`` and ``lng`` keys.

    Returns:
        Maximum distance in meters; 0.0 if *members* is empty.
    """
    if not members:
        return 0.0

    max_dist = 0.0
    for m in members:
        d = _haversine_distance(centroid_lat, centroid_lng, m["lat"], m["lng"])
        if d > max_dist:
            max_dist = d
    return max_dist


# ---------------------------------------------------------------------------
# DBSCAN stop generation
# ---------------------------------------------------------------------------

def generate_stops_from_employees(
    employees: list[dict],
    eps_m: float = DEFAULT_EPS_METERS,
    min_pts: int = DEFAULT_MIN_PTS,
) -> list[dict]:
    """Generate candidate stop locations from employee home coordinates.

    Uses DBSCAN clustering with the haversine metric to group nearby
    employees into candidate stops.  Each cluster centroid becomes a
    candidate stop location.

    CDC SOTREG v5.0 defaults:
    - eps = 500 m (converted to radians for haversine metric)
    - min_samples = 5 employees to form a stop

    Args:
        employees: List of dicts, each containing:
            - ``employee_id`` (str): Unique employee identifier.
            - ``lat`` (float): Home latitude in degrees.
            - ``lng`` (float): Home longitude in degrees.
        eps_m: Maximum distance in meters between two samples for
            them to be considered in the same neighbourhood.
        min_pts: Minimum number of employees to form a cluster (stop).

    Returns:
        List of stop dicts, each containing:
        - ``cluster_id`` (int): Sequential cluster identifier (0-based).
        - ``centroid_lat`` (float): Mean latitude of cluster members.
        - ``centroid_lng`` (float): Mean longitude of cluster members.
        - ``employee_count`` (int): Number of employees in the cluster.
        - ``employee_ids`` (list[str]): IDs of employees in the cluster.
        - ``catchment_radius_m`` (float): Maximum distance from centroid
          to any cluster member, in meters.
        - ``source`` (str): Always ``"dbscan"``.

    Raises:
        ValueError: If *eps_m* is non-positive or *min_pts* < 1.
    """
    # ---- Input validation ---------------------------------------------------
    if eps_m <= 0:
        raise ValueError(f"eps_m must be positive, got {eps_m}")
    if min_pts < 1:
        raise ValueError(f"min_pts must be >= 1, got {min_pts}")

    if not employees:
        logger.info("No employees provided; returning empty stop list")
        return []

    if len(employees) < min_pts:
        logger.warning(
            "Only %d employees provided but min_pts=%d; "
            "DBSCAN will classify all as noise",
            len(employees),
            min_pts,
        )

    # ---- Validate and extract coordinates -----------------------------------
    valid_employees: list[dict] = []
    for emp in employees:
        lat = emp.get("lat")
        lng = emp.get("lng")
        emp_id = emp.get("employee_id")

        if lat is None or lng is None or emp_id is None:
            logger.warning(
                "Skipping employee with missing data: id=%s, lat=%s, lng=%s",
                emp_id,
                lat,
                lng,
            )
            continue

        if not (-90.0 <= lat <= 90.0):
            logger.warning(
                "Skipping employee %s: latitude %s out of range [-90, 90]",
                emp_id,
                lat,
            )
            continue

        if not (-180.0 <= lng <= 180.0):
            logger.warning(
                "Skipping employee %s: longitude %s out of range [-180, 180]",
                emp_id,
                lng,
            )
            continue

        valid_employees.append(emp)

    if not valid_employees:
        logger.info("No valid employees after filtering; returning empty list")
        return []

    logger.info(
        "Running DBSCAN on %d employees (eps=%dm, min_pts=%d)",
        len(valid_employees),
        int(eps_m),
        min_pts,
    )

    # ---- Prepare data for DBSCAN -------------------------------------------
    # sklearn DBSCAN with haversine expects (lat, lng) in radians
    coords_rad = np.array([
        [math.radians(e["lat"]), math.radians(e["lng"])]
        for e in valid_employees
    ])

    # eps must be in radians for haversine: eps_rad = eps_m / (R_earth * 1000)
    eps_rad = eps_m / (EARTH_RADIUS_KM * 1000.0)

    # ---- Run DBSCAN ---------------------------------------------------------
    db = DBSCAN(
        eps=eps_rad,
        min_samples=min_pts,
        metric="haversine",
        algorithm="ball_tree",
    )
    labels = db.fit_predict(coords_rad)

    # ---- Build cluster/stop results -----------------------------------------
    # Collect members by label (label -1 = noise, skip)
    cluster_members: dict[int, list[dict]] = {}
    noise_count = 0
    for idx, label in enumerate(labels):
        if label == -1:
            noise_count += 1
            continue
        cluster_members.setdefault(label, []).append(valid_employees[idx])

    if noise_count > 0:
        logger.info(
            "DBSCAN classified %d employees as noise (not assigned to any stop)",
            noise_count,
        )

    stops: list[dict] = []
    for seq_id, (label, members) in enumerate(
        sorted(cluster_members.items())
    ):
        # Compute centroid as mean of member coordinates (in degrees)
        lats = [m["lat"] for m in members]
        lngs = [m["lng"] for m in members]
        centroid_lat = sum(lats) / len(lats)
        centroid_lng = sum(lngs) / len(lngs)

        # Compute catchment radius
        catchment_m = _compute_catchment_radius(centroid_lat, centroid_lng, members)

        employee_ids = [m["employee_id"] for m in members]

        stops.append({
            "cluster_id": seq_id,
            "centroid_lat": round(centroid_lat, 6),
            "centroid_lng": round(centroid_lng, 6),
            "employee_count": len(members),
            "employee_ids": employee_ids,
            "catchment_radius_m": round(catchment_m, 1),
            "source": "dbscan",
        })

    logger.info(
        "Generated %d candidate stops from %d employees "
        "(%d noise, eps=%dm, min_pts=%d)",
        len(stops),
        len(valid_employees),
        noise_count,
        int(eps_m),
        min_pts,
    )

    return stops


# ---------------------------------------------------------------------------
# Stop merging (post-processing)
# ---------------------------------------------------------------------------

def merge_nearby_stops(
    stops: list[dict],
    merge_distance_m: float = 200.0,
) -> list[dict]:
    """Merge stops whose centroids are within *merge_distance_m* meters.

    When two stops are close enough to be merged, the resulting stop has:
    - centroid at the weighted-average position (by employee count)
    - the union of employee IDs
    - catchment radius recomputed

    This is useful as a post-processing step after DBSCAN to consolidate
    stops that ended up very close due to parameter sensitivity.

    Args:
        stops: List of stop dicts as returned by
            :func:`generate_stops_from_employees`.
        merge_distance_m: Maximum centroid-to-centroid distance in meters
            for merging.  Must be positive.

    Returns:
        A new list of merged stop dicts with sequential ``cluster_id``.

    Raises:
        ValueError: If *merge_distance_m* is non-positive.
    """
    if merge_distance_m <= 0:
        raise ValueError(
            f"merge_distance_m must be positive, got {merge_distance_m}"
        )

    if len(stops) <= 1:
        return list(stops)

    # Track which stops have been merged into another
    merged_into: dict[int, int] = {}  # original index -> merged-into index
    result_groups: list[list[dict]] = []

    working = [dict(s) for s in stops]  # shallow copy

    for i in range(len(working)):
        if i in merged_into:
            continue

        group = [working[i]]

        for j in range(i + 1, len(working)):
            if j in merged_into:
                continue

            dist = _haversine_distance(
                working[i]["centroid_lat"],
                working[i]["centroid_lng"],
                working[j]["centroid_lat"],
                working[j]["centroid_lng"],
            )
            if dist <= merge_distance_m:
                group.append(working[j])
                merged_into[j] = i

        result_groups.append(group)

    # Build merged stops
    merged_stops: list[dict] = []
    for seq_id, group in enumerate(result_groups):
        total_count = sum(s["employee_count"] for s in group)
        all_ids: list[str] = []
        weighted_lat = 0.0
        weighted_lng = 0.0

        for s in group:
            weight = s["employee_count"]
            weighted_lat += s["centroid_lat"] * weight
            weighted_lng += s["centroid_lng"] * weight
            all_ids.extend(s["employee_ids"])

        centroid_lat = weighted_lat / total_count
        centroid_lng = weighted_lng / total_count

        # Recompute catchment as max distance from merged centroid
        max_radius = 0.0
        for s in group:
            for eid in s["employee_ids"]:
                # Use original centroid as proxy — the actual employee coords
                # are not available here, so use catchment_radius + inter-centroid
                # distance as upper bound.
                inter_dist = _haversine_distance(
                    centroid_lat,
                    centroid_lng,
                    s["centroid_lat"],
                    s["centroid_lng"],
                )
                candidate = inter_dist + s["catchment_radius_m"]
                if candidate > max_radius:
                    max_radius = candidate

        merged_stops.append({
            "cluster_id": seq_id,
            "centroid_lat": round(centroid_lat, 6),
            "centroid_lng": round(centroid_lng, 6),
            "employee_count": total_count,
            "employee_ids": all_ids,
            "catchment_radius_m": round(max_radius, 1),
            "source": "dbscan_merged",
        })

    merged_count = len(stops) - len(merged_stops)
    if merged_count > 0:
        logger.info(
            "Merged %d nearby stops (distance <= %dm): %d -> %d stops",
            merged_count,
            int(merge_distance_m),
            len(stops),
            len(merged_stops),
        )

    return merged_stops
