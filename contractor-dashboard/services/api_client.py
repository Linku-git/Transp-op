"""HTTP client for Transpop API with JWT auth and token refresh."""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

API_BASE: str = os.getenv("TRANSPOP_API_URL", "http://localhost:8000/api/v1")
TIMEOUT: int = 15


class TranspopClient:
    """Sync HTTP client with JWT bearer auth."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token
        self._client = httpx.Client(base_url=API_BASE, timeout=TIMEOUT)

    @property
    def headers(self) -> dict[str, str]:
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        """Send a GET request."""
        resp = self._client.get(path, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: dict | None = None) -> dict[str, Any]:
        """Send a POST request."""
        resp = self._client.post(path, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # High-level data methods (fall back to demo data when API is down)
    # ------------------------------------------------------------------ #

    def get_kpis(self, period: str = "month") -> dict[str, Any]:
        """Get KPI data -- falls back to demo data."""
        try:
            return self.get(f"/kpis/contractor?period={period}")
        except Exception:
            return self._demo_kpis(period)

    def get_sla_data(self, days: int = 30) -> dict[str, Any]:
        """Get SLA compliance data."""
        try:
            return self.get(f"/sotreg/operators/sla?days={days}")
        except Exception:
            return self._demo_sla(days)

    def get_financial_data(self, month: str | None = None) -> dict[str, Any]:
        """Get financial reconciliation data."""
        try:
            params = {"month": month} if month else {}
            return self.get("/sotreg/operators/financial", params=params)
        except Exception:
            return self._demo_financial()

    def get_fleet_status(self) -> dict[str, Any]:
        """Get fleet vehicle status."""
        try:
            return self.get("/sotreg/operators/fleet")
        except Exception:
            return self._demo_fleet()

    # ------------------------------------------------------------------ #
    # Demo data generators
    # ------------------------------------------------------------------ #

    @staticmethod
    def _demo_kpis(period: str) -> dict[str, Any]:
        """Generate demo KPI data."""
        return {
            "trips_completed": {"value": 1247, "previous": 1189, "delta_pct": 4.9},
            "on_time_pct": {"value": 94.2, "previous": 92.8, "delta_pct": 1.5},
            "satisfaction": {"value": 4.3, "previous": 4.1, "delta_pct": 4.9},
            "utilization": {"value": 87.5, "previous": 85.2, "delta_pct": 2.7},
            "period": period,
        }

    @staticmethod
    def _demo_sla(days: int) -> dict[str, Any]:
        """Generate demo SLA data."""
        import numpy as np

        rng = np.random.RandomState(42)
        dates = [f"2026-03-{14 + i:02d}" for i in range(min(days, 30))]
        otp_values: list[float] = (
            (92 + rng.normal(0, 2, len(dates))).clip(85, 100).tolist()
        )
        target: float = 95.0
        penalties: list[dict[str, Any]] = []
        for d, otp in zip(dates, otp_values):
            rounded_otp: float = round(otp, 1)
            if rounded_otp < target:
                penalty = round((target - rounded_otp) * 500, 2)  # 500 MAD per % below target
            else:
                penalty = 0.0
            penalties.append({"date": d, "otp": rounded_otp, "penalty_mad": penalty})
        return {
            "target_otp": target,
            "daily_data": penalties,
            "total_penalty_mad": round(
                sum(p["penalty_mad"] for p in penalties), 2
            ),
            "avg_otp": round(sum(otp_values) / len(otp_values), 1),
        }

    @staticmethod
    def _demo_financial() -> dict[str, Any]:
        """Generate demo financial data."""
        lignes: list[dict[str, Any]] = [
            {
                "ligne": "Ligne A1",
                "invoiced_trips": 320,
                "actual_trips": 315,
                "amount_mad": 192_000.00,
                "status": "paid",
            },
            {
                "ligne": "Ligne B2",
                "invoiced_trips": 280,
                "actual_trips": 280,
                "amount_mad": 168_000.00,
                "status": "paid",
            },
            {
                "ligne": "Ligne C3",
                "invoiced_trips": 250,
                "actual_trips": 247,
                "amount_mad": 148_200.00,
                "status": "pending",
            },
            {
                "ligne": "Ligne D4",
                "invoiced_trips": 200,
                "actual_trips": 205,
                "amount_mad": 123_000.00,
                "status": "disputed",
            },
            {
                "ligne": "Ligne E5",
                "invoiced_trips": 180,
                "actual_trips": 180,
                "amount_mad": 108_000.00,
                "status": "paid",
            },
        ]
        monthly: list[dict[str, Any]] = [
            {"month": "2026-01", "revenue_mad": 680_000},
            {"month": "2026-02", "revenue_mad": 710_000},
            {"month": "2026-03", "revenue_mad": 739_200},
            {"month": "2026-04", "revenue_mad": 695_000},
        ]
        return {
            "lignes": lignes,
            "monthly_revenue": monthly,
            "total_invoiced_mad": sum(lg["amount_mad"] for lg in lignes),
            "total_disputed_mad": sum(
                lg["amount_mad"] for lg in lignes if lg["status"] == "disputed"
            ),
        }

    @staticmethod
    def _demo_fleet() -> dict[str, Any]:
        """Generate demo fleet status."""
        vehicles: list[dict[str, Any]] = [
            {
                "id": "v1",
                "plate": "12345-A-78",
                "type": "Bus Standard",
                "status": "active",
                "lat": 33.5731,
                "lng": -7.5898,
                "fuel_pct": 72,
            },
            {
                "id": "v2",
                "plate": "23456-B-12",
                "type": "Bus Standard",
                "status": "active",
                "lat": 33.5950,
                "lng": -7.6187,
                "fuel_pct": 58,
            },
            {
                "id": "v3",
                "plate": "34567-C-34",
                "type": "Minibus",
                "status": "maintenance",
                "lat": 33.5500,
                "lng": -7.6300,
                "fuel_pct": 90,
            },
            {
                "id": "v4",
                "plate": "45678-D-56",
                "type": "Bus Standard",
                "status": "active",
                "lat": 33.6100,
                "lng": -7.5000,
                "fuel_pct": 45,
            },
            {
                "id": "v5",
                "plate": "56789-E-78",
                "type": "Bus Articule",
                "status": "idle",
                "lat": 33.5600,
                "lng": -7.5500,
                "fuel_pct": 100,
            },
            {
                "id": "v6",
                "plate": "67890-F-90",
                "type": "Minibus",
                "status": "active",
                "lat": 33.5800,
                "lng": -7.5700,
                "fuel_pct": 35,
            },
        ]
        maintenance: list[dict[str, Any]] = [
            {
                "vehicle": "34567-C-34",
                "type": "Vidange",
                "due_date": "2026-04-15",
                "severity": "medium",
            },
            {
                "vehicle": "56789-E-78",
                "type": "Pneus",
                "due_date": "2026-04-20",
                "severity": "low",
            },
            {
                "vehicle": "12345-A-78",
                "type": "Freins",
                "due_date": "2026-04-25",
                "severity": "high",
            },
        ]
        return {
            "vehicles": vehicles,
            "maintenance_schedule": maintenance,
            "summary": {"active": 4, "maintenance": 1, "idle": 1, "total": 6},
            "availability_by_type": {
                "Bus Standard": 75.0,
                "Minibus": 50.0,
                "Bus Articule": 0.0,
            },
        }
