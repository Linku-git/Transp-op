# Session 16 — Modal Analysis Frontend

## Phase: 1 — MVP Core (Module C)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-15|Session 15]]

> Previous: [[sessions/session-15|Session 15]] | Next: [[sessions/session-17|Session 17]]

## Complexity: Medium

## Objective
Build the modal analysis frontend page with distribution charts, shift analysis, and insights.

---

## Tasks

- [x] Create `frontend/src/api/modal.ts` — API client functions
- [x] Create `frontend/src/types/modal.ts` — TypeScript interfaces
- [x] Create `frontend/src/pages/modal/ModalAnalysisPage.tsx`:
  - Site selector dropdown (or "All Sites")
  - Modal distribution pie chart (Recharts PieChart)
  - Shift potential bar chart (employees willing to switch)
  - Weather impact analysis chart
  - Carpool contribution chart (seats offered vs demand)
  - Distance/time distribution histograms
  - Shadow zones summary card
- [x] Create `frontend/src/components/charts/PieChart.tsx` — Reusable pie chart (Recharts)
- [x] Create `frontend/src/components/charts/BarChart.tsx` — Reusable bar chart
- [x] Create `frontend/src/components/charts/Histogram.tsx` — Distribution histogram
- [x] Add modal analysis route and Sidebar link
- [x] Implement global vs per-site toggle

## Files to Create/Modify
- `frontend/src/api/modal.ts` (create)
- `frontend/src/types/modal.ts` (create)
- `frontend/src/pages/modal/ModalAnalysisPage.tsx` (create)
- `frontend/src/components/charts/PieChart.tsx` (create)
- `frontend/src/components/charts/BarChart.tsx` (create)
- `frontend/src/components/charts/Histogram.tsx` (create)
- `frontend/src/routes.tsx` (modify)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

## Tests
- [x] `ModalAnalysisPage.test.tsx` — Renders charts with mock data
- [x] `PieChart.test.tsx` — Renders with data
- [x] `BarChart.test.tsx` — Renders with data

## Acceptance Criteria
- Pie chart shows modal distribution with correct percentages
- Site filter updates all charts
- Bar chart shows shift potential
- Distribution histograms render correctly
- All chart components are reusable

## Test Results
- Tests written: 3 (PieChart, BarChart, ModalAnalysisPage)
- Tests passing: 30 frontend (3 new + 27 prior)
- Tests failing: 0

## Notes
- Recharts mocked in tests to avoid SVG/canvas issues in jsdom
- Charts use design system tokens: teal for data, surface-container-highest at 20% for grid
- Distance histogram bins hardcoded (0-5, 5-10, 10-20, 20-30, 30+) from distribution data
- Mobility scores table shows top 10 with inline teal progress bars

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
