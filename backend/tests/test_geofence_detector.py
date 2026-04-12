"""Tests for Geofence Detection service (Session 121)."""
from __future__ import annotations

import pytest

from app.services.sotreg.geofence_detector import (
    AlertType,
    Geofence,
    GeofenceDetector,
    GeofenceType,
)


@pytest.fixture
def detector() -> GeofenceDetector:
    """Create a GeofenceDetector with test geofences."""
    casablanca_zone = Geofence(
        id="gf-casa", name="Casablanca Depot",
        fence_type=GeofenceType.CIRCLE,
        center_lat=33.5731, center_lng=-7.5898,
        radius_m=500,
    )
    industrial_zone = Geofence(
        id="gf-indus", name="Industrial Zone",
        fence_type=GeofenceType.POLYGON,
        polygon=[
            (33.58, -7.60), (33.58, -7.58),
            (33.56, -7.58), (33.56, -7.60),
        ],
    )
    return GeofenceDetector(geofences=[casablanca_zone, industrial_zone])


class TestGeofenceEnter:
    def test_enter_circle(self, detector: GeofenceDetector) -> None:
        # First position: outside
        alerts = detector.check_position("v1", 33.60, -7.60, 100)
        assert len(alerts) == 0

        # Move inside circle (within 500m of 33.5731, -7.5898)
        alerts = detector.check_position("v1", 33.5731, -7.5898, 200)
        enter_alerts = [a for a in alerts if a.alert_type == AlertType.ENTER]
        assert len(enter_alerts) >= 1
        assert any(a.geofence_id == "gf-casa" for a in enter_alerts)

    def test_enter_polygon(self, detector: GeofenceDetector) -> None:
        # Outside polygon
        alerts = detector.check_position("v2", 33.55, -7.65, 100)
        assert len(alerts) == 0

        # Inside polygon (33.57, -7.59 is within the rectangle)
        alerts = detector.check_position("v2", 33.57, -7.59, 200)
        enter_alerts = [a for a in alerts if a.alert_type == AlertType.ENTER]
        assert len(enter_alerts) >= 1


class TestGeofenceExit:
    def test_exit_circle(self, detector: GeofenceDetector) -> None:
        # Start inside
        detector.check_position("v3", 33.5731, -7.5898, 100)

        # Move outside
        alerts = detector.check_position("v3", 33.60, -7.60, 200)
        exit_alerts = [a for a in alerts if a.alert_type == AlertType.EXIT]
        assert len(exit_alerts) >= 1
        assert any(a.geofence_id == "gf-casa" for a in exit_alerts)


class TestCircleGeofence:
    def test_point_at_center(self, detector: GeofenceDetector) -> None:
        alerts = detector.check_position("v4", 33.5731, -7.5898, 100)
        state = detector.get_vehicle_state("v4")
        assert "gf-casa" in state

    def test_point_outside_radius(self, detector: GeofenceDetector) -> None:
        # ~5 km away
        alerts = detector.check_position("v5", 33.62, -7.55, 100)
        state = detector.get_vehicle_state("v5")
        assert "gf-casa" not in state


class TestConnectionState:
    def test_no_transition_when_staying_inside(self, detector: GeofenceDetector) -> None:
        # Enter
        detector.check_position("v6", 33.5731, -7.5898, 100)
        # Stay inside — no new alert
        alerts = detector.check_position("v6", 33.5735, -7.5895, 200)
        assert len([a for a in alerts if a.geofence_id == "gf-casa"]) == 0

    def test_geofence_count(self, detector: GeofenceDetector) -> None:
        assert detector.geofence_count == 2

    def test_add_remove_geofence(self) -> None:
        d = GeofenceDetector()
        gf = Geofence(id="test", name="Test", fence_type=GeofenceType.CIRCLE,
                       center_lat=33.0, center_lng=-7.0, radius_m=100)
        d.add_geofence(gf)
        assert d.geofence_count == 1
        d.remove_geofence("test")
        assert d.geofence_count == 0
