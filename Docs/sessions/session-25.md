# Session 25 — Optimization Analytics Panel

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-24|Session 24]]

> Previous: [[sessions/session-24|Session 24]] | Next: [[sessions/session-26|Session 26]]

## Complexity: Medium

## Objective
Build the analytics panel alongside the optimization map, showing KPIs, per-site breakdown, and operations metrics.

---

## Tasks

- [ ] Create `frontend/src/components/optimization/MetricsPanel.tsx` — KPI cards: total vehicles, avg occupancy, total distance, fuel cost, CO2 saved, time saved
- [ ] Create `frontend/src/components/optimization/RouteList.tsx` — Expandable route list per vehicle (stops, passengers, distance, time)
- [ ] Create `frontend/src/components/optimization/ClusterTable.tsx` — Cluster details table (cluster ID, employee count, PMR count, assigned vehicle)
- [ ] Create `frontend/src/components/optimization/SiteBreakdown.tsx` — Per-site summary table
- [ ] Create `frontend/src/components/charts/GaugeChart.tsx` — Single metric gauge (occupancy rate)
- [ ] Create `frontend/src/api/kpis.ts` — KPI API client
- [ ] Add `GET /kpis/operations` endpoint call
- [ ] Create `frontend/src/pages/optimization/OptimizationResultPage.tsx` — Full results with map + analytics
- [ ] Create `frontend/src/pages/optimization/OptimizationHistoryPage.tsx` — Past runs table with compare button
- [ ] Add export buttons: PDF, Excel, GeoJSON (call export API)

## Files to Create/Modify
- `frontend/src/components/optimization/MetricsPanel.tsx` (create)
- `frontend/src/components/optimization/RouteList.tsx` (create)
- `frontend/src/components/optimization/ClusterTable.tsx` (create)
- `frontend/src/components/optimization/SiteBreakdown.tsx` (create)
- `frontend/src/components/charts/GaugeChart.tsx` (create)
- `frontend/src/api/kpis.ts` (create)
- `frontend/src/pages/optimization/OptimizationResultPage.tsx` (create)
- `frontend/src/pages/optimization/OptimizationHistoryPage.tsx` (create)

## Tests
- [ ] `MetricsPanel.test.tsx` — Renders KPI cards with correct values
- [ ] `RouteList.test.tsx` — Expands to show route stops
- [ ] `GaugeChart.test.tsx` — Renders gauge
- [ ] `OptimizationHistoryPage.test.tsx` — Lists past runs

## Acceptance Criteria
- KPI cards show correct metrics from optimization results
- Route list expandable per vehicle showing stops
- Per-site breakdown table shows correct data
- Export buttons generate downloads
- History page shows past optimization runs

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
