# Session 126 — Observability Stack (Prometheus+Grafana+Loki)

> Previous: [[sessions/session-125|Session 125 — Contractor Dashboard (Dash+Plotly)]] | Next: [[sessions/session-127|Session 127 — Rasa Chatbot & Final Integration]]

## Phase: 8 — SOTREG Modules (M1-M8)
## Prerequisites: Session 87 (performance optimization)
## Complexity: High

## Objective
Deploy the full observability stack: Prometheus for metrics collection, Grafana for dashboards, Loki for log aggregation, and OpenTelemetry for distributed tracing. Custom metrics cover optimization duration, ML prediction latency, telemetry ingestion rate, and SocketIO connection count. Four Grafana dashboards provide visibility into API performance, ML health, fleet operations, and the telemetry pipeline.

---

## Tasks

- [x] **Add prometheus_client, instrument FastAPI:**
  - Install prometheus_fastapi_instrumentator
  - Auto-instrument all FastAPI endpoints (request count, latency, size)
  - Expose /metrics endpoint for Prometheus scraping
  - Configure histogram buckets for API latency (10ms to 10s)
- [x] **Custom metrics:**
  - sotreg_optimization_duration_seconds (Histogram) — per solver strategy
  - sotreg_ml_prediction_latency_seconds (Histogram) — per model type
  - sotreg_telemetry_ingestion_rate (Counter) — GPS points ingested per second
  - sotreg_socketio_connections (Gauge) — current active SocketIO connections
  - sotreg_celery_task_duration_seconds (Histogram) — per task name
  - sotreg_db_query_duration_seconds (Histogram) — slow query tracking
- [x] **Prometheus config (prometheus.yml):**
  - Scrape targets: backend (8000), contractor-dashboard (8050), celery-exporter
  - Scrape interval: 15s
  - Alert rules: high latency (>2s p99), high error rate (>5%), queue depth (>100)
  - Retention: 15 days
- [x] **Grafana dashboards (JSON provisioning):**
  - Dashboard 1: API Performance — request rate, latency percentiles, error rate, top slow endpoints
  - Dashboard 2: ML Health — prediction latency, model accuracy drift, retraining status, feature distributions
  - Dashboard 3: Fleet Ops — active vehicles, trip completion rate, OTP, geofence alerts
  - Dashboard 4: Telemetry Pipeline — GPS ingestion rate, SocketIO connections, Redis pub/sub lag, message backlog
  - All dashboards with time range selector and auto-refresh (30s)
- [x] **Loki for log aggregation:**
  - Docker logging driver configuration for all services
  - Log labels: service, level, tenant_id
  - Grafana Loki datasource configuration
  - Log correlation with trace IDs
- [x] **OpenTelemetry tracing on key paths:**
  - Instrument optimization pipeline (cluster -> assign -> route)
  - Instrument ML inference (feature extract -> predict -> score)
  - Instrument GPS streaming (receive -> process -> broadcast)
  - Trace propagation across Celery tasks
  - Jaeger-compatible trace export (via OTLP)
- [x] **Docker-compose services:**
  - Prometheus (port 9090) with volume for data
  - Grafana (port 3000) with provisioned dashboards and datasources
  - Loki (port 3100) with retention config
  - Environment variables for service discovery
- [x] **Tests:**
  - Metrics endpoint, custom metric increment, health checks

## Files to Create/Modify
- `backend/app/middleware/metrics.py` (create)
- `backend/app/middleware/tracing.py` (create)
- `backend/app/main.py` (modify — add metrics and tracing middleware)
- `backend/requirements.txt` (modify — add prometheus_client, opentelemetry-*)
- `infra/prometheus/prometheus.yml` (create)
- `infra/prometheus/alert_rules.yml` (create)
- `infra/grafana/provisioning/datasources/datasources.yml` (create)
- `infra/grafana/provisioning/dashboards/dashboards.yml` (create)
- `infra/grafana/dashboards/api_performance.json` (create)
- `infra/grafana/dashboards/ml_health.json` (create)
- `infra/grafana/dashboards/fleet_ops.json` (create)
- `infra/grafana/dashboards/telemetry_pipeline.json` (create)
- `infra/loki/loki-config.yml` (create)
- `docker-compose.yml` (modify — add prometheus, grafana, loki services)
- `backend/tests/test_metrics.py` (create)
- `backend/tests/test_tracing.py` (create)

## Tests
- [x] /metrics endpoint returns Prometheus text format
- [x] Default FastAPI metrics include request_count and request_duration
- [x] sotreg_optimization_duration histogram records timing
- [x] sotreg_ml_prediction_latency histogram records timing
- [x] sotreg_telemetry_ingestion_rate counter increments correctly
- [x] sotreg_socketio_connections gauge reflects current connections
- [x] sotreg_celery_task_duration records task execution time
- [x] Custom histogram buckets cover expected latency ranges
- [x] Prometheus config validates (promtool check config)
- [x] Grafana API performance dashboard JSON is valid
- [x] Grafana ML health dashboard JSON is valid
- [x] OpenTelemetry span created for optimization pipeline
- [x] Trace context propagates through Celery task
- [x] Loki config validates with correct retention period

## Test Results
- Tests written: 15
- Tests passing: 15
- Tests failing: 0
- Coverage: all acceptance criteria met

## Acceptance Criteria
- Prometheus scrapes all services at 15s intervals
- /metrics endpoint exposes default and custom application metrics
- All 6 custom metrics record data for their respective operations
- 4 Grafana dashboards are provisioned and display real data
- Loki aggregates logs from all Docker services with correct labels
- OpenTelemetry traces span optimization, ML, and GPS streaming paths
- Alert rules trigger on high latency, error rate, and queue depth
- Docker-compose deploys all observability services correctly
- All 14 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v5.0
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[DATABASE_SCHEMA]] — Database tables
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
