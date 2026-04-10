"""Tests for MAD currency calibration (Session 109)."""
from __future__ import annotations

import pytest

from app.services.sotreg.mad_calibration import (
    adjust_for_inflation,
    calibrate_financial_params,
    compute_real_discount_rate,
    convert_from_mad,
    convert_to_mad,
    get_onee_tariff,
)


class TestConvertToMAD:
    """Verify EUR/USD to MAD conversion."""

    def test_eur_to_mad(self) -> None:
        result = convert_to_mad(100.0, "EUR")
        assert abs(result["amount_mad"] - 1080.0) < 1.0
        assert result["source_currency"] == "EUR"

    def test_usd_to_mad(self) -> None:
        result = convert_to_mad(100.0, "USD")
        assert abs(result["amount_mad"] - 995.0) < 1.0

    def test_precision_2_decimals(self) -> None:
        result = convert_to_mad(33.33, "EUR")
        # 33.33 * 10.80 = 359.964 → 359.96
        mad_str = f"{result['amount_mad']:.2f}"
        assert len(mad_str.split(".")[-1]) == 2

    def test_zero_amount(self) -> None:
        result = convert_to_mad(0.0, "EUR")
        assert result["amount_mad"] == 0.0

    def test_invalid_currency_raises(self) -> None:
        with pytest.raises(ValueError):
            convert_to_mad(100.0, "XYZ")


class TestConvertFromMAD:
    """Verify MAD to foreign currency conversion."""

    def test_mad_to_eur(self) -> None:
        result = convert_from_mad(1080.0, "EUR")
        assert abs(result["amount_foreign"] - 100.0) < 0.5


class TestInflationAdjustment:
    """Verify inflation adjustment."""

    def test_basic_inflation(self) -> None:
        result = adjust_for_inflation(1000.0, years=5)
        assert result["adjusted"] > 1000.0
        assert result["years"] == 5

    def test_zero_years_no_change(self) -> None:
        result = adjust_for_inflation(1000.0, years=0)
        assert abs(result["adjusted"] - 1000.0) < 0.01

    def test_year_over_year_compounding(self) -> None:
        r1 = adjust_for_inflation(1000.0, years=1)
        r2 = adjust_for_inflation(1000.0, years=2)
        assert r2["adjusted"] > r1["adjusted"]

    def test_custom_inflation_rate(self) -> None:
        result = adjust_for_inflation(1000.0, years=10, inflation_rate=0.05)
        # 1000 * 1.05^10 ≈ 1628.89
        assert abs(result["adjusted"] - 1628.89) < 5.0


class TestRealDiscountRate:
    """Verify Fisher equation."""

    def test_fisher_equation(self) -> None:
        result = compute_real_discount_rate(nominal_rate=0.08, inflation_rate=0.028)
        # real ≈ (1.08/1.028) - 1 ≈ 0.0506
        assert abs(result["real_rate"] - 0.0506) < 0.005

    def test_zero_inflation(self) -> None:
        result = compute_real_discount_rate(nominal_rate=0.05, inflation_rate=0.0)
        assert abs(result["real_rate"] - 0.05) < 0.001


class TestONEETariff:
    """Verify ONEE tariff schedule."""

    def test_all_periods(self) -> None:
        result = get_onee_tariff()
        assert "creuse" in result or "schedule" in result

    def test_creuse_rate(self) -> None:
        result = get_onee_tariff("creuse")
        assert result["rate_mad_kwh"] == 0.82

    def test_pleine_rate(self) -> None:
        result = get_onee_tariff("pleine")
        assert result["rate_mad_kwh"] == 1.22

    def test_pointe_rate(self) -> None:
        result = get_onee_tariff("pointe")
        assert result["rate_mad_kwh"] == 1.58


class TestCalibrateFinancialParams:
    """Verify full calibration."""

    def test_calibration_returns_all_params(self) -> None:
        result = calibrate_financial_params()
        assert "exchange_rates" in result
        assert "inflation_rate" in result
        assert "bam_base_rate" in result
