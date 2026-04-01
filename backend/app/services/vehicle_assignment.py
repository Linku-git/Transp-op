from __future__ import annotations

import logging
import math
import uuid
from dataclasses import dataclass, field

from app.services.clustering import ClusterResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

EARTH_RADIUS_KM = 6_371.0


@dataclass
class VehicleCandidate:
    """A vehicle available for assignment."""

    vehicle_id: uuid.UUID
    capacity: int
    is_pmr_accessible: bool
    zfe_compliant: bool
    type: str
    is_volunteer: bool = False


@dataclass
class AssignmentResult:
    """Result of assigning a vehicle to a (sub-)cluster."""

    cluster_index: int
    vehicle_id: uuid.UUID | None  # None if no vehicle available
    employee_ids: list[uuid.UUID] = field(default_factory=list)
    employee_count: int = 0
    pmr_count: int = 0
    occupancy_rate: float = 0.0  # employees / vehicle capacity
    was_split: bool = False
    was_merged: bool = False


@dataclass
class AssignmentSummary:
    """Overall summary of the vehicle assignment process."""

    assignments: list[AssignmentResult] = field(default_factory=list)
    total_vehicles_used: int = 0
    total_employees_assigned: int = 0
    avg_occupancy_rate: float = 0.0
    unassigned_clusters: list[int] = field(default_factory=list)
    recommended_vehicles: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Distance helper
