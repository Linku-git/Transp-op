"""Stripe payment integration for billing management."""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StripeCustomer:
    id: str
    email: str
    name: str
    metadata: dict | None = None


@dataclass
class StripeSubscription:
    id: str
    customer_id: str
    plan_id: str
    status: str
    current_period_start: int = 0
    current_period_end: int = 0


class StripeWebhookError(Exception):
    pass


class StripeClient:
    """Stripe API client for customer and subscription management."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("STRIPE_API_KEY", ""))
        self.webhook_secret = cfg.get(
            "webhook_secret", os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        )

    async def create_customer(
        self, email: str, name: str, metadata: dict | None = None
    ) -> StripeCustomer:
        """Create a Stripe customer.

        Production: POST https://api.stripe.com/v1/customers
        """
        logger.info("Stripe: Creating customer %s", email)
        return StripeCustomer(
            id=f"cus_{email.replace('@', '_').replace('.', '_')}",
            email=email, name=name, metadata=metadata,
        )

    async def create_subscription(
        self, customer_id: str, plan_id: str
    ) -> StripeSubscription:
        """Create a subscription.

        Production: POST https://api.stripe.com/v1/subscriptions
        """
        logger.info("Stripe: Creating subscription for %s (plan: %s)", customer_id, plan_id)
        now = int(time.time())
        return StripeSubscription(
            id=f"sub_{customer_id}_{plan_id}",
            customer_id=customer_id, plan_id=plan_id,
            status="active",
            current_period_start=now,
            current_period_end=now + 30 * 86400,
        )

    async def cancel_subscription(self, subscription_id: str) -> StripeSubscription:
        """Cancel a subscription."""
        logger.info("Stripe: Canceling subscription %s", subscription_id)
        return StripeSubscription(
            id=subscription_id, customer_id="", plan_id="", status="canceled",
        )

    async def get_subscription(self, subscription_id: str) -> StripeSubscription:
        """Get subscription details."""
        return StripeSubscription(
            id=subscription_id, customer_id="", plan_id="", status="active",
        )

    def verify_webhook_signature(
        self, payload: bytes, signature: str, timestamp: str
    ) -> bool:
        """Verify Stripe webhook signature (HMAC SHA256).

        Production uses stripe.Webhook.construct_event().
        """
        if not self.webhook_secret:
            raise StripeWebhookError("Webhook secret not configured")

        signed_payload = f"{timestamp}.{payload.decode()}"
        expected = hmac.new(
            self.webhook_secret.encode(),
            signed_payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        provided = signature.replace("v1=", "")
        return hmac.compare_digest(expected, provided)

    async def handle_webhook(self, event_type: str, data: dict) -> dict:
        """Process a Stripe webhook event."""
        logger.info("Stripe webhook: %s", event_type)

        if event_type == "payment_intent.succeeded":
            return {"status": "payment_confirmed", "amount": data.get("amount", 0)}
        elif event_type == "payment_intent.payment_failed":
            return {"status": "payment_failed", "error": data.get("last_payment_error", "")}
        elif event_type == "customer.subscription.updated":
            return {"status": "subscription_updated", "subscription_id": data.get("id", "")}
        elif event_type == "customer.subscription.deleted":
            return {"status": "subscription_canceled", "subscription_id": data.get("id", "")}

        return {"status": "unhandled", "event_type": event_type}
