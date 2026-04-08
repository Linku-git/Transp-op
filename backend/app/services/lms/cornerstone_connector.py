from __future__ import annotations

import logging
import os

from app.services.lms.base_connector import BaseLMSConnector, LMSCourse, LMSCompletion

logger = logging.getLogger(__name__)


class CornerstoneConnector(BaseLMSConnector):
    """Cornerstone OnDemand LMS connector."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.provider_name = "cornerstone"
        self.base_url = config.get(
            "base_url", os.environ.get("CORNERSTONE_BASE_URL", "")
        )
        self.api_key = config.get(
            "api_key", os.environ.get("CORNERSTONE_API_KEY", "")
        )

    async def fetch_catalog(self) -> list[LMSCourse]:
        """Fetch training catalog from Cornerstone API.

        In production, this would call:
        GET {base_url}/x/odata/api/views/vw_rpt_training
        """
        logger.info("Fetching catalog from Cornerstone: %s", self.base_url)

        # Stub: In production, use httpx/aiohttp to call Cornerstone OData API
        # For now, return empty catalog (connector framework is ready)
        return []

    async def export_completion(self, completion: LMSCompletion) -> bool:
        """Export completion to Cornerstone.

        In production, this would call:
        POST {base_url}/x/odata/api/user-learning
        """
        logger.info(
            "Exporting completion to Cornerstone: %s for %s",
            completion.external_id,
            completion.employee_external_id,
        )
        # Stub: ready for production integration
        return True

    async def handle_webhook(self, payload: dict) -> LMSCompletion | None:
        """Process Cornerstone webhook for completion events."""
        event_type = payload.get("event_type")
        if event_type != "completion":
            return None

        return LMSCompletion(
            external_id=payload.get("course_id", ""),
            employee_external_id=payload.get("user_id", ""),
            completed_at=payload.get("completed_at", ""),
            score=payload.get("score"),
            time_spent_seconds=payload.get("duration_seconds"),
        )
