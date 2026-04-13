"""Transpop API client for Rasa chatbot custom actions.

Provides methods to query the Transpop backend API for fleet status,
trip information, KPIs, maintenance alerts, and driver schedules.
All methods return dict or None on failure with graceful fallback to demo data.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class TranspopChatbotClient:
    """HTTP client for Transpop backend API queries."""

    def __init__(self) -> None:
        self.base_url: str = os.getenv("TRANSPOP_API_URL", "http://backend:8000/api/v1")
        self.token: str = os.getenv("TRANSPOP_JWT_TOKEN", "")
        self.timeout: float = 10.0

    def _headers(self) -> dict[str, str]:
        """Return authorization headers for API requests."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _demo_fleet_summary(self) -> dict[str, Any]:
        """Return demo fleet data when API is unreachable."""
        return {
            "total": 106,
            "active": 89,
            "maintenance": 12,
            "inactive": 5,
            "electric": 24,
            "diesel": 82,
        }

    def _demo_kpi_dashboard(self) -> dict[str, Any]:
        """Return demo KPI data when API is unreachable."""
        return {
            "otp": 87.3,
            "fill_rate": 72.5,
            "co2_saved_kg": 4520.0,
            "total_trips": 312,
            "avg_delay_min": 3.2,
        }

    def _demo_maintenance_alerts(self) -> dict[str, Any]:
        """Return demo maintenance data when API is unreachable."""
        return {
            "total_alerts": 8,
            "critical": 2,
            "warning": 4,
            "info": 2,
            "alerts": [
                {"vehicle": "BUS-042", "type": "critical", "message": "Freinage: usure plaquettes >90%"},
                {"vehicle": "BUS-017", "type": "warning", "message": "Vidange: 500km restants"},
            ],
        }

    def _demo_trip_info(self, ligne_id: str) -> dict[str, Any]:
        """Return demo trip data when API is unreachable."""
        return {
            "ligne_id": ligne_id,
            "name": f"Ligne {ligne_id}",
            "status": "active",
            "next_departure": "08:30",
            "stops": 12,
            "duration_min": 45,
        }

    def _demo_schedule(self) -> dict[str, Any]:
        """Return demo schedule data when API is unreachable."""
        return {
            "driver": "Conducteur",
            "shifts": [
                {"date": "demain", "start": "06:00", "end": "14:00", "ligne": "Ligne 5"},
                {"date": "apres-demain", "start": "14:00", "end": "22:00", "ligne": "Ligne 3"},
            ],
        }

    def get_fleet_summary(self) -> Optional[dict[str, Any]]:
        """Fetch fleet summary from Transpop API.

        Tries GET /api/v1/vehicles/fleet-summary first.
        Falls back to demo data if API is unreachable.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/vehicles/fleet-summary",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Fleet summary fetched successfully")
                    return data
                logger.warning(
                    "Fleet summary API returned status %d", response.status_code
                )
        except httpx.HTTPError as exc:
            logger.warning("Fleet summary API unreachable: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error fetching fleet summary: %s", exc)

        logger.info("Using demo fleet data as fallback")
        return self._demo_fleet_summary()

    def get_trip_info(self, ligne_id: str) -> Optional[dict[str, Any]]:
        """Fetch trip information for a specific ligne.

        Tries GET /api/v1/sotreg/lignes/{ligne_id}.
        Falls back to demo data if API is unreachable.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/sotreg/lignes/{ligne_id}",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Trip info fetched for ligne %s", ligne_id)
                    return data
                logger.warning(
                    "Trip info API returned status %d for ligne %s",
                    response.status_code,
                    ligne_id,
                )
        except httpx.HTTPError as exc:
            logger.warning("Trip info API unreachable: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error fetching trip info: %s", exc)

        logger.info("Using demo trip data for ligne %s as fallback", ligne_id)
        return self._demo_trip_info(ligne_id)

    def get_kpi_dashboard(self) -> Optional[dict[str, Any]]:
        """Fetch KPI dashboard data.

        Tries GET /api/v1/kpis/operations first.
        Falls back to demo data if API is unreachable.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/kpis/operations",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info("KPI dashboard fetched successfully")
                    return data
                logger.warning(
                    "KPI dashboard API returned status %d", response.status_code
                )
        except httpx.HTTPError as exc:
            logger.warning("KPI dashboard API unreachable: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error fetching KPI dashboard: %s", exc)

        logger.info("Using demo KPI data as fallback")
        return self._demo_kpi_dashboard()

    def get_maintenance_alerts(self) -> Optional[dict[str, Any]]:
        """Fetch active maintenance alerts.

        Tries GET /api/v1/sotreg/telemetry/alerts.
        Falls back to demo data if API is unreachable.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/sotreg/telemetry/alerts",
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Maintenance alerts fetched successfully")
                    return data
                logger.warning(
                    "Maintenance alerts API returned status %d", response.status_code
                )
        except httpx.HTTPError as exc:
            logger.warning("Maintenance alerts API unreachable: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error fetching maintenance alerts: %s", exc)

        logger.info("Using demo maintenance data as fallback")
        return self._demo_maintenance_alerts()

    def get_driver_schedule(self, driver_id: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Fetch driver schedule.

        Tries GET /api/v1/trips/upcoming for current user schedule.
        Falls back to demo data if API is unreachable.
        """
        try:
            url = f"{self.base_url}/trips/upcoming"
            if driver_id:
                url = f"{url}?driver_id={driver_id}"

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._headers())
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Driver schedule fetched successfully")
                    return data
                logger.warning(
                    "Driver schedule API returned status %d", response.status_code
                )
        except httpx.HTTPError as exc:
            logger.warning("Driver schedule API unreachable: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error fetching driver schedule: %s", exc)

        logger.info("Using demo schedule data as fallback")
        return self._demo_schedule()
