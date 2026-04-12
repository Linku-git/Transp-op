"""Tests for RandomForest Driver Risk Scoring (Session 120)."""
from __future__ import annotations

import uuid

import numpy as np
import pytest

from app.models.driver_profile import DriverProfile
from app.services.sotreg.driver_risk import (
    CATEGORY_THRESHOLDS,
    FEATURE_NAMES,
    PENALTY_WEIGHTS,
    DriverFeatures,
    RiskResult,
    classify_risk,
    compute_risk_score,
    extract_features_matrix,
    generate_synthetic_training_data,
    score_driver,
    score_drivers_batch,
    train_risk_model,
)


class TestDriverProfileModel:
    """Tests for DriverProfile SQLAlchemy model."""

    def test_has_required_columns(self) -> None:
        """DriverProfile has all required columns."""
        columns = {c.name for c in DriverProfile.__table__.columns}
        required = {
            "id", "tenant_id", "driver_id", "licence_type",
            "experience_years", "total_km_driven", "risk_score",
            "risk_category", "last_scored_at", "created_at", "updated_at",
        }
        assert required.issubset(columns)

    def test_tablename(self) -> None:
        """DriverProfile uses correct table name."""
        assert DriverProfile.__tablename__ == "driver_profile"

    def test_indexes(self) -> None:
        """DriverProfile has composite indexes."""
        index_names = {idx.name for idx in DriverProfile.__table__.indexes}
        assert "ix_driver_profile_tenant" in index_names
        assert "ix_driver_profile_driver" in index_names
        assert "ix_driver_profile_risk" in index_names


class TestScoringFormula:
    """Tests for risk scoring formula."""

    def test_zero_infractions_yields_100(self) -> None:
        """No infractions yields perfect score 100."""
        features = DriverFeatures(driver_id="d1")
        assert compute_risk_score(features) == 100.0

    def test_known_infractions_score(self) -> None:
        """Known infractions produce expected score."""
        # 2 speed (-10) + 1 accel (-3) + 1 geofence (-10) = -23 → 77
        features = DriverFeatures(
            driver_id="d1",
            nb_alertes_vitesse=2,
            nb_alertes_acceleration=1,
            nb_alertes_geofencing=1,
        )
        assert compute_risk_score(features) == pytest.approx(77.0)

    def test_score_clamped_to_zero(self) -> None:
        """Score is clamped to 0 (not negative) for extreme infractions."""
        features = DriverFeatures(
            driver_id="d1",
            nb_alertes_vitesse=50,
            nb_alertes_geofencing=20,
        )
        assert compute_risk_score(features) == 0.0

    def test_score_clamped_to_100(self) -> None:
        """Score never exceeds 100."""
        features = DriverFeatures(driver_id="d1")
        assert compute_risk_score(features) <= 100.0

    def test_penalty_weights_correct(self) -> None:
        """Penalty weights match spec."""
        assert PENALTY_WEIGHTS["nb_alertes_vitesse"] == 5.0
        assert PENALTY_WEIGHTS["nb_alertes_acceleration"] == 3.0
        assert PENALTY_WEIGHTS["nb_alertes_freinage"] == 3.0
        assert PENALTY_WEIGHTS["nb_alertes_geofencing"] == 10.0
        assert PENALTY_WEIGHTS["nb_alertes_temps"] == 8.0


class TestRiskClassification:
    """Tests for risk category classification."""

    def test_category_low(self) -> None:
        """Score >= 75 is 'low' risk."""
        assert classify_risk(75) == "low"
        assert classify_risk(100) == "low"

    def test_category_medium(self) -> None:
        """Score 50-74 is 'medium' risk."""
        assert classify_risk(74) == "medium"
        assert classify_risk(50) == "medium"

    def test_category_high(self) -> None:
        """Score 25-49 is 'high' risk."""
        assert classify_risk(49) == "high"
        assert classify_risk(25) == "high"

    def test_category_critical(self) -> None:
        """Score < 25 is 'critical' risk."""
        assert classify_risk(24) == "critical"
        assert classify_risk(0) == "critical"

    def test_boundaries(self) -> None:
        """Category boundaries are correct."""
        assert classify_risk(75) == "low"
        assert classify_risk(74.9) == "medium"
        assert classify_risk(50) == "medium"
        assert classify_risk(49.9) == "high"
        assert classify_risk(25) == "high"
        assert classify_risk(24.9) == "critical"


