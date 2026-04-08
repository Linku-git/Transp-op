from __future__ import annotations

import logging
import os

from app.services.lms.base_connector import BaseLMSConnector, LMSCourse, LMSCompletion

logger = logging.getLogger(__name__)


class TalentLMSConnector(BaseLMSConnector):
    """TalentLMS connector."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.provider_name = "talentlms"
        self.domain = config.get(
            "domain", os.environ.get("TALENTLMS_DOMAIN", "")
        )
        self.api_key = config.get(
            "api_key", os.environ.get("TALENTLMS_API_KEY", "")
        )

    async def fetch_catalog(self) -> list[LMSCourse]:
        """Fetch training catalog from TalentLMS API.

        In production, this would call:
        GET https://{domain}.talentlms.com/api/v1/courses
        """
        logger.info("Fetching catalog from TalentLMS: %s", self.domain)
        return []

    async def export_completion(self, completion: LMSCompletion) -> bool:
        """Export completion to TalentLMS.

        In production, this would call:
        POST https://{domain}.talentlms.com/api/v1/goToCourse
        """
        logger.info(
            "Exporting completion to TalentLMS: %s",
            completion.external_id,
        )
        return True

    async def handle_webhook(self, payload: dict) -> LMSCompletion | None:
        """Process TalentLMS webhook."""
        event_type = payload.get("event_type")
        if event_type != "completion":
            return None

        return LMSCompletion(
            external_id=payload.get("course_id", ""),
            employee_external_id=payload.get("user_id", ""),
            completed_at=payload.get("completed_at", ""),
            score=payload.get("score"),
        )
