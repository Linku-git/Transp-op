"""Tests for API client, fleet, health check, and MAD formatting."""
from __future__ import annotations

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestFleetMap:
    """Test 9: Fleet data for map rendering."""

    def test_fleet_vehicles_have_coordinates(self) -> None:
        """All vehicles have lat/lng for map rendering."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_fleet()
        for v in data["vehicles"]:
            assert "lat" in v and "lng" in v
            assert 30 <= v["lat"] <= 36  # Morocco latitude range
            assert -10 <= v["lng"] <= -5  # Morocco longitude range

    def test_fleet_summary_totals(self) -> None:
        """Fleet summary counts match actual vehicle list."""
        from services.api_client import TranspopClient

        data = TranspopClient._demo_fleet()
        summary = data["summary"]
        vehicles = data["vehicles"]

        assert summary["total"] == len(vehicles)
        active_count = sum(1 for v in vehicles if v["status"] == "active")
        assert summary["active"] == active_count


class TestTokenRefresh:
    """Test 10: Token validation handles errors gracefully."""

    def test_validate_token_returns_false_on_error(self) -> None:
        """validate_token returns False when API is unreachable."""
        from services.auth import validate_token

        # With no server running, validation should return False
        result = validate_token("fake-token-12345")
        assert result is False

    def test_authenticate_returns_none_on_error(self) -> None:
        """authenticate returns None when API is unreachable."""
        from services.auth import authenticate

        result = authenticate("test@example.com", "password123")
        assert result is None


class TestHealthCheck:
    """Test 11: Health check endpoint."""

    def test_health_returns_json(self) -> None:
        """Health endpoint returns valid JSON with status field."""
        from app import server

        client = server.test_client()
        resp = client.get("/health")
        data = json.loads(resp.data)
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_content_type(self) -> None:
        """Health endpoint returns application/json content type."""
        from app import server

        client = server.test_client()
        resp = client.get("/health")
        assert resp.content_type == "application/json"


class TestMADFormatting:
    """Test 12: MAD currency formatting."""

    def test_format_mad_basic(self) -> None:
        """Format a simple amount to MAD."""
        from components.kpi_card import format_mad

        assert format_mad(15000.00) == "15,000.00 MAD"

    def test_format_mad_large(self) -> None:
        """Format a large amount with thousands separators."""
        from components.kpi_card import format_mad

        assert format_mad(1234567.89) == "1,234,567.89 MAD"

    def test_format_mad_zero(self) -> None:
        """Format zero MAD."""
        from components.kpi_card import format_mad

        assert format_mad(0) == "0.00 MAD"

    def test_format_mad_negative(self) -> None:
        """Format negative amount."""
        from components.kpi_card import format_mad

        assert format_mad(-500.50) == "-500.50 MAD"
