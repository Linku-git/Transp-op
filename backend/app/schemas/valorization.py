from __future__ import annotations

from pydantic import BaseModel, Field


class ValorizationConfig(BaseModel):
    """Configurable parameters for valorization calculations."""
    avg_commute_minutes: float = Field(
        default=40.0, description="Average round-trip commute time in minutes"
    )
    working_days_per_week: int = Field(default=5)
    working_weeks_per_year: int = Field(default=50)
    engagement_rate: float = Field(
        default=0.20, description="Expected content engagement rate (0-1)"
    )
    training_hour_cost: float = Field(
        default=35.0, description="Cost per training hour in EUR"
    )
    employee_count: int = Field(default=1200)


class ValorizationMetrics(BaseModel):
    """Calculated valorization KPIs."""
    # Time metrics
    annual_commute_hours_per_employee: float
    total_annual_commute_hours: float
    training_hours_recovered_per_employee: float
    total_training_hours_recovered: float

    # Monetary metrics
    value_per_employee: float
    total_monetary_value: float

    # Rates
    engagement_rate: float
    training_hour_cost: float
    employee_count: int

    # Breakdown
    daily_commute_minutes: float
    weekly_commute_hours: float


class ValorizationKPI(BaseModel):
    """Dashboard-formatted KPI data."""
    label: str
    value: str
    unit: str
    trend: str | None = None
    description: str | None = None
