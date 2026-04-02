from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.services.roi_calculator import (
    compute_roi_absenteeism,
    compute_roi_retention,
    compute_roi_fleet_optimization,
    compute_roi_journey_productivity,
    compute_payback_months,
    calculate_roi,
    WORKING_DAYS_PER_YEAR,
)
from tests.conftest import login_as_admin


# ---------------------------------------------------------------------------
# Unit tests — individual ROI levers
# ---------------------------------------------------------------------------


def test_roi_absenteeism_calculation() -> None:
    """Known inputs produce expected absenteeism ROI."""
    # (0.08 - 0.05) × 500 × 350 × 220 = 0.03 × 500 × 350 × 220 = 1,155,000
    result = compute_roi_absenteeism(
        baseline_absence_rate=Decimal("0.08"),
        target_absence_rate=Decimal("0.05"),
        headcount=500,
        daily_cost=Decimal("350"),
    )
    expected = Decimal("0.03") * 500 * Decimal("350") * WORKING_DAYS_PER_YEAR
    assert result == expected.quantize(Decimal("0.01"))
    assert float(result) == 1155000.00


def test_roi_retention_calculation() -> None:
    """Known inputs produce expected retention ROI."""
    # (0.15 - 0.10) × 500 × 25000 = 0.05 × 500 × 25000 = 625,000
    result = compute_roi_retention(
        turnover_rate_before=Decimal("0.15"),
        turnover_rate_after=Decimal("0.10"),
        headcount=500,
        replacement_cost=Decimal("25000"),
    )
    assert float(result) == 625000.00


def test_roi_fleet_optimization() -> None:
    """Fleet optimization lever calculates correctly."""
    result = compute_roi_fleet_optimization(
        current_fleet_annual_cost=Decimal("2000000"),
        optimized_fleet_annual_cost=Decimal("1500000"),
    )
    assert float(result) == 500000.00

    # No savings if optimized is more expensive
    result_no_savings = compute_roi_fleet_optimization(
        current_fleet_annual_cost=Decimal("1000000"),
        optimized_fleet_annual_cost=Decimal("1200000"),
    )
    assert float(result_no_savings) == 0.00


def test_roi_journey_productivity() -> None:
    """Journey productivity lever calculates correctly."""
    # 200 hours × 0.30 engagement × 45 cost × 500 headcount = 1,350,000
    result = compute_roi_journey_productivity(
        annual_travel_hours=Decimal("200"),
        engagement_rate=Decimal("0.30"),
        training_hour_cost=Decimal("45"),
        headcount=500,
    )
    assert float(result) == 1350000.00


def test_roi_total() -> None:
    """Total ROI equals sum of all 4 levers."""
    result = calculate_roi(
        headcount=500,
        daily_cost=Decimal("350"),
        baseline_absence_rate=Decimal("0.08"),
        target_absence_rate=Decimal("0.05"),
        replacement_cost=Decimal("25000"),
        turnover_rate_before=Decimal("0.15"),
        turnover_rate_after=Decimal("0.10"),
        annual_travel_hours=Decimal("200"),
        engagement_rate=Decimal("0.30"),
        training_hour_cost=Decimal("45"),
        total_investment=Decimal("3000000"),
        current_fleet_annual_cost=Decimal("2000000"),
        optimized_fleet_annual_cost=Decimal("1500000"),
    )
    expected_total = (
        result["roi_absenteeism"]
        + result["roi_retention"]
        + result["roi_fleet_optimization"]
        + result["roi_journey"]
    )
    assert abs(result["roi_total"] - expected_total) < 0.01


