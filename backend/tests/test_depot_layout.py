"""Tests for depot layout planner (SOTREG M3)."""
from __future__ import annotations

import pytest

from app.services.sotreg.depot_layout import compute_depot_layout


class TestComputeDepotLayout:
    """Verify depot layout area calculations."""

    def test_basic_layout(self) -> None:
        """5 chargers, 10 vehicles should produce valid layout."""
        result = compute_depot_layout(charger_count=5, fleet_size=10)
        assert result["total_area_m2"] > 0
        assert result["charging_area_m2"] > 0
        assert result["parking_area_m2"] > 0
        assert result["charger_count"] == 5
        assert result["parking_bays"] == 10

    def test_parking_bays_match_fleet(self) -> None:
        """Parking bays should match fleet size."""
        result = compute_depot_layout(charger_count=3, fleet_size=20)
        assert result["parking_bays"] == 20

    def test_maintenance_area_minimum(self) -> None:
        """Maintenance area should meet minimum threshold."""
        result = compute_depot_layout(charger_count=2, fleet_size=5, include_maintenance=True)
        assert result["maintenance_area_m2"] >= 50.0  # MIN threshold

    def test_no_maintenance_area_when_disabled(self) -> None:
        """No maintenance area when include_maintenance=False."""
        result = compute_depot_layout(charger_count=2, fleet_size=5, include_maintenance=False)
        assert result["maintenance_area_m2"] == 0.0

    def test_charger_positions_count(self) -> None:
        """Should have one position per charger."""
        result = compute_depot_layout(charger_count=4, fleet_size=8)
        assert len(result["charger_positions"]) == 4

    def test_charger_positions_have_coordinates(self) -> None:
        """Each position should have x, y, width, depth."""
        result = compute_depot_layout(charger_count=3, fleet_size=6)
        for pos in result["charger_positions"]:
            assert "x" in pos
            assert "y" in pos
            assert "bay_width" in pos
            assert "bay_depth" in pos

    def test_zero_chargers(self) -> None:
        """Zero chargers → charging area is zero but parking still computed."""
        result = compute_depot_layout(charger_count=0, fleet_size=5)
        assert result["charging_area_m2"] == 0.0
        assert result["parking_area_m2"] > 0
        assert len(result["charger_positions"]) == 0

    def test_zero_fleet(self) -> None:
        """Zero fleet → no parking area."""
        result = compute_depot_layout(charger_count=3, fleet_size=0)
        assert result["parking_area_m2"] == 0.0
        assert result["charging_area_m2"] > 0

    def test_single_vehicle(self) -> None:
        """Single vehicle edge case."""
        result = compute_depot_layout(charger_count=1, fleet_size=1)
        assert result["total_area_m2"] > 0
        assert result["parking_bays"] == 1
        assert len(result["charger_positions"]) == 1

    def test_more_chargers_more_area(self) -> None:
        """More chargers → larger total area."""
        small = compute_depot_layout(charger_count=2, fleet_size=10)
        large = compute_depot_layout(charger_count=10, fleet_size=10)
        assert large["total_area_m2"] > small["total_area_m2"]

    def test_dimensions_present(self) -> None:
        """Should include estimated rectangular dimensions."""
        result = compute_depot_layout(charger_count=4, fleet_size=8)
        assert "dimensions" in result
        assert "width_m" in result["dimensions"] or "width" in result["dimensions"]

    def test_circulation_area_included(self) -> None:
        """Circulation area (driveways) should be non-zero for non-empty depot."""
        result = compute_depot_layout(charger_count=3, fleet_size=10)
        assert result["circulation_area_m2"] > 0
