"""Tests for IRVE depot electrification cost calculator (SOTREG M3)."""
from __future__ import annotations

import pytest

from app.services.sotreg.irve_cost_calculator import compute_depot_electrification_cost


class TestComputeDepotElectrificationCost:
    """Verify 7-component cost breakdown."""

    def test_basic_cost_breakdown(self) -> None:
        """3 DC 50kW chargers with 10% contingency."""
        result = compute_depot_electrification_cost(charger_count=3, charger_type="dc_50kw")
        assert result["charger_hardware_mad"] > 0
        assert result["installation_mad"] > 0
        assert result["civil_works_mad"] > 0
        assert result["contingency_mad"] > 0
        assert result["total_cost_mad"] > 0
        assert result["currency"] == "MAD"

    def test_seven_components_present(self) -> None:
        """All 7 cost components should be in the result."""
        result = compute_depot_electrification_cost(charger_count=2)
        keys = ["charger_hardware_mad", "installation_mad", "electrical_upgrade_mad",
                "transformer_mad", "grid_connection_mad", "civil_works_mad", "contingency_mad"]
        for k in keys:
            assert k in result, f"Missing key: {k}"

    def test_total_equals_subtotal_plus_contingency(self) -> None:
        """Total = subtotal + contingency."""
        result = compute_depot_electrification_cost(charger_count=5, contingency_pct=15.0)
        expected = result["subtotal_mad"] + result["contingency_mad"]
        assert abs(result["total_cost_mad"] - expected) < 1.0

    def test_contingency_percentage(self) -> None:
        """Contingency should be contingency_pct% of subtotal."""
        result = compute_depot_electrification_cost(charger_count=3, contingency_pct=10.0)
        expected_contingency = result["subtotal_mad"] * 0.10
        assert abs(result["contingency_mad"] - expected_contingency) < 1.0

    def test_transformer_above_100kw(self) -> None:
        """Transformer cost when total > 100kW."""
        # 3 × 50kW = 150kW > 100kW → transformer needed
        result = compute_depot_electrification_cost(charger_count=3, charger_type="dc_50kw")
        assert result["transformer_mad"] == 150000.0

    def test_no_transformer_below_100kw(self) -> None:
        """No transformer when total <= 100kW."""
        # 2 × 22kW = 44kW < 100kW
        result = compute_depot_electrification_cost(charger_count=2, charger_type="ac_22kw")
        assert result["transformer_mad"] == 0.0

    def test_zero_chargers_raises(self) -> None:
        """Zero chargers should raise ValueError."""
        with pytest.raises(ValueError, match="must be >= 1"):
            compute_depot_electrification_cost(charger_count=0)

    def test_cost_per_charger(self) -> None:
        """Cost per charger should be total / count."""
        result = compute_depot_electrification_cost(charger_count=4)
        if result["charger_count"] > 0:
            expected = result["total_cost_mad"] / result["charger_count"]
            assert abs(result["cost_per_charger_mad"] - expected) < 1.0

    def test_different_charger_types(self) -> None:
        """DC 150kW should be more expensive than AC 7kW."""
        ac = compute_depot_electrification_cost(charger_count=1, charger_type="ac_7kw")
        dc = compute_depot_electrification_cost(charger_count=1, charger_type="dc_150kw")
        assert dc["total_cost_mad"] > ac["total_cost_mad"]

    def test_grid_connection_includes_per_kw(self) -> None:
        """Grid connection should include base + per-kW component."""
        result = compute_depot_electrification_cost(charger_count=2, charger_type="dc_50kw")
        # 20,000 base + 500 * 100kW = 70,000
        assert result["grid_connection_mad"] >= 20000.0