def test_payback_period() -> None:
    """Payback period in months calculated correctly."""
    # Investment 3,000,000 / Annual ROI 3,630,000 × 12 = ~9.9 months
    result = calculate_roi(
        headcount=500,
        daily_cost=Decimal("350"),
        baseline_absence_rate=Decimal("0.08"),
        target_absence_rate=Decimal("0.05"),
        replacement_cost=Decimal("25000"),
        turnover_rate_before=Decimal("0.15"),
        turnover_rate_after=Decimal("0.10"),
        annual_travel_hours=Decimal("200"),
        engagement_rate=Decimal("0.30"),
        training_hour_cost=Decimal("45"),
        total_investment=Decimal("3000000"),
        current_fleet_annual_cost=Decimal("2000000"),
        optimized_fleet_annual_cost=Decimal("1500000"),
    )
    assert result["payback_months"] is not None
    assert result["payback_months"] > 0
    # Payback = 3000000 / total_roi × 12
    expected_payback = 3000000 / result["roi_total"] * 12
    assert abs(result["payback_months"] - expected_payback) < 0.2


def test_roi_zero_investment() -> None:
    """Zero investment returns None payback and 0 ROI percentage."""
    result = calculate_roi(
        headcount=100,
        daily_cost=Decimal("300"),
        baseline_absence_rate=Decimal("0.06"),
        target_absence_rate=Decimal("0.04"),
        replacement_cost=Decimal("20000"),
        turnover_rate_before=Decimal("0.12"),
        turnover_rate_after=Decimal("0.08"),
        annual_travel_hours=Decimal("150"),
        engagement_rate=Decimal("0.25"),
        training_hour_cost=Decimal("40"),
        total_investment=Decimal("0"),
    )
    # ROI levers should still compute
    assert result["roi_total"] > 0
    # But payback is undefined with zero investment
    payback = compute_payback_months(Decimal("0"), Decimal(str(result["roi_total"])))
    # With zero investment, payback should be 0 months (instant)
    assert payback is not None
    assert float(payback) == 0.0
    # ROI percentage should be 0 (avoid division by zero)
    assert result["roi_percentage"] == 0.0


# ---------------------------------------------------------------------------
# Integration tests — API endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_roi_endpoint_response(client: AsyncClient) -> None:
    """POST /financial/roi/calculate returns valid response structure."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/financial/roi/calculate",
        headers=headers,
        json={
            "headcount": 500,
            "daily_cost": 350,
            "baseline_absence_rate": 0.08,
            "target_absence_rate": 0.05,
            "replacement_cost": 25000,
            "turnover_rate_before": 0.15,
            "turnover_rate_after": 0.10,
            "annual_travel_hours": 200,
            "engagement_rate": 0.30,
            "training_hour_cost": 45,
            "total_investment": 3000000,
            "current_fleet_annual_cost": 2000000,
            "optimized_fleet_annual_cost": 1500000,
        },
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    assert "roi_absenteeism" in data
    assert "roi_retention" in data
    assert "roi_fleet_optimization" in data
    assert "roi_journey" in data
    assert "roi_total" in data
    assert "roi_percentage" in data
    assert "payback_months" in data
    assert data["roi_total"] > 0
    assert data["payback_months"] > 0
    assert data["headcount"] == 500
    # No scenario_id provided, so stored_id should be null
    assert data["stored_id"] is None


@pytest.mark.asyncio
async def test_roi_stored_in_db(client: AsyncClient) -> None:
    """ROI results persisted in ROICalculation table when scenario_id provided."""
    token = await login_as_admin(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a financial scenario first
    scenario_resp = await client.post(
        "/api/v1/financial/scenarios",
        headers=headers,
        json={
            "name": "ROI Test Scenario",
            "investment_model": "capex",
            "duration_years": 5,
        },
    )
    assert scenario_resp.status_code == 201
    scenario_id = scenario_resp.json()["id"]

    # Calculate ROI with scenario_id to persist
    resp = await client.post(
        "/api/v1/financial/roi/calculate",
        headers=headers,
        json={
            "scenario_id": scenario_id,
            "headcount": 200,
            "daily_cost": 300,
            "baseline_absence_rate": 0.07,
            "target_absence_rate": 0.04,
            "replacement_cost": 20000,
            "turnover_rate_before": 0.12,
            "turnover_rate_after": 0.08,
            "annual_travel_hours": 180,
            "engagement_rate": 0.25,
            "training_hour_cost": 40,
            "total_investment": 1500000,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["stored_id"] is not None
    assert data["roi_total"] > 0
