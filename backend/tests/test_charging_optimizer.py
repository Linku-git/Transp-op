"""Tests for charging optimizer and IRVE sizing (SOTREG M2)."""
from __future__ import annotations

import math

import pytest

from app.services.sotreg.charging_optimizer import (
    CHARGER_SPECS,
    ONEE_DEMAND_CHARGE_MAD_KVA,
    ONEE_TARIFF_MAD_KWH,
    compute_charging_schedule,
    compute_irve_costs,
    compute_irve_sizing,
)


# ---------------------------------------------------------------------------
# Charging schedule tests
# ---------------------------------------------------------------------------


class TestComputeChargingSchedule:
    """Verify SOC-based charging optimization with ONEE tariffs."""

    def test_basic_charging_schedule(self) -> None:
        """Basic schedule from 20% to 62% SOC."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=20.0,
            target_soc_pct=62.0,
            charger_power_kw=50.0,
        )
        assert result["target_soc_pct"] == 62.0
        # Energy needed: (62 - 20) / 100 * 60 = 25.2 kWh
        assert abs(result["energy_needed_kwh"] - 25.2) < 0.1
        assert result["charging_duration_hours"] > 0
        assert result["currency"] == "MAD"
        assert result["total_energy_cost_mad"] > 0

    def test_qin_2016_soc_62_default(self) -> None:
        """Default target is SOC=62% (Qin 2016 optimal)."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=30.0,
        )
        assert result["target_soc_pct"] == 62.0

    def test_no_charging_needed(self) -> None:
        """Already at target SOC — no energy needed."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=62.0,
            target_soc_pct=62.0,
        )
        assert result["energy_needed_kwh"] == 0.0
        assert result["total_energy_cost_mad"] == 0.0

    def test_above_target_soc(self) -> None:
        """Current SOC above target — no charging needed."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=80.0,
            target_soc_pct=62.0,
        )
        assert result["energy_needed_kwh"] == 0.0

    def test_onee_tariff_structure(self) -> None:
        """Verify ONEE tariff values are correct."""
        assert float(ONEE_TARIFF_MAD_KWH["pointe"]) == 1.58
        assert float(ONEE_TARIFF_MAD_KWH["pleine"]) == 1.22
        assert float(ONEE_TARIFF_MAD_KWH["creuse"]) == 0.82

    def test_peak_demand_charge(self) -> None:
        """Monthly demand charge based on peak power."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=20.0,
            target_soc_pct=62.0,
            charger_power_kw=50.0,
        )
        expected = 50.0 * float(ONEE_DEMAND_CHARGE_MAD_KVA)
        assert abs(result["monthly_demand_charge_mad"] - expected) < 1.0
        assert result["peak_demand_kw"] == 50.0

    def test_schedule_has_windows(self) -> None:
        """Schedule should contain at least one charging window."""
        result = compute_charging_schedule(
            battery_capacity_kwh=60.0,
            current_soc_pct=10.0,
            target_soc_pct=62.0,
            charger_power_kw=50.0,
        )
        assert len(result["schedule"]) > 0
        for window in result["schedule"]:
            assert "window_name" in window
            assert "duration_hours" in window
            assert "energy_kwh" in window
            assert "cost_mad" in window

    def test_invalid_battery_capacity_raises(self) -> None:
        with pytest.raises(ValueError, match="must be positive"):
            compute_charging_schedule(battery_capacity_kwh=-10.0, current_soc_pct=20.0)

    def test_invalid_soc_raises(self) -> None:
        with pytest.raises(ValueError, match="between 0 and 100"):
            compute_charging_schedule(battery_capacity_kwh=60.0, current_soc_pct=150.0)


# ---------------------------------------------------------------------------
# IRVE sizing tests
# ---------------------------------------------------------------------------


class TestComputeIRVESizing:
    """Verify IRVE infrastructure sizing calculations."""

    def test_basic_sizing(self) -> None:
        """Basic sizing for 10 vehicles."""
        result = compute_irve_sizing(
            fleet_size=10,
            daily_km_per_vehicle=150.0,
            battery_capacity_kwh=60.0,
        )
        assert result["charger_count"] >= 1
        assert result["charger_type"] == "dc_50kw"
        assert result["total_installed_power_kw"] > 0
        assert result["total_capex_mad"] > 0
        assert result["currency"] == "MAD"

    def test_single_vehicle_fleet(self) -> None:
        """Edge case: single vehicle fleet needs at least 1 charger."""
        result = compute_irve_sizing(
            fleet_size=1,
            daily_km_per_vehicle=100.0,
            battery_capacity_kwh=60.0,
        )
        assert result["charger_count"] >= 1

    def test_larger_fleet_more_chargers(self) -> None:
        """Larger fleet should require more chargers."""
        small = compute_irve_sizing(fleet_size=5, daily_km_per_vehicle=150.0, battery_capacity_kwh=60.0)
        large = compute_irve_sizing(fleet_size=50, daily_km_per_vehicle=150.0, battery_capacity_kwh=60.0)
        assert large["charger_count"] > small["charger_count"]

    def test_ac_charger_type(self) -> None:
        """AC charger should work with lower power."""
        result = compute_irve_sizing(
            fleet_size=5,
            daily_km_per_vehicle=80.0,
            battery_capacity_kwh=60.0,
            preferred_charger_type="ac_22kw",
        )
        assert result["charger_type"] == "ac_22kw"
        assert result["power_per_charger_kw"] == 22.0

    def test_cost_breakdown(self) -> None:
        """Cost breakdown should include all components."""
        result = compute_irve_sizing(
            fleet_size=10,
            daily_km_per_vehicle=150.0,
            battery_capacity_kwh=60.0,
        )
        assert result["hardware_cost_mad"] > 0
        assert result["installation_cost_mad"] > 0
        assert result["grid_connection_cost_mad"] > 0
        total = (
            result["hardware_cost_mad"]
            + result["installation_cost_mad"]
            + result["transformer_cost_mad"]
            + result["grid_connection_cost_mad"]
        )
        assert abs(result["total_capex_mad"] - total) < 1.0

    def test_transformer_cost_above_100kw(self) -> None:
        """Transformer required when total power > 100 kW."""
        result = compute_irve_sizing(
            fleet_size=20,
            daily_km_per_vehicle=200.0,
            battery_capacity_kwh=60.0,
            preferred_charger_type="dc_50kw",
        )
        if result["total_installed_power_kw"] > 100:
            assert result["transformer_cost_mad"] == 150000.0

    def test_daily_energy_calculation(self) -> None:
        """Daily energy = daily_km * consumption_per_km * fleet_size."""
        result = compute_irve_sizing(
            fleet_size=10,
            daily_km_per_vehicle=100.0,
            battery_capacity_kwh=60.0,
            energy_consumption_kwh_per_km=0.25,
        )
        expected_per_vehicle = 100.0 * 0.25
        assert abs(result["daily_energy_per_vehicle_kwh"] - expected_per_vehicle) < 0.1
        expected_total = expected_per_vehicle * 10
        assert abs(result["daily_energy_demand_kwh"] - expected_total) < 1.0

    def test_charger_specs(self) -> None:
        """Verify charger spec constants are correct."""
        assert CHARGER_SPECS["ac_7kw"]["power_kw"] == 7
        assert CHARGER_SPECS["ac_22kw"]["power_kw"] == 22
        assert CHARGER_SPECS["dc_50kw"]["power_kw"] == 50
        assert CHARGER_SPECS["dc_150kw"]["power_kw"] == 150


# ---------------------------------------------------------------------------
# IRVE cost calculator tests
# ---------------------------------------------------------------------------


class TestComputeIRVECosts:
    """Verify IRVE cost calculator with TCO projections."""

    def test_basic_cost_calculation(self) -> None:
        """Basic cost for 3 DC 50kW chargers."""
        result = compute_irve_costs(
            charger_count=3,
            charger_type="dc_50kw",
            annual_energy_kwh=100000.0,
        )
        assert result["hardware_cost"] > 0
        assert result["installation_cost"] > 0
        assert result["annual_electricity_cost"] > 0
        assert result["total_capex"] > 0
        assert result["currency"] == "MAD"

    def test_5_year_tco(self) -> None:
        """5-year TCO should equal CAPEX + 5 * annual OPEX."""
        result = compute_irve_costs(
            charger_count=2,
            charger_type="dc_50kw",
            annual_energy_kwh=50000.0,
        )
        expected_5y = result["total_capex"] + 5 * result["annual_opex"]
        assert abs(result["5_year_tco"] - expected_5y) < 1.0

    def test_10_year_tco(self) -> None:
        """10-year TCO should equal CAPEX + 10 * annual OPEX."""
        result = compute_irve_costs(
            charger_count=2,
            charger_type="dc_50kw",
            annual_energy_kwh=50000.0,
        )
        expected_10y = result["total_capex"] + 10 * result["annual_opex"]
        assert abs(result["10_year_tco"] - expected_10y) < 1.0

    def test_zero_energy_no_electricity_cost(self) -> None:
        """Zero energy usage → zero electricity cost."""
        result = compute_irve_costs(
            charger_count=1,
            charger_type="ac_7kw",
            annual_energy_kwh=0.0,
        )
        assert result["annual_electricity_cost"] == 0.0
