# Session 43 — Report Generation Frontend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-42|Session 42]]
## Complexity: Medium
> Previous: [[sessions/session-42|Session 42]] | Next: [[sessions/session-44|Session 44]]

## Objective
Build the frontend pages for browsing generated report history and generating new reports with configurable parameters, format selection, and download support.

---

## Tasks
- [ ] Create ReportListPage at `/reports` displaying generated report history with download links
- [ ] Create ReportGeneratorPage at `/reports/generate`
- [ ] Build report type selector (operational, modal, fleet, financial, RSE, HR, sizing)
- [ ] Build parameter configuration panel (site scope, date range, format: PDF/Excel/CSV)
- [ ] Add generate button with progress indicator
- [ ] Implement download on completion
- [ ] Create GET `/export/history` backend endpoint for report history
- [ ] Write frontend tests

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
- [ ] Test ReportListPage renders report history entries with download links
- [ ] Test ReportListPage fetches data from GET `/export/history`
- [ ] Test ReportGeneratorPage renders report type selector with all options
- [ ] Test parameter configuration panel accepts site scope, date range, and format
- [ ] Test generate button triggers report generation and shows progress indicator
- [ ] Test download is initiated on report completion
- [ ] Test GET `/export/history` returns paginated list of generated reports

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

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
