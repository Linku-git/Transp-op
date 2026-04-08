from __future__ import annotations

import logging
import os

from app.schemas.valorization import ValorizationConfig, ValorizationMetrics, ValorizationKPI

logger = logging.getLogger(__name__)


def get_config() -> ValorizationConfig:
    """Load valorization config from environment or defaults."""
    return ValorizationConfig(
        avg_commute_minutes=float(os.environ.get("VALORIZATION_COMMUTE_MINUTES", "40")),
        working_days_per_week=int(os.environ.get("VALORIZATION_WORK_DAYS", "5")),
        working_weeks_per_year=int(os.environ.get("VALORIZATION_WORK_WEEKS", "50")),
        engagement_rate=float(os.environ.get("VALORIZATION_ENGAGEMENT_RATE", "0.20")),
        training_hour_cost=float(os.environ.get("VALORIZATION_TRAINING_HOUR_COST", "35")),
        employee_count=int(os.environ.get("VALORIZATION_EMPLOYEE_COUNT", "1200")),
    )


def calculate_valorization(
    config: ValorizationConfig | None = None,
) -> ValorizationMetrics:
    """Calculate valorization metrics from configuration.

    Baseline scenario:
    - 40min round-trip * 5 days * 50 weeks = 166.67 annual commute hours
    - At 20% engagement = 33.33 hours recovered per employee
    - At 35 EUR/hour = 1,166.67 EUR value per employee
    """
    cfg = config or get_config()

    # Daily commute in hours
    daily_commute_hours = cfg.avg_commute_minutes / 60.0

    # Weekly commute hours
    weekly_commute_hours = daily_commute_hours * cfg.working_days_per_week

    # Annual commute hours per employee
    annual_commute_hours = weekly_commute_hours * cfg.working_weeks_per_year

    # Total annual commute hours across all employees
    total_annual_commute_hours = annual_commute_hours * cfg.employee_count

    # Training hours recovered (commute time * engagement rate)
    recovered_per_employee = annual_commute_hours * cfg.engagement_rate
    total_recovered = recovered_per_employee * cfg.employee_count

    # Monetary value
    value_per_employee = recovered_per_employee * cfg.training_hour_cost
    total_monetary_value = value_per_employee * cfg.employee_count

    return ValorizationMetrics(
        annual_commute_hours_per_employee=round(annual_commute_hours, 2),
        total_annual_commute_hours=round(total_annual_commute_hours, 2),
        training_hours_recovered_per_employee=round(recovered_per_employee, 2),
        total_training_hours_recovered=round(total_recovered, 2),
        value_per_employee=round(value_per_employee, 2),
        total_monetary_value=round(total_monetary_value, 2),
        engagement_rate=cfg.engagement_rate,
        training_hour_cost=cfg.training_hour_cost,
        employee_count=cfg.employee_count,
        daily_commute_minutes=cfg.avg_commute_minutes,
        weekly_commute_hours=round(weekly_commute_hours, 2),
    )


def get_valorization_kpis(
    config: ValorizationConfig | None = None,
) -> list[ValorizationKPI]:
    """Format valorization metrics for dashboard KPI widgets."""
    metrics = calculate_valorization(config)

    return [
        ValorizationKPI(
            label="Heures de formation récupérées",
            value=f"{metrics.total_training_hours_recovered:,.0f}",
            unit="heures/an",
            description=f"{metrics.training_hours_recovered_per_employee:.0f}h par employé",
        ),
        ValorizationKPI(
            label="Valeur monétaire totale",
            value=f"{metrics.total_monetary_value:,.0f}",
            unit="EUR/an",
            description=f"{metrics.value_per_employee:.0f} EUR par employé",
        ),
        ValorizationKPI(
            label="Taux d'engagement",
            value=f"{metrics.engagement_rate * 100:.0f}",
            unit="%",
            description="Contenu consommé pendant le trajet",
        ),
        ValorizationKPI(
            label="Temps de trajet valorisé",
            value=f"{metrics.daily_commute_minutes:.0f}",
            unit="min/jour",
            description=f"{metrics.weekly_commute_hours:.1f}h par semaine",
        ),
        ValorizationKPI(
            label="Coût horaire formation",
            value=f"{metrics.training_hour_cost:.0f}",
            unit="EUR/h",
            description="Coût de référence par heure de formation",
        ),
        ValorizationKPI(
            label="Effectif concerné",
            value=f"{metrics.employee_count:,}",
            unit="employés",
        ),
    ]


def get_roi_journey_lever(
    config: ValorizationConfig | None = None,
) -> dict:
    """Get the roi_journey lever value for ROI calculator integration."""
    metrics = calculate_valorization(config)
    return {
        "lever_name": "roi_journey",
        "label": "Valorisation du trajet",
        "annual_value": metrics.total_monetary_value,
        "hours_recovered": metrics.total_training_hours_recovered,
        "per_employee_value": metrics.value_per_employee,
        "assumptions": {
            "commute_minutes": metrics.daily_commute_minutes,
            "engagement_rate": metrics.engagement_rate,
            "training_hour_cost": metrics.training_hour_cost,
            "employee_count": metrics.employee_count,
        },
    }
