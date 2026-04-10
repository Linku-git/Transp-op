"""Tests for SOTREG Celery tasks (Session 109)."""
from __future__ import annotations

from app.tasks.sotreg_tasks import (
    SOTREG_BEAT_SCHEDULE,
    SOTREG_CACHE_KEYS,
    task_compute_avl_kpis,
    task_compute_fleet_diagnostics,
    task_retrain_maintenance_model,
)


class TestCeleryTasks:
    """Verify SOTREG Celery task execution."""

    def test_avl_kpis_executes(self) -> None:
        result = task_compute_avl_kpis()
        assert result["status"] == "completed"
        assert "lignes_processed" in result
        assert "metrics_stored" in result

    def test_avl_kpis_with_tenant(self) -> None:
        result = task_compute_avl_kpis(tenant_id="test-tenant")
        assert result["tenant_id"] == "test-tenant"

    def test_maintenance_retrain_executes(self) -> None:
        result = task_retrain_maintenance_model()
        assert result["status"] == "completed"
        assert result["model_retrained"] is True

    def test_fleet_diagnostics_executes(self) -> None:
        result = task_compute_fleet_diagnostics()
        assert result["status"] == "completed"
        assert result["snapshot_created"] is True

    def test_beat_schedule_contains_tasks(self) -> None:
        assert "sotreg-avl-kpis-daily" in SOTREG_BEAT_SCHEDULE
        assert "sotreg-maintenance-weekly" in SOTREG_BEAT_SCHEDULE
        assert "sotreg-fleet-diagnostics-daily" in SOTREG_BEAT_SCHEDULE

    def test_daily_schedule_24h(self) -> None:
        assert SOTREG_BEAT_SCHEDULE["sotreg-avl-kpis-daily"]["schedule"] == 86400.0

    def test_weekly_schedule_7d(self) -> None:
        assert SOTREG_BEAT_SCHEDULE["sotreg-maintenance-weekly"]["schedule"] == 604800.0

    def test_cache_keys_defined(self) -> None:
        assert "fleet_context" in SOTREG_CACHE_KEYS
        assert "avl_kpis" in SOTREG_CACHE_KEYS
        assert "maintenance_model" in SOTREG_CACHE_KEYS
