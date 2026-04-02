# Session 44 — KPI Snapshot System

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-39|Session 39]]
## Complexity: Low
> Previous: [[sessions/session-43|Session 43]] | Next: [[sessions/session-45|Session 45]]

## Objective
Implement a KPI snapshot system that captures daily KPI values for all sites, enabling historical trend tracking for dashboard charts.

---

## Tasks
- [x] Create KPISnapshot model and Alembic migration
- [x] Create POST `/kpis/snapshot` endpoint (single site or all sites)
- [x] Implement Celery scheduled task `daily_kpi_snapshot` for all tenants/sites
- [x] Support 6 KPI types: mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score
- [x] Implement GET `/kpis/trend` with kpi_type, site_id, date range filters
- [x] Write tests (7 tests)

## Files to Create/Modify
- `backend/app/models/kpi_snapshot.py`
- `backend/alembic/versions/xxx_add_kpi_snapshot.py` (migration)
- `backend/app/routers/kpis.py` (add snapshot endpoint)
- `backend/app/tasks/kpi_tasks.py` (Celery scheduled task)
- `backend/app/services/kpi_service.py`
- `backend/tests/test_kpi_snapshot.py`

## Tests
- [x] Test KPI snapshot creation with specific site_id
- [x] Test snapshot for all sites (no site_id)
- [x] Test all 6 KPI types captured
- [x] Test trend query returns time-series data
- [x] Test trend date range filtering
- [x] Test invalid KPI type returns 422
- [x] Test Celery task function is importable and callable

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0

## Files Created/Modified
- `backend/app/models/kpi_snapshot.py` (created) — SQLAlchemy model
- `backend/alembic/versions/e5f6a7b8c9d0_add_kpi_snapshot.py` (created) — migration
- `backend/app/services/kpi_service.py` (created) — capture + trend query service
- `backend/app/tasks/kpi_tasks.py` (created) — Celery daily task
- `backend/app/api/v1/kpis.py` (modified) — POST /kpis/snapshot + GET /kpis/trend
- `backend/app/models/__init__.py` (modified) — added KPISnapshot
- `backend/tests/test_kpi_snapshot.py` (created) — 7 tests

## Acceptance Criteria
- KPISnapshot model exists with fields for site, KPI type, value, and timestamp
- Database migration runs successfully
- POST `/kpis/snapshot` creates and persists a snapshot record
- Celery scheduled task runs daily and generates snapshots for all configured sites
- All six KPI types are supported: mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score
- Historical trend queries return correctly ordered time-series data
- Trend queries support filtering by site, KPI type, and date range
- All tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[DATABASE_SCHEMA]] — Database tables
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
