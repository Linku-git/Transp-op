from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import get_current_user
from app.models.auth import User
from app.schemas.valorization import (
    ValorizationConfig,
    ValorizationMetrics,
    ValorizationKPI,
)
from app.services.valorization_engine import (
    calculate_valorization,
    get_valorization_kpis,
    get_roi_journey_lever,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/valorization/metrics", response_model=ValorizationMetrics)
async def valorization_metrics_endpoint(
    avg_commute_minutes: float = Query(default=40.0),
    engagement_rate: float = Query(default=0.20, ge=0, le=1),
    training_hour_cost: float = Query(default=35.0, ge=0),
    employee_count: int = Query(default=1200, ge=1),
    current_user: User = Depends(get_current_user),
) -> ValorizationMetrics:
    """Get journey valorization metrics with configurable parameters."""
    config = ValorizationConfig(
        avg_commute_minutes=avg_commute_minutes,
        engagement_rate=engagement_rate,
        training_hour_cost=training_hour_cost,
        employee_count=employee_count,
    )
    return calculate_valorization(config)


@router.get("/kpis/valorization", response_model=list[ValorizationKPI])
async def valorization_kpis_endpoint(
    avg_commute_minutes: float = Query(default=40.0),
    engagement_rate: float = Query(default=0.20, ge=0, le=1),
    training_hour_cost: float = Query(default=35.0, ge=0),
    employee_count: int = Query(default=1200, ge=1),
    current_user: User = Depends(get_current_user),
) -> list[ValorizationKPI]:
    """Get valorization KPIs formatted for dashboard widgets."""
    config = ValorizationConfig(
        avg_commute_minutes=avg_commute_minutes,
        engagement_rate=engagement_rate,
        training_hour_cost=training_hour_cost,
        employee_count=employee_count,
    )
    return get_valorization_kpis(config)


@router.get("/valorization/roi-lever")
async def valorization_roi_lever_endpoint(
    avg_commute_minutes: float = Query(default=40.0),
    engagement_rate: float = Query(default=0.20, ge=0, le=1),
    training_hour_cost: float = Query(default=35.0, ge=0),
    employee_count: int = Query(default=1200, ge=1),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get roi_journey lever for ROI calculator integration."""
    config = ValorizationConfig(
        avg_commute_minutes=avg_commute_minutes,
        engagement_rate=engagement_rate,
        training_hour_cost=training_hour_cost,
        employee_count=employee_count,
    )
    return get_roi_journey_lever(config)
