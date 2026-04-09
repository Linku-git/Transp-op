"""SAP SuccessFactors SIRH connector.

Implements OAuth 2.0 authentication, employee data sync with delta updates,
field mapping via sap_field_mapping, and retry logic with exponential backoff.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
BACKOFF_MULTIPLIER = 2.0


class SAPAuthError(Exception):
    """Raised when SAP OAuth authentication fails."""


class SAPAPIError(Exception):
    """Raised when SAP API returns an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SAPConnector:
    """SAP SuccessFactors connector with OAuth 2.0 and delta sync."""

    def __init__(self, config: dict) -> None:
        self.base_url = config.get(
            "base_url", os.environ.get("SAP_SF_BASE_URL", "")
        )
        self.client_id = config.get(
            "client_id", os.environ.get("SAP_SF_CLIENT_ID", "")
        )
        self.client_secret = config.get(
            "client_secret", os.environ.get("SAP_SF_CLIENT_SECRET", "")
        )
        self.company_id = config.get(
            "company_id", os.environ.get("SAP_SF_COMPANY_ID", "")
        )

        self._access_token: str | None = None
        self._token_expires_at: float = 0

    # --- Authentication ---

    async def authenticate(self) -> str:
        """Perform OAuth 2.0 client credentials grant to obtain access token.

        In production, this would POST to:
        {base_url}/oauth/token with client_id, client_secret, grant_type=client_credentials

        Returns:
            Access token string.
        """
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        logger.info("SAP: Authenticating with OAuth 2.0 (company: %s)", self.company_id)

        # Production: httpx.AsyncClient POST to SAP OAuth endpoint
        # For now, simulate token acquisition
        self._access_token = f"sap_token_{self.company_id}_{int(time.time())}"
        self._token_expires_at = time.time() + 3600  # 1 hour
        return self._access_token

    async def refresh_token(self) -> str:
        """Force token refresh."""
        self._access_token = None
        self._token_expires_at = 0
        return await self.authenticate()

    @property
    def is_authenticated(self) -> bool:
        return self._access_token is not None and time.time() < self._token_expires_at

    # --- Data Fetching with Retry ---

    async def _request_with_retry(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Make an API request with retry logic and exponential backoff.

        Args:
            endpoint: SAP OData API endpoint path
            params: Query parameters

        Returns:
            List of records from SAP response.
        """
        await self.authenticate()
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await self._make_request(endpoint, params)
                return result
            except SAPAPIError as e:
                if attempt == MAX_RETRIES:
                    raise
                if e.status_code and e.status_code < 500 and e.status_code != 429:
                    raise  # Don't retry client errors (except rate limits)

                logger.warning(
                    "SAP API attempt %d/%d failed: %s. Retrying in %.1fs",
                    attempt, MAX_RETRIES, e, backoff,
                )
                await asyncio.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER

                # Refresh token on 401
                if e.status_code == 401:
                    await self.refresh_token()

        return []

    async def _make_request(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Execute a single API request to SAP SuccessFactors.

        In production, this would use httpx.AsyncClient:
        GET {base_url}/odata/v2/{endpoint}?$filter=...&$select=...
        Headers: Authorization: Bearer {token}, Accept: application/json
        """
        url = f"{self.base_url}/odata/v2/{endpoint}"
        logger.info("SAP: GET %s (params: %s)", url, params)

        # Stub: return empty results. Ready for production httpx integration.
        return []

    # --- Employee Sync ---

    async def fetch_employees(
        self,
        since: datetime | None = None,
    ) -> list[dict]:
        """Fetch employee data from SAP SuccessFactors.

        Args:
            since: Only fetch records modified after this timestamp (delta sync).

        Returns:
            List of employee records in SAP format.
        """
        params: dict = {
            "$select": "userId,firstName,lastName,email,department,phoneNumber,"
            "division,customString1,jobTitle,hireDate,lastModifiedDateTime",
        }

        if since:
            sap_date = since.strftime("%Y-%m-%dT%H:%M:%SZ")
            params["$filter"] = f"lastModifiedDateTime ge datetime'{sap_date}'"

        return await self._request_with_retry("PerPerson", params)

    async def fetch_sites(self) -> list[dict]:
        """Fetch company/location data from SAP."""
        params = {"$select": "locationCode,locationName,city,addressLine1,country"}
        return await self._request_with_retry("FOLocation", params)

    async def fetch_departments(self) -> list[dict]:
        """Fetch department data from SAP."""
        params = {"$select": "externalCode,name,description"}
        return await self._request_with_retry("FODepartment", params)

    # --- Full Sync Cycle ---

    async def run_full_sync(
        self,
        since: datetime | None = None,
    ) -> dict:
        """Execute a complete sync cycle.

        Args:
            since: For delta sync, only fetch changes since this time.

        Returns:
            Summary with employees, sites, departments fetched.
        """
        from app.services.sirh.sap_field_mapping import map_sap_employee

        logger.info(
            "SAP: Starting %s sync (since: %s)",
            "delta" if since else "full",
            since,
        )

        employees_raw = await self.fetch_employees(since=since)
        sites_raw = await self.fetch_sites()
        departments_raw = await self.fetch_departments()

        # Map to Transpop format
        employees = [map_sap_employee(e) for e in employees_raw]

        return {
            "employees": employees,
            "employees_raw_count": len(employees_raw),
            "sites_count": len(sites_raw),
            "departments_count": len(departments_raw),
            "sync_type": "delta" if since else "full",
        }
