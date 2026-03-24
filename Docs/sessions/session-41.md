# Session 41 — RSE/Environment Dashboard

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-23|Session 23]]
## Complexity: Medium
> Previous: [[sessions/session-40|Session 40]] | Next: [[sessions/session-42|Session 42]]

## Objective
Build the RSE (Corporate Social Responsibility) and environment dashboard with backend KPI endpoints, DPEF report generation, and a frontend page displaying CO2 savings, modal shift, and ZFE compliance metrics.

---

## Tasks
- [ ] Create GET `/kpis/rse` endpoint returning CO2 saved, private vehicles avoided, soft/electric modes share, and ZFE compliance percentage
- [ ] Create POST `/export/rse/dpef` endpoint for DPEF report generation
- [ ] Create RSEDashboard frontend page at `/dashboard/rse`
- [ ] Build private vehicles avoided counter component
- [ ] Build CO2 saved display with trend line
- [ ] Build soft/electric modes pie chart
- [ ] Build ZFE compliance gauge component
- [ ] Add DPEF report generation button
- [ ] Build modal shift before/after comparison visualization
- [ ] Write tests for CO2 calculation logic
- [ ] Write tests for DPEF report generation

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
- [ ] Test CO2 saved calculation produces accurate figures from transport data
- [ ] Test private vehicles avoided count is derived correctly
- [ ] Test soft/electric modes share percentages sum to 100%
- [ ] Test ZFE compliance percentage calculation
- [ ] Test DPEF report generation produces a valid downloadable document
- [ ] Test GET `/kpis/rse` returns all expected fields
- [ ] Test POST `/export/rse/dpef` returns a file response
- [ ] Test RSEDashboard frontend renders all sections

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

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
