"""JWT authentication service for contractor dashboard."""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

API_BASE: str = os.getenv("TRANSPOP_API_URL", "http://localhost:8000/api/v1")


def authenticate(email: str, password: str) -> dict | None:
    """Authenticate against Transpop API and return token + user info."""
    try:
        resp = httpx.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "token": data.get("access_token", ""),
                "user": data.get("user", {}),
            }
        return None
    except Exception as e:
        logger.error("Auth failed: %s", e)
        return None


def validate_token(token: str) -> bool:
    """Validate JWT token against API."""
    try:
        resp = httpx.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False
