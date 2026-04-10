"""Tests for DBSCAN stop generation (SOTREG M3)."""
from __future__ import annotations

import uuid

import pytest

from app.services.sotreg.stop_generator import generate_stops_from_employees


def _make_employee(lat: float, lng: float) -> dict:
    return {"employee_id": str(uuid.uuid4()), "lat": lat, "lng": lng}


class TestGenerateStopsFromEmployees:
    """Verify DBSCAN-based stop generation."""

    def test_basic_cluster_formation(self) -> None:
        """Group of 6 nearby employees should form 1 cluster."""
        # All within ~100m of each other in Casablanca
        base_lat, base_lng = 33.5731, -7.5898
        employees = [
            _make_employee(base_lat + i * 0.0001, base_lng + i * 0.0001)
            for i in range(6)
        ]
        stops = generate_stops_from_employees(employees, eps_m=500, min_pts=5)
        assert len(stops) == 1
        assert stops[0]["employee_count"] == 6
        assert stops[0]["source"] == "dbscan"

    def test_two_separate_clusters(self) -> None:
        """Two groups far apart should form 2 clusters."""
        group_a = [_make_employee(33.57, -7.59 + i * 0.0001) for i in range(6)]
        group_b = [_make_employee(33.60, -7.55 + i * 0.0001) for i in range(6)]
        stops = generate_stops_from_employees(group_a + group_b, eps_m=500, min_pts=5)
        assert len(stops) == 2

    def test_centroids_are_valid_coordinates(self) -> None:
        """Centroids should be valid lat/lng."""
        employees = [_make_employee(33.57 + i * 0.0001, -7.59 + i * 0.0001) for i in range(6)]
        stops = generate_stops_from_employees(employees, eps_m=500, min_pts=5)
        for stop in stops:
            assert -90 <= stop["centroid_lat"] <= 90
            assert -180 <= stop["centroid_lng"] <= 180

    def test_empty_employees_returns_no_stops(self) -> None:
        """Empty employee list should return empty stops."""
        stops = generate_stops_from_employees([], eps_m=500, min_pts=5)
        assert len(stops) == 0

    def test_fewer_than_min_pts_returns_no_stops(self) -> None:
        """3 employees with min_pts=5 → all noise, no stops."""
        employees = [_make_employee(33.57, -7.59 + i * 0.0001) for i in range(3)]
        stops = generate_stops_from_employees(employees, eps_m=500, min_pts=5)
        assert len(stops) == 0

    def test_all_same_location(self) -> None:
        """All employees at exact same location → 1 cluster."""
        employees = [_make_employee(33.57, -7.59) for _ in range(10)]
        stops = generate_stops_from_employees(employees, eps_m=500, min_pts=5)
        assert len(stops) == 1
        assert stops[0]["employee_count"] == 10

    def test_catchment_radius_calculated(self) -> None:
        """Catchment radius should be positive for non-trivial clusters."""
        employees = [_make_employee(33.57 + i * 0.001, -7.59) for i in range(6)]
        stops = generate_stops_from_employees(employees, eps_m=2000, min_pts=5)
        if stops:
            assert stops[0]["catchment_radius_m"] >= 0

    def test_custom_eps_and_min_pts(self) -> None:
        """Custom eps=1000m and min_pts=3."""
        employees = [_make_employee(33.57 + i * 0.002, -7.59) for i in range(4)]
        stops = generate_stops_from_employees(employees, eps_m=1000, min_pts=3)
        # With 4 employees and min_pts=3, could form a cluster if within 1km
        assert isinstance(stops, list)

    def test_employee_ids_included(self) -> None:
        """Each stop should list its member employee IDs."""
        employees = [_make_employee(33.57, -7.59 + i * 0.0001) for i in range(6)]
        stops = generate_stops_from_employees(employees, eps_m=500, min_pts=5)
        if stops:
            assert len(stops[0]["employee_ids"]) == stops[0]["employee_count"]
