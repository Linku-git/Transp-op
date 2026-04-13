"""Tests for KPI page and app initialization."""
from __future__ import annotations

import json
import sys
import os

import pytest

# Ensure the contractor-dashboard root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAppInit:
    """Test 1: App server object exists and health check works."""

    def test_app_server_exists(self) -> None:
        """The Dash app exposes a Flask server object."""
        from app import server

        assert server is not None
        assert hasattr(server, "test_client")

    def test_health_check(self) -> None:
        """GET /health returns 200 with JSON status healthy."""
        from app import server

        client = server.test_client()
        resp = client.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "healthy"


class TestLoginPage:
    """Test 2: Login page renders correctly."""

    def test_login_layout_has_inputs(self) -> None:
        """Login layout contains email and password inputs."""
        from app import login_layout

        # Flatten the component tree and check for input IDs
        ids_found: set[str] = set()
        _collect_ids(login_layout, ids_found)
        assert "login-email" in ids_found
        assert "login-password" in ids_found
        assert "btn-login" in ids_found


class TestKPICards:
    """Test 3: KPI cards render with correct data."""

    def test_demo_kpi_data_structure(self) -> None:
        """Demo KPI data has all required fields."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_kpis("month")
        assert "trips_completed" in data
        assert "on_time_pct" in data
        assert "satisfaction" in data
        assert "utilization" in data
        assert data["period"] == "month"

        # Each KPI has value, previous, delta_pct
        for key in ["trips_completed", "on_time_pct", "satisfaction", "utilization"]:
            kpi = data[key]
            assert "value" in kpi
            assert "previous" in kpi
            assert "delta_pct" in kpi


class TestDeltaCalculation:
    """Test 4: Delta percentage calculation is correct."""

    def test_positive_delta(self) -> None:
        """Trips completed shows positive delta."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_kpis("month")
        trips = data["trips_completed"]
        # value=1247, previous=1189 -> delta should be positive
        assert trips["delta_pct"] > 0
        # Verify approximate delta: (1247-1189)/1189 * 100 ~ 4.9%
        expected = (trips["value"] - trips["previous"]) / trips["previous"] * 100
        assert abs(trips["delta_pct"] - expected) < 0.5

    def test_all_deltas_are_float(self) -> None:
        """All delta values are numeric."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_kpis("month")
        for key in ["trips_completed", "on_time_pct", "satisfaction", "utilization"]:
            assert isinstance(data[key]["delta_pct"], (int, float))


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _collect_ids(component: object, ids: set[str]) -> None:
    """Recursively collect component IDs from a Dash layout tree."""
    if hasattr(component, "id") and component.id:
        ids.add(component.id)
    if hasattr(component, "children"):
        children = component.children
        if isinstance(children, (list, tuple)):
            for child in children:
                _collect_ids(child, ids)
        elif children is not None:
            _collect_ids(children, ids)
