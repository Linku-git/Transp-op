"""Prometheus metrics middleware for Transpop API."""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Custom histogram buckets
LATENCY_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logger.warning("prometheus_client not installed — metrics disabled")

# Define metrics (only if prometheus available)
if HAS_PROMETHEUS:
    optimization_duration = Histogram(
        'sotreg_optimization_duration_seconds',
        'Duration of optimization runs',
        ['strategy'],
        buckets=LATENCY_BUCKETS,
    )
    ml_prediction_latency = Histogram(
        'sotreg_ml_prediction_latency_seconds',
        'ML model prediction latency',
        ['model_type'],
        buckets=LATENCY_BUCKETS,
    )
    telemetry_ingestion_rate = Counter(
        'sotreg_telemetry_ingestion_rate_total',
        'GPS telemetry points ingested',
    )
    socketio_connections = Gauge(
        'sotreg_socketio_connections',
        'Current active SocketIO connections',
    )
    celery_task_duration = Histogram(
        'sotreg_celery_task_duration_seconds',
        'Celery task execution duration',
        ['task_name'],
        buckets=LATENCY_BUCKETS,
    )
    db_query_duration = Histogram(
        'sotreg_db_query_duration_seconds',
        'Database query duration',
        ['query_type'],
        buckets=LATENCY_BUCKETS,
    )
else:
    # No-op stubs
    class _NoOpMetric:
        def observe(self, *a: Any, **kw: Any) -> None:
            pass

        def inc(self, *a: Any, **kw: Any) -> None:
            pass

        def dec(self, *a: Any, **kw: Any) -> None:
            pass

        def set(self, *a: Any, **kw: Any) -> None:
            pass

        def labels(self, *a: Any, **kw: Any) -> _NoOpMetric:
            return self

        def time(self) -> _NoOpTimer:
            return _NoOpTimer()

    class _NoOpTimer:
        def __enter__(self) -> _NoOpTimer:
            return self

        def __exit__(self, *a: Any) -> None:
            pass

    _noop = _NoOpMetric()
    optimization_duration = _noop  # type: ignore[assignment]
    ml_prediction_latency = _noop  # type: ignore[assignment]
    telemetry_ingestion_rate = _noop  # type: ignore[assignment]
    socketio_connections = _noop  # type: ignore[assignment]
    celery_task_duration = _noop  # type: ignore[assignment]
    db_query_duration = _noop  # type: ignore[assignment]


def record_optimization(strategy: str, duration_s: float) -> None:
    """Record optimization run duration by strategy."""
    optimization_duration.labels(strategy=strategy).observe(duration_s)


def record_ml_prediction(model_type: str, duration_s: float) -> None:
    """Record ML model prediction latency."""
    ml_prediction_latency.labels(model_type=model_type).observe(duration_s)


def record_telemetry_ingestion(count: int = 1) -> None:
    """Increment GPS telemetry ingestion counter."""
    telemetry_ingestion_rate.inc(count)


def set_socketio_connections(count: int) -> None:
    """Set the current number of active SocketIO connections."""
    socketio_connections.set(count)


def record_celery_task(task_name: str, duration_s: float) -> None:
    """Record Celery task execution duration."""
    celery_task_duration.labels(task_name=task_name).observe(duration_s)


def record_db_query(query_type: str, duration_s: float) -> None:
    """Record database query duration."""
    db_query_duration.labels(query_type=query_type).observe(duration_s)


def setup_metrics(app: Any) -> None:
    """Instrument FastAPI app with Prometheus metrics."""
    if not HAS_PROMETHEUS:
        logger.info("Prometheus metrics disabled (prometheus_client not installed)")
        return

    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            excluded_handlers=["/health", "/metrics"],
        ).instrument(app).expose(app, endpoint="/metrics")
        logger.info("Prometheus metrics enabled at /metrics")
    except ImportError:
        # Fallback: manual /metrics endpoint
        from starlette.requests import Request
        from starlette.responses import Response

        @app.get("/metrics")
        async def metrics_endpoint(request: Request) -> Response:
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )
        logger.info("Prometheus metrics enabled at /metrics (manual endpoint)")
