from __future__ import annotations

import logging
import os

from app.services.lms.base_connector import BaseLMSConnector, LMSCourse, LMSCompletion

logger = logging.getLogger(__name__)


class Learning360Connector(BaseLMSConnector):
    """360Learning LMS connector."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.provider_name = "360learning"
        self.api_key = config.get(
            "api_key", os.environ.get("LEARNING360_API_KEY", "")
        )

    async def fetch_catalog(self) -> list[LMSCourse]:
        """Fetch training catalog from 360Learning API.

        In production, this would call:
        GET https://app.360learning.com/api/v1/programs
        """
        logger.info("Fetching catalog from 360Learning")
        return []

    async def export_completion(self, completion: LMSCompletion) -> bool:
        """Export completion to 360Learning.

        In production, this would call:
        POST https://app.360learning.com/api/v1/completions
        """
        logger.info(
            "Exporting completion to 360Learning: %s",
            completion.external_id,
        )
        return True

    async def handle_webhook(self, payload: dict) -> LMSCompletion | None:
        """Process 360Learning webhook."""
        event_type = payload.get("event_type")
        if event_type != "completion":
            return None

        return LMSCompletion(
            external_id=payload.get("program_id", ""),
            employee_external_id=payload.get("learner_id", ""),
            completed_at=payload.get("completed_at", ""),
            score=payload.get("score"),
        )
