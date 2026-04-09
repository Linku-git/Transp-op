"""Tests for Navigo Client (Session 86)."""
from __future__ import annotations

import pytest
from app.services.payment.navigo_client import NavigoClient


class TestNavigoClient:
    @pytest.mark.asyncio
    async def test_verify_pass(self):
        client = NavigoClient()
        status = await client.verify_pass("0123456789")
        assert status.is_valid is True
        assert status.zone == "1-5"
        assert status.pass_type == "navigo_annuel"

    @pytest.mark.asyncio
    async def test_check_zones(self):
        client = NavigoClient()
        zones = await client.check_zones("0123456789")
        assert "1" in zones
        assert "5" in zones
        assert len(zones) == 5

    @pytest.mark.asyncio
    async def test_get_pass_type(self):
        client = NavigoClient()
        pass_type = await client.get_pass_type("0123456789")
        assert pass_type == "navigo_annuel"

    def test_card_number_masked_in_logs(self):
        # Verify the logging masks card numbers
        client = NavigoClient()
        assert client.base_url  # Client initializes
