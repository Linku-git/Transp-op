from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Active location sharing sessions
_active_sessions: dict[str, dict] = {}


def start_location_sharing(
    alert_id: uuid.UUID,
    employee_id: uuid.UUID,
    lat: float,
    lng: float,
) -> dict:
    """Start real-time location sharing for an emergency alert."""
    session_key = str(alert_id)
    _active_sessions[session_key] = {
        "alert_id": str(alert_id),
        "employee_id": str(employee_id),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_lat": lat,
        "last_lng": lng,
        "is_active": True,
    }
    logger.info(f"Location sharing started for alert {alert_id}")
    return _active_sessions[session_key]


def update_location(
    alert_id: uuid.UUID,
    lat: float,
    lng: float,
) -> bool:
    """Update shared location for an active emergency session."""
    session_key = str(alert_id)
    if session_key not in _active_sessions:
        return False
    if not _active_sessions[session_key]["is_active"]:
        return False

    _active_sessions[session_key]["last_lat"] = lat
    _active_sessions[session_key]["last_lng"] = lng
    return True


def stop_location_sharing(alert_id: uuid.UUID) -> bool:
    """Stop location sharing when emergency is resolved."""
    session_key = str(alert_id)
    if session_key in _active_sessions:
        _active_sessions[session_key]["is_active"] = False
        logger.info(f"Location sharing stopped for alert {alert_id}")
        return True
    return False


def get_active_sessions() -> list[dict]:
    """Get all active location sharing sessions."""
    return [s for s in _active_sessions.values() if s["is_active"]]


def is_sharing_active(alert_id: uuid.UUID) -> bool:
    """Check if location sharing is active for an alert."""
    session_key = str(alert_id)
    return session_key in _active_sessions and _active_sessions[session_key]["is_active"]
