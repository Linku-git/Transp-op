"""Tests for Emergency Alert System (Session 66)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.emergency_alert import EmergencyAlert
from app.schemas.emergency_alert import (
    EmergencyAlertTrigger,
    EmergencyAlertResolve,
    EmergencyAlertResponse,
    EmergencyAlertListResponse,
)
from app.services.emergency_routing import determine_responders
from app.services.location_sharing import (
    start_location_sharing,
    update_location,
    stop_location_sharing,
    is_sharing_active,
    get_active_sessions,
)


class TestEmergencyAlertModel:
    def test_create(self):
        alert = EmergencyAlert(
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            triggered_at=datetime.now(timezone.utc),
            lat=33.58,
            lng=-7.63,
            alert_type="panic",
            responders_notified=[{"role": "admin"}],
        )
        assert alert.alert_type == "panic"
        assert alert.resolved_at is None

    def test_all_alert_types(self):
        for t in ["panic", "medical", "vehicle_incident", "other"]:
            alert = EmergencyAlert(
                tenant_id=uuid.uuid4(),
                employee_id=uuid.uuid4(),
                triggered_at=datetime.now(timezone.utc),
                alert_type=t,
            )
            assert alert.alert_type == t


class TestEmergencySchemas:
    def test_trigger_schema(self):
        schema = EmergencyAlertTrigger(lat=33.58, lng=-7.63, alert_type="panic")
        assert schema.alert_type == "panic"

    def test_trigger_rejects_invalid_type(self):
        with pytest.raises(Exception):
            EmergencyAlertTrigger(lat=33.58, lng=-7.63, alert_type="invalid")

    def test_trigger_rejects_invalid_lat(self):
        with pytest.raises(Exception):
            EmergencyAlertTrigger(lat=100, lng=-7.63)

    def test_resolve_schema(self):
        schema = EmergencyAlertResolve(resolution_notes="All clear")
        assert schema.resolution_notes == "All clear"

    def test_list_response(self):
        resp = EmergencyAlertListResponse(data=[], total=0, page=1, pages=1)
        assert resp.total == 0


class TestEmergencyRouting:
    def test_panic_notifies_emergency_services(self):
        responders = determine_responders("panic")
        roles = [r["role"] for r in responders]
        assert "site_security" in roles
        assert "admin" in roles
        assert "emergency_services" in roles

    def test_medical_notifies_medical_service(self):
        responders = determine_responders("medical")
        roles = [r["role"] for r in responders]
        assert "medical_service" in roles

    def test_other_notifies_base_responders(self):
        responders = determine_responders("other")
        roles = [r["role"] for r in responders]
        assert "site_security" in roles
        assert "admin" in roles
        assert "emergency_services" not in roles

    def test_responders_have_timestamps(self):
        responders = determine_responders("panic")
        for r in responders:
            assert "notified_at" in r
            assert "channel" in r

    def test_site_id_passed(self):
        site_id = uuid.uuid4()
        responders = determine_responders("panic", site_id=site_id)
        site_resp = [r for r in responders if r["role"] == "site_security"]
        assert site_resp[0]["site_id"] == str(site_id)


class TestLocationSharing:
    def test_start_and_check(self):
        alert_id = uuid.uuid4()
        emp_id = uuid.uuid4()
        result = start_location_sharing(alert_id, emp_id, 33.58, -7.63)
        assert result["is_active"] is True
        assert is_sharing_active(alert_id) is True

    def test_update_location(self):
        alert_id = uuid.uuid4()
        start_location_sharing(alert_id, uuid.uuid4(), 33.58, -7.63)
        assert update_location(alert_id, 33.59, -7.64) is True

    def test_update_nonexistent_fails(self):
        assert update_location(uuid.uuid4(), 33.59, -7.64) is False

    def test_stop_sharing(self):
        alert_id = uuid.uuid4()
        start_location_sharing(alert_id, uuid.uuid4(), 33.58, -7.63)
        assert stop_location_sharing(alert_id) is True
        assert is_sharing_active(alert_id) is False

    def test_stop_nonexistent(self):
        assert stop_location_sharing(uuid.uuid4()) is False

    def test_get_active_sessions(self):
        alert_id = uuid.uuid4()
        start_location_sharing(alert_id, uuid.uuid4(), 33.58, -7.63)
        sessions = get_active_sessions()
        assert any(s["alert_id"] == str(alert_id) for s in sessions)
