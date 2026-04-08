"""Tests for RTI Config & Adaptive Sizing (Session 59)."""
from __future__ import annotations

import uuid
from datetime import time

import pytest

from app.models.rti_config import RTIConfig
from app.schemas.rti_config import RTIConfigCreate, RTIConfigUpdate, RTIConfigResponse
from app.services.adaptive_sizing import (
    calculate_buffer_vehicles,
    should_activate_buffer,
    is_degraded_mode,
)
from app.services.pool_recomposition import (
    RecompositionTrigger,
    trigger_recomposition,
)
from app.services.rti_fallback import (
    FallbackType,
    evaluate_fallback,
)


class TestRTIConfigModel:
    def test_create(self):
        config = RTIConfig(
            tenant_id=uuid.uuid4(),
            site_id=uuid.uuid4(),
            max_wait_seconds=90,
            compliance_target_pct=95.0,
            buffer_vehicle_count=3,
        )
        assert config.max_wait_seconds == 90
        assert config.compliance_target_pct == 95.0

    def test_with_night_mode(self):
        config = RTIConfig(
            tenant_id=uuid.uuid4(),
            site_id=uuid.uuid4(),
            night_mode_start=time(20, 0),
            night_mode_end=time(6, 30),
        )
        assert config.night_mode_start == time(20, 0)


class TestRTIConfigSchemas:
    def test_create_schema(self):
        schema = RTIConfigCreate(
            site_id=uuid.uuid4(),
            max_wait_seconds=120,
            compliance_target_pct=90.0,
        )
        assert schema.max_wait_seconds == 120

    def test_create_schema_rejects_low_wait(self):
        with pytest.raises(Exception):
            RTIConfigCreate(site_id=uuid.uuid4(), max_wait_seconds=10)

    def test_update_schema_partial(self):
        schema = RTIConfigUpdate(compliance_target_pct=85.0)
        assert schema.max_wait_seconds is None
        assert schema.compliance_target_pct == 85.0


class TestAdaptiveSizing:
    def test_buffer_for_small_fleet(self):
        buffer = calculate_buffer_vehicles(10)
        assert buffer >= 1

    def test_buffer_for_large_fleet(self):
        buffer = calculate_buffer_vehicles(100)
        assert buffer >= 2

    def test_buffer_scales_with_fleet(self):
        small = calculate_buffer_vehicles(10)
        large = calculate_buffer_vehicles(100)
        assert large > small

    def test_min_buffer_is_one(self):
        buffer = calculate_buffer_vehicles(1)
        assert buffer >= 1

    def test_should_activate_when_compliance_low(self):
        assert should_activate_buffer(85.0, 95.0) is True

    def test_should_not_activate_when_compliance_ok(self):
        assert should_activate_buffer(92.0, 95.0) is False

    def test_degraded_mode_below_target(self):
        assert is_degraded_mode(90.0, 95.0) is True

    def test_not_degraded_at_target(self):
        assert is_degraded_mode(95.0, 95.0) is False


class TestPoolRecomposition:
    def test_trigger_absence(self):
        result = trigger_recomposition(
            trigger=RecompositionTrigger.EMPLOYEE_ABSENCE,
            site_id=uuid.uuid4(),
            affected_employee_ids=[uuid.uuid4() for _ in range(30)],
        )
        assert result.success is True
        assert result.employees_affected == 30
        assert result.vehicles_reassigned == 2

    def test_trigger_shift_change(self):
        result = trigger_recomposition(
            trigger=RecompositionTrigger.SHIFT_CHANGE,
            site_id=uuid.uuid4(),
        )
        assert result.success is True

    def test_result_to_dict(self):
        result = trigger_recomposition(
            trigger=RecompositionTrigger.VEHICLE_BREAKDOWN,
            site_id=uuid.uuid4(),
        )
        d = result.to_dict()
        assert d["trigger"] == "vehicle_breakdown"
        assert "timestamp" in d


class TestFallbackProtocol:
    def test_no_fallback_when_compliant(self):
        action = evaluate_fallback(
            site_id=uuid.uuid4(),
            current_compliance_pct=96.0,
            target_compliance_pct=95.0,
            buffer_vehicles_available=3,
            buffer_vehicles_active=0,
        )
        assert action is None

    def test_buffer_activation_when_degraded(self):
        action = evaluate_fallback(
            site_id=uuid.uuid4(),
            current_compliance_pct=88.0,
            target_compliance_pct=95.0,
            buffer_vehicles_available=3,
            buffer_vehicles_active=0,
        )
        assert action is not None
        assert action.fallback_type == FallbackType.BUFFER_ACTIVATION
        assert action.executed is True

    def test_tad_request_when_buffers_exhausted(self):
        action = evaluate_fallback(
            site_id=uuid.uuid4(),
            current_compliance_pct=80.0,
            target_compliance_pct=95.0,
            buffer_vehicles_available=3,
            buffer_vehicles_active=3,
        )
        assert action is not None
        assert action.fallback_type == FallbackType.TAD_REQUEST
        assert action.executed is True
        assert action.details["tad_vehicles_needed"] >= 1

    def test_fallback_to_dict(self):
        action = evaluate_fallback(
            site_id=uuid.uuid4(),
            current_compliance_pct=80.0,
            target_compliance_pct=95.0,
            buffer_vehicles_available=0,
            buffer_vehicles_active=0,
        )
        assert action is not None
        d = action.to_dict()
        assert d["type"] == "tad_request"
        assert "timestamp" in d
