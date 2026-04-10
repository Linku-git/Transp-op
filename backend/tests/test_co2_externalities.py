"""Tests for CO2 externalities valorization (SOTREG M5)."""
from __future__ import annotations

import pytest

from app.services.sotreg.co2_externalities import (
    compute_co2_savings_npv,
    compute_co2_valorization,
)


class TestComputeCO2Valorization:
    """Verify CO2 emissions monetization."""

    def test_diesel_to_electric(self) -> None:
        """Diesel → electric should have significant CO2 savings."""
        result = compute_co2_valorization(
            fleet_annual_km=40000.0,
            current_motorization="diesel",
            target_motorization="electrique",
            carbon_price_mad_tco2=200.0,
            vehicle_count=10,
        )
        assert result["avoided_emissions_tco2"] > 0
        assert result["valorization_mad"] > 0
        assert result["currency"] == "MAD"

    def test_carbon_price_applied(self) -> None:
        """Valorization should scale with carbon price."""
        low = compute_co2_valorization(
            fleet_annual_km=40000.0, carbon_price_mad_tco2=100.0
        )
        high = compute_co2_valorization(
            fleet_annual_km=40000.0, carbon_price_mad_tco2=300.0
        )
        assert high["valorization_mad"] > low["valorization_mad"]

    def test_15year_valorization(self) -> None:
        """15-year valorization should be ~15x annual."""
        result = compute_co2_valorization(fleet_annual_km=40000.0, vehicle_count=5)
        assert result["valorization_15year_mad"] > result["valorization_mad"]

    def test_same_motorization_zero_savings(self) -> None:
        """Same motorization → zero avoided emissions."""
        result = compute_co2_valorization(
            fleet_annual_km=40000.0,
            current_motorization="diesel",
            target_motorization="diesel",
        )
        assert result["avoided_emissions_tco2"] == 0.0
        assert result["valorization_mad"] == 0.0

    def test_electric_includes_grid_factor(self) -> None:
        """Electric target should account for grid emissions."""
        result = compute_co2_valorization(
            fleet_annual_km=40000.0,
            target_motorization="electrique",
            energy_consumption_kwh_per_km=0.25,
        )
        # Target emissions should be > 0 due to grid factor
        assert result["target_emissions_tco2"] > 0

    def test_vehicle_count_scaling(self) -> None:
        """More vehicles → proportionally more savings."""
        single = compute_co2_valorization(fleet_annual_km=40000.0, vehicle_count=1)
        ten = compute_co2_valorization(fleet_annual_km=40000.0, vehicle_count=10)
        assert abs(ten["valorization_mad"] - single["valorization_mad"] * 10) < 1.0


class TestComputeCO2SavingsNPV:
    """Verify NPV of CO2 savings over time."""

    def test_basic_npv(self) -> None:
        """NPV of savings should be positive for diesel→electric."""
        result = compute_co2_savings_npv(
            fleet_annual_km=40000.0,
            discount_rate=0.08,
            horizon_years=15,
        )
        assert result["npv_co2_savings_mad"] > 0
        assert len(result["yearly_savings"]) == 15
        assert result["total_avoided_tco2"] > 0

    def test_carbon_price_escalation(self) -> None:
        """Later years should have higher carbon price."""
        result = compute_co2_savings_npv(
            fleet_annual_km=40000.0,
            carbon_price_escalation_pct=5.0,
            horizon_years=10,
        )
        savings = result["yearly_savings"]
        assert savings[-1]["carbon_price"] > savings[0]["carbon_price"]

    def test_discount_rate_reduces_npv(self) -> None:
        """Higher discount rate → lower NPV."""
        low_r = compute_co2_savings_npv(fleet_annual_km=40000.0, discount_rate=0.03)
        high_r = compute_co2_savings_npv(fleet_annual_km=40000.0, discount_rate=0.15)
        assert low_r["npv_co2_savings_mad"] > high_r["npv_co2_savings_mad"]
