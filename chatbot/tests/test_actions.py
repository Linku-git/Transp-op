"""Custom action tests for Transpop chatbot -- Session 127.

Tests verify that the API client correctly queries endpoints
and returns formatted data for Rasa actions.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add chatbot directory to path for imports
chatbot_dir = Path(__file__).parent.parent
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

from actions.api_client import TranspopChatbotClient

logger = logging.getLogger(__name__)


class TestActionQueryFleetStatus:
    """Test fleet status action returns formatted summary."""

    def test_returns_fleet_summary_from_demo(self) -> None:
        """Fleet summary returns vehicle counts from demo fallback."""
        client = TranspopChatbotClient()
        # Will hit demo fallback since no real API is running
        data = client.get_fleet_summary()

        assert data is not None
        assert "total" in data
        assert "active" in data
        assert "maintenance" in data
        assert data["total"] > 0
        # Verify breakdown adds up
        assert (
            data["active"] + data["maintenance"] + data.get("inactive", 0)
            == data["total"]
        )


class TestActionQueryKPI:
    """Test KPI query action returns formatted response."""

    def test_returns_kpi_response_from_demo(self) -> None:
        """KPI dashboard returns performance metrics from demo fallback."""
        client = TranspopChatbotClient()
        # Will hit demo fallback since no real API is running
        data = client.get_kpi_dashboard()

        assert data is not None
        assert "otp" in data
        assert "fill_rate" in data
        assert "co2_saved_kg" in data
        assert data["otp"] > 0
        assert data["co2_saved_kg"] > 0
