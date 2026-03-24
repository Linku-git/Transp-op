# Session 60 — RTI Monitoring Dashboard

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-58|Session 58]]
## Complexity: Medium
> Previous: [[sessions/session-59|Session 59]] | Next: [[sessions/session-61|Session 61]]

## Objective
Build a real-time RTI monitoring dashboard with live compliance gauges, stop wait time heatmaps, risk stop overlays with vehicle positions, violation alerts, and historical compliance trends.

---

## Tasks
- [ ] Create `RTIMonitoringDashboard` page at `/dashboard/rti`
- [ ] Implement live RTI compliance gauge:
  - Circular/radial gauge showing current compliance percentage
  - Color-coded: green (>=95%), yellow (85-95%), red (<85%)
  - Updates periodically (configurable polling interval, default 30s)
- [ ] Implement stop wait time heatmap:
  - Map overlay showing wait times at each stop
  - Color gradient from green (short wait) to red (long wait)
  - Click on stop for detailed wait time history
- [ ] Implement risk stop map overlay:
  - Display risk-scored stops from Session 57
  - Show real-time vehicle positions from Session 58
  - Vehicle markers with heading indicators
  - Risk stops colored by severity (green/orange/red)
- [ ] Implement RTI violation alert list:
  - Table of recent violations (wait time exceeded threshold)
  - Columns: stop name, vehicle, scheduled time, actual wait, severity
  - Sortable and filterable
- [ ] Implement historical compliance trends:
  - Line chart showing compliance percentage over time
  - Configurable time range (day, week, month)
  - Overlay target compliance line
- [ ] Implement `GET /kpis/rti` endpoint:
  - Current compliance percentage
  - Average wait time
  - Number of active violations
  - Trend data for charts

## Files to Create/Modify
- `frontend/src/pages/dashboard/RTIMonitoringDashboard.tsx`
- `frontend/src/components/rti/ComplianceGauge.tsx`
- `frontend/src/components/rti/WaitTimeHeatmap.tsx`
- `frontend/src/components/rti/RiskStopMapOverlay.tsx`
- `frontend/src/components/rti/ViolationAlertList.tsx`
- `frontend/src/components/rti/ComplianceTrendChart.tsx`
- `frontend/src/api/rti.ts`
- `backend/app/api/endpoints/kpis_rti.py`
- `backend/app/api/router.py` (register KPI endpoint)
- `frontend/src/routes.tsx` (add route)

## Tests
- [ ] Test compliance gauge renders correct percentage and color
- [ ] Test gauge updates on polling interval
- [ ] Test heatmap displays stops with correct color coding
- [ ] Test risk stop overlay shows markers with severity colors
- [ ] Test vehicle positions display on map
- [ ] Test violation alert list renders and sorts correctly
- [ ] Test compliance trend chart renders with correct time ranges
- [ ] Test GET /kpis/rti returns expected data structure

## Acceptance Criteria
- RTI Monitoring Dashboard is accessible at /dashboard/rti
- Live compliance gauge shows real-time percentage with color coding
- Stop wait time heatmap visualizes wait times across all stops
- Risk stop map overlay shows risk-scored stops alongside live vehicle positions
- Violation alert list displays recent threshold violations
- Historical compliance trend chart supports day/week/month views
- GET /kpis/rti endpoint returns all required KPI data
- All frontend tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
- [[DATABASE_SCHEMA]]
- [[API_ENDPOINTS]]
- [[FRONTEND_PAGES]]
