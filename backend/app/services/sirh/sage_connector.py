"""Sage HR SIRH connector with API Key auth and rate limiting."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RATE_LIMIT_PER_HOUR = 500
INITIAL_BACKOFF = 1.0
BACKOFF_MULTIPLIER = 2.0


class SageAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SageConnector:
    """Sage HR connector with API Key authentication and rate limiting."""

    def __init__(self, config: dict) -> None:
        self.base_url = config.get(
            "base_url", os.environ.get("SAGE_BASE_URL", "")
        )
        self.api_key = config.get(
            "api_key", os.environ.get("SAGE_API_KEY", "")
        )
        self.rate_limit = config.get("rate_limit", RATE_LIMIT_PER_HOUR)
        self._request_count = 0
        self._window_start = time.time()

    @property
    def is_authenticated(self) -> bool:
        return bool(self.api_key)

    async def _check_rate_limit(self) -> None:
        now = time.time()
        if now - self._window_start >= 3600:
            self._request_count = 0
            self._window_start = now

        if self._request_count >= self.rate_limit:
            wait_time = 3600 - (now - self._window_start)
            logger.warning("Sage: Rate limit reached. Waiting %.0fs", wait_time)
            await asyncio.sleep(min(wait_time, 60))
            self._request_count = 0
            self._window_start = time.time()

        self._request_count += 1

    async def _request_with_retry(
        self, endpoint: str, params: dict | None = None
    ) -> list[dict]:
        backoff = INITIAL_BACKOFF
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                await self._check_rate_limit()
                return await self._make_request(endpoint, params)
            except SageAPIError as e:
                if attempt == MAX_RETRIES:
                    raise
                if e.status_code and e.status_code < 500 and e.status_code != 429:
                    raise
                logger.warning(
                    "Sage attempt %d/%d failed: %s", attempt, MAX_RETRIES, e
                )
                await asyncio.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER
        return []

    async def _make_request(
        self, endpoint: str, params: dict | None = None
    ) -> list[dict]:
        """Execute API request. In production: httpx with X-API-Key header."""
        url = f"{self.base_url}/api/{endpoint}"
        logger.info("Sage: GET %s (params: %s)", url, params)
        return []

    async def fetch_employees(self, since: datetime | None = None) -> list[dict]:
        params: dict = {}
        if since:
            params["date_modification_min"] = since.strftime("%d/%m/%Y")
        return await self._request_with_retry("salaries", params)

    async def fetch_payroll(self, period: str | None = None) -> list[dict]:
        params: dict = {}
        if period:
            params["periode"] = period
        return await self._request_with_retry("bulletins-paie", params)

    async def run_full_sync(self, since: datetime | None = None) -> dict:
        from app.services.sirh.sage_field_mapping import map_sage_employee

        employees_raw = await self.fetch_employees(since=since)
        payroll_raw = await self.fetch_payroll()
        employees = [map_sage_employee(e) for e in employees_raw]

        return {
            "employees": employees,
            "employees_raw_count": len(employees_raw),
            "payroll_count": len(payroll_raw),
            "sync_type": "delta" if since else "full",
        }
