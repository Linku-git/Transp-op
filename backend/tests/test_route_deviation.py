"""Tests for Route Deviation Detection service (Session 121)."""
from __future__ import annotations

import pytest

from app.services.sotreg.route_deviation import (
    DEFAULT_DEVIATION_THRESHOLD_M,
    DeviationResult,
    check_route_deviation,
    haversine_distance,
    point_to_segment_distance,
)


# Simple route: Casablanca → Rabat (straight line approximation)
ROUTE_POINTS = [
    (33.57, -7.59),   # Casablanca
    (33.70, -7.40),   # Midpoint 1
    (33.85, -7.10),   # Midpoint 2
    (34.02, -6.83),   # Rabat
]


class TestRouteDeviation:
    def test_on_route_zero_deviation(self) -> None:
        """Vehicle on route has near-zero deviation."""
        result = check_route_deviation(
            "v1", 33.70, -7.40, ROUTE_POINTS, "route-1",
        )
        assert result.deviation_m < 50  # within 50m of route point
        assert result.is_deviated is False

    def test_far_from_route_deviated(self) -> None:
        """Vehicle far from route is marked as deviated."""
        # Point 10km away from route
        result = check_route_deviation(
            "v1", 33.70, -7.10, ROUTE_POINTS, "route-1", threshold_m=200,
        )
        assert result.is_deviated is True
        assert result.deviation_m > 200

    def test_default_threshold_200m(self) -> None:
        """Default threshold is 200 meters."""
        assert DEFAULT_DEVIATION_THRESHOLD_M == 200.0

    def test_custom_threshold(self) -> None:
        """Custom threshold is used for deviation check."""
        result = check_route_deviation(
            "v1", 33.70, -7.40, ROUTE_POINTS, "route-1", threshold_m=1,
        )
        # Even a point very near might be slightly off
        assert result.threshold_m == 1

    def test_insufficient_route_points(self) -> None:
        """Less than 2 route points returns no deviation."""
        result = check_route_deviation("v1", 33.7, -7.4, [(33.7, -7.4)], "r1")
        assert result.deviation_m == 0.0
        assert result.is_deviated is False

    def test_nearest_segment_identified(self) -> None:
        """Nearest segment index is correctly identified."""
        result = check_route_deviation("v1", 33.70, -7.40, ROUTE_POINTS, "route-1")
        assert 0 <= result.nearest_segment_index < len(ROUTE_POINTS) - 1


class TestPointToSegment:
    def test_point_on_segment_zero(self) -> None:
        """Point on segment has near-zero distance."""
        dist = point_to_segment_distance(33.70, -7.40, 33.60, -7.50, 33.80, -7.30)
        assert dist < 1000  # close to midpoint of segment

    def test_perpendicular_distance(self) -> None:
        """Perpendicular distance is computed correctly."""
        # Point directly beside a north-south segment
        dist = point_to_segment_distance(33.5, -7.49, 33.0, -7.50, 34.0, -7.50)
        assert dist > 0
        assert dist < 2000  # ~1.1 km at this latitude

    def test_degenerate_segment(self) -> None:
        """Degenerate segment (zero length) returns distance to point."""
        dist = point_to_segment_distance(33.5, -7.5, 33.5, -7.5, 33.5, -7.5)
        assert dist == pytest.approx(0.0, abs=0.1)


class TestDeviationResult:
    def test_dataclass_fields(self) -> None:
        result = DeviationResult(
            vehicle_id="v1", deviation_m=150.5, is_deviated=False,
            threshold_m=200, nearest_segment_index=2, planned_route_id="r1",
        )
        assert result.vehicle_id == "v1"
        assert result.deviation_m == 150.5
        assert result.is_deviated is False
