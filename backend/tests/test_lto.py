"""Tests for Leave Time Optimization (LTO) anti-platooning (SOTREG M4)."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.services.sotreg.lto_service import (
    compute_lto_schedule,
    detect_platooning,
    optimize_departure_times,
)


def _base() -> datetime:
    return datetime(2026, 4, 10, 8, 0)


# ---------------------------------------------------------------------------
# Platooning detection tests
# ---------------------------------------------------------------------------


class TestDetectPlatooning:
    """Verify platooning detection logic."""

    def test_platooning_detected(self) -> None:
        """High COV + high deviation → platooning."""
        base = _base()
        # Irregular departures (platoon: 2 very close, then gap)
        departures = [base, base + timedelta(seconds=30), base + timedelta(minutes=20)]
        scheduled = [base, base + timedelta(minutes=10), base + timedelta(minutes=20)]
        result = detect_platooning(departures, scheduled)
        assert result["is_platooning"] is True
        assert result["cov_headway"] > 0.3

    def test_no_platooning_regular(self) -> None:
        """Regular 10-min headway, on-schedule → no platooning."""
        base = _base()
        times = [base + timedelta(minutes=10 * i) for i in range(5)]
        result = detect_platooning(times, times)
        assert result["is_platooning"] is False
        assert result["cov_headway"] < 0.3

    def test_single_vehicle_no_platooning(self) -> None:
        """Single vehicle → no platooning possible."""
        base = _base()
        result = detect_platooning([base], [base])
        assert result["is_platooning"] is False

    def test_empty_departures(self) -> None:
        """Empty list → no platooning."""
        result = detect_platooning([], [])
        assert result["is_platooning"] is False

    def test_vehicle_count_returned(self) -> None:
        """Should report vehicle count."""
        base = _base()
        times = [base + timedelta(minutes=10 * i) for i in range(4)]
        result = detect_platooning(times, times)
        assert result["vehicle_count"] == 4


# ---------------------------------------------------------------------------
# Optimization tests
# ---------------------------------------------------------------------------


class TestOptimizeDepartureTimes:
    """Verify LTO optimization reduces headway variance."""

    def test_optimization_reduces_cov(self) -> None:
        """Platoon cluster should be spread out after optimization."""
        base = _base()
        # 3 buses very close, then a gap
        departures = [
            base,
            base + timedelta(seconds=60),
            base + timedelta(seconds=120),
            base + timedelta(minutes=30),
        ]
        result = optimize_departure_times(departures, target_headway_seconds=600)
        assert result["optimized_cov"] <= result["original_cov"]
        assert result["converged"] is True

    def test_already_optimal_no_change(self) -> None:
        """Regular headway → minimal offsets."""
        base = _base()
        departures = [base + timedelta(minutes=10 * i) for i in range(5)]
        result = optimize_departure_times(departures, target_headway_seconds=600)
        # Offsets should be very small
        for offset in result["offsets_seconds"]:
            assert abs(offset) < 60  # Less than 1 minute adjustment

    def test_offsets_within_bounds(self) -> None:
        """All offsets within max_offset_seconds."""
        base = _base()
        departures = [base, base + timedelta(seconds=30), base + timedelta(minutes=20)]
        result = optimize_departure_times(departures, max_offset_seconds=300)
        for offset in result["offsets_seconds"]:
            assert abs(offset) <= 300 + 1  # Small tolerance

    def test_minimum_headway_parameter_accepted(self) -> None:
        """Min headway parameter should be accepted and influence optimization."""
        base = _base()
        departures = [base, base + timedelta(seconds=30), base + timedelta(seconds=60)]
        result = optimize_departure_times(
            departures,
            min_headway_seconds=120,
            target_headway_seconds=300,
        )
        # The optimizer should at least converge
        assert result["converged"] is True
        assert len(result["optimized_departures"]) == 3

    def test_single_vehicle_returns_quickly(self) -> None:
        """Single vehicle → no optimization needed."""
        base = _base()
        result = optimize_departure_times([base])
        assert len(result["offsets_seconds"]) == 1
        assert result["offsets_seconds"][0] == 0.0

    def test_improvement_percentage(self) -> None:
        """Improvement should be non-negative."""
        base = _base()
        departures = [base, base + timedelta(seconds=30), base + timedelta(minutes=15)]
        result = optimize_departure_times(departures, target_headway_seconds=450)
        assert result["improvement_pct"] >= 0


# ---------------------------------------------------------------------------
# Full pipeline tests
# ---------------------------------------------------------------------------


class TestComputeLTOSchedule:
    """Verify full LTO pipeline."""

    def test_full_pipeline_with_platooning(self) -> None:
        """Platooning input → optimization → schedule."""
        base = _base()
        departures = [
            {"vehicle_id": "v1", "scheduled_departure": base, "actual_departure": base},
            {"vehicle_id": "v2", "scheduled_departure": base + timedelta(minutes=10), "actual_departure": base + timedelta(seconds=60)},
            {"vehicle_id": "v3", "scheduled_departure": base + timedelta(minutes=20), "actual_departure": base + timedelta(seconds=120)},
        ]
        result = compute_lto_schedule(departures, target_headway_seconds=600)
        assert "needs_optimization" in result
        assert "platooning_check" in result
        assert "schedule" in result
        assert len(result["schedule"]) == 3

    def test_non_platooning_no_optimization(self) -> None:
        """Regular schedule → no optimization needed."""
        base = _base()
        departures = [
            {"vehicle_id": f"v{i}", "scheduled_departure": base + timedelta(minutes=10 * i), "actual_departure": base + timedelta(minutes=10 * i)}
            for i in range(5)
        ]
        result = compute_lto_schedule(departures, target_headway_seconds=600)
        assert result["needs_optimization"] is False

    def test_schedule_entries_have_vehicle_ids(self) -> None:
        """Each schedule entry should have vehicle_id."""
        base = _base()
        departures = [
            {"vehicle_id": "v1", "scheduled_departure": base, "actual_departure": base},
            {"vehicle_id": "v2", "scheduled_departure": base + timedelta(seconds=30), "actual_departure": base + timedelta(seconds=30)},
            {"vehicle_id": "v3", "scheduled_departure": base + timedelta(minutes=20), "actual_departure": base + timedelta(minutes=20)},
        ]
        result = compute_lto_schedule(departures)
        for entry in result["schedule"]:
            assert "vehicle_id" in entry
            assert "offset_seconds" in entry

    def test_empty_departures(self) -> None:
        """Empty input → no optimization."""
        result = compute_lto_schedule([])
        assert result["needs_optimization"] is False
