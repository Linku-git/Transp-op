# Session 40 — HR Dashboard Frontend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-39|Session 39]]
## Complexity: Medium
> Previous: [[sessions/session-39|Session 39]] | Next: [[sessions/session-41|Session 41]]

## Objective
Build the HR dashboard frontend page with visualizations for mobility coverage, score evolution, absenteeism correlation, retention impact, and shadow zones.

---

## Tasks
- [ ] Create HRDashboard page at `/dashboard/hr`
- [ ] Build mobility coverage heatmap table (by site/shift)
- [ ] Build mobility score evolution line chart
- [ ] Build absenteeism correlation scatter plot
- [ ] Build retention impact card
- [ ] Build shadow zones list with map overlay
- [ ] Add alert indicators for unaddressed mobility gaps
- [ ] Create reusable HeatmapTable component
- [ ] Create reusable ScatterPlot chart component
- [ ] Write frontend tests

## Files to Create/Modify
- `frontend/src/pages/HRDashboard.tsx`
- `frontend/src/components/charts/HeatmapTable.tsx`
- `frontend/src/components/charts/ScatterPlot.tsx`
- `frontend/src/components/dashboard/RetentionImpactCard.tsx`
- `frontend/src/components/dashboard/ShadowZonesList.tsx`
- `frontend/src/routes.tsx` (add `/dashboard/hr` route)
- `frontend/src/tests/HRDashboard.test.tsx`

## Tests
- [ ] Test HRDashboard page renders all sections
- [ ] Test HeatmapTable component displays coverage data correctly
- [ ] Test ScatterPlot component renders correlation data points
- [ ] Test RetentionImpactCard displays cost comparison
- [ ] Test ShadowZonesList renders employee/location entries
- [ ] Test alert indicators appear when mobility gaps exist
- [ ] Test page fetches data from `/kpis/hr` endpoint on load

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

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