class TestFeatureExtraction:
    """Tests for feature extraction."""

    def test_feature_vector_length(self) -> None:
        """Feature vector has 8 elements."""
        features = DriverFeatures(driver_id="d1")
        vec = features.to_vector()
        assert len(vec) == 8

    def test_feature_names_count(self) -> None:
        """8 feature names defined."""
        assert len(FEATURE_NAMES) == 8

    def test_feature_matrix_shape(self) -> None:
        """Feature matrix has correct shape (n, 8)."""
        drivers = [DriverFeatures(driver_id=f"d{i}") for i in range(10)]
        X = extract_features_matrix(drivers)
        assert X.shape == (10, 8)


class TestRandomForestTraining:
    """Tests for RandomForest model training."""

    def test_trains_on_synthetic_data(self) -> None:
        """RandomForest trains on synthetic telematics data."""
        X, y = generate_synthetic_training_data(n_samples=100)
        model, metrics = train_risk_model(X, y, n_estimators=10)
        assert model is not None
        assert "accuracy" in metrics
        assert metrics["accuracy"] > 0.0

    def test_feature_importance_sums_to_one(self) -> None:
        """Feature importances sum to approximately 1.0."""
        X, y = generate_synthetic_training_data(n_samples=200)
        model, metrics = train_risk_model(X, y, n_estimators=20)
        importances = metrics["feature_importance"]
        total = sum(importances.values())
        assert total == pytest.approx(1.0, abs=0.01)

    def test_feature_importance_all_features(self) -> None:
        """All 8 features have importance values."""
        X, y = generate_synthetic_training_data(n_samples=200)
        _, metrics = train_risk_model(X, y, n_estimators=20)
        importances = metrics["feature_importance"]
        assert len(importances) == 8
        for name in FEATURE_NAMES:
            assert name in importances

    def test_class_weight_balanced(self) -> None:
        """Model uses class_weight='balanced'."""
        X, y = generate_synthetic_training_data(n_samples=100)
        model, _ = train_risk_model(X, y, n_estimators=10)
        assert model.class_weight == "balanced"


class TestBatchScoring:
    """Tests for batch driver scoring."""

    def test_batch_scores_all(self) -> None:
        """Batch scoring processes all drivers."""
        drivers = [
            DriverFeatures(driver_id=f"d{i}", nb_alertes_vitesse=i)
            for i in range(10)
        ]
        results = score_drivers_batch(drivers)
        assert len(results) == 10
        assert all(isinstance(r, RiskResult) for r in results)

    def test_batch_categories_vary(self) -> None:
        """Batch scoring produces varied categories."""
        drivers = [
            DriverFeatures(driver_id="safe"),
            DriverFeatures(driver_id="risky", nb_alertes_vitesse=10, nb_alertes_geofencing=5),
        ]
        results = score_drivers_batch(drivers)
        categories = {r.risk_category for r in results}
        assert len(categories) >= 2  # at least two different categories


class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_risk_score_request_defaults(self) -> None:
        """DriverRiskScoreRequest has default force=False."""
        from app.schemas.driver_risk import DriverRiskScoreRequest
        req = DriverRiskScoreRequest()
        assert req.force is False

    def test_risk_response_schema(self) -> None:
        """DriverRiskScoreResponse accepts all fields."""
        from app.schemas.driver_risk import DriverRiskScoreResponse
        resp = DriverRiskScoreResponse(
            status="completed", message="Scored 20 drivers", drivers_scored=20,
        )
        assert resp.drivers_scored == 20

    def test_api_endpoints_registered(self) -> None:
        """Driver risk API endpoints are registered."""
        from app.api.v1.sotreg_ml import router
        paths = [r.path for r in router.routes]
        assert any("driver-risk" in p for p in paths)
