"""Tests for RTI Backend System (Session 58)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.vehicle_position import VehiclePosition
from app.models.rti_event import RTIEvent
from app.schemas.vehicle_position import VehiclePositionCreate, VehiclePositionCurrent
from app.schemas.rti_event import RTIEventCreate, RTIComplianceResponse
from app.services.eta_calculator import haversine_distance_km, calculate_eta_seconds
from app.services.rti_service import position_to_redis_dict, COMPLIANCE_THRESHOLD_SECONDS


class TestVehiclePositionModel:
    def test_create(self):
        pos = VehiclePosition(
            tenant_id=uuid.uuid4(),
            vehicle_id=uuid.uuid4(),
            lat=33.58,
            lng=-7.63,
            heading=90.0,
            speed=25.0,
            recorded_at=datetime.now(timezone.utc),
        )
        assert pos.lat == 33.58
        assert pos.heading == 90.0


class TestRTIEventModel:
    def test_create(self):
        event = RTIEvent(
            tenant_id=uuid.uuid4(),
            vehicle_id=uuid.uuid4(),
            event_type="arrival",
            scheduled_at=datetime.now(timezone.utc),
            actual_at=datetime.now(timezone.utc) + timedelta(seconds=60),
            wait_duration_seconds=60,
        )
        assert event.event_type == "arrival"
        assert event.wait_duration_seconds == 60


class TestEtaCalculator:
    def test_haversine_distance_zero(self):
        d = haversine_distance_km(33.58, -7.63, 33.58, -7.63)
        assert d == pytest.approx(0.0, abs=0.001)

    def test_haversine_distance_known(self):
        # Casablanca to Rabat ~86 km
        d = haversine_distance_km(33.57, -7.59, 34.02, -6.83)
        assert 75 < d < 100

    def test_calculate_eta_default_speed(self):
        # 25 km at 25 km/h = 1 hour = 3600s
        eta = calculate_eta_seconds(
            vehicle_lat=33.58, vehicle_lng=-7.63,
            stop_lat=33.58, stop_lng=-7.63,
        )
        assert eta == 0  # Same point

    def test_calculate_eta_with_speed(self):
        # ~10 km distance at 60 km/h = 10 min = 600s
        eta = calculate_eta_seconds(
            vehicle_lat=33.58, vehicle_lng=-7.63,
            stop_lat=33.67, stop_lng=-7.63,
            vehicle_speed_kmh=60.0,
        )
        assert 400 < eta < 800  # Roughly 10 min

    def test_calculate_eta_zero_speed_uses_default(self):
        eta = calculate_eta_seconds(
            vehicle_lat=33.58, vehicle_lng=-7.63,
            stop_lat=33.60, stop_lng=-7.63,
            vehicle_speed_kmh=0,
        )
        assert eta > 0


class TestRTIService:
    def test_position_to_redis_dict(self):
        vid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        result = position_to_redis_dict(
            vehicle_id=vid,
            lat=33.58, lng=-7.63,
            heading=90.0, speed=25.0,
            recorded_at=now,
            eta_seconds=120,
        )
        assert result["vehicle_id"] == str(vid)
        assert result["lat"] == 33.58
        assert result["eta_seconds"] == 120

    def test_compliance_threshold(self):
        assert COMPLIANCE_THRESHOLD_SECONDS == 90


class TestSchemas:
    def test_position_create(self):
        schema = VehiclePositionCreate(
            vehicle_id=uuid.uuid4(),
            lat=33.58, lng=-7.63,
            heading=45.0, speed=30.0,
            recorded_at=datetime.now(timezone.utc),
        )
        assert schema.lat == 33.58

    def test_position_create_rejects_invalid_lat(self):
        with pytest.raises(Exception):
            VehiclePositionCreate(
                vehicle_id=uuid.uuid4(),
                lat=100, lng=-7.63,
                recorded_at=datetime.now(timezone.utc),
            )

    def test_position_current(self):
        current = VehiclePositionCurrent(
            vehicle_id="v-1", lat=33.58, lng=-7.63,
            recorded_at="2026-04-08T08:30:00", eta_seconds=120,
        )
        assert current.eta_seconds == 120

    def test_event_create(self):
        schema = RTIEventCreate(
            vehicle_id=uuid.uuid4(),
            event_type="delay",
        )
        assert schema.event_type == "delay"

    def test_compliance_response(self):
        resp = RTIComplianceResponse(
            total_events=100,
            compliant_events=85,
            compliance_percentage=85.0,
        )
        assert resp.compliance_percentage == 85.0
        assert resp.threshold_seconds == 90
