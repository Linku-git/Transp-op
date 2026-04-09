from __future__ import annotations
from pydantic import BaseModel


class PaymentStatusResponse(BaseModel):
    provider: str
    status: str
    subscription_id: str | None = None
    plan_id: str | None = None


class WebhookEvent(BaseModel):
    event_type: str
    data: dict


class TransportPassStatus(BaseModel):
    card_number: str
    holder_name: str
    is_valid: bool
    zone: str
    pass_type: str
    expiry_date: str | None = None


class TransportBenefitStatus(BaseModel):
    employee_id: str
    provider: str
    monthly_amount: float
    balance: float
    is_active: bool
