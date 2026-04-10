"""Tests for phased electrification transition planner (SOTREG M6)."""
from __future__ import annotations
import pytest
from app.services.sotreg.transition_planner import (
    compute_plan_progress, generate_transition_plan, validate_plan_inputs,
)

class TestGenerateTransitionPlan:
    def test_moderate_plan_3_phases(self) -> None:
        result = generate_transition_plan(fleet_size=100, total_budget_mad=50000000.0)
        assert result["total_phases"] == 3
        assert len(result["phases"]) == 3
        assert result["scenario_type"] == "moderate"

    def test_aggressive_fewer_years(self) -> None:
        agg = generate_transition_plan(fleet_size=50, total_budget_mad=30000000.0, scenario_type="aggressive")
        con = generate_transition_plan(fleet_size=50, total_budget_mad=30000000.0, scenario_type="conservative")
        agg_span = agg["phases"][-1]["end_year"] - agg["phases"][0]["start_year"]
        con_span = con["phases"][-1]["end_year"] - con["phases"][0]["start_year"]
        assert agg_span <= con_span

    def test_budget_allocation_formula(self) -> None:
        result = generate_transition_plan(fleet_size=10, total_budget_mad=10000000.0,
                                          vehicle_unit_cost_mad=300000.0, irve_cost_per_vehicle_mad=90000.0)
        for phase in result["phases"]:
            expected = phase["vehicles_to_convert"] * (300000.0 + 90000.0)
            assert abs(phase["budget_allocated_mad"] - expected) < 1.0

    def test_phases_ordered_by_year(self) -> None:
        result = generate_transition_plan(fleet_size=50, total_budget_mad=30000000.0)
        for i in range(1, len(result["phases"])):
            assert result["phases"][i]["start_year"] >= result["phases"][i-1]["start_year"]

    def test_total_vehicles_equals_fleet(self) -> None:
        result = generate_transition_plan(fleet_size=100, total_budget_mad=50000000.0)
        total = sum(p["vehicles_to_convert"] for p in result["phases"])
        assert total == 100

    def test_milestones_generated(self) -> None:
        result = generate_transition_plan(fleet_size=50, total_budget_mad=25000000.0)
        assert len(result["milestones"]) >= 3

    def test_budget_surplus_calculated(self) -> None:
        result = generate_transition_plan(fleet_size=10, total_budget_mad=100000000.0)
        assert result["budget_surplus_or_deficit_mad"] > 0

    def test_single_vehicle_fleet(self) -> None:
        result = generate_transition_plan(fleet_size=1, total_budget_mad=500000.0)
        assert result["total_vehicles_converted"] == 1

    def test_currency_mad(self) -> None:
        result = generate_transition_plan(fleet_size=10, total_budget_mad=5000000.0)
        assert result.get("currency", "MAD") == "MAD"

class TestValidatePlanInputs:
    def test_valid_inputs(self) -> None:
        result = validate_plan_inputs(fleet_size=50, total_budget_mad=10000000.0,
                                       start_year=2026, scenario_type="moderate")
        assert result["valid"] is True

    def test_zero_fleet_invalid(self) -> None:
        result = validate_plan_inputs(fleet_size=0, total_budget_mad=10000000.0,
                                       start_year=2026, scenario_type="moderate")
        assert result["valid"] is False

    def test_zero_budget_invalid(self) -> None:
        result = validate_plan_inputs(fleet_size=50, total_budget_mad=0.0,
                                       start_year=2026, scenario_type="moderate")
        assert result["valid"] is False

    def test_invalid_scenario_type(self) -> None:
        result = validate_plan_inputs(fleet_size=50, total_budget_mad=10000000.0,
                                       start_year=2026, scenario_type="invalid")
        assert result["valid"] is False

class TestComputePlanProgress:
    def test_no_completed_phases(self) -> None:
        phases = [
            {"status": "planned", "budget_allocated_mad": 5000000, "start_year": 2026, "end_year": 2028, "name": "Pilot"},
            {"status": "planned", "budget_allocated_mad": 10000000, "start_year": 2028, "end_year": 2031, "name": "Scale"},
        ]
        result = compute_plan_progress(phases)
        assert result["pct_complete"] == 0.0
        assert result["phases_completed"] == 0

    def test_all_completed(self) -> None:
        phases = [
            {"status": "completed", "budget_allocated_mad": 5000000, "start_year": 2024, "end_year": 2025, "name": "Pilot"},
            {"status": "completed", "budget_allocated_mad": 10000000, "start_year": 2025, "end_year": 2026, "name": "Scale"},
        ]
        result = compute_plan_progress(phases, current_year=2027)
        assert result["phases_completed"] == 2
        assert result["phases_remaining"] == 0
