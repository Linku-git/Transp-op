"""Tests for Security-Constrained Pooling (Session 63)."""
from __future__ import annotations

import uuid

import pytest

from app.models.clustering_config import ClusteringConfig
from app.services.security_constraints import (
    SecurityConstraintConfig,
    EmployeeSecurityProfile,
    StopSecurityInfo,
    apply_security_constraints,
    filter_night_stops,
    suggest_alternative_stops,
    compute_three_dimension_score,
    should_assign_priority_vehicle,
)
from app.services.night_routing import (
    process_night_route,
    is_night_shift,
    NightRouteResult,
)


def _employee(score: int = 50, night: bool = False) -> EmployeeSecurityProfile:
    return EmployeeSecurityProfile(
        employee_id=str(uuid.uuid4()),
        lat=33.58, lng=-7.63,
        security_score=score,
        is_night_shift=night,
    )


def _stop(critical: bool = False, lighting: float = 0.7) -> StopSecurityInfo:
    return StopSecurityInfo(
        stop_id=str(uuid.uuid4()),
        lat=33.58, lng=-7.63,
        composite_risk_score=0.8 if critical else 0.3,
        is_critical=critical,
        lighting_score=lighting,
    )


class TestNightGroupMinimum:
    def test_clusters_below_min_are_merged(self):
        clusters = [
            [_employee(), _employee()],  # size 2 < min 3
            [_employee(), _employee(), _employee(), _employee()],  # size 4
        ]
        result = apply_security_constraints(clusters, is_night=True)
        # Undersized cluster merged into first valid cluster
        assert all(len(c) >= 3 for c in result)

    def test_day_clusters_not_affected(self):
        clusters = [
            [_employee()],  # size 1 — OK for day
            [_employee(), _employee()],
        ]
        result = apply_security_constraints(clusters, is_night=False)
        assert len(result) == 2  # Unchanged


class TestNightStopFiltering:
    def test_critical_stops_excluded(self):
        stops = [_stop(critical=True), _stop(critical=False)]
        allowed, excluded = filter_night_stops(stops)
        assert len(excluded) == 1
        assert excluded[0].is_critical

    def test_poorly_lit_stops_excluded(self):
        stops = [_stop(lighting=0.2), _stop(lighting=0.8)]
        allowed, excluded = filter_night_stops(stops)
        assert len(excluded) == 1
        assert excluded[0].lighting_score < 0.4

    def test_safe_stops_allowed(self):
        stops = [_stop(critical=False, lighting=0.8)]
        allowed, excluded = filter_night_stops(stops)
        assert len(allowed) == 1
        assert len(excluded) == 0


class TestAlternativeStops:
    def test_alternatives_exclude_critical(self):
        excluded = _stop(critical=True)
        all_stops = [
            _stop(critical=True),
            _stop(critical=False, lighting=0.8),
            _stop(critical=False, lighting=0.6),
        ]
        alts = suggest_alternative_stops(excluded, all_stops)
        assert all(not s.is_critical for s in alts)

    def test_returns_max_3(self):
        excluded = _stop(critical=True)
        all_stops = [_stop(critical=False, lighting=0.7) for _ in range(10)]
        alts = suggest_alternative_stops(excluded, all_stops)
        assert len(alts) <= 3


class TestThreeDimensionScore:
    def test_perfect_match(self):
        score = compute_three_dimension_score(
            geo_distance=0.0,
            shift_compatible=True,
            security_score_diff=0.0,
        )
        assert score == 0.0

    def test_worst_match(self):
        score = compute_three_dimension_score(
            geo_distance=1.0,
            shift_compatible=False,
            security_score_diff=1.0,
        )
        assert score == 1.0

    def test_geo_only_matters_with_weight(self):
        cfg = SecurityConstraintConfig(geo_weight=1.0, shift_weight=0.0, security_weight=0.0)
        score = compute_three_dimension_score(
            geo_distance=0.5,
            shift_compatible=False,
            security_score_diff=1.0,
            config=cfg,
        )
        assert score == pytest.approx(0.5, abs=0.01)

    def test_security_weight_changes_score(self):
        low_sec = SecurityConstraintConfig(security_weight=0.1)
        high_sec = SecurityConstraintConfig(security_weight=0.5)

        score_low = compute_three_dimension_score(0.5, True, 0.8, config=low_sec)
        score_high = compute_three_dimension_score(0.5, True, 0.8, config=high_sec)
        assert score_high > score_low


class TestPriorityVehicle:
    def test_night_route_gets_priority(self):
        assert should_assign_priority_vehicle(True, False) is True

    def test_high_risk_gets_priority(self):
        assert should_assign_priority_vehicle(False, True) is True

    def test_normal_route_no_priority(self):
        assert should_assign_priority_vehicle(False, False) is False

    def test_disabled_config(self):
        cfg = SecurityConstraintConfig(priority_vehicle_for_night=False)
        assert should_assign_priority_vehicle(True, True, cfg) is False


class TestNightRouting:
    def test_process_night_route(self):
        route_stops = [
            _stop(critical=True),
            _stop(critical=False, lighting=0.8),
            _stop(critical=False, lighting=0.6),
        ]
        all_stops = route_stops + [_stop(critical=False, lighting=0.9)]

        result = process_night_route(route_stops, all_stops)
        assert isinstance(result, NightRouteResult)
        assert result.is_valid
        assert len(result.excluded_stops) == 1
        assert len(result.route_stops) == 2

    def test_is_night_shift(self):
        assert is_night_shift(22) is True
        assert is_night_shift(5) is True
        assert is_night_shift(8) is False
        assert is_night_shift(14) is False


class TestClusteringConfigModel:
    def test_create(self):
        config = ClusteringConfig(
            tenant_id=uuid.uuid4(),
            site_id=uuid.uuid4(),
            geo_weight=0.4,
            shift_weight=0.35,
            security_weight=0.25,
            night_min_group_size=4,
        )
        assert config.geo_weight == 0.4
        assert config.night_min_group_size == 4
