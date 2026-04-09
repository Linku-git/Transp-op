"""SWVL API client."""
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


class SWVLClient(BaseOperatorClient):
    """SWVL API client for sizing plan transmission and data exchange."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.provider_name = "swvl"
        self.base_url = config.get("base_url", os.environ.get("SWVL_BASE_URL", ""))
        self.client_id = config.get("client_id", os.environ.get("SWVL_CLIENT_ID", ""))
        self.client_secret = config.get("client_secret", os.environ.get("SWVL_CLIENT_SECRET", ""))
        self._token: str | None = None
        self._token_expires: float = 0

    async def authenticate(self) -> bool:
        """Authenticate with SWVL API using OAuth.

        Production: POST {base_url}/api/v2/auth/token
        """
        logger.info("SWVL: Authenticating (client: %s)", self.client_id)
        self._token = f"swvl_token_{self.client_id}_{int(time.time())}"
        self._token_expires = time.time() + 3600
        self._authenticated = True
        return True

    async def send_sizing_plan(self, payload: SizingPlanPayload) -> OperatorResponse:
        """Transmit sizing plan to SWVL.

        Production: POST {base_url}/api/v2/corporate/plans
        """
        formatted = self.format_sizing_plan(payload)
        errors = self.validate_format(formatted)
        if errors:
            return OperatorResponse(success=False, message=f"Validation errors: {'; '.join(errors)}")

        if not self._authenticated:
            await self.authenticate()

        logger.info("SWVL: Sending sizing plan %s (v%d)", payload.plan_id, payload.version)
        return OperatorResponse(
            success=True,
            reference_id=f"swvl_ref_{payload.plan_id}",
            message="Plan received successfully",
        )

    async def get_schedules(self) -> list[dict]:
        """Fetch schedules from SWVL."""
        if not self._authenticated:
            await self.authenticate()
        return []

    async def get_capacity(self) -> dict:
        """Fetch capacity from SWVL."""
        if not self._authenticated:
            await self.authenticate()
        return {"available_buses": 0, "total_seats": 0}

    async def get_routes(self) -> list[dict]:
        """Fetch routes from SWVL.

        Production: GET {base_url}/api/v2/corporate/routes
        """
        if not self._authenticated:
            await self.authenticate()
        return []

    def format_sizing_plan(self, payload: SizingPlanPayload) -> dict:
        """Convert to SWVL corporate plan format."""
        return {
            "corporate_plan": {
                "plan_reference": payload.plan_id,
                "plan_version": payload.version,
                "fleet_requirements": [
                    {
                        "bus_type": v.get("type", "standard"),
                        "quantity": v.get("count", 0),
                        "seat_capacity": v.get("capacity", 0),
                        "wheelchair_accessible": v.get("pmr_accessible", False),
                    }
                    for v in payload.vehicles
                ],
                "routes": [
                    {
                        "route_name": r.get("name", ""),
                        "waypoints": r.get("stops", []),
                        "distance_km": r.get("distance_km", 0),
                    }
                    for r in payload.routes
                ],
                "timetable": payload.schedules,
                "ridership": {
                    "total_commuters": payload.passenger_counts.get("total", 0),
                    "by_campus": payload.passenger_counts.get("by_site", {}),
                },
                "accessibility": {
                    "wheelchair_users": payload.pmr_requirements.get("pmr_employees", 0),
                    "accessible_buses_needed": payload.pmr_requirements.get("pmr_vehicles_needed", 0),
                },
                "sla": {
                    "punctuality_target": payload.rti_targets.get("on_time_target_pct", 95),
                    "max_waiting_time_min": payload.rti_targets.get("max_wait_minutes", 10),
                    "real_time_tracking": payload.rti_targets.get("real_time_tracking", True),
                },
            }
        }

    def validate_format(self, data: dict) -> list[str]:
        """Validate SWVL format before sending."""
        errors: list[str] = []
        plan = data.get("corporate_plan", {})
        if not plan.get("plan_reference"):
            errors.append("Missing plan_reference")
        if not isinstance(plan.get("fleet_requirements"), list):
            errors.append("Missing or invalid fleet_requirements")
        return errors
