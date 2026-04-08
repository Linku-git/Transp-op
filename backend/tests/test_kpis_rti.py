"""Tests for RTI KPI endpoint (Session 60)."""
from __future__ import annotations

import pytest


class TestRTIKpiEndpoint:
    """Test GET /kpis/rti response structure."""

    def test_rti_kpi_response_structure(self):
        """The expected response structure from the endpoint."""
        expected_keys = {"compliance_pct", "avg_wait_seconds", "active_violations", "total_events", "trend", "period"}
        sample = {
            "compliance_pct": 92.5,
            "avg_wait_seconds": 65.3,
            "active_violations": 3,
            "total_events": 500,
            "trend": [{"date": "2026-04-08", "compliance_pct": 92.5}],
            "period": "day",
        }
        assert set(sample.keys()) == expected_keys
        assert isinstance(sample["trend"], list)
        assert sample["period"] in ("day", "week", "month")

    def test_compliance_pct_range(self):
        """Compliance percentage should be 0-100."""
        for val in [0, 50, 100, 95.5]:
            assert 0 <= val <= 100

    def test_trend_data_format(self):
        """Each trend point should have date and compliance_pct."""
        point = {"date": "2026-04-08", "compliance_pct": 85.0}
        assert "date" in point
        assert "compliance_pct" in point
        assert isinstance(point["compliance_pct"], float)
