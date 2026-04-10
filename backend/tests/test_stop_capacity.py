"""Tests for HCM 2000 stop capacity model (SOTREG M3)."""
from __future__ import annotations

import pytest

from app.services.sotreg.stop_capacity import (
    compute_los_grade,
    compute_stop_analysis,
    compute_stop_capacity,
)


class TestComputeStopCapacity:
    """Verify HCM 2000 capacity formula: Bs = N × 3600 × (g/C) / [t_c + t_d×(g/C) + Z×c_v×t_d]."""

    def test_basic_capacity(self) -> None:
        """Single berth with default parameters should give reasonable capacity."""
        result = compute_stop_capacity(n_berths=1)
        assert result["capacity_buses_per_hour"] > 0
        assert result["n_berths"] == 1

    def test_more_berths_more_capacity(self) -> None:
        """More berths → higher capacity (linear)."""
        cap_1 = compute_stop_capacity(n_berths=1)
        cap_3 = compute_stop_capacity(n_berths=3)
        assert cap_3["capacity_buses_per_hour"] > cap_1["capacity_buses_per_hour"]

    def test_higher_green_ratio_more_capacity(self) -> None:
        """Higher g/C → more green time → more capacity."""
        cap_low = compute_stop_capacity(green_ratio=0.3)
        cap_high = compute_stop_capacity(green_ratio=0.7)
        assert cap_high["capacity_buses_per_hour"] > cap_low["capacity_buses_per_hour"]

    def test_longer_dwell_less_capacity(self) -> None:
        """Longer dwell time → less capacity."""
        cap_short = compute_stop_capacity(dwell_time_s=20.0)
        cap_long = compute_stop_capacity(dwell_time_s=60.0)
        assert cap_short["capacity_buses_per_hour"] > cap_long["capacity_buses_per_hour"]

    def test_effective_dwell_returned(self) -> None:
        """Effective dwell time should be in the result."""
        result = compute_stop_capacity(dwell_time_s=30.0)
        assert result["effective_dwell_s"] > 0

    def test_z_factor_confidence(self) -> None:
        """Higher Z → more conservative → less capacity."""
        cap_low_z = compute_stop_capacity(z_factor=1.28)  # 90%
        cap_high_z = compute_stop_capacity(z_factor=2.33)  # 99%
        assert cap_low_z["capacity_buses_per_hour"] > cap_high_z["capacity_buses_per_hour"]

    def test_hcm_reference_values(self) -> None:
        """HCM reference: 1 berth, g/C=0.5, t_d=30s, t_c=15s → ~25-35 buses/hr."""
        result = compute_stop_capacity(
            n_berths=1,
            green_ratio=0.5,
            dwell_time_s=30.0,
            clearance_time_s=15.0,
            cv_dwell=0.6,
            z_factor=1.96,
        )
        # Bs = 1 × 3600 × 0.5 / [15 + 30×0.5 + 1.96×0.6×30]
        # = 1800 / [15 + 15 + 35.28] = 1800 / 65.28 ≈ 27.6
        assert 20 < result["capacity_buses_per_hour"] < 40


class TestComputeLOSGrade:
    """Verify LOS grading from A through F."""

    def test_los_a_low_utilization(self) -> None:
        """Utilization < 0.25 → LOS A."""
        result = compute_los_grade(demand_buses_per_hour=5, capacity_buses_per_hour=30)
        assert result["los_grade"] == "A"
        assert result["utilization"] < 0.25

    def test_los_b(self) -> None:
        """Utilization 0.25-0.40 → LOS B."""
        result = compute_los_grade(demand_buses_per_hour=9, capacity_buses_per_hour=30)
        assert result["los_grade"] == "B"

    def test_los_c(self) -> None:
        """Utilization 0.40-0.60 → LOS C."""
        result = compute_los_grade(demand_buses_per_hour=15, capacity_buses_per_hour=30)
        assert result["los_grade"] == "C"

    def test_los_d(self) -> None:
        """Utilization 0.60-0.75 → LOS D."""
        result = compute_los_grade(demand_buses_per_hour=20, capacity_buses_per_hour=30)
        assert result["los_grade"] == "D"

    def test_los_e_at_capacity(self) -> None:
        """Utilization 0.75-1.0 → LOS E."""
        result = compute_los_grade(demand_buses_per_hour=25, capacity_buses_per_hour=30)
        assert result["los_grade"] == "E"

    def test_los_f_over_capacity(self) -> None:
        """Utilization > 1.0 → LOS F."""
        result = compute_los_grade(demand_buses_per_hour=35, capacity_buses_per_hour=30)
        assert result["los_grade"] == "F"
        assert result["utilization"] > 1.0

    def test_zero_demand_los_a(self) -> None:
        """Zero demand → LOS A."""
        result = compute_los_grade(demand_buses_per_hour=0, capacity_buses_per_hour=30)
        assert result["los_grade"] == "A"

    def test_avg_wait_increases_with_utilization(self) -> None:
        """Wait time should increase with utilization."""
        low = compute_los_grade(demand_buses_per_hour=5, capacity_buses_per_hour=30)
        high = compute_los_grade(demand_buses_per_hour=25, capacity_buses_per_hour=30)
        assert high["avg_wait_seconds"] > low["avg_wait_seconds"]

    def test_los_has_description(self) -> None:
        """All grades should have a description."""
        result = compute_los_grade(demand_buses_per_hour=15, capacity_buses_per_hour=30)
        assert result["description"]
        assert isinstance(result["description"], str)


class TestComputeStopAnalysis:
    """Verify full stop analysis combining capacity and LOS."""

    def test_basic_analysis(self) -> None:
        """Basic analysis should return capacity, los, derived sections."""
        result = compute_stop_analysis(
            n_berths=2,
            demand_passengers=50,
            avg_boarding_time_s=3.0,
            vehicle_capacity=40,
            headway_minutes=10.0,
        )
        assert "capacity" in result
        assert "los" in result
        assert result["capacity"]["capacity_buses_per_hour"] > 0
        assert result["los"]["los_grade"] in ["A", "B", "C", "D", "E", "F"]

    def test_high_demand_los_degrades(self) -> None:
        """High demand (short headway) should degrade LOS."""
        low = compute_stop_analysis(
            demand_passengers=20,
            headway_minutes=15.0,
        )
        high = compute_stop_analysis(
            demand_passengers=100,
            headway_minutes=3.0,
        )
        grades = ["A", "B", "C", "D", "E", "F"]
        assert grades.index(high["los"]["los_grade"]) >= grades.index(low["los"]["los_grade"])
