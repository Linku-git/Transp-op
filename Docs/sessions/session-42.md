# Session 42 — Enhanced Reporting Engine

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-30|Session 30]]
## Complexity: Medium
> Previous: [[sessions/session-41|Session 41]] | Next: [[sessions/session-43|Session 43]]

## Objective
Extend the export engine with new report types, a GeneratedReport model for persistence, and API endpoints for modal analysis, fleet utilization, volunteer driver/bonus, and HR mobility reports.

---

## Tasks
- [x] Create GeneratedReport model and Alembic migration
- [x] Extend export engine with modal analysis report (PDF/Excel)
- [x] Extend export engine with fleet utilization report
- [x] Extend export engine with volunteer driver report
- [x] Extend export engine with HR mobility report (coverage + shadow zones)
- [x] Create GET `/export/modal-report` endpoint
- [x] Create GET `/export/fleet-report` endpoint
- [x] Create GET `/export/volunteer-report` endpoint
- [x] Create GET `/export/hr-mobility` endpoint
- [x] Store generated reports in DB (GeneratedReport table)
- [x] Write tests (7 tests)

## Files to Create/Modify
- `backend/app/models/generated_report.py`
- `backend/alembic/versions/xxx_add_generated_report.py` (migration)
- `backend/app/services/export_engine.py`
- `backend/app/routers/export.py`
- `backend/tests/test_export_engine.py`
- `backend/tests/test_generated_report.py`

## Tests
- [x] Test GeneratedReport model creation via endpoint
- [x] Test modal analysis report generates valid PDF (%PDF- header)
- [x] Test modal analysis report generates valid Excel (PK zip header)
- [x] Test fleet utilization report produces PDF
- [x] Test volunteer driver report produces PDF
- [x] Test HR mobility report produces PDF
- [x] Test generated reports are stored in DB across multiple endpoints

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0

## Files Created/Modified
- `backend/app/models/generated_report.py` (created) — SQLAlchemy model
- `backend/alembic/versions/d4e5f6a7b8c9_add_generated_report.py` (created)
- `backend/app/services/report_engine.py` (created) — 4 report generators (PDF + Excel)
- `backend/app/api/v1/exports.py` (modified) — 4 new endpoints + _persist_report helper
- `backend/app/models/__init__.py` (modified) — added GeneratedReport
- `backend/tests/test_generated_report.py` (created) — 7 tests

## Acceptance Criteria
- GeneratedReport model exists with fields for file_url, format, and params
- Database migration runs successfully
- Modal analysis report generates PDF and Excel formats with embedded charts
- Fleet utilization report provides fleet usage and efficiency data
- Volunteer driver/bonus report includes driver participation and bonus figures
- HR mobility report covers per-site coverage, mobility score, and shadow zones
- All four export endpoints return downloadable files in the requested format
- Generated reports are persisted in the database for future retrieval
- All tests pass for each report type

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
