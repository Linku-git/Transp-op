from __future__ import annotations

import uuid

import pytest

from app.services.vehicle_assignment import (
    AssignmentResult,
    AssignmentSummary,
    VehicleCandidate,
    _find_best_vehicle,
    _haversine_km,
    assign_vehicles_to_clusters,
    merge_clusters,
    split_cluster,
)
from app.services.clustering import ClusterResult


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_cluster(
    employee_count: int,
    pmr_count: int = 0,
    lat: float = 33.5,
    lng: float = -7.6,
) -> ClusterResult:
    return ClusterResult(
        centroid_lat=lat,
        centroid_lng=lng,
        employee_ids=[uuid.uuid4() for _ in range(employee_count)],
        pmr_count=pmr_count,
        employee_count=employee_count,
    )


def _make_vehicle(
    capacity: int,
    pmr: bool = False,
    zfe: bool = False,
    type: str = "Minibus",
    is_volunteer: bool = False,
) -> VehicleCandidate:
    return VehicleCandidate(
        vehicle_id=uuid.uuid4(),
        capacity=capacity,
        is_pmr_accessible=pmr,
        zfe_compliant=zfe,
        type=type,
        is_volunteer=is_volunteer,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_basic_assignment():
    """Three clusters each get a vehicle when fleet has enough capacity."""
    clusters = [
        _make_cluster(5),
        _make_cluster(8),
        _make_cluster(3),
    ]
    vehicles = [
        _make_vehicle(10),
        _make_vehicle(8),
        _make_vehicle(5),
    ]

    summary = assign_vehicles_to_clusters(
        clusters=clusters,
        vehicles=vehicles,
        site_zfe=False,
    )

    assert summary.total_vehicles_used == 3, (
        f"Expected 3 vehicles used, got {summary.total_vehicles_used}"
    )
    assert len(summary.unassigned_clusters) == 0, (
        "All clusters should be assigned"
    )
    # Every assignment should have a vehicle
    for a in summary.assignments:
        assert a.vehicle_id is not None, (
            f"Cluster index {a.cluster_index} should have a vehicle assigned"
        )


def test_capacity_respected():
    """A vehicle must never be assigned more employees than its capacity."""
    clusters = [_make_cluster(10)]
    vehicles = [_make_vehicle(8)]

    summary = assign_vehicles_to_clusters(
        clusters=clusters,
        vehicles=vehicles,
        site_zfe=False,
    )

    for a in summary.assignments:
        assert a.occupancy_rate <= 1.0, (
            f"Occupancy rate {a.occupancy_rate} exceeds 1.0 for cluster "
            f"index {a.cluster_index}"
        )

    # The cluster of 10 cannot fit in vehicle of 8, so either it was split
    # or left unassigned (partially or fully).
    has_split = any(a.was_split for a in summary.assignments)
    has_unassigned = any(a.vehicle_id is None for a in summary.assignments)
    assert has_split or has_unassigned, (
        "Cluster of 10 employees with max vehicle capacity 8 should result "
        "in a split or at least one unassigned sub-cluster"
    )


def test_cluster_split():
    """split_cluster divides an oversized cluster into valid sub-clusters."""
    cluster = _make_cluster(15)

    sub_clusters = split_cluster(cluster, max_capacity=8)

    assert len(sub_clusters) == 2, (
        f"Expected 2 sub-clusters, got {len(sub_clusters)}"
    )
    total_employees = sum(sc.employee_count for sc in sub_clusters)
    assert total_employees == 15, (
        f"Total employees across sub-clusters should be 15, got {total_employees}"
    )
    for sc in sub_clusters:
        assert sc.employee_count <= 8, (
            f"Sub-cluster has {sc.employee_count} employees, exceeds max_capacity=8"
        )


def test_cluster_merge():
    """merge_clusters combines small nearby clusters when capacity allows."""
    clusters = [
        _make_cluster(2, lat=33.500, lng=-7.600),
        _make_cluster(3, lat=33.501, lng=-7.601),
        _make_cluster(2, lat=33.502, lng=-7.602),
    ]

    merged = merge_clusters(
        clusters=clusters,
        max_capacity=10,
        max_distance_km=5.0,
    )

    assert len(merged) < len(clusters), (
        f"Expected fewer clusters after merge, got {len(merged)} from {len(clusters)}"
    )
    total_original = sum(c.employee_count for c in clusters)
    total_merged = sum(c.employee_count for c in merged)
    assert total_merged == total_original, (
        f"Total employees should be preserved: expected {total_original}, "
        f"got {total_merged}"
    )


def test_pmr_matching():
    """A cluster with PMR employees must be assigned a PMR-accessible vehicle."""
    cluster = _make_cluster(5, pmr_count=2)
    pmr_vehicle = _make_vehicle(10, pmr=True)
    regular_vehicle = _make_vehicle(10, pmr=False)

    summary = assign_vehicles_to_clusters(
        clusters=[cluster],
        vehicles=[pmr_vehicle, regular_vehicle],
        site_zfe=False,
    )

    assigned = [a for a in summary.assignments if a.vehicle_id is not None]
    assert len(assigned) == 1, "Cluster should be assigned exactly one vehicle"
    assert assigned[0].vehicle_id == pmr_vehicle.vehicle_id, (
        "The PMR-accessible vehicle should be selected for a cluster with PMR employees"
    )


def test_zfe_compliance():
    """When site_zfe=True, only ZFE-compliant vehicles should be assigned."""
    cluster = _make_cluster(5)
    zfe_vehicle = _make_vehicle(8, zfe=True)
    non_zfe_vehicle = _make_vehicle(8, zfe=False)

    summary = assign_vehicles_to_clusters(
        clusters=[cluster],
        vehicles=[zfe_vehicle, non_zfe_vehicle],
        site_zfe=True,
    )

    assigned = [a for a in summary.assignments if a.vehicle_id is not None]
    assert len(assigned) == 1, "Cluster should be assigned exactly one vehicle"
    assert assigned[0].vehicle_id == zfe_vehicle.vehicle_id, (
        "The ZFE-compliant vehicle should be selected when site is in a ZFE zone"
    )


def test_minimize_vehicles():
    """The algorithm should pick the smallest sufficient vehicle (best-fit)."""
    cluster = _make_cluster(5)
    small_vehicle = _make_vehicle(5)
    large_vehicle = _make_vehicle(20)

    summary = assign_vehicles_to_clusters(
        clusters=[cluster],
        vehicles=[small_vehicle, large_vehicle],
        site_zfe=False,
    )

    assigned = [a for a in summary.assignments if a.vehicle_id is not None]
    assert len(assigned) == 1, "Cluster should be assigned exactly one vehicle"
    assert assigned[0].vehicle_id == small_vehicle.vehicle_id, (
        "Best-fit should prefer the capacity-5 vehicle over the capacity-20 vehicle "
        "for a cluster of 5 employees"
    )


def test_volunteer_integration():
    """Volunteer drivers are used when no fleet vehicles are available."""
    cluster = _make_cluster(3)
    volunteer = _make_vehicle(4, is_volunteer=True)

    summary = assign_vehicles_to_clusters(
        clusters=[cluster],
        vehicles=[],
        site_zfe=False,
        volunteer_drivers=[volunteer],
    )

    assigned = [a for a in summary.assignments if a.vehicle_id is not None]
    assert len(assigned) == 1, "Cluster should be assigned to the volunteer driver"
    assert assigned[0].vehicle_id == volunteer.vehicle_id, (
        "The volunteer driver vehicle should be used when fleet is empty"
    )


def test_no_vehicles_available():
    """When no vehicles or volunteers exist, clusters are unassigned with recommendations."""
    clusters = [
        _make_cluster(5),
        _make_cluster(8),
    ]

    summary = assign_vehicles_to_clusters(
        clusters=clusters,
        vehicles=[],
        site_zfe=False,
        volunteer_drivers=[],
    )

    assert len(summary.unassigned_clusters) == 2, (
        f"Expected 2 unassigned clusters, got {len(summary.unassigned_clusters)}"
    )
    assert len(summary.recommended_vehicles) == 2, (
        f"Expected 2 recommendations, got {len(summary.recommended_vehicles)}"
    )
    for rec in summary.recommended_vehicles:
        assert "suggested_type" in rec, (
            "Each recommendation must include a suggested_type"
        )
        assert "suggested_min_capacity" in rec, (
            "Each recommendation must include a suggested_min_capacity"
        )
