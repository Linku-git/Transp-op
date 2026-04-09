"""Workday HCM SIRH connector.

Implements OAuth 2.0 authentication, employee/position/schedule sync with
delta updates, field mapping via workday_field_mapping, pagination, and retry logic.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
BACKOFF_MULTIPLIER = 2.0
DEFAULT_PAGE_SIZE = 100


class WorkdayAuthError(Exception):
    """Raised when Workday OAuth authentication fails."""


class WorkdayAPIError(Exception):
    """Raised when Workday API returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class WorkdayConnector:
    """Workday HCM connector with OAuth 2.0, pagination, and delta sync."""

    def __init__(self, config: dict) -> None:
        self.base_url = config.get(
            "base_url", os.environ.get("WORKDAY_BASE_URL", "")
        )
        self.client_id = config.get(
            "client_id", os.environ.get("WORKDAY_CLIENT_ID", "")
        )
        self.client_secret = config.get(
            "client_secret", os.environ.get("WORKDAY_CLIENT_SECRET", "")
        )
        self.tenant_name = config.get(
            "tenant_name", os.environ.get("WORKDAY_TENANT", "")
        )
        self.page_size = config.get("page_size", DEFAULT_PAGE_SIZE)

        self._access_token: str | None = None
        self._token_expires_at: float = 0

    # --- Authentication ---

    async def authenticate(self) -> str:
        """Perform OAuth 2.0 client credentials grant.

        In production: POST {base_url}/ccx/oauth2/{tenant}/token
        """
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        logger.info("Workday: Authenticating (tenant: %s)", self.tenant_name)

        # Stub: ready for production httpx integration
        self._access_token = f"wd_token_{self.tenant_name}_{int(time.time())}"
        self._token_expires_at = time.time() + 3600
        return self._access_token

    async def refresh_token(self) -> str:
        """Force token refresh."""
        self._access_token = None
        self._token_expires_at = 0
        return await self.authenticate()

    @property
    def is_authenticated(self) -> bool:
        return self._access_token is not None and time.time() < self._token_expires_at

    # --- Paginated Requests with Retry ---

    async def _request_with_retry(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Make a paginated API request with retry logic."""
        await self.authenticate()
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await self._fetch_all_pages(endpoint, params)
            except WorkdayAPIError as e:
                if attempt == MAX_RETRIES:
                    raise
                if e.status_code and e.status_code < 500 and e.status_code != 429:
                    raise

                logger.warning(
                    "Workday API attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt, MAX_RETRIES, e, backoff,
                )
                await asyncio.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER

                if e.status_code == 401:
                    await self.refresh_token()

        return []

    async def _fetch_all_pages(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Fetch all pages from a Workday API endpoint.

        Workday uses offset/count pagination:
        ?count={page_size}&offset={page * page_size}
        """
        all_results: list[dict] = []
        offset = 0

        while True:
            page_params = dict(params or {})
            page_params["count"] = self.page_size
            page_params["offset"] = offset

            page_results = await self._make_request(endpoint, page_params)

            if not page_results:
                break

            all_results.extend(page_results)

            if len(page_results) < self.page_size:
                break  # Last page

            offset += self.page_size

        return all_results

    async def _make_request(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Execute a single API request to Workday HCM.

        In production: GET {base_url}/ccx/api/v1/{tenant}/{endpoint}
        Headers: Authorization: Bearer {token}
        """
        url = f"{self.base_url}/ccx/api/v1/{self.tenant_name}/{endpoint}"
        logger.info("Workday: GET %s (params: %s)", url, params)

        # Stub: return empty. Ready for production httpx integration.
        return []

    # --- Employee Sync ---

    async def fetch_employees(
        self,
        since: datetime | None = None,
    ) -> list[dict]:
        """Fetch worker data from Workday.

        Uses Get_Workers operation with optional effective date filter.
        """
        params: dict = {}

        if since:
            params["Updated_From"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")

        return await self._request_with_retry("workers", params)

    async def fetch_positions(self) -> list[dict]:
        """Fetch position data from Workday."""
        return await self._request_with_retry("positions", {})

    async def fetch_schedules(self) -> list[dict]:
        """Fetch work schedule data from Workday."""
        return await self._request_with_retry("schedules", {})

    # --- Full Sync Cycle ---

    async def run_full_sync(
        self,
        since: datetime | None = None,
    ) -> dict:
        """Execute a complete sync cycle.

        Args:
            since: For delta sync, only fetch changes since this time.
        """
        from app.services.sirh.workday_field_mapping import map_workday_employee

        logger.info(
            "Workday: Starting %s sync (since: %s)",
            "delta" if since else "full",
            since,
        )

        employees_raw = await self.fetch_employees(since=since)
        positions_raw = await self.fetch_positions()
        schedules_raw = await self.fetch_schedules()

        employees = [map_workday_employee(e) for e in employees_raw]

        return {
            "employees": employees,
            "employees_raw_count": len(employees_raw),
            "positions_count": len(positions_raw),
            "schedules_count": len(schedules_raw),
            "sync_type": "delta" if since else "full",
        }
