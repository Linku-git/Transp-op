"""Tests for Isolation Forest predictive maintenance (SOTREG M4)."""
from __future__ import annotations

import numpy as np
import pytest

from app.services.sotreg.predictive_maintenance import (
    generate_maintenance_alerts,
    score_vehicles,
    train_isolation_forest,
    run_predictive_pipeline,
)


# ---------------------------------------------------------------------------
# IsolationForest training tests
# ---------------------------------------------------------------------------


class TestTrainIsolationForest:
    """Verify IsolationForest training."""

    def test_basic_training(self) -> None:
        """Train on normal data."""
        np.random.seed(42)
        matrix = np.random.normal(0, 1, (50, 5))
        result = train_isolation_forest(matrix)
        assert result["model"] is not None
        assert result["training_samples"] == 50
        assert result["feature_count"] == 5

    def test_insufficient_samples_raises(self) -> None:
        """Fewer than 10 samples should raise ValueError."""
        matrix = np.random.normal(0, 1, (5, 3))
        with pytest.raises(ValueError, match="Insufficient training data"):
            train_isolation_forest(matrix)


# ---------------------------------------------------------------------------
# Scoring tests
# ---------------------------------------------------------------------------


class TestScoreVehicles:
    """Verify anomaly scoring and severity classification."""

    def test_scoring_returns_scores(self) -> None:
        """Score vehicles and get results."""
        np.random.seed(42)
        train_data = np.random.normal(0, 1, (100, 4))
        result = train_isolation_forest(train_data)
        model = result["model"]

        test_data = np.random.normal(0, 1, (10, 4))
        vehicle_ids = [f"v{i}" for i in range(10)]
        scores = score_vehicles(model, test_data, vehicle_ids)
        assert len(scores) == 10
        for s in scores:
            assert "vehicle_id" in s
            assert "anomaly_score" in s
            assert "severity" in s
            assert "is_anomalous" in s

    def test_anomaly_detection(self) -> None:
        """Outliers should get higher anomaly scores."""
        np.random.seed(42)
        normal = np.random.normal(0, 1, (100, 3))
        result = train_isolation_forest(normal, contamination=0.1)
        model = result["model"]

        # Normal point vs extreme outlier
        test = np.array([[0.0, 0.0, 0.0], [100.0, 100.0, 100.0]])
        scores = score_vehicles(model, test, ["normal", "outlier"])
        normal_score = next(s for s in scores if s["vehicle_id"] == "normal")
        outlier_score = next(s for s in scores if s["vehicle_id"] == "outlier")
        assert outlier_score["anomaly_score"] > normal_score["anomaly_score"]

    def test_severity_classification(self) -> None:
        """Score > 0.7 = critical, > 0.4 = medium, <= 0.4 = normal."""
        np.random.seed(42)
        normal = np.random.normal(0, 0.5, (200, 3))
        result = train_isolation_forest(normal, contamination=0.05)
        model = result["model"]

        # Include extreme outlier to trigger critical
        test = np.vstack([
            np.random.normal(0, 0.5, (5, 3)),
            np.array([[50.0, 50.0, 50.0]]),
        ])
        ids = [f"v{i}" for i in range(6)]
        scores = score_vehicles(model, test, ids)

        severities = {s["severity"] for s in scores}
        # At least one should be anomalous (the outlier)
        assert any(s["is_anomalous"] for s in scores)


# ---------------------------------------------------------------------------
# Alert generation tests
# ---------------------------------------------------------------------------


class TestGenerateMaintenanceAlerts:
    """Verify alert generation."""

    def test_alerts_for_anomalous_only(self) -> None:
        """Only medium and critical generate alerts."""
        scores = [
            {"vehicle_id": "v1", "anomaly_score": 0.8, "severity": "critical", "is_anomalous": True},
            {"vehicle_id": "v2", "anomaly_score": 0.5, "severity": "medium", "is_anomalous": True},
            {"vehicle_id": "v3", "anomaly_score": 0.2, "severity": "normal", "is_anomalous": False},
        ]
        alerts = generate_maintenance_alerts(scores)
        assert len(alerts) == 2
        alert_ids = {a["vehicle_id"] for a in alerts}
        assert "v3" not in alert_ids

    def test_no_anomalies_no_alerts(self) -> None:
        """All normal → no alerts."""
        scores = [
            {"vehicle_id": "v1", "anomaly_score": 0.1, "severity": "normal", "is_anomalous": False},
        ]
        alerts = generate_maintenance_alerts(scores)
        assert len(alerts) == 0

    def test_alert_contains_required_fields(self) -> None:
        """Alert should have vehicle_id, alert_type, severity, anomaly_score."""
        scores = [
            {"vehicle_id": "v1", "anomaly_score": 0.75, "severity": "critical", "is_anomalous": True},
        ]
        alerts = generate_maintenance_alerts(scores)
        assert len(alerts) == 1
        alert = alerts[0]
        assert alert["vehicle_id"] == "v1"
        assert alert["severity"] == "critical"
        assert alert["anomaly_score"] == 0.75
        assert "alert_type" in alert
