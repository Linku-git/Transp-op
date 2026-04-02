# Session 41 — RSE/Environment Dashboard

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-23|Session 23]]
## Complexity: Medium
> Previous: [[sessions/session-40|Session 40]] | Next: [[sessions/session-42|Session 42]]

## Objective
Build the RSE (Corporate Social Responsibility) and environment dashboard with backend KPI endpoints, DPEF report generation, and a frontend page displaying CO2 savings, modal shift, and ZFE compliance metrics.

---

## Tasks
- [x] Create GET `/kpis/rse` endpoint returning CO2 saved, vehicles avoided, modal distribution, ZFE compliance
- [x] Create POST `/kpis/rse/dpef` endpoint for DPEF PDF report generation
- [x] Create RSEDashboardPage at `/dashboard/rse`
- [x] Build private vehicles avoided counter (summary card)
- [x] Build CO2TrendLine with Recharts line chart
- [x] Build modal distribution PieChart + ModalShiftComparison (before/after)
- [x] Build ZFEComplianceGauge (SVG semicircle)
- [x] Add DPEF export button (downloads PDF)
- [x] Build ModalShiftComparison (grouped bar chart)
- [x] Write backend tests (7 tests)
- [x] Write frontend tests (6 tests)
- [ ] **Browser verification**: pending (manual check)

## Files to Create/Modify
- `backend/app/routers/kpis.py` (add RSE endpoint)
- `backend/app/services/rse_analytics.py`
- `backend/app/routers/export.py` (add DPEF export)
- `backend/tests/test_rse_analytics.py`
- `frontend/src/pages/RSEDashboard.tsx`
- `frontend/src/components/dashboard/CO2TrendLine.tsx`
- `frontend/src/components/dashboard/ZFEComplianceGauge.tsx`
- `frontend/src/components/dashboard/ModalShiftComparison.tsx`
- `frontend/src/routes.tsx` (add `/dashboard/rse` route)
- `frontend/src/tests/RSEDashboard.test.tsx`

## Tests
- [x] Test CO2 saved calculation returns all fields
- [x] Test private vehicles avoided count
- [x] Test modal distribution with category percentages
- [x] Test ZFE compliance percentage (0-100)
- [x] Test DPEF report generation (PDF bytes)
- [x] Test GET `/kpis/rse` returns all 4 sections
- [x] Test POST `/kpis/rse/dpef` returns PDF with headers
- [x] Test RSE dashboard renders loading state
- [x] Test RSE dashboard renders content
- [x] Test CO2TrendLine renders SVG
- [x] Test ZFEComplianceGauge shows percentage
- [x] Test ModalShiftComparison renders before/after
- [x] Test DPEF export button present

## Test Results
- Tests written: 13
- Tests passing: 13
- Tests failing: 0

## Files Created/Modified
- `backend/app/services/rse_analytics.py` (created) — 5 analytics + DPEF PDF
- `backend/app/api/v1/kpis.py` (modified) — GET /kpis/rse + POST /kpis/rse/dpef
- `backend/tests/test_rse_analytics.py` (created) — 7 tests
- `frontend/src/types/rse.ts` (created)
- `frontend/src/api/rse.ts` (created)
- `frontend/src/components/dashboard/CO2TrendLine.tsx` (created)
- `frontend/src/components/dashboard/ZFEComplianceGauge.tsx` (created)
- `frontend/src/components/dashboard/ModalShiftComparison.tsx` (created)
- `frontend/src/pages/dashboard/RSEDashboardPage.tsx` (created)
- `frontend/src/pages/dashboard/__tests__/RSEDashboard.test.tsx` (created) — 6 tests
- `frontend/src/routes.tsx` (modified)
- `frontend/src/i18n/fr.json` + `en.json` (modified)

## Acceptance Criteria
- GET `/kpis/rse` returns CO2 saved, private vehicles avoided, soft/electric modes share, and ZFE compliance percentage
- POST `/export/rse/dpef` generates and returns a downloadable DPEF report
- RSEDashboard page is accessible at `/dashboard/rse`
- Private vehicles avoided counter displays accurate count
- CO2 saved visualization includes a trend line over time
- Soft/electric modes pie chart shows modal distribution
- ZFE compliance gauge reflects current compliance percentage
- DPEF report generation button triggers export and provides download
- Modal shift before/after comparison shows improvement metrics
- All backend and frontend tests pass
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