# ---------------------------------------------------------------------------


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the great-circle distance in km between two points."""
    lat1_r, lng1_r = math.radians(lat1), math.radians(lng1)
    lat2_r, lng2_r = math.radians(lat2), math.radians(lng2)

    dlat = lat2_r - lat1_r
    dlng = lng2_r - lng1_r

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# Vehicle selection
# ---------------------------------------------------------------------------


def _find_best_vehicle(
    cluster: ClusterResult,
    available_vehicles: list[VehicleCandidate],
    site_zfe: bool,
) -> VehicleCandidate | None:
    """Find the smallest vehicle that fits the cluster, respecting constraints.

    Filters:
      - PMR-accessible vehicles only when cluster has PMR employees.
      - ZFE-compliant vehicles only when the site is in a ZFE zone.

    Among eligible vehicles, returns the one with the smallest capacity
    that is still >= the cluster employee count (best-fit).
    """
    candidates = list(available_vehicles)

    if cluster.pmr_count > 0:
        candidates = [v for v in candidates if v.is_pmr_accessible]

    if site_zfe:
        candidates = [v for v in candidates if v.zfe_compliant]

    # Only vehicles that can hold the entire cluster
    candidates = [v for v in candidates if v.capacity >= cluster.employee_count]

    if not candidates:
        return None

    # Best-fit: smallest sufficient capacity to minimise wasted seats
    candidates.sort(key=lambda v: v.capacity)
    return candidates[0]


# ---------------------------------------------------------------------------
# Cluster splitting
# ---------------------------------------------------------------------------


def split_cluster(
    cluster: ClusterResult,
    max_capacity: int,
    employee_locations: dict[uuid.UUID, tuple[float, float]] | None = None,
    employee_pmr: dict[uuid.UUID, bool] | None = None,
) -> list[ClusterResult]:
    """Split a cluster that exceeds *max_capacity* into sub-clusters.

    Uses geographic bisection: employees are sorted by latitude, then
    divided into consecutive chunks of at most *max_capacity*.

    Args:
        cluster: The oversized cluster.
        max_capacity: Maximum employees per sub-cluster.
        employee_locations: Mapping employee_id -> (lat, lng).  When
            provided, sub-cluster centroids are recalculated from actual
            locations.  Otherwise the original cluster centroid is reused.
        employee_pmr: Mapping employee_id -> is_pmr flag for accurate
            PMR counting in sub-clusters.

    Returns:
        A list of smaller ClusterResult objects.
    """
    if cluster.employee_count <= max_capacity:
        return [cluster]

    emp_ids = list(cluster.employee_ids)

    # Sort by latitude when we have location data; otherwise keep order
    if employee_locations:
        emp_ids.sort(key=lambda eid: employee_locations.get(eid, (0.0, 0.0))[0])

    sub_clusters: list[ClusterResult] = []
    for i in range(0, len(emp_ids), max_capacity):
        chunk = emp_ids[i : i + max_capacity]

        # Recalculate centroid from actual positions if available
        if employee_locations:
            lats = [employee_locations[eid][0] for eid in chunk if eid in employee_locations]
            lngs = [employee_locations[eid][1] for eid in chunk if eid in employee_locations]
            centroid_lat = sum(lats) / len(lats) if lats else cluster.centroid_lat
            centroid_lng = sum(lngs) / len(lngs) if lngs else cluster.centroid_lng
        else:
            centroid_lat = cluster.centroid_lat
            centroid_lng = cluster.centroid_lng

        # PMR count for sub-cluster
        if employee_pmr:
            pmr = sum(1 for eid in chunk if employee_pmr.get(eid, False))
        else:
            # Distribute original PMR count proportionally
            ratio = len(chunk) / cluster.employee_count
            pmr = round(cluster.pmr_count * ratio)

        sub_clusters.append(
            ClusterResult(
                centroid_lat=round(centroid_lat, 8),
                centroid_lng=round(centroid_lng, 8),
                employee_ids=chunk,
                pmr_count=pmr,
                employee_count=len(chunk),
            )
        )

    logger.info(
        "Split cluster (%d employees) into %d sub-clusters (max_capacity=%d)",
        cluster.employee_count,
        len(sub_clusters),
        max_capacity,
    )
    return sub_clusters


# ---------------------------------------------------------------------------
# Cluster merging
# ---------------------------------------------------------------------------


def merge_clusters(
    clusters: list[ClusterResult],
    max_capacity: int,
    max_distance_km: float = 5.0,
) -> list[ClusterResult]:
    """Merge small clusters that are geographically close.

    Greedy approach: sort by ascending size, then try to merge the
    smallest cluster with the nearest compatible cluster.

    Two clusters are merged only when:
      - Their combined employee count <= *max_capacity*.
      - The haversine distance between centroids <= *max_distance_km*.

    The merged centroid is the weighted mean of the two centroids.

    Returns:
        A new list of (potentially merged) ClusterResult objects.
    """
    if len(clusters) <= 1:
        return list(clusters)

    # Work on a mutable copy sorted by size (ascending)
    remaining = sorted(clusters, key=lambda c: c.employee_count)
    merged_flags = [False] * len(remaining)
    result: list[ClusterResult] = []

    for i in range(len(remaining)):
        if merged_flags[i]:
            continue

        best_j: int | None = None
        best_dist = float("inf")

        for j in range(i + 1, len(remaining)):
            if merged_flags[j]:
                continue

            combined = remaining[i].employee_count + remaining[j].employee_count
            if combined > max_capacity:
                continue

            dist = _haversine_km(
                remaining[i].centroid_lat,
                remaining[i].centroid_lng,
                remaining[j].centroid_lat,
                remaining[j].centroid_lng,
            )
            if dist <= max_distance_km and dist < best_dist:
                best_dist = dist
                best_j = j

        if best_j is not None:
            ci = remaining[i]
            cj = remaining[best_j]
            total = ci.employee_count + cj.employee_count

            # Weighted centroid
            w_lat = (
                ci.centroid_lat * ci.employee_count
                + cj.centroid_lat * cj.employee_count
            ) / total
            w_lng = (
                ci.centroid_lng * ci.employee_count
                + cj.centroid_lng * cj.employee_count
            ) / total

            merged = ClusterResult(
                centroid_lat=round(w_lat, 8),
                centroid_lng=round(w_lng, 8),
                employee_ids=ci.employee_ids + cj.employee_ids,
                pmr_count=ci.pmr_count + cj.pmr_count,
                employee_count=total,
            )
            result.append(merged)
            merged_flags[best_j] = True

            logger.debug(
                "Merged clusters (%d + %d employees, dist=%.2f km)",
                ci.employee_count,
                cj.employee_count,
                best_dist,
            )
        else:
            result.append(remaining[i])

    logger.info(
        "Merge pass: %d clusters -> %d clusters (max_capacity=%d, max_dist=%.1f km)",
        len(clusters),
        len(result),
        max_capacity,
        max_distance_km,
    )
    return result


# ---------------------------------------------------------------------------
# Main assignment engine
# ---------------------------------------------------------------------------


def assign_vehicles_to_clusters(
    clusters: list[ClusterResult],
    vehicles: list[VehicleCandidate],
    site_zfe: bool,
    volunteer_drivers: list[VehicleCandidate] | None = None,
    employee_locations: dict[uuid.UUID, tuple[float, float]] | None = None,
    employee_pmr: dict[uuid.UUID, bool] | None = None,
) -> AssignmentSummary:
    """Assign vehicles to clusters using best-fit decreasing bin-packing.

    Algorithm:
      1. Sort vehicles by capacity descending (best-fit decreasing).
      2. For each cluster, find the smallest vehicle that fits.
      3. If no single vehicle fits, split the cluster and retry.
      4. After fleet vehicles are exhausted, use volunteer drivers.
      5. Clusters that still have no vehicle get recommendations.

    Args:
        clusters: Output from the clustering engine.
        vehicles: Fleet vehicles available for assignment.
        site_zfe: Whether the site is in a ZFE (low-emission) zone.
        volunteer_drivers: Optional supplemental volunteer driver vehicles.
        employee_locations: Optional mapping for accurate cluster splitting.
        employee_pmr: Optional mapping for accurate PMR counting in splits.

    Returns:
        An AssignmentSummary with all assignments and diagnostics.
    """
    if not clusters:
        return AssignmentSummary()

    # Sort fleet by capacity descending for best-fit decreasing
    available_fleet: list[VehicleCandidate] = sorted(
        vehicles, key=lambda v: v.capacity, reverse=True
    )
    available_volunteers: list[VehicleCandidate] = sorted(
        volunteer_drivers or [], key=lambda v: v.capacity, reverse=True
    )

    # Track which vehicles have been consumed
    used_fleet_ids: set[uuid.UUID] = set()
    used_volunteer_ids: set[uuid.UUID] = set()

    assignments: list[AssignmentResult] = []
    unassigned_indices: list[int] = []
    recommendations: list[dict] = []

    # Determine max fleet capacity for splitting decisions
    max_fleet_capacity = max((v.capacity for v in available_fleet), default=0)
    max_any_capacity = max(
        max_fleet_capacity,
        max((v.capacity for v in available_volunteers), default=0),
    )

    for idx, cluster in enumerate(clusters):
        # Filter to vehicles not yet used
        remaining_fleet = [
            v for v in available_fleet if v.vehicle_id not in used_fleet_ids
        ]

        vehicle = _find_best_vehicle(cluster, remaining_fleet, site_zfe)

        if vehicle is not None:
            used_fleet_ids.add(vehicle.vehicle_id)
            assignments.append(
                AssignmentResult(
                    cluster_index=idx,
                    vehicle_id=vehicle.vehicle_id,
                    employee_ids=list(cluster.employee_ids),
                    employee_count=cluster.employee_count,
                    pmr_count=cluster.pmr_count,
                    occupancy_rate=round(
                        cluster.employee_count / vehicle.capacity, 4
                    ),
                )
            )
            continue

        # No single vehicle fits -- try splitting the cluster
        if max_any_capacity > 0 and cluster.employee_count > max_any_capacity:
            sub_clusters = split_cluster(
                cluster, max_any_capacity, employee_locations, employee_pmr
            )
        elif max_fleet_capacity > 0 and cluster.employee_count > max_fleet_capacity:
            sub_clusters = split_cluster(
                cluster, max_fleet_capacity, employee_locations, employee_pmr
            )
        else:
            # Cluster fits in theory but all suitable vehicles are taken
            sub_clusters = [cluster]

        split_happened = len(sub_clusters) > 1

        all_sub_assigned = True
        for sub in sub_clusters:
            remaining_fleet = [
                v for v in available_fleet if v.vehicle_id not in used_fleet_ids
            ]
            sv = _find_best_vehicle(sub, remaining_fleet, site_zfe)

            if sv is not None:
                used_fleet_ids.add(sv.vehicle_id)
                assignments.append(
                    AssignmentResult(
                        cluster_index=idx,
                        vehicle_id=sv.vehicle_id,
                        employee_ids=list(sub.employee_ids),
                        employee_count=sub.employee_count,
                        pmr_count=sub.pmr_count,
                        occupancy_rate=round(
                            sub.employee_count / sv.capacity, 4
                        ),
                        was_split=split_happened,
                    )
                )
                continue

            # Try volunteer drivers
            remaining_vol = [
                v
                for v in available_volunteers
                if v.vehicle_id not in used_volunteer_ids
            ]
            vv = _find_best_vehicle(sub, remaining_vol, site_zfe)

            if vv is not None:
                used_volunteer_ids.add(vv.vehicle_id)
                assignments.append(
                    AssignmentResult(
                        cluster_index=idx,
                        vehicle_id=vv.vehicle_id,
                        employee_ids=list(sub.employee_ids),
                        employee_count=sub.employee_count,
                        pmr_count=sub.pmr_count,
                        occupancy_rate=round(
                            sub.employee_count / vv.capacity, 4
                        ),
                        was_split=split_happened,
                    )
                )
                continue

            # Truly unassigned sub-cluster
            all_sub_assigned = False
            assignments.append(
                AssignmentResult(
                    cluster_index=idx,
                    vehicle_id=None,
                    employee_ids=list(sub.employee_ids),
                    employee_count=sub.employee_count,
                    pmr_count=sub.pmr_count,
                    occupancy_rate=0.0,
                    was_split=split_happened,
                )
            )

        if not all_sub_assigned and idx not in unassigned_indices:
            unassigned_indices.append(idx)
            recommendations.append(
                _recommend_vehicle(cluster, site_zfe)
            )

    # Build summary
    assigned_with_vehicle = [a for a in assignments if a.vehicle_id is not None]
    total_used = len({a.vehicle_id for a in assigned_with_vehicle})
    total_assigned = sum(a.employee_count for a in assigned_with_vehicle)
    avg_occ = (
        sum(a.occupancy_rate for a in assigned_with_vehicle) / len(assigned_with_vehicle)
        if assigned_with_vehicle
        else 0.0
    )

    summary = AssignmentSummary(
        assignments=assignments,
        total_vehicles_used=total_used,
        total_employees_assigned=total_assigned,
        avg_occupancy_rate=round(avg_occ, 4),
        unassigned_clusters=unassigned_indices,
        recommended_vehicles=recommendations,
    )

    logger.info(
        "Assignment complete: %d vehicles used, %d employees assigned, "
        "%.1f%% avg occupancy, %d unassigned clusters",
        summary.total_vehicles_used,
        summary.total_employees_assigned,
        summary.avg_occupancy_rate * 100,
        len(summary.unassigned_clusters),
    )

    return summary


# ---------------------------------------------------------------------------
# Recommendation helper
# ---------------------------------------------------------------------------


def _recommend_vehicle(cluster: ClusterResult, site_zfe: bool) -> dict:
    """Generate a vehicle recommendation for an unassigned cluster."""
    # Suggest a vehicle type based on cluster size
    if cluster.employee_count <= 4:
        suggested_type = "Voiture"
    elif cluster.employee_count <= 9:
        suggested_type = "Minivan"
    elif cluster.employee_count <= 20:
        suggested_type = "Minibus"
    else:
        suggested_type = "Bus"

    return {
        "cluster_employee_count": cluster.employee_count,
        "pmr_required": cluster.pmr_count > 0,
        "zfe_required": site_zfe,
        "suggested_type": suggested_type,
        "suggested_min_capacity": cluster.employee_count,
    }
