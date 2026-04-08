"""Tests for Security Scoring Engine (Session 62)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from app.models.security_score import SecurityScore
from app.services.security_scoring import (
    compute_security_score,
    classify_risk_level,
    is_night_hour,
    generate_heatmap,
    aggregate_scores,
    compute_time_slot_risk,
)


class TestSecurityScoring:
    def test_perfect_safety(self):
        score, level, factors = compute_security_score(
            questionnaire_rating=5,
            vulnerable_stop_count=0,
            night_commute_exposure=0.0,
            avg_stop_isolation=0.0,
        )
        assert score == 100
        assert level == "low"

    def test_worst_safety(self):
        score, level, factors = compute_security_score(
            questionnaire_rating=1,
            vulnerable_stop_count=10,
            night_commute_exposure=1.0,
            avg_stop_isolation=1.0,
        )
        assert score <= 25
        assert level == "critical"

    def test_medium_safety(self):
        score, level, factors = compute_security_score(
            questionnaire_rating=3,
            vulnerable_stop_count=3,
            night_commute_exposure=0.3,
            avg_stop_isolation=0.4,
        )
        assert 30 < score < 80

    def test_factors_included(self):
        _, _, factors = compute_security_score(
            questionnaire_rating=4,
            vulnerable_stop_count=2,
        )
        assert "questionnaire_score" in factors
        assert "vulnerable_stops_score" in factors
        assert "night_exposure_score" in factors
        assert "stop_isolation_score" in factors
        assert "weights" in factors

    def test_default_values(self):
        score, level, _ = compute_security_score()
        assert 0 <= score <= 100
        assert level in ("low", "medium", "high", "critical")


class TestRiskClassification:
    def test_critical(self):
        assert classify_risk_level(20) == "critical"
        assert classify_risk_level(25) == "critical"

    def test_high(self):
        assert classify_risk_level(30) == "high"
        assert classify_risk_level(50) == "high"

    def test_medium(self):
        assert classify_risk_level(55) == "medium"
        assert classify_risk_level(75) == "medium"

    def test_low(self):
        assert classify_risk_level(80) == "low"
        assert classify_risk_level(100) == "low"


class TestNightHours:
    def test_night_at_22h(self):
        assert is_night_hour(22) is True

    def test_night_at_3am(self):
        assert is_night_hour(3) is True

    def test_night_at_6_30(self):
        assert is_night_hour(6, 30) is True

    def test_day_at_6_31(self):
        assert is_night_hour(6, 31) is False

    def test_day_at_noon(self):
        assert is_night_hour(12) is False

    def test_night_at_20h(self):
        assert is_night_hour(20) is True

    def test_day_at_19h59(self):
        assert is_night_hour(19, 59) is False


class TestHeatmap:
    def test_heatmap_generates_8_slots(self):
        heatmap = generate_heatmap()
        assert len(heatmap) == 8

    def test_night_slots_have_higher_risk(self):
        heatmap = generate_heatmap(base_risk=0.3)
        night_risks = [s["risk_score"] for s in heatmap if s["is_night"]]
        day_risks = [s["risk_score"] for s in heatmap if not s["is_night"]]
        assert min(night_risks) > min(day_risks)

    def test_heatmap_fields(self):
        heatmap = generate_heatmap()
        for slot in heatmap:
            assert "time_slot" in slot
            assert "risk_score" in slot
            assert "is_night" in slot


class TestAggregation:
    def test_aggregate_by_site(self):
        scores = [
            {"site_id": "s1", "score": 80},
            {"site_id": "s1", "score": 60},
            {"site_id": "s2", "score": 40},
        ]
        result = aggregate_scores(scores, "site_id")
        assert len(result) == 2

        s1 = next(r for r in result if r["group_value"] == "s1")
        assert s1["avg_score"] == 70.0
        assert s1["employee_count"] == 2

    def test_risk_distribution(self):
        scores = [
            {"team": "A", "score": 90},  # low
            {"team": "A", "score": 20},  # critical
        ]
        result = aggregate_scores(scores, "team")
        dist = result[0]["risk_distribution"]
        assert dist["low"] == 1
        assert dist["critical"] == 1


class TestSecurityScoreModel:
    def test_create(self):
        s = SecurityScore(
            tenant_id=uuid.uuid4(),
            employee_id=uuid.uuid4(),
            score=75,
            risk_level="medium",
            contributing_factors={"q": 80, "v": 70},
            computed_at=datetime.now(timezone.utc),
        )
        assert s.score == 75
        assert s.risk_level == "medium"
