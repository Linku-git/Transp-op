"""Tests for observability stack (Session 126)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.middleware.metrics import (
    HAS_PROMETHEUS,
    LATENCY_BUCKETS,
    record_celery_task,
    record_db_query,
    record_ml_prediction,
    record_optimization,
    record_telemetry_ingestion,
    set_socketio_connections,
)
from app.middleware.tracing import (
    HAS_OTEL,
    get_tracer,
    setup_tracing,
    trace_span,
)

INFRA_DIR = Path(__file__).parent.parent.parent / "infra"


class TestMetricsHelpers:
    """Test that metric recording functions work without error."""

    def test_metrics_helpers_dont_crash(self) -> None:
        """All metric recording functions work without error."""
        record_optimization("ortools", 1.5)
        record_ml_prediction("demand_forecast", 0.3)
        record_telemetry_ingestion(10)
        set_socketio_connections(42)
        record_celery_task("ml_retrain", 15.0)
        record_db_query("select", 0.05)

    def test_histogram_buckets_cover_range(self) -> None:
        """Bucket range starts at <= 0.01 and ends at >= 10.0."""
        assert LATENCY_BUCKETS[0] <= 0.01
        assert LATENCY_BUCKETS[-1] >= 10.0
        assert len(LATENCY_BUCKETS) >= 8

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_optimization_histogram_records(self) -> None:
        """Optimization histogram registers in Prometheus."""
        from prometheus_client import REGISTRY

        record_optimization("cw", 2.5)
        metric = REGISTRY._names_to_collectors.get(
            "sotreg_optimization_duration_seconds"
        )
        assert metric is not None

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_ml_prediction_histogram_records(self) -> None:
        """ML prediction histogram registers in Prometheus."""
        from prometheus_client import REGISTRY

        record_ml_prediction("driver_risk", 0.15)
        metric = REGISTRY._names_to_collectors.get(
            "sotreg_ml_prediction_latency_seconds"
        )
        assert metric is not None

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_telemetry_counter_increments(self) -> None:
        """Telemetry ingestion counter registers in Prometheus."""
        from prometheus_client import REGISTRY

        record_telemetry_ingestion(5)
        metric = REGISTRY._names_to_collectors.get(
            "sotreg_telemetry_ingestion_rate_total"
        )
        assert metric is not None

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_socketio_gauge_set(self) -> None:
        """SocketIO gauge registers in Prometheus."""
        from prometheus_client import REGISTRY

        set_socketio_connections(100)
        metric = REGISTRY._names_to_collectors.get("sotreg_socketio_connections")
        assert metric is not None

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_celery_task_histogram(self) -> None:
        """Celery task histogram registers in Prometheus."""
        from prometheus_client import REGISTRY

        record_celery_task("optimization_run", 30.0)
        metric = REGISTRY._names_to_collectors.get(
            "sotreg_celery_task_duration_seconds"
        )
        assert metric is not None

    @pytest.mark.skipif(not HAS_PROMETHEUS, reason="prometheus_client not installed")
    def test_db_query_histogram(self) -> None:
        """DB query histogram registers in Prometheus."""
        from prometheus_client import REGISTRY

        record_db_query("insert", 0.02)
        metric = REGISTRY._names_to_collectors.get(
            "sotreg_db_query_duration_seconds"
        )
        assert metric is not None


class TestPrometheusConfig:
    """Validate Prometheus configuration files."""

    def test_prometheus_yml_parses(self) -> None:
        """Prometheus config YAML is valid and has expected scrape jobs."""
        path = INFRA_DIR / "prometheus" / "prometheus.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        assert config["global"]["scrape_interval"] == "15s"
        assert len(config["scrape_configs"]) >= 2
        jobs = [sc["job_name"] for sc in config["scrape_configs"]]
        assert "transpop-api" in jobs

    def test_alert_rules_yml_parses(self) -> None:
        """Alert rules YAML has expected alert definitions."""
        path = INFRA_DIR / "prometheus" / "alert_rules.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        rules = config["groups"][0]["rules"]
        alert_names = [r["alert"] for r in rules]
        assert "HighAPILatency" in alert_names
        assert "HighErrorRate" in alert_names


class TestGrafanaDashboards:
    """Validate Grafana dashboard JSON files."""

    def test_api_performance_dashboard_valid(self) -> None:
        """API performance dashboard JSON is valid with required panels."""
        path = INFRA_DIR / "grafana" / "dashboards" / "api_performance.json"
        with open(path) as f:
            dashboard = json.load(f)
        assert "panels" in dashboard
        assert len(dashboard["panels"]) >= 4
        assert dashboard.get("refresh") == "30s"
        assert dashboard.get("title") is not None

    def test_ml_health_dashboard_valid(self) -> None:
        """ML health dashboard JSON is valid with required panels."""
        path = INFRA_DIR / "grafana" / "dashboards" / "ml_health.json"
        with open(path) as f:
            dashboard = json.load(f)
        assert "panels" in dashboard
        assert len(dashboard["panels"]) >= 4


class TestTracing:
    """Test OpenTelemetry tracing (or no-op fallback)."""

    def test_trace_span_context_manager(self) -> None:
        """trace_span context manager works with attributes and events."""
        with trace_span("test-span", {"key": "value"}) as span:
            span.set_attribute("test", "true")
            span.add_event("test-event")

    def test_get_tracer_returns_something(self) -> None:
        """get_tracer always returns a non-None value."""
        tracer = get_tracer()
        assert tracer is not None


class TestLokiConfig:
    """Validate Loki configuration."""

    def test_loki_config_retention(self) -> None:
        """Loki config has 7-day retention and correct port."""
        path = INFRA_DIR / "loki" / "loki-config.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        assert config["limits_config"]["retention_period"] == "168h"
        assert config["server"]["http_listen_port"] == 3100
