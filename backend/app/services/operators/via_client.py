"""Via Transportation API client."""
from __future__ import annotations

import logging
import os
import time

from app.services.operators.base_operator_client import (
    BaseOperatorClient,
    SizingPlanPayload,
    OperatorResponse,
    OperatorAPIError,
)

logger = logging.getLogger(__name__)


class ViaClient(BaseOperatorClient):
    """Via Transportation API client for sizing plan transmission and data exchange."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.provider_name = "via"
        self.base_url = config.get("base_url", os.environ.get("VIA_BASE_URL", ""))
        self.api_key = config.get("api_key", os.environ.get("VIA_API_KEY", ""))
        self.org_id = config.get("org_id", os.environ.get("VIA_ORG_ID", ""))
        self._token: str | None = None
        self._token_expires: float = 0

    async def authenticate(self) -> bool:
        """Authenticate with Via API using API key.

        Production: POST {base_url}/v1/auth/token
        """
        logger.info("Via: Authenticating (org: %s)", self.org_id)
        self._token = f"via_token_{self.org_id}_{int(time.time())}"
        self._token_expires = time.time() + 3600
        self._authenticated = True
        return True

    async def send_sizing_plan(self, payload: SizingPlanPayload) -> OperatorResponse:
        """Transmit sizing plan to Via.

        Production: POST {base_url}/v1/service-plans
        """
        formatted = self.format_sizing_plan(payload)
        errors = self.validate_format(formatted)
        if errors:
            return OperatorResponse(success=False, message=f"Validation errors: {'; '.join(errors)}")

        if not self._authenticated:
            await self.authenticate()

        logger.info("Via: Sending sizing plan %s (v%d)", payload.plan_id, payload.version)
        # Stub: ready for production httpx
        return OperatorResponse(
            success=True,
            reference_id=f"via_ref_{payload.plan_id}",
            message="Sizing plan accepted",
        )

    async def get_schedules(self) -> list[dict]:
        """Fetch schedules from Via.

        Production: GET {base_url}/v1/schedules
        """
        if not self._authenticated:
            await self.authenticate()
        logger.info("Via: Fetching schedules")
        return []

    async def get_capacity(self) -> dict:
        """Fetch capacity from Via.

        Production: GET {base_url}/v1/capacity
        """
        if not self._authenticated:
            await self.authenticate()
        logger.info("Via: Fetching capacity")
        return {"available_vehicles": 0, "max_passengers": 0}

    async def get_routes(self) -> list[dict]:
        """Fetch routes from Via.

        Production: GET {base_url}/v1/routes
        """
        if not self._authenticated:
            await self.authenticate()
        return []

    def format_sizing_plan(self, payload: SizingPlanPayload) -> dict:
        """Convert to Via's service plan format."""
        return {
            "service_plan": {
                "external_id": payload.plan_id,
                "version": payload.version,
                "fleet": [
                    {
                        "vehicle_type": v.get("type", ""),
                        "count": v.get("count", 0),
                        "capacity": v.get("capacity", 0),
                        "pmr_accessible": v.get("pmr_accessible", False),
                    }
                    for v in payload.vehicles
                ],
                "service_routes": [
                    {
                        "name": r.get("name", ""),
                        "stops": r.get("stops", []),
                        "schedule_type": "fixed",
                    }
                    for r in payload.routes
                ],
                "schedules": payload.schedules,
                "demand": {
                    "total_riders": payload.passenger_counts.get("total", 0),
                    "by_zone": payload.passenger_counts.get("by_site", {}),
                },
                "accessibility": {
                    "pmr_riders": payload.pmr_requirements.get("pmr_employees", 0),
                    "pmr_vehicles": payload.pmr_requirements.get("pmr_vehicles_needed", 0),
                },
                "performance_targets": {
                    "on_time_pct": payload.rti_targets.get("on_time_target_pct", 95),
                    "max_wait_min": payload.rti_targets.get("max_wait_minutes", 10),
                },
            }
        }

    def validate_format(self, data: dict) -> list[str]:
        """Validate Via format before sending."""
        errors: list[str] = []
        plan = data.get("service_plan", {})
        if not plan.get("external_id"):
            errors.append("Missing external_id")
        if not isinstance(plan.get("fleet"), list):
            errors.append("Missing or invalid fleet")
        return errors
