"""Tests for Value Measurement Engine (Session 76)."""
from __future__ import annotations

import pytest

from app.schemas.valorization import ValorizationConfig, ValorizationMetrics, ValorizationKPI
from app.services.valorization_engine import (
    calculate_valorization,
    get_valorization_kpis,
    get_roi_journey_lever,
)


class TestValorizationCalculation:
    """Test core valorization calculation logic."""

    def test_baseline_scenario(self):
        """40min round-trip * 5 days * 50 weeks = ~166.67h; at 20% = ~33.33h recovered."""
        config = ValorizationConfig(
            avg_commute_minutes=40,
            working_days_per_week=5,
            working_weeks_per_year=50,
            engagement_rate=0.20,
            training_hour_cost=35.0,
            employee_count=1,
        )
        metrics = calculate_valorization(config)

        # 40min/day * 5 days * 50 weeks = 10000 min = 166.67 hours
        assert metrics.annual_commute_hours_per_employee == pytest.approx(166.67, abs=0.1)
        # 166.67 * 0.20 = 33.33 hours
        assert metrics.training_hours_recovered_per_employee == pytest.approx(33.33, abs=0.1)

    def test_monetary_value_per_employee(self):
        config = ValorizationConfig(
            avg_commute_minutes=40,
            engagement_rate=0.20,
            training_hour_cost=35.0,
            employee_count=1,
        )
        metrics = calculate_valorization(config)

        # 33.33 hours * 35 EUR/h = ~1166.67 EUR
        assert metrics.value_per_employee == pytest.approx(1166.67, abs=1)

    def test_total_scales_with_employee_count(self):
        config = ValorizationConfig(
            avg_commute_minutes=40,
            engagement_rate=0.20,
            training_hour_cost=35.0,
            employee_count=1200,
        )
        metrics = calculate_valorization(config)

        # Total may differ slightly from per_employee * count due to rounding
        assert metrics.total_training_hours_recovered == pytest.approx(
            metrics.training_hours_recovered_per_employee * 1200, rel=0.01
        )
        assert metrics.total_monetary_value == pytest.approx(
            metrics.value_per_employee * 1200, rel=0.01
        )

    def test_higher_engagement_rate(self):
        low = calculate_valorization(ValorizationConfig(engagement_rate=0.10))
        high = calculate_valorization(ValorizationConfig(engagement_rate=0.40))

        assert high.training_hours_recovered_per_employee > low.training_hours_recovered_per_employee
        assert high.total_monetary_value > low.total_monetary_value

    def test_different_commute_times(self):
        short = calculate_valorization(ValorizationConfig(avg_commute_minutes=20))
        long = calculate_valorization(ValorizationConfig(avg_commute_minutes=60))

        assert long.annual_commute_hours_per_employee > short.annual_commute_hours_per_employee

    def test_different_training_costs(self):
        cheap = calculate_valorization(ValorizationConfig(training_hour_cost=20))
        expensive = calculate_valorization(ValorizationConfig(training_hour_cost=50))

        assert expensive.total_monetary_value > cheap.total_monetary_value

    def test_zero_engagement_yields_zero(self):
        metrics = calculate_valorization(ValorizationConfig(engagement_rate=0.0))

        assert metrics.training_hours_recovered_per_employee == 0
        assert metrics.total_monetary_value == 0

    def test_weekly_commute_hours(self):
        config = ValorizationConfig(avg_commute_minutes=40, working_days_per_week=5)
        metrics = calculate_valorization(config)

        # 40min * 5 = 200min = 3.33h
        assert metrics.weekly_commute_hours == pytest.approx(3.33, abs=0.1)


class TestValorizationKPIs:
    def test_returns_six_kpis(self):
        kpis = get_valorization_kpis()
        assert len(kpis) == 6

    def test_kpi_labels(self):
        kpis = get_valorization_kpis()
        labels = [k.label for k in kpis]
        assert "Heures de formation récupérées" in labels
        assert "Valeur monétaire totale" in labels
        assert "Taux d'engagement" in labels

    def test_kpi_units(self):
        kpis = get_valorization_kpis()
        units = [k.unit for k in kpis]
        assert "heures/an" in units
        assert "EUR/an" in units
        assert "%" in units

    def test_kpi_with_custom_config(self):
        config = ValorizationConfig(engagement_rate=0.30, employee_count=500)
        kpis = get_valorization_kpis(config)
        engagement_kpi = next(k for k in kpis if k.unit == "%")
        assert engagement_kpi.value == "30"


class TestROILever:
    def test_roi_lever_structure(self):
        lever = get_roi_journey_lever()
        assert lever["lever_name"] == "roi_journey"
        assert lever["label"] == "Valorisation du trajet"
        assert "annual_value" in lever
        assert "hours_recovered" in lever
        assert "per_employee_value" in lever
        assert "assumptions" in lever

    def test_roi_lever_assumptions(self):
        config = ValorizationConfig(
            avg_commute_minutes=45,
            engagement_rate=0.25,
            training_hour_cost=40,
            employee_count=800,
        )
        lever = get_roi_journey_lever(config)
        assert lever["assumptions"]["commute_minutes"] == 45
        assert lever["assumptions"]["engagement_rate"] == 0.25
        assert lever["assumptions"]["training_hour_cost"] == 40
        assert lever["assumptions"]["employee_count"] == 800

    def test_roi_lever_value_matches_metrics(self):
        config = ValorizationConfig()
        metrics = calculate_valorization(config)
        lever = get_roi_journey_lever(config)

        assert lever["annual_value"] == metrics.total_monetary_value
        assert lever["hours_recovered"] == metrics.total_training_hours_recovered


class TestValorizationSchemas:
    def test_config_defaults(self):
        config = ValorizationConfig()
        assert config.avg_commute_minutes == 40.0
        assert config.engagement_rate == 0.20
        assert config.training_hour_cost == 35.0

    def test_config_custom(self):
        config = ValorizationConfig(
            avg_commute_minutes=60,
            engagement_rate=0.30,
            training_hour_cost=50,
            employee_count=500,
        )
        assert config.avg_commute_minutes == 60
        assert config.employee_count == 500

    def test_kpi_schema(self):
        kpi = ValorizationKPI(
            label="Test", value="42", unit="EUR",
            description="Test description"
        )
        assert kpi.label == "Test"
        assert kpi.trend is None
