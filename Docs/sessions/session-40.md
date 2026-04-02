# Session 40 — HR Dashboard Frontend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-39|Session 39]]
## Complexity: Medium
> Previous: [[sessions/session-39|Session 39]] | Next: [[sessions/session-41|Session 41]]

## Objective
Build the HR dashboard frontend page with visualizations for mobility coverage, score evolution, absenteeism correlation, retention impact, and shadow zones.

---

## Tasks
- [x] Create HRDashboardPage at `/dashboard/hr`
- [x] Build mobility coverage HeatmapTable (by site/shift/department)
- [x] Build mobility score evolution LineChart
- [x] Build absenteeism correlation ScatterPlot
- [x] Build RetentionImpactCard
- [x] Build ShadowZonesList
- [x] Add MobilityAlerts (critical/warning banners)
- [x] Create reusable HeatmapTable component
- [x] Create reusable ScatterPlot chart component
- [x] Write frontend tests (8 tests)
- [ ] **Browser verification**: pending (manual check)

## Files to Create/Modify
- `frontend/src/pages/HRDashboard.tsx`
- `frontend/src/components/charts/HeatmapTable.tsx`
- `frontend/src/components/charts/ScatterPlot.tsx`
- `frontend/src/components/dashboard/RetentionImpactCard.tsx`
- `frontend/src/components/dashboard/ShadowZonesList.tsx`
- `frontend/src/routes.tsx` (add `/dashboard/hr` route)
- `frontend/src/tests/HRDashboard.test.tsx`

## Tests
- [x] Test HRDashboard page renders loading state
- [x] Test HRDashboard renders content sections
- [x] Test HeatmapTable displays color-coded coverage data
- [x] Test ScatterPlot renders SVG with data points
- [x] Test RetentionImpactCard shows savings and turnover
- [x] Test ShadowZonesList renders employee entries
- [x] Test MobilityAlerts shows critical alert when coverage < 60%
- [x] Test MobilityAlerts shows no alerts when coverage is good

## Test Results
- Tests written: 8
- Tests passing: 8
- Tests failing: 0

## Files Created/Modified
- `frontend/src/types/hr.ts` (created)
- `frontend/src/api/hr.ts` (created)
- `frontend/src/components/charts/HeatmapTable.tsx` (created)
- `frontend/src/components/charts/ScatterPlot.tsx` (created)
- `frontend/src/components/dashboard/RetentionImpactCard.tsx` (created)
- `frontend/src/components/dashboard/ShadowZonesList.tsx` (created)
- `frontend/src/components/dashboard/MobilityAlerts.tsx` (created)
- `frontend/src/pages/dashboard/HRDashboardPage.tsx` (created)
- `frontend/src/pages/dashboard/__tests__/HRDashboard.test.tsx` (created)
- `frontend/src/routes.tsx` (modified)
- `frontend/src/i18n/fr.json` (modified)
- `frontend/src/i18n/en.json` (modified)

## Acceptance Criteria
- HRDashboard page is accessible at `/dashboard/hr`
- Mobility coverage heatmap table shows coverage percentages by site and shift
- Mobility score evolution line chart displays trends over time
- Absenteeism correlation scatter plot visualizes transport-absence relationship
- Retention impact card shows cost of replacement vs mobility solution cost
- Shadow zones list displays affected employees with a map overlay
- Alert indicators highlight unaddressed mobility gaps
- HeatmapTable and ScatterPlot are reusable components
- All frontend tests pass
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
