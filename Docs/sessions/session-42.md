# Session 42 — Enhanced Reporting Engine

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-30|Session 30]]
## Complexity: Medium
> Previous: [[sessions/session-41|Session 41]] | Next: [[sessions/session-43|Session 43]]

## Objective
Extend the export engine with new report types, a GeneratedReport model for persistence, and API endpoints for modal analysis, fleet utilization, volunteer driver/bonus, and HR mobility reports.

---

## Tasks
- [ ] Create GeneratedReport model and database migration
- [ ] Extend export engine with modal analysis report (PDF/Excel with charts)
- [ ] Extend export engine with fleet utilization report
- [ ] Extend export engine with volunteer driver/bonus report
- [ ] Extend export engine with HR mobility report (per-site coverage, mobility score, shadow zones)
- [ ] Create GET `/export/modal-report` endpoint
- [ ] Create GET `/export/fleet-report` endpoint
- [ ] Create GET `/export/volunteer-report` endpoint
- [ ] Create GET `/export/hr-mobility` endpoint
- [ ] Store generated reports in DB with file_url, format, and params
- [ ] Write tests for each report type generation

## Files to Create/Modify
- `backend/app/models/generated_report.py`
- `backend/alembic/versions/xxx_add_generated_report.py` (migration)
- `backend/app/services/export_engine.py`
- `backend/app/routers/export.py`
- `backend/tests/test_export_engine.py`
- `backend/tests/test_generated_report.py`

## Tests
- [ ] Test GeneratedReport model creation and persistence
- [ ] Test modal analysis report generates valid PDF and Excel output with charts
- [ ] Test fleet utilization report produces correct fleet usage metrics
- [ ] Test volunteer driver/bonus report includes driver details and bonus calculations
- [ ] Test HR mobility report contains per-site coverage, mobility score, and shadow zones
- [ ] Test each export endpoint returns a downloadable file
- [ ] Test generated reports are stored in the database with correct file_url, format, and params

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
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
