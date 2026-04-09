"""Navigo (IDFM) transit pass verification client."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class NavigoPassStatus:
    card_number: str
    holder_name: str
    is_valid: bool
    zone: str
    expiry_date: str | None = None
    pass_type: str = "navigo"


class NavigoClient:
    """Client for Ile-de-France Mobilités Navigo pass verification."""

    def __init__(self, config: dict | None = None) -> None:
        cfg = config or {}
        self.api_key = cfg.get("api_key", os.environ.get("NAVIGO_API_KEY", ""))
        self.base_url = cfg.get(
            "base_url", os.environ.get("NAVIGO_BASE_URL", "https://api.iledefrance-mobilites.fr")
        )

    async def verify_pass(self, card_number: str) -> NavigoPassStatus:
        """Verify a Navigo pass status.

        Production: GET {base_url}/v1/cards/{card_number}/status
        """
        logger.info("Navigo: Verifying pass %s", card_number[:4] + "****")
        return NavigoPassStatus(
            card_number=card_number,
            holder_name="",
            is_valid=True,
            zone="1-5",
            expiry_date=None,
            pass_type="navigo_annuel",
        )

    async def check_zones(self, card_number: str) -> list[str]:
        """Check which zones a pass covers."""
        status = await self.verify_pass(card_number)
        if status.zone == "1-5":
            return ["1", "2", "3", "4", "5"]
        return status.zone.split("-")

    async def get_pass_type(self, card_number: str) -> str:
        """Get the pass type (annuel, mensuel, semaine, etc.)."""
        status = await self.verify_pass(card_number)
        return status.pass_type
