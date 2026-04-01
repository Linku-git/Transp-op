from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from app.services.clustering import ClusterResult, EmployeePoint
from app.services.osrm_client import (
    NearestResult,
    RouteResult,
    _haversine_meters,
    osrm_nearest,
    osrm_route,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class AccessLeg:
    """Walking path from an employee to their meeting zone."""

    employee_id: uuid.UUID
    meeting_zone_lat: float
    meeting_zone_lng: float
    walking_distance_meters: float
    walking_time_seconds: float
    within_constraint: bool


@dataclass
class MeetingZone:
    """Optimized meeting/gathering point for a cluster."""

    cluster_index: int
    lat: float
    lng: float
    road_name: str | None
    snap_distance_meters: float
    pmr_accessible: bool
    employee_count: int
    pmr_count: int
    employee_ids: list[uuid.UUID] = field(default_factory=list)
    access_legs: list[AccessLeg] = field(default_factory=list)
    all_within_constraint: bool = True


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


async def optimize_meeting_zones(
    clusters: list[ClusterResult],
    employees: list[EmployeePoint],
    max_walking_distance_meters: float = 800.0,
    use_osrm: bool = True,
) -> list[MeetingZone]:
    """Calculate optimal meeting zones for a set of clusters.

    For each cluster:
    1. Start with cluster centroid
    2. Snap to nearest road (via OSRM or fallback)
    3. Check PMR accessibility
    4. Compute access legs for each employee
    5. Verify walking distance constraints

    Args:
        clusters: Cluster results from clustering engine.
        employees: Full employee list (for coordinate lookup).
        max_walking_distance_meters: Max allowed walking distance.
        use_osrm: Whether to use OSRM (False for unit tests).

    Returns:
        List of MeetingZone, one per cluster.
    """
    # Build employee lookup
    emp_lookup: dict[uuid.UUID, EmployeePoint] = {
        e.employee_id: e for e in employees
    }

    zones: list[MeetingZone] = []

    for idx, cluster in enumerate(clusters):
        # Step 1: Snap centroid to road
        if use_osrm:
            try:
                snap = await osrm_nearest(cluster.centroid_lat, cluster.centroid_lng)
            except Exception:
                logger.warning(
                    "OSRM nearest failed for cluster %d, using raw centroid", idx
                )
                snap = NearestResult(
                    lat=cluster.centroid_lat,
                    lng=cluster.centroid_lng,
                    distance_meters=0.0,
                )
        else:
            # Fallback: use centroid directly
            snap = NearestResult(
                lat=cluster.centroid_lat,
                lng=cluster.centroid_lng,
                distance_meters=0.0,
            )

        # Step 2: PMR accessibility check
        pmr_accessible = _check_pmr_accessibility(cluster, snap)

        # Step 3: Compute access legs
        access_legs: list[AccessLeg] = []
        all_within = True

        for emp_id in cluster.employee_ids:
            emp = emp_lookup.get(emp_id)
            if emp is None:
                continue

            if use_osrm:
                try:
                    route = await osrm_route(
                        emp.lat, emp.lng, snap.lat, snap.lng, profile="walking"
                    )
                except Exception:
                    # Fallback to haversine
                    dist = _haversine_meters(emp.lat, emp.lng, snap.lat, snap.lng)
                    route = RouteResult(
                        distance_meters=dist,
                        duration_seconds=dist / 1000.0 / 4.5 * 3600.0,
                    )
            else:
                dist = _haversine_meters(emp.lat, emp.lng, snap.lat, snap.lng)
                walking_speed_kmh = 4.5
                duration = (dist / 1000.0) / walking_speed_kmh * 3600.0
                route = RouteResult(
                    distance_meters=dist, duration_seconds=duration
                )

            within = route.distance_meters <= max_walking_distance_meters
            if not within:
                all_within = False

            access_legs.append(
                AccessLeg(
                    employee_id=emp_id,
                    meeting_zone_lat=snap.lat,
                    meeting_zone_lng=snap.lng,
                    walking_distance_meters=round(route.distance_meters, 1),
                    walking_time_seconds=round(route.duration_seconds, 1),
                    within_constraint=within,
                )
            )

        zone = MeetingZone(
            cluster_index=idx,
            lat=snap.lat,
            lng=snap.lng,
            road_name=snap.road_name,
            snap_distance_meters=round(snap.distance_meters, 1),
            pmr_accessible=pmr_accessible,
            employee_count=cluster.employee_count,
            pmr_count=cluster.pmr_count,
            employee_ids=cluster.employee_ids,
            access_legs=access_legs,
            all_within_constraint=all_within,
        )
        zones.append(zone)

    logger.info(
        "Meeting zone optimization: %d zones, %d within constraints",
        len(zones),
        sum(1 for z in zones if z.all_within_constraint),
    )
    return zones


# ---------------------------------------------------------------------------
# PMR accessibility check
# ---------------------------------------------------------------------------


def _check_pmr_accessibility(
    cluster: ClusterResult, snap: NearestResult
) -> bool:
    """Check if the meeting zone is PMR-accessible.

    For clusters with PMR employees, the meeting zone must:
    - Be on a road (snap distance < 50m — implies paved surface)
    - Have reasonable snap distance (not in a field/forest)

    For clusters without PMR, always return True.
    """
    if cluster.pmr_count == 0:
        return True

    # PMR zones need to be close to road infrastructure
    return snap.distance_meters < 50.0
