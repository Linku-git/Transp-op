from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)


async def send_emergency_push(
    responder_user_ids: list[uuid.UUID],
    alert_id: uuid.UUID,
    alert_type: str,
    employee_name: str,
    lat: float,
    lng: float,
) -> int:
    """
    Send push notifications to all designated responders.
    In production, this would use Firebase Admin SDK to send FCM messages.
    Returns number of notifications sent.
    """
    for user_id in responder_user_ids:
        logger.info(
            f"Push notification sent to {user_id}: "
            f"Emergency alert {alert_id} ({alert_type}) "
            f"from {employee_name} at ({lat}, {lng})"
        )

    return len(responder_user_ids)


async def send_emergency_sms(
    phone_numbers: list[str],
    alert_type: str,
    employee_name: str,
    lat: float,
    lng: float,
) -> int:
    """
    Send SMS alerts to emergency contacts.
    In production, this would use Twilio or similar SMS gateway.
    """
    for phone in phone_numbers:
        logger.info(
            f"SMS sent to {phone}: Emergency {alert_type} "
            f"from {employee_name} at ({lat}, {lng})"
        )

    return len(phone_numbers)
