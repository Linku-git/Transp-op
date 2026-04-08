# Session 43 — Report Generation Frontend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-42|Session 42]]
## Complexity: Medium
> Previous: [[sessions/session-42|Session 42]] | Next: [[sessions/session-44|Session 44]]

## Objective
Build the frontend pages for browsing generated report history and generating new reports with configurable parameters, format selection, and download support.

---

## Tasks
- [x] Create ReportListPage at `/reports` with history table, download links, filter
- [x] Create ReportGeneratorPage at `/reports/generate`
- [x] Build ReportTypeSelector (7 report types in card grid)
- [x] Build ParameterConfigPanel (PDF/Excel format + generate button)
- [x] Add generate button with loading spinner
- [x] Implement browser download on completion
- [x] Create GET `/export/history` backend endpoint with pagination
- [x] Write frontend tests (6 tests)
- [ ] **Browser verification**: pending (manual check)

## Files to Create/Modify
- `frontend/src/pages/ReportListPage.tsx`
- `frontend/src/pages/ReportGeneratorPage.tsx`
- `frontend/src/components/reports/ReportTypeSelector.tsx`
- `frontend/src/components/reports/ParameterConfigPanel.tsx`
- `frontend/src/routes.tsx` (add `/reports` and `/reports/generate` routes)
- `backend/app/routers/export.py` (add `/export/history` endpoint)
- `frontend/src/tests/ReportListPage.test.tsx`
- `frontend/src/tests/ReportGeneratorPage.test.tsx`

## Tests
- [x] Test ReportListPage renders with table
- [x] Test ReportTypeSelector renders all 7 types
- [x] Test type selection click handler works
- [x] Test ParameterConfigPanel shows format options + generate button
- [x] Test ReportGeneratorPage renders type selector
- [x] Test report history API mock returns paginated list

## Test Results
- Tests written: 6
- Tests passing: 6
- Tests failing: 0

## Files Created/Modified
- `backend/app/api/v1/exports.py` (modified) — GET /export/history endpoint
- `frontend/src/types/reports.ts` (created)
- `frontend/src/api/reports.ts` (created)
- `frontend/src/components/reports/ReportTypeSelector.tsx` (created)
- `frontend/src/components/reports/ParameterConfigPanel.tsx` (created)
- `frontend/src/pages/reports/ReportListPage.tsx` (created)
- `frontend/src/pages/reports/ReportGeneratorPage.tsx` (created)
- `frontend/src/pages/reports/__tests__/Reports.test.tsx` (created)
- `frontend/src/routes.tsx` (modified)
- `frontend/src/i18n/fr.json` + `en.json` (modified)

## Acceptance Criteria
- ReportListPage is accessible at `/reports` and displays a history of generated reports
- Each report entry shows download links for retrieving the file
- ReportGeneratorPage is accessible at `/reports/generate`
- Report type selector offers operational, modal, fleet, financial, RSE, HR, and sizing options
- Parameter configuration allows selecting site scope, date range, and output format (PDF/Excel/CSV)
- Generate button starts generation and displays a progress indicator
- Completed reports are automatically available for download
- GET `/export/history` endpoint returns the list of previously generated reports
- All frontend tests pass
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
