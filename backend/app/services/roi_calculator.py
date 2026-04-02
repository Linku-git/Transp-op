from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

# Working days per year (French standard)
WORKING_DAYS_PER_YEAR = 220


def _q(value: Decimal) -> Decimal:
    """Round to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q1(value: Decimal) -> Decimal:
    """Round to 1 decimal place (for payback months)."""
    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Individual ROI levers
# ---------------------------------------------------------------------------


def compute_roi_absenteeism(
    baseline_absence_rate: Decimal,
    target_absence_rate: Decimal,
    headcount: int,
    daily_cost: Decimal,
) -> Decimal:
    """
    ROI from absenteeism reduction.

    Formula: (baseline_rate - target_rate) × headcount × daily_cost × working_days
    """
    rate_reduction = baseline_absence_rate - target_absence_rate
    if rate_reduction <= 0:
        return Decimal("0")
    return _q(rate_reduction * headcount * daily_cost * WORKING_DAYS_PER_YEAR)


def compute_roi_retention(
    turnover_rate_before: Decimal,
    turnover_rate_after: Decimal,
    headcount: int,
    replacement_cost: Decimal,
) -> Decimal:
    """
    ROI from reduced employee turnover.

    Formula: (turnover_before - turnover_after) × headcount × replacement_cost
    """
    turnover_reduction = turnover_rate_before - turnover_rate_after
    if turnover_reduction <= 0:
        return Decimal("0")
    return _q(turnover_reduction * headcount * replacement_cost)


def compute_roi_fleet_optimization(
    current_fleet_annual_cost: Decimal,
    optimized_fleet_annual_cost: Decimal,
) -> Decimal:
    """
    ROI from fleet cost savings via optimized routing and fill rates.

    Formula: current_cost - optimized_cost
    """
    savings = current_fleet_annual_cost - optimized_fleet_annual_cost
    return _q(max(savings, Decimal("0")))


def compute_roi_journey_productivity(
    annual_travel_hours: Decimal,
    engagement_rate: Decimal,
    training_hour_cost: Decimal,
    headcount: int,
) -> Decimal:
    """
    ROI from productive hours gained during transport.

    Formula: annual_travel_hours × engagement_rate × training_hour_cost × headcount
    """
    return _q(annual_travel_hours * engagement_rate * training_hour_cost * headcount)


def compute_payback_months(
    total_investment: Decimal,
    annual_roi_total: Decimal,
) -> Decimal | None:
    """
    Payback period in months.

    Formula: (total_investment / annual_roi_total) × 12
    Returns None if annual ROI is zero or negative.
    """
    if annual_roi_total <= 0:
        return None
    return _q1((total_investment / annual_roi_total) * 12)


# ---------------------------------------------------------------------------
# Full ROI calculation
# ---------------------------------------------------------------------------


def calculate_roi(
    headcount: int,
    daily_cost: Decimal,
    baseline_absence_rate: Decimal,
    target_absence_rate: Decimal,
    replacement_cost: Decimal,
    turnover_rate_before: Decimal,
    turnover_rate_after: Decimal,
    annual_travel_hours: Decimal,
    engagement_rate: Decimal,
    training_hour_cost: Decimal,
    total_investment: Decimal,
    current_fleet_annual_cost: Decimal = Decimal("0"),
    optimized_fleet_annual_cost: Decimal = Decimal("0"),
) -> dict:
    """
    Compute all 4 ROI levers, total ROI, ROI percentage, and payback period.

    Returns a dict with all computed values.
    """
    roi_absenteeism = compute_roi_absenteeism(
        baseline_absence_rate=baseline_absence_rate,
        target_absence_rate=target_absence_rate,
        headcount=headcount,
        daily_cost=daily_cost,
    )

    roi_retention = compute_roi_retention(
        turnover_rate_before=turnover_rate_before,
        turnover_rate_after=turnover_rate_after,
        headcount=headcount,
        replacement_cost=replacement_cost,
    )

    roi_fleet = compute_roi_fleet_optimization(
        current_fleet_annual_cost=current_fleet_annual_cost,
        optimized_fleet_annual_cost=optimized_fleet_annual_cost,
    )

    roi_journey = compute_roi_journey_productivity(
        annual_travel_hours=annual_travel_hours,
        engagement_rate=engagement_rate,
        training_hour_cost=training_hour_cost,
        headcount=headcount,
    )

    roi_total = _q(roi_absenteeism + roi_retention + roi_fleet + roi_journey)

    payback = compute_payback_months(total_investment, roi_total)

    roi_percentage = (
        _q((roi_total / total_investment) * 100)
        if total_investment > 0
        else Decimal("0")
    )

    return {
        "roi_absenteeism": float(roi_absenteeism),
        "roi_retention": float(roi_retention),
        "roi_fleet_optimization": float(roi_fleet),
        "roi_journey": float(roi_journey),
        "roi_total": float(roi_total),
        "roi_percentage": float(roi_percentage),
        "payback_months": float(payback) if payback is not None else None,
        "total_investment": float(total_investment),
        "headcount": headcount,
        "working_days_per_year": WORKING_DAYS_PER_YEAR,
    }
