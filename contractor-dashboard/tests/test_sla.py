"""Tests for SLA Compliance page."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSLAOTPChart:
    """Test 5: SLA OTP data is correctly structured."""

    def test_sla_data_has_daily_entries(self) -> None:
        """SLA data contains 30 daily entries."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_sla(30)
        assert "daily_data" in data
        assert len(data["daily_data"]) == 30

    def test_sla_data_has_target(self) -> None:
        """SLA data includes target OTP of 95%."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_sla(30)
        assert data["target_otp"] == 95.0

    def test_otp_values_in_valid_range(self) -> None:
        """All OTP values are between 85 and 100."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_sla(30)
        for entry in data["daily_data"]:
            assert 85 <= entry["otp"] <= 100


class TestPenaltyCalculation:
    """Test 6: Penalty calculation follows 500 MAD per % below target."""

    def test_penalty_500_mad_per_point(self) -> None:
        """Penalty is 500 MAD for each percentage point below 95% target."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_sla(30)
        target = data["target_otp"]  # 95.0

        for entry in data["daily_data"]:
            if entry["otp"] < target:
                expected_penalty = round((target - entry["otp"]) * 500, 2)
                assert entry["penalty_mad"] == expected_penalty, (
                    f"Date {entry['date']}: OTP={entry['otp']}, "
                    f"expected penalty={expected_penalty}, got={entry['penalty_mad']}"
                )
            else:
                assert entry["penalty_mad"] == 0.0

    def test_total_penalty_is_sum(self) -> None:
        """Total penalty equals sum of daily penalties."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_sla(30)
        computed_total = round(
            sum(e["penalty_mad"] for e in data["daily_data"]), 2
        )
        assert data["total_penalty_mad"] == computed_total
