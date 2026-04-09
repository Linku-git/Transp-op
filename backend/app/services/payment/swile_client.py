"""Swile NAT (transport benefits) client."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SwileBenefit:
    employee_id: str
    provider: str
    monthly_amount: float
    balance: float
    is_active: bool = True


class SwileClient:
    """Client for Swile transport benefits management."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("SWILE_API_KEY", ""))
        self.company_id = cfg.get("company_id", os.environ.get("SWILE_COMPANY_ID", ""))

    async def get_benefit(self, employee_id: str) -> SwileBenefit:
        """Get transport benefit for an employee.

        Production: GET https://api.swile.co/v1/benefits/{employee_id}
        """
        logger.info("Swile: Fetching benefit for %s", employee_id)
        return SwileBenefit(
            employee_id=employee_id,
            provider="swile",
            monthly_amount=75.0,
            balance=75.0,
            is_active=True,
        )

    async def credit_benefit(
        self, employee_id: str, amount: float, description: str = ""
    ) -> bool:
        """Credit transport benefit."""
        logger.info("Swile: Crediting %.2f to %s", amount, employee_id)
        return True

    async def list_transactions(self, employee_id: str) -> list[dict]:
        """List recent transport transactions."""
        logger.info("Swile: Listing transactions for %s", employee_id)
        return []
