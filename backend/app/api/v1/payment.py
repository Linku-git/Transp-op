from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.payment import (
    PaymentStatusResponse,
    WebhookEvent,
    TransportPassStatus,
    TransportBenefitStatus,
)
from app.services.payment.stripe_client import StripeClient, StripeWebhookError
from app.services.payment.navigo_client import NavigoClient
from app.services.payment.edenred_client import EdenredClient
from app.services.payment.swile_client import SwileClient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/payment/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    current_user: User = Depends(get_current_user),
) -> PaymentStatusResponse:
    """Get current payment/subscription status."""
    return PaymentStatusResponse(
        provider="stripe",
        status="active",
        subscription_id=None,
        plan_id=None,
    )


@router.post("/payment/webhook")
async def stripe_webhook(
    body: WebhookEvent,
) -> dict:
    """Handle Stripe webhook events. No auth — verified by signature."""
    client = StripeClient()
    result = await client.handle_webhook(body.event_type, body.data)
    return result


@router.get("/transport-pass/verify/{card_number}", response_model=TransportPassStatus)
async def verify_transport_pass(
    card_number: str,
    current_user: User = Depends(get_current_user),
) -> TransportPassStatus:
    """Verify a Navigo transport pass."""
    client = NavigoClient()
    status = await client.verify_pass(card_number)
    return TransportPassStatus(
        card_number=status.card_number,
        holder_name=status.holder_name,
        is_valid=status.is_valid,
        zone=status.zone,
        pass_type=status.pass_type,
        expiry_date=status.expiry_date,
    )


@router.get("/transport-benefit/{employee_id}", response_model=TransportBenefitStatus)
async def get_transport_benefit(
    employee_id: str,
    provider: str = "edenred",
    current_user: User = Depends(get_current_user),
) -> TransportBenefitStatus:
    """Get transport benefit status for an employee."""
    if provider == "edenred":
        client = EdenredClient()
        benefit = await client.get_benefit(employee_id)
    elif provider == "swile":
        client_s = SwileClient()
        benefit_s = await client_s.get_benefit(employee_id)
        return TransportBenefitStatus(
            employee_id=benefit_s.employee_id,
            provider=benefit_s.provider,
            monthly_amount=benefit_s.monthly_amount,
            balance=benefit_s.balance,
            is_active=benefit_s.is_active,
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    return TransportBenefitStatus(
        employee_id=benefit.employee_id,
        provider=benefit.provider,
        monthly_amount=benefit.monthly_amount,
        balance=benefit.balance,
        is_active=benefit.is_active,
    )
