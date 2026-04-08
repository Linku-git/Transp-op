"""Tests for Stop Risk Score model and algorithm (Session 57)."""
from __future__ import annotations

import uuid

import pytest

from app.models.stop_risk_score import StopRiskScore
from app.services.risk_scoring import (
    compute_risk_score,
    is_critical,
    compute_and_flag,
    RiskWeights,
    DEFAULT_CRITICAL_THRESHOLD,
)
from app.schemas.stop_risk_score import StopRiskScoreCreate, StopRiskScoreUpdate


class TestRiskScoringAlgorithm:
    """Test the weighted risk scoring formula."""

    def test_all_safe_scores_produce_low_risk(self):
        score = compute_risk_score(
            isolation_score=0.0,  # not isolated
            lighting_score=1.0,  # well lit
            tc_frequency_score=1.0,  # frequent transport
            night_risk_multiplier=0.0,
            employee_perception_avg=1.0,  # feels safe
        )
        assert score == 0.0

    def test_all_dangerous_scores_produce_high_risk(self):
        score = compute_risk_score(
            isolation_score=1.0,  # very isolated
            lighting_score=0.0,  # no lighting
            tc_frequency_score=0.0,  # no transport
            night_risk_multiplier=1.0,
            employee_perception_avg=0.0,  # feels unsafe
            is_night=True,
        )
        assert score == 1.0

    def test_middle_scores_produce_medium_risk(self):
        score = compute_risk_score(
            isolation_score=0.5,
            lighting_score=0.5,
            tc_frequency_score=0.5,
            night_risk_multiplier=0.5,
            employee_perception_avg=0.5,
            is_night=True,
        )
        assert 0.3 < score < 0.7

    def test_night_flag_adds_risk(self):
        day_score = compute_risk_score(
            isolation_score=0.5,
            lighting_score=0.5,
            tc_frequency_score=0.5,
            night_risk_multiplier=1.0,
            employee_perception_avg=0.5,
            is_night=False,
        )
        night_score = compute_risk_score(
            isolation_score=0.5,
            lighting_score=0.5,
            tc_frequency_score=0.5,
            night_risk_multiplier=1.0,
            employee_perception_avg=0.5,
            is_night=True,
        )
        assert night_score > day_score

    def test_custom_weights(self):
        weights = RiskWeights(
            isolation=1.0,
            lighting=0.0,
            tc_frequency=0.0,
            night_risk=0.0,
            employee_perception=0.0,
        )
        score = compute_risk_score(
            isolation_score=0.8,
            lighting_score=0.0,
            tc_frequency_score=0.0,
            night_risk_multiplier=1.0,
            employee_perception_avg=0.0,
            weights=weights,
        )
        assert score == pytest.approx(0.8, abs=0.01)

    def test_scores_are_clamped(self):
        score = compute_risk_score(
            isolation_score=1.5,  # out of range
            lighting_score=-0.5,  # out of range
            tc_frequency_score=2.0,
            night_risk_multiplier=3.0,
            employee_perception_avg=-1.0,
            is_night=True,
        )
        assert 0.0 <= score <= 1.0


class TestCriticalFlag:
    """Test critical threshold flagging."""

    def test_above_threshold_is_critical(self):
        assert is_critical(0.75, 0.7) is True

    def test_below_threshold_is_not_critical(self):
        assert is_critical(0.5, 0.7) is False

    def test_exactly_at_threshold_is_critical(self):
        assert is_critical(0.7, 0.7) is True

    def test_default_threshold(self):
        assert DEFAULT_CRITICAL_THRESHOLD == 0.7


class TestComputeAndFlag:
    """Test combined computation."""

    def test_returns_tuple(self):
        result = compute_and_flag(
            isolation_score=0.9,
            lighting_score=0.1,
            tc_frequency_score=0.1,
            night_risk_multiplier=1.0,
            employee_perception_avg=0.1,
        )
        assert isinstance(result, tuple)
        assert len(result) == 2
        score, critical = result
        assert isinstance(score, float)
        assert isinstance(critical, bool)

    def test_high_risk_is_flagged_critical(self):
        score, critical = compute_and_flag(
            isolation_score=1.0,
            lighting_score=0.0,
            tc_frequency_score=0.0,
            night_risk_multiplier=1.0,
            employee_perception_avg=0.0,
        )
        assert score > 0.7
        assert critical is True

    def test_low_risk_is_not_critical(self):
        score, critical = compute_and_flag(
            isolation_score=0.1,
            lighting_score=0.9,
            tc_frequency_score=0.9,
            night_risk_multiplier=0.1,
            employee_perception_avg=0.9,
        )
        assert score < 0.7
        assert critical is False


class TestStopRiskScoreModel:
    """Test model creation."""

    def test_model_creation(self):
        stop = StopRiskScore(
            tenant_id=uuid.uuid4(),
            stop_name="Test Stop",
            lat=33.58,
            lng=-7.63,
            isolation_score=0.7,
            lighting_score=0.3,
            tc_frequency_score=0.4,
            night_risk_multiplier=1.2,
            employee_perception_avg=0.3,
            composite_risk_score=0.75,
            is_critical=True,
        )
        assert stop.stop_name == "Test Stop"
        assert stop.is_critical is True

    def test_explicit_values(self):
        stop = StopRiskScore(
            tenant_id=uuid.uuid4(),
            stop_name="Default Stop",
            lat=33.0,
            lng=-7.0,
            isolation_score=0.5,
            lighting_score=0.5,
            composite_risk_score=0.0,
            is_critical=False,
        )
        assert stop.isolation_score == 0.5
        assert stop.lighting_score == 0.5
        assert stop.is_critical is False


class TestSchemas:
    """Test Pydantic schemas."""

    def test_create_schema_validation(self):
        schema = StopRiskScoreCreate(
            stop_name="Test",
            lat=33.58,
            lng=-7.63,
            isolation_score=0.8,
        )
        assert schema.isolation_score == 0.8

    def test_create_schema_rejects_invalid_lat(self):
        with pytest.raises(Exception):
            StopRiskScoreCreate(stop_name="Test", lat=100, lng=-7.63)

    def test_create_schema_rejects_invalid_score(self):
        with pytest.raises(Exception):
            StopRiskScoreCreate(
                stop_name="Test", lat=33, lng=-7, isolation_score=1.5
            )

    def test_update_schema_partial(self):
        schema = StopRiskScoreUpdate(isolation_score=0.9)
        assert schema.isolation_score == 0.9
        assert schema.lighting_score is None

    def test_response_from_attributes(self):
        assert StopRiskScoreCreate.model_config.get("from_attributes") is None  # Create doesn't need it
        from app.schemas.stop_risk_score import StopRiskScoreResponse
        assert StopRiskScoreResponse.model_config.get("from_attributes") is True
