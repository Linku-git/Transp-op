"""Tests for Swile Client (Session 86)."""
from __future__ import annotations

import pytest
from app.services.payment.swile_client import SwileClient


class TestSwileClient:
    @pytest.mark.asyncio
    async def test_get_benefit(self):
        client = SwileClient()
        benefit = await client.get_benefit("emp-456")
        assert benefit.employee_id == "emp-456"
        assert benefit.provider == "swile"
        assert benefit.monthly_amount == 75.0
        assert benefit.is_active is True

    @pytest.mark.asyncio
    async def test_credit_benefit(self):
        client = SwileClient()
        result = await client.credit_benefit("emp-456", 75.0)
        assert result is True

    @pytest.mark.asyncio
    async def test_list_transactions(self):
        client = SwileClient()
        transactions = await client.list_transactions("emp-456")
        assert isinstance(transactions, list)
