from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.services.cost_analysis import (
    compute_cost_per_available_seat,
    compute_cost_per_occupied_seat,
    compute_annual_cost_per_employee,
    compute_breakeven_point,
    calculate_cost_analysis,
)
from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Unit tests — PRD example: 50-seat bus at 120,000 EUR/year
# ---------------------------------------------------------------------------


def test_cost_per_available_seat() -> None:
    """PRD example: 120K/year, 50-seat bus = 5.45 EUR per available seat."""
    # 120,000 / (50 × 220 × 2) = 120,000 / 22,000 = 5.45
    result = compute_cost_per_available_seat(
        annual_route_cost=Decimal("120000"),
        vehicle_capacity=50,
        working_days=220,
        trips_per_day=2,
    )
    assert float(result) == 5.45


def test_cost_per_occupied_seat() -> None:
    """At 80% fill rate: 5.45 / 0.80 = 6.82 EUR per occupied seat."""
    cost_available = Decimal("5.45")
    result = compute_cost_per_occupied_seat(
        cost_per_available_seat=cost_available,
        fill_rate=Decimal("0.80"),
    )
    assert float(result) == 6.81  # 5.45 / 0.80 = 6.8125 → rounds to 6.81


def test_annual_cost_per_employee() -> None:
    """Total cost divided by transported employees."""
    result = compute_annual_cost_per_employee(
        total_annual_cost=Decimal("120000"),
        transported_employees=40,
    )
    # 120,000 / 40 = 3,000
    assert float(result) == 3000.00


def test_breakeven_calculation() -> None:
    """Breakeven point matches expected N employees."""
    # Transport: 120,000/year
    # Allowance per employee: 15km × 0.25 EUR/km × 220 days × 2 trips = 1,650 EUR/year
    # Breakeven: 120,000 / 1,650 = 72.73 → ceil = 73
    breakeven = compute_breakeven_point(
        annual_transport_cost=Decimal("120000"),
        average_distance_km=Decimal("15"),
        kilometric_allowance_per_km=Decimal("0.25"),
        working_days=220,
        trips_per_day=2,
    )
    assert breakeven == 73


def test_breakeven_edge_cases() -> None:
    """Edge cases: zero fill rate, zero cost, single employee."""
    # Zero allowance rate → breakeven = 0
    breakeven_zero = compute_breakeven_point(
        annual_transport_cost=Decimal("120000"),
        average_distance_km=Decimal("15"),
        kilometric_allowance_per_km=Decimal("0"),
    )
    assert breakeven_zero == 0

    # Zero transport cost → breakeven = 0
    breakeven_free = compute_breakeven_point(
        annual_transport_cost=Decimal("0"),
        average_distance_km=Decimal("15"),
        kilometric_allowance_per_km=Decimal("0.25"),
    )
    assert breakeven_free == 0

    # Zero fill rate in occupied seat → returns 0
    result = compute_cost_per_occupied_seat(
        cost_per_available_seat=Decimal("5.45"),
        fill_rate=Decimal("0"),
    )
    assert float(result) == 0.0

    # Zero employees → returns 0
    result = compute_annual_cost_per_employee(
        total_annual_cost=Decimal("120000"),
        transported_employees=0,
    )
    assert float(result) == 0.0


# ---------------------------------------------------------------------------
# Integration test — API endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cost_analysis_endpoint(client: AsyncClient) -> None:
    """POST /financial/cost-analysis returns valid response structure."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/financial/cost-analysis",
        headers=headers,
        json={
            "annual_route_cost": 120000,
            "vehicle_capacity": 50,
            "fill_rate": 0.80,
            "transported_employees": 40,
            "average_distance_km": 15,
            "kilometric_allowance_per_km": 0.25,
            "working_days": 220,
            "trips_per_day": 2,
        },
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    assert data["cost_per_available_seat"] == 5.45
    assert data["annual_cost_per_employee"] == 3000.0
    assert data["breakeven_employees"] == 73
    assert data["vehicle_capacity"] == 50
    assert "breakeven_chart" in data
    assert len(data["breakeven_chart"]) > 0
    assert data["breakeven_chart"][0]["employees"] == 1
