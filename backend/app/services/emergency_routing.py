from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def determine_responders(
    alert_type: str,
    site_id: uuid.UUID | None = None,
) -> list[dict]:
    """
    Determine which responders should be notified based on alert type.
    In production, this would query the site's security contacts from the DB.
    """
    responders = []

    # Always notify site security
    responders.append({
        "role": "site_security",
        "site_id": str(site_id) if site_id else None,
        "notified_at": datetime.now(timezone.utc).isoformat(),
        "channel": "push",
    })

    # Always notify admin
    responders.append({
        "role": "admin",
        "notified_at": datetime.now(timezone.utc).isoformat(),
        "channel": "push",
    })

    # Medical alerts additionally notify medical services
    if alert_type == "medical":
        responders.append({
            "role": "medical_service",
            "notified_at": datetime.now(timezone.utc).isoformat(),
            "channel": "sms",
        })

    # Panic alerts notify emergency services
    if alert_type == "panic":
        responders.append({
            "role": "emergency_services",
            "notified_at": datetime.now(timezone.utc).isoformat(),
            "channel": "sms",
        })

    logger.info(
        f"Alert routing: {alert_type} → {len(responders)} responders "
        f"(site={site_id})"
    )

    return responders
