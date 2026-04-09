"""Tests for Edenred Client (Session 86)."""
from __future__ import annotations

import pytest
from app.services.payment.edenred_client import EdenredClient


class TestEdenredClient:
    @pytest.mark.asyncio
    async def test_get_benefit(self):
        client = EdenredClient()
        benefit = await client.get_benefit("emp-123")
        assert benefit.employee_id == "emp-123"
        assert benefit.provider == "edenred"
        assert benefit.monthly_amount == 75.0
        assert benefit.is_active is True

    @pytest.mark.asyncio
    async def test_credit_benefit(self):
        client = EdenredClient()
        result = await client.credit_benefit("emp-123", 75.0, "Monthly transport")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_card(self):
        client = EdenredClient()
        result = await client.verify_card("4111111111111111")
        assert result is True
