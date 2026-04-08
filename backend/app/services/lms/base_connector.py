from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LMSCourse:
    """Standardized course representation from any LMS."""
    external_id: str
    title: str
    duration_minutes: int | None = None
    is_mandatory: bool = False
    certification_name: str | None = None
    metadata: dict | None = None


@dataclass
class LMSCompletion:
    """Standardized completion record for export to LMS."""
    external_id: str
    employee_external_id: str
    completed_at: str
    score: float | None = None
    time_spent_seconds: int | None = None


class BaseLMSConnector(ABC):
    """Abstract base class for LMS integrations."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.provider_name: str = "base"

    @abstractmethod
    async def fetch_catalog(self) -> list[LMSCourse]:
        """Import training catalog from the LMS."""

    @abstractmethod
    async def export_completion(self, completion: LMSCompletion) -> bool:
        """Export a single completion record to the LMS."""

    @abstractmethod
    async def handle_webhook(self, payload: dict) -> LMSCompletion | None:
        """Process a webhook event from the LMS."""

    async def test_connection(self) -> bool:
        """Test connectivity to the LMS API."""
        try:
            await self.fetch_catalog()
            return True
        except Exception as e:
            logger.warning("LMS connection test failed for %s: %s", self.provider_name, e)
            return False
