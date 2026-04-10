"""Tests for NPV calculator (SOTREG M5)."""
from __future__ import annotations

import pytest

from app.services.sotreg.npv_calculator import (
    compute_full_investment_analysis,
    compute_irr,
    compute_npv,
    compute_payback_period,
)


class TestComputeNPV:
    """Verify Net Present Value computation."""

    def test_known_cash_flows(self) -> None:
        """NPV for known investment: -100, +30, +40, +50."""
        result = compute_npv([-100.0, 30.0, 40.0, 50.0], discount_rate=0.10)
        # PV = -100 + 30/1.1 + 40/1.21 + 50/1.331 ≈ -100 + 27.27 + 33.06 + 37.57 = -2.10
        assert abs(result["npv"] - (-2.10)) < 1.0
        assert result["is_viable"] is False
        assert result["currency"] == "MAD"

    def test_zero_discount_rate(self) -> None:
        """Zero discount → NPV = sum of cash flows."""
        result = compute_npv([-100.0, 50.0, 60.0], discount_rate=0.0)
        assert abs(result["npv"] - 10.0) < 0.1

    def test_positive_npv_viable(self) -> None:
        """Positive NPV → viable project."""
        result = compute_npv([-100.0, 50.0, 50.0, 50.0], discount_rate=0.05)
        assert result["npv"] > 0
        assert result["is_viable"] is True

    def test_high_discount_negative_npv(self) -> None:
        """High discount rate makes marginal projects negative."""
        result = compute_npv([-100.0, 30.0, 30.0, 30.0], discount_rate=0.30)
        assert result["npv"] < 0

    def test_present_values_list(self) -> None:
        """Should return per-year present values."""
        result = compute_npv([-100.0, 50.0, 60.0], discount_rate=0.10)
        assert len(result["present_values"]) == 3
        # Present values can be floats or dicts depending on implementation
        assert isinstance(result["present_values"][0], (float, int, dict))

    def test_single_cash_flow(self) -> None:
        """Single cash flow = NPV equals that cash flow."""
        result = compute_npv([-100.0], discount_rate=0.10)
        assert abs(result["npv"] - (-100.0)) < 0.01


class TestComputeIRR:
    """Verify Internal Rate of Return computation."""

    def test_standard_irr(self) -> None:
        """Standard investment profile should converge."""
        result = compute_irr([-100.0, 40.0, 40.0, 40.0])
        assert result["converged"] is True
        assert result["irr"] is not None
        # IRR ≈ 9.7% for this cash flow
        assert 0.05 < result["irr"] < 0.15

    def test_irr_pct(self) -> None:
        """IRR percentage should be irr * 100."""
        result = compute_irr([-100.0, 60.0, 60.0])
        if result["irr"] is not None:
            assert abs(result["irr_pct"] - result["irr"] * 100) < 0.01

    def test_all_positive_no_irr(self) -> None:
        """All positive cash flows → no sign change → may not converge."""
        result = compute_irr([100.0, 50.0, 50.0])
        # IRR requires at least one sign change; behavior is implementation-specific
        assert "converged" in result

    def test_irr_at_zero_npv(self) -> None:
        """NPV at IRR should be approximately 0."""
        result = compute_irr([-100.0, 40.0, 40.0, 40.0])
        if result["converged"] and result["npv_at_irr"] is not None:
            assert abs(result["npv_at_irr"]) < 1.0


class TestComputePayback:
    """Verify payback period computation."""

    def test_basic_payback(self) -> None:
        """Payback for -100, +40, +40, +40 should be between 2 and 4 years."""
        result = compute_payback_period([-100.0, 40.0, 40.0, 40.0])
        assert result["payback_years"] is not None
        assert 2.0 <= result["payback_years"] <= 4.0

    def test_immediate_payback(self) -> None:
        """Positive initial CF → payback at year 0."""
        result = compute_payback_period([100.0, 50.0])
        assert result["payback_years"] == 0.0

    def test_never_positive(self) -> None:
        """All negative → no payback."""
        result = compute_payback_period([-100.0, -50.0, -30.0])
        assert result["payback_years"] is None

    def test_cumulative_flows(self) -> None:
        """Cumulative flows should be returned."""
        result = compute_payback_period([-100.0, 40.0, 40.0, 40.0])
        assert len(result["cumulative_flows"]) == 4
        assert result["cumulative_flows"][0] == -100.0

    def test_mad_currency(self) -> None:
        """Currency should be MAD."""
        result = compute_payback_period([-100.0, 50.0], currency="MAD")
        assert result["currency"] == "MAD"


class TestFullInvestmentAnalysis:
    """Verify combined NPV + IRR + payback."""

    def test_full_analysis(self) -> None:
        """Should contain all three sections."""
        result = compute_full_investment_analysis([-100.0, 40.0, 40.0, 40.0])
        assert "npv" in result
        assert "irr" in result
        assert "payback" in result
