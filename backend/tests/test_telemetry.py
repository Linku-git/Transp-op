"""Tests for telemetry ingestion and feature extraction (SOTREG M4)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.services.sotreg.telemetry_ingestion import process_telemetry_batch, validate_reading
from app.services.sotreg.feature_extraction import extract_rolling_features, build_feature_matrix


def _vid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Telemetry ingestion tests
# ---------------------------------------------------------------------------


class TestValidateReading:
    """Verify telemetry reading validation."""

    def test_valid_vibration(self) -> None:
        result = validate_reading("vibration", 5.0)
        assert result["valid"] is True

    def test_invalid_sensor_type(self) -> None:
        result = validate_reading("unknown_sensor", 5.0)
        assert result["valid"] is False

    def test_value_out_of_range(self) -> None:
        result = validate_reading("temperature", 500.0)  # max is 200
        assert result["valid"] is False

    def test_value_at_boundary(self) -> None:
        result = validate_reading("speed", 0.0)
        assert result["valid"] is True


class TestProcessTelemetryBatch:
    """Verify batch telemetry processing."""

    def test_all_valid_readings(self) -> None:
        vid = _vid()
        readings = [
            {"vehicle_id": vid, "timestamp": datetime.utcnow(), "sensor_type": "vibration", "value": 3.5, "unit": "g"},
            {"vehicle_id": vid, "timestamp": datetime.utcnow(), "sensor_type": "temperature", "value": 85.0, "unit": "C"},
        ]
        result = process_telemetry_batch(readings)
        assert result["accepted"] == 2
        assert result["rejected"] == 0

    def test_mixed_valid_invalid(self) -> None:
        vid = _vid()
        readings = [
            {"vehicle_id": vid, "timestamp": datetime.utcnow(), "sensor_type": "vibration", "value": 3.5},
            {"vehicle_id": vid, "timestamp": datetime.utcnow(), "sensor_type": "invalid_type", "value": 1.0},
        ]
        result = process_telemetry_batch(readings)
        assert result["accepted"] == 1
        assert result["rejected"] == 1
        assert len(result["errors"]) == 1

    def test_empty_batch(self) -> None:
        result = process_telemetry_batch([])
        assert result["accepted"] == 0
        assert result["rejected"] == 0

    def test_large_batch(self) -> None:
        vid = _vid()
        readings = [
            {"vehicle_id": vid, "timestamp": datetime.utcnow(), "sensor_type": "speed", "value": float(i % 100)}
            for i in range(100)
        ]
        result = process_telemetry_batch(readings)
        assert result["accepted"] == 100


# ---------------------------------------------------------------------------
# Feature extraction tests
# ---------------------------------------------------------------------------


class TestExtractRollingFeatures:
    """Verify rolling window feature extraction."""

    def test_basic_feature_extraction(self) -> None:
        vid = _vid()
        now = datetime.utcnow()
        readings = [
            {"vehicle_id": vid, "timestamp": now - timedelta(minutes=i), "sensor_type": "vibration", "value": 3.0 + i * 0.1}
            for i in range(30)
        ]
        result = extract_rolling_features(readings, reference_time=now)
        assert "features" in result
        assert len(result["features"]) > 0

    def test_multiple_sensor_types(self) -> None:
        vid = _vid()
        now = datetime.utcnow()
        readings = []
        for sensor in ["vibration", "temperature"]:
            for i in range(10):
                readings.append({
                    "vehicle_id": vid,
                    "timestamp": now - timedelta(minutes=i),
                    "sensor_type": sensor,
                    "value": float(i),
                })
        result = extract_rolling_features(readings, reference_time=now)
        assert "features" in result

    def test_empty_readings(self) -> None:
        result = extract_rolling_features([], reference_time=datetime.utcnow())
        assert result["features"] == {} or len(result.get("features", {})) == 0


class TestBuildFeatureMatrix:
    """Verify feature matrix construction."""

    def test_basic_matrix(self) -> None:
        features = [
            {"vehicle_id": "v1", "features": {"vibration_1h_mean": 3.0, "vibration_1h_std": 0.5}, "feature_names": ["vibration_1h_mean", "vibration_1h_std"]},
            {"vehicle_id": "v2", "features": {"vibration_1h_mean": 4.0, "vibration_1h_std": 0.8}, "feature_names": ["vibration_1h_mean", "vibration_1h_std"]},
        ]
        result = build_feature_matrix(features)
        assert result["matrix"].shape == (2, 2)
        assert len(result["vehicle_ids"]) == 2
        assert len(result["feature_names"]) == 2

    def test_empty_features_raises(self) -> None:
        with pytest.raises(ValueError):
            build_feature_matrix([])
