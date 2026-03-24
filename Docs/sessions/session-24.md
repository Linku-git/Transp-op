# Session 24 — Optimization Frontend — Interactive Map

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-23|Session 23]]

> Previous: [[sessions/session-23|Session 23]] | Next: [[sessions/session-25|Session 25]]

## Complexity: High

## Objective
Build the optimization page interactive map with clusters, routes, meeting zones, access legs, and layer controls.

---

## Tasks

- [ ] Create `frontend/src/api/optimization.ts` — API client functions
- [ ] Create `frontend/src/types/optimization.ts` — TypeScript interfaces (Optimization, Cluster, Route, MeetingZone)
- [ ] Create `frontend/src/stores/optimizationStore.ts` — Zustand store
- [ ] Create `frontend/src/pages/optimization/OptimizationPage.tsx`:
  - Controls panel (left): site selector, date picker, condition type, algorithm settings
  - "Run Optimization" button (triggers async, shows progress)
  - Map area (center/right): full interactive Leaflet map
- [ ] Create `frontend/src/components/maps/ClusterRegion.tsx` — Cluster boundary polygon/circle
- [ ] Create `frontend/src/components/maps/RoutePolyline.tsx` — Vehicle route polyline (solid line, colored per vehicle)
- [ ] Create `frontend/src/components/maps/MeetingZone.tsx` — Meeting zone radius circle
- [ ] Create `frontend/src/components/maps/AccessLeg.tsx` — Dashed line (employee -> gathering point)
- [ ] Create `frontend/src/components/maps/MapLegend.tsx` — Legend with layer toggles:
  - Show/hide: employee points, clusters, routes, meeting zones, access legs, site markers
  - Per-vehicle route toggle
- [ ] Implement progress indicator for async optimization run
- [ ] Implement WebSocket connection for real-time progress updates
- [ ] Add route details popup (click route -> show vehicle info, stops, metrics)
- [ ] Add optimization routes to `routes.tsx`
- [ ] Add "Optimization" link to Sidebar

## Files to Create/Modify
- `frontend/src/api/optimization.ts` (create)
- `frontend/src/types/optimization.ts` (create)
- `frontend/src/stores/optimizationStore.ts` (create)
- `frontend/src/pages/optimization/OptimizationPage.tsx` (create)
- `frontend/src/components/maps/ClusterRegion.tsx` (create)
- `frontend/src/components/maps/RoutePolyline.tsx` (create)
- `frontend/src/components/maps/MeetingZone.tsx` (create)
- `frontend/src/components/maps/AccessLeg.tsx` (create)
- `frontend/src/components/maps/MapLegend.tsx` (create)
- `frontend/src/routes.tsx` (modify)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

## Tests
- [ ] `OptimizationPage.test.tsx` — Renders controls and map
- [ ] `RoutePolyline.test.tsx` — Renders polyline on map
- [ ] `MapLegend.test.tsx` — Toggles layer visibility
- [ ] `ClusterRegion.test.tsx` — Renders cluster boundary

## Acceptance Criteria
- Map displays clusters, routes, meeting zones, access legs
- Layer toggle controls work (show/hide each layer)
- Route polylines colored per vehicle
- Access legs shown as dashed lines
- Optimization progress shown during async run
- Per-vehicle route selection works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
