"""Tests for Supernetwork equilibrium (SOTREG M5)."""
from __future__ import annotations

import pytest

from app.services.sotreg.supernetwork_equilibrium import (
    compute_supernetwork_equilibrium,
)


class TestSupernetworkEquilibrium:
    """Verify Frank-Wolfe network equilibrium."""

    def test_simple_two_link_network(self) -> None:
        """Two parallel links between same OD pair."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 10.0, "capacity": 100.0},
            {"from_node": 0, "to_node": 1, "free_flow_cost": 15.0, "capacity": 200.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 150.0}]
        result = compute_supernetwork_equilibrium(links, demands)
        assert result["converged"] is True
        assert result["total_system_cost"] > 0
        assert len(result["link_flows"]) == 2

    def test_flows_satisfy_demand(self) -> None:
        """Sum of flows on parallel links should equal demand."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 10.0, "capacity": 100.0},
            {"from_node": 0, "to_node": 1, "free_flow_cost": 12.0, "capacity": 100.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 80.0}]
        result = compute_supernetwork_equilibrium(links, demands)
        total_flow = sum(f["flow"] for f in result["link_flows"])
        assert abs(total_flow - 80.0) < 1.0

    def test_convergence_within_limit(self) -> None:
        """Should converge within max_iterations."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 10.0, "capacity": 50.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 30.0}]
        result = compute_supernetwork_equilibrium(links, demands, max_iterations=100)
        assert result["iterations"] <= 100

    def test_zero_demand(self) -> None:
        """Zero demand → zero flows."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 10.0, "capacity": 100.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 0.0}]
        result = compute_supernetwork_equilibrium(links, demands)
        for f in result["link_flows"]:
            assert f["flow"] == 0.0

    def test_single_link(self) -> None:
        """Single link: all demand on that link."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 5.0, "capacity": 200.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 100.0}]
        result = compute_supernetwork_equilibrium(links, demands)
        assert abs(result["link_flows"][0]["flow"] - 100.0) < 1.0

    def test_gap_reported(self) -> None:
        """Relative gap should be reported."""
        links = [
            {"from_node": 0, "to_node": 1, "free_flow_cost": 10.0, "capacity": 100.0},
        ]
        demands = [{"origin": 0, "destination": 1, "demand": 50.0}]
        result = compute_supernetwork_equilibrium(links, demands)
        assert "gap" in result
        assert result["gap"] >= 0
