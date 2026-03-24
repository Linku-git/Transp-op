# Session 44 — KPI Snapshot System

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-39|Session 39]]
## Complexity: Low
> Previous: [[sessions/session-43|Session 43]] | Next: [[sessions/session-45|Session 45]]

## Objective
Implement a KPI snapshot system that captures daily KPI values for all sites, enabling historical trend tracking for dashboard charts.

---

## Tasks
- [ ] Create KPISnapshot model and database migration
- [ ] Create POST `/kpis/snapshot` endpoint to save a snapshot for historical tracking
- [ ] Implement Celery scheduled task for daily KPI snapshot across all sites
- [ ] Support KPI types: mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score
- [ ] Implement historical trend queries for dashboard charts
- [ ] Write tests for snapshot creation, trend queries, and scheduled task

## Files to Create/Modify
- `backend/app/models/kpi_snapshot.py`
- `backend/alembic/versions/xxx_add_kpi_snapshot.py` (migration)
- `backend/app/routers/kpis.py` (add snapshot endpoint)
- `backend/app/tasks/kpi_tasks.py` (Celery scheduled task)
- `backend/app/services/kpi_service.py`
- `backend/tests/test_kpi_snapshot.py`

## Tests
- [ ] Test KPISnapshot model creation and field validation
- [ ] Test POST `/kpis/snapshot` saves a snapshot with correct KPI values
- [ ] Test Celery scheduled task runs daily and creates snapshots for all sites
- [ ] Test all KPI types (mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score) are captured
- [ ] Test historical trend query returns time-series data for a given KPI type and site
- [ ] Test trend query supports date range filtering

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
