"""Tests for SocketIO GPS Streaming service (Session 121)."""
from __future__ import annotations

import time

import pytest

from app.services.sotreg.socketio_gps import (
    ConnectionManager,
    VehiclePositionEvent,
    VehicleStatusEvent,
    create_socketio_server,
    HEARTBEAT_INTERVAL,
    STALE_TIMEOUT,
)


class TestConnectionManager:
    def test_connect_increments_count(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1", "user1")
        assert cm.connection_count == 1
        cm.connect("sid2", "user2")
        assert cm.connection_count == 2

    def test_disconnect_decrements_count(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        cm.disconnect("sid1")
        assert cm.connection_count == 0

    def test_join_room(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        cm.join_room("sid1", "vehicle:v1", "vehicle")
        assert "sid1" in cm.get_room_members("vehicle:v1")
        assert cm.get_room_count("vehicle:v1") == 1

    def test_leave_room(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        cm.join_room("sid1", "vehicle:v1")
        cm.leave_room("sid1", "vehicle:v1")
        assert cm.get_room_count("vehicle:v1") == 0

    def test_disconnect_removes_from_rooms(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        cm.join_room("sid1", "vehicle:v1")
        cm.join_room("sid1", "ligne:l1", "ligne")
        cm.disconnect("sid1")
        assert cm.get_room_count("vehicle:v1") == 0
        assert cm.get_room_count("ligne:l1") == 0

    def test_multiple_connections_same_room(self) -> None:
        cm = ConnectionManager()
        for i in range(100):
            cm.connect(f"sid{i}")
            cm.join_room(f"sid{i}", "vehicle:v1")
        assert cm.get_room_count("vehicle:v1") == 100
        assert cm.connection_count == 100

    def test_heartbeat_updates_timestamp(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        time.sleep(0.01)
        cm.heartbeat("sid1")
        info = cm._connections["sid1"]
        assert info.last_heartbeat > info.connected_at

    def test_stale_detection(self) -> None:
        cm = ConnectionManager()
        info = cm.connect("sid1")
        # Manually set old heartbeat
        info.last_heartbeat = time.time() - STALE_TIMEOUT - 10
        stale = cm.get_stale_connections()
        assert "sid1" in stale

    def test_cleanup_stale(self) -> None:
        cm = ConnectionManager()
        info = cm.connect("sid1")
        info.last_heartbeat = time.time() - STALE_TIMEOUT - 10
        cleaned = cm.cleanup_stale()
        assert "sid1" in cleaned
        assert cm.connection_count == 0

    def test_metrics(self) -> None:
        cm = ConnectionManager()
        cm.connect("sid1")
        cm.join_room("sid1", "vehicle:v1")
        cm.join_room("sid1", "ligne:l1", "ligne")
        metrics = cm.get_metrics()
        assert metrics["total_connections"] == 1
        assert metrics["total_rooms"] == 2
        assert metrics["vehicle_rooms"] == 1
        assert metrics["ligne_rooms"] == 1


class TestSocketIOServer:
    def test_create_server_mock(self) -> None:
        """Server creation works even without python-socketio."""
        config = create_socketio_server()
        assert config["namespace"] == "/gps"
        assert config["type"] in ("socketio", "mock")

    def test_server_config_constants(self) -> None:
        assert HEARTBEAT_INTERVAL == 25
        assert STALE_TIMEOUT == 60


class TestEventDataclasses:
    def test_vehicle_position_event(self) -> None:
        event = VehiclePositionEvent(
            vehicle_id="v1", lat=33.57, lng=-7.59,
            speed_kmh=45.0, heading=90.0, timestamp=1000.0,
        )
        assert event.vehicle_id == "v1"
        assert event.speed_kmh == 45.0

    def test_vehicle_status_event(self) -> None:
        event = VehicleStatusEvent(
            vehicle_id="v1", engine_on=True, doors_open=False,
            passenger_count=12, timestamp=1000.0,
        )
        assert event.passenger_count == 12
