"""Tests for Stripe Client (Session 86)."""
from __future__ import annotations

import pytest
from app.services.payment.stripe_client import StripeClient, StripeWebhookError


class TestStripeAuth:
    @pytest.mark.asyncio
    async def test_create_customer(self):
        client = StripeClient()
        customer = await client.create_customer("test@company.ma", "Test User")
        assert customer.email == "test@company.ma"
        assert customer.id.startswith("cus_")

    @pytest.mark.asyncio
    async def test_create_subscription(self):
        client = StripeClient()
        sub = await client.create_subscription("cus_123", "plan_transport")
        assert sub.status == "active"
        assert sub.customer_id == "cus_123"
        assert sub.current_period_end > sub.current_period_start

    @pytest.mark.asyncio
    async def test_cancel_subscription(self):
        client = StripeClient()
        sub = await client.cancel_subscription("sub_123")
        assert sub.status == "canceled"

    @pytest.mark.asyncio
    async def test_get_subscription(self):
        client = StripeClient()
        sub = await client.get_subscription("sub_123")
        assert sub.status == "active"


class TestStripeWebhook:
    @pytest.mark.asyncio
    async def test_payment_succeeded(self):
        client = StripeClient()
        result = await client.handle_webhook(
            "payment_intent.succeeded", {"amount": 15000}
        )
        assert result["status"] == "payment_confirmed"
        assert result["amount"] == 15000

    @pytest.mark.asyncio
    async def test_payment_failed(self):
        client = StripeClient()
        result = await client.handle_webhook(
            "payment_intent.payment_failed",
            {"last_payment_error": "card_declined"},
        )
        assert result["status"] == "payment_failed"

    @pytest.mark.asyncio
    async def test_subscription_updated(self):
        client = StripeClient()
        result = await client.handle_webhook(
            "customer.subscription.updated", {"id": "sub_123"}
        )
        assert result["status"] == "subscription_updated"

    @pytest.mark.asyncio
    async def test_subscription_deleted(self):
        client = StripeClient()
        result = await client.handle_webhook(
            "customer.subscription.deleted", {"id": "sub_456"}
        )
        assert result["status"] == "subscription_canceled"

    @pytest.mark.asyncio
    async def test_unhandled_event(self):
        client = StripeClient()
        result = await client.handle_webhook("charge.refunded", {})
        assert result["status"] == "unhandled"

    def test_verify_signature_no_secret_raises(self):
        client = StripeClient({"webhook_secret": ""})
        with pytest.raises(StripeWebhookError):
            client.verify_webhook_signature(b"payload", "sig", "ts")

    def test_verify_signature_with_secret(self):
        client = StripeClient({"webhook_secret": "whsec_test123"})
        # Valid HMAC check — signature won't match but method runs
        result = client.verify_webhook_signature(b"payload", "v1=invalid", "123")
        assert result is False
