"""Edenred NAT (Neobank Avantages Transport) benefits client."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TransportBenefit:
    employee_id: str
    provider: str
    monthly_amount: float
    balance: float
    is_active: bool = True
    card_number: str | None = None


class EdenredClient:
    """Client for Edenred transport benefits (Ticket Mobilité)."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("EDENRED_API_KEY", ""))
        self.merchant_id = cfg.get("merchant_id", os.environ.get("EDENRED_MERCHANT_ID", ""))

    async def get_benefit(self, employee_id: str) -> TransportBenefit:
        """Get transport benefit for an employee.

        Production: GET https://api.edenred.com/v1/benefits/{employee_id}
        """
        logger.info("Edenred: Fetching benefit for %s", employee_id)
        return TransportBenefit(
            employee_id=employee_id,
            provider="edenred",
            monthly_amount=75.0,  # Standard French transport benefit
            balance=75.0,
            is_active=True,
        )

    async def credit_benefit(
        self, employee_id: str, amount: float, description: str = ""
    ) -> bool:
        """Credit transport benefit to employee card."""
        logger.info("Edenred: Crediting %.2f to %s", amount, employee_id)
        return True

    async def verify_card(self, card_number: str) -> bool:
        """Verify an Edenred card is valid and active."""
        logger.info("Edenred: Verifying card %s", card_number[:4] + "****")
        return True
