"""Tests for AVL-based KPI engine (SOTREG M4)."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.services.sotreg.avl_kpi_service import (
    compute_all_kpis,
    compute_commercial_speed,
    compute_headway_cov,
    compute_load_factor,
    compute_otp,
)


# ---------------------------------------------------------------------------
# OTP tests
# ---------------------------------------------------------------------------


class TestComputeOTP:
    """Verify On-Time Performance computation."""

    def test_all_on_time(self) -> None:
        """All arrivals within 90s → OTP = 100%."""
        base = datetime(2026, 4, 10, 8, 0)
        arrivals = [
            {"scheduled_time": base, "actual_time": base + timedelta(seconds=30)},
            {"scheduled_time": base + timedelta(minutes=10), "actual_time": base + timedelta(minutes=10, seconds=45)},
            {"scheduled_time": base + timedelta(minutes=20), "actual_time": base + timedelta(minutes=20, seconds=-20)},
        ]
        result = compute_otp(arrivals)
        assert result["otp_pct"] == 100.0
        assert result["meets_target"] is True
        assert result["total_arrivals"] == 3
        assert result["on_time_count"] == 3

    def test_some_late(self) -> None:
        """Mix of on-time and late → OTP < 100%."""
        base = datetime(2026, 4, 10, 8, 0)
        arrivals = [
            {"scheduled_time": base, "actual_time": base + timedelta(seconds=30)},
            {"scheduled_time": base + timedelta(minutes=10), "actual_time": base + timedelta(minutes=10, seconds=120)},
        ]
        result = compute_otp(arrivals)
        assert result["otp_pct"] == 50.0
        assert result["meets_target"] is False
        assert result["late_count"] == 1

    def test_otp_above_95_meets_target(self) -> None:
        """OTP > 95% → meets_target = True."""
        base = datetime(2026, 4, 10, 8, 0)
        arrivals = [
            {"scheduled_time": base + timedelta(minutes=i), "actual_time": base + timedelta(minutes=i, seconds=10)}
            for i in range(20)
        ]
        result = compute_otp(arrivals)
        assert result["otp_pct"] >= 95.0
        assert result["meets_target"] is True

    def test_otp_below_95_fails_target(self) -> None:
        """OTP < 95% → meets_target = False."""
        base = datetime(2026, 4, 10, 8, 0)
        # 10 on-time, 10 late
        arrivals = [
            {"scheduled_time": base + timedelta(minutes=i), "actual_time": base + timedelta(minutes=i, seconds=10)}
            for i in range(10)
        ] + [
            {"scheduled_time": base + timedelta(minutes=i), "actual_time": base + timedelta(minutes=i, seconds=200)}
            for i in range(10, 20)
        ]
        result = compute_otp(arrivals)
        assert result["otp_pct"] < 95.0
        assert result["meets_target"] is False

    def test_empty_arrivals(self) -> None:
        """Empty arrivals → OTP 0% or default."""
        result = compute_otp([])
        assert result["total_arrivals"] == 0

    def test_avg_delay_computed(self) -> None:
        """Average delay should be computed."""
        base = datetime(2026, 4, 10, 8, 0)
        arrivals = [
            {"scheduled_time": base, "actual_time": base + timedelta(seconds=60)},
            {"scheduled_time": base + timedelta(minutes=10), "actual_time": base + timedelta(minutes=10, seconds=120)},
        ]
        result = compute_otp(arrivals)
        assert result["avg_delay_seconds"] > 0


# ---------------------------------------------------------------------------
# Headway COV tests
# ---------------------------------------------------------------------------


class TestComputeHeadwayCOV:
    """Verify Coefficient of Variation of headway."""

    def test_regular_headway_low_cov(self) -> None:
        """Perfectly regular 10-min headway → COV ≈ 0."""
        base = datetime(2026, 4, 10, 8, 0)
        times = [base + timedelta(minutes=10 * i) for i in range(10)]
        result = compute_headway_cov(times)
        assert result["cov"] < 0.05
        assert result["meets_target"] is True

    def test_irregular_headway_high_cov(self) -> None:
        """Highly irregular headway → COV > 0.3."""
        base = datetime(2026, 4, 10, 8, 0)
        times = [
            base,
            base + timedelta(minutes=2),
            base + timedelta(minutes=20),
            base + timedelta(minutes=22),
            base + timedelta(minutes=50),
        ]
        result = compute_headway_cov(times)
        assert result["cov"] > 0.3
        assert result["meets_target"] is False

    def test_cov_below_03_meets_target(self) -> None:
        """COV < 0.3 → meets_target = True."""
        base = datetime(2026, 4, 10, 8, 0)
        times = [base + timedelta(minutes=10 * i) for i in range(6)]
        result = compute_headway_cov(times)
        assert result["meets_target"] is True

    def test_single_departure_no_headway(self) -> None:
        """Single departure → no headway to compute."""
        result = compute_headway_cov([datetime(2026, 4, 10, 8, 0)])
        assert result["headway_count"] == 0

    def test_empty_departures(self) -> None:
        """Empty list → no headway."""
        result = compute_headway_cov([])
        assert result["headway_count"] == 0


# ---------------------------------------------------------------------------
# Load factor tests
# ---------------------------------------------------------------------------


class TestComputeLoadFactor:
    """Verify load factor computation."""

    def test_full_vehicles(self) -> None:
        """All vehicles full → load factor = 1.0."""
        observations = [
            {"passenger_count": 40, "vehicle_capacity": 40},
            {"passenger_count": 40, "vehicle_capacity": 40},
        ]
        result = compute_load_factor(observations)
        assert abs(result["load_factor"] - 1.0) < 0.01

    def test_half_full(self) -> None:
        """Half-full → load factor ≈ 0.5."""
        observations = [
            {"passenger_count": 20, "vehicle_capacity": 40},
            {"passenger_count": 20, "vehicle_capacity": 40},
        ]
        result = compute_load_factor(observations)
        assert abs(result["load_factor"] - 0.5) < 0.01

    def test_empty_observations(self) -> None:
        """No observations → defaults."""
        result = compute_load_factor([])
        assert result["observation_count"] == 0

    def test_peak_load_factor(self) -> None:
        """Peak load factor should be the max."""
        observations = [
            {"passenger_count": 10, "vehicle_capacity": 40},
            {"passenger_count": 35, "vehicle_capacity": 40},
            {"passenger_count": 20, "vehicle_capacity": 40},
        ]
        result = compute_load_factor(observations)
        assert abs(result["peak_load_factor"] - 0.875) < 0.01


# ---------------------------------------------------------------------------
# Commercial speed tests
# ---------------------------------------------------------------------------


class TestComputeCommercialSpeed:
    """Verify commercial speed computation."""

    def test_basic_speed(self) -> None:
        """100 km in 2 hours = 50 km/h."""
        trips = [{"distance_km": 100.0, "duration_hours": 2.0}]
        result = compute_commercial_speed(trips)
        assert abs(result["commercial_speed_kmh"] - 50.0) < 0.1

    def test_multiple_trips(self) -> None:
        """Aggregate across trips."""
        trips = [
            {"distance_km": 50.0, "duration_hours": 1.0},
            {"distance_km": 100.0, "duration_hours": 2.5},
        ]
        result = compute_commercial_speed(trips)
        # Total: 150 km / 3.5 hours = 42.86 km/h
        assert abs(result["commercial_speed_kmh"] - 42.86) < 0.5
        assert result["trip_count"] == 2

    def test_empty_trips(self) -> None:
        """No trips → default."""
        result = compute_commercial_speed([])
        assert result["trip_count"] == 0


# ---------------------------------------------------------------------------
# Batch compute tests
# ---------------------------------------------------------------------------


class TestComputeAllKPIs:
    """Verify batch KPI computation."""

    def test_all_kpis_present(self) -> None:
        """All data provided → all 4 KPIs computed."""
        base = datetime(2026, 4, 10, 8, 0)
        result = compute_all_kpis(
            arrivals=[
                {"scheduled_time": base, "actual_time": base + timedelta(seconds=30)},
            ],
            departure_times=[base, base + timedelta(minutes=10)],
            load_observations=[{"passenger_count": 20, "vehicle_capacity": 40}],
            trips=[{"distance_km": 50.0, "duration_hours": 1.0}],
        )
        assert "otp" in result
        assert "headway_cov" in result
        assert "load_factor" in result
        assert "commercial_speed" in result
        assert "computed_at" in result

    def test_partial_data(self) -> None:
        """Only OTP data → only OTP computed."""
        base = datetime(2026, 4, 10, 8, 0)
        result = compute_all_kpis(
            arrivals=[
                {"scheduled_time": base, "actual_time": base + timedelta(seconds=30)},
            ],
        )
        assert "otp" in result
        assert "headway_cov" not in result

    def test_no_data(self) -> None:
        """No data at all → empty results."""
        result = compute_all_kpis()
        assert "computed_at" in result
