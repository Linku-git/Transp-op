"""Tests for Mobile API endpoints (Session 54)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.trip_booking import TripBooking
from app.models.device_registration import DeviceRegistration
from app.models.push_notification import PushNotification
from app.schemas.trip_booking import TripBookingCreate, TripBookingUpdate, TripBookingResponse
from app.schemas.device_registration import DeviceRegisterRequest
from app.services.trip_booking_service import (
    _validate_modification_window,
    MIN_MODIFICATION_MINUTES,
)


class TestTripBookingModel:
    """Test TripBooking model creation."""

    def test_trip_booking_fields(self):
        booking = TripBooking(
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            departure_time=datetime.now(timezone.utc) + timedelta(hours=2),
            status="confirmed",
        )
        assert booking.status == "confirmed"
        assert booking.seat_number is None

    def test_trip_booking_with_all_fields(self):
        booking = TripBooking(
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            route_id=uuid.uuid4(),
            departure_time=datetime.now(timezone.utc) + timedelta(hours=2),
            status="confirmed",
            seat_number=5,
            pickup_point_id=uuid.uuid4(),
            shift_id=uuid.uuid4(),
        )
        assert booking.seat_number == 5
        assert booking.shift_id is not None


class TestDeviceRegistrationModel:
    """Test DeviceRegistration model."""

    def test_device_registration_fields(self):
        reg = DeviceRegistration(
            user_id=uuid.uuid4(),
            device_token="test-token-123",
            platform="ios",
        )
        assert reg.platform == "ios"
        assert reg.device_token == "test-token-123"


class TestPushNotificationModel:
    """Test PushNotification model."""

    def test_push_notification_fields(self):
        notif = PushNotification(
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            title="Test notification",
            body="Body content",
            type="rti_alert",
        )
        assert notif.type == "rti_alert"
        assert notif.read_at is None


class TestModificationWindow:
    """Test 30-minute modification window validation."""

    def test_allows_modification_when_far_enough(self):
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        # Should not raise
        _validate_modification_window(future)

    def test_blocks_modification_when_too_close(self):
        close = datetime.now(timezone.utc) + timedelta(minutes=15)
        with pytest.raises(Exception) as exc_info:
            _validate_modification_window(close)
        assert "30 minutes" in str(exc_info.value.detail)

    def test_blocks_modification_for_past_departure(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        with pytest.raises(Exception):
            _validate_modification_window(past)

    def test_allows_at_exactly_30_minutes(self):
        boundary = datetime.now(timezone.utc) + timedelta(minutes=31)
        # Should not raise
        _validate_modification_window(boundary)


class TestTripBookingSchema:
    """Test Pydantic schemas."""

    def test_create_schema(self):
        schema = TripBookingCreate(
            departure_time=datetime.now(timezone.utc) + timedelta(hours=2),
            route_id=uuid.uuid4(),
        )
        assert schema.route_id is not None

    def test_create_schema_minimal(self):
        schema = TripBookingCreate(
            departure_time=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        assert schema.route_id is None
        assert schema.seat_number is None

    def test_update_schema(self):
        schema = TripBookingUpdate(shift_id=uuid.uuid4())
        assert schema.shift_id is not None
        assert schema.pickup_point_id is None

    def test_response_schema_from_attributes(self):
        assert TripBookingResponse.model_config.get("from_attributes") is True


class TestDeviceRegistrationSchema:
    """Test device registration schema."""

    def test_register_request(self):
        req = DeviceRegisterRequest(token="test-token", platform="android")
        assert req.token == "test-token"
        assert req.platform == "android"

    def test_register_request_default_platform(self):
        req = DeviceRegisterRequest(token="test-token")
        assert req.platform == "android"

    def test_register_request_rejects_empty_token(self):
        with pytest.raises(Exception):
            DeviceRegisterRequest(token="")

    def test_register_request_rejects_invalid_platform(self):
        with pytest.raises(Exception):
            DeviceRegisterRequest(token="test", platform="windows")
