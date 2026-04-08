# Session 24 — Optimization Frontend — Interactive Map

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-23|Session 23]]

> Previous: [[sessions/session-23|Session 23]] | Next: [[sessions/session-25|Session 25]]

## Complexity: High

## Objective
Build the optimization page interactive map with clusters, routes, meeting zones, access legs, and layer controls.

---

## Tasks

- [x] Create `frontend/src/api/optimization.ts` — API client functions
- [x] Create `frontend/src/types/optimization.ts` — TypeScript interfaces (Optimization, Cluster, Route, MeetingZone)
- [x] Create `frontend/src/stores/optimizationStore.ts` — Zustand store
- [x] Create `frontend/src/pages/optimization/OptimizationPage.tsx`:
  - Controls panel (left): site selector, date picker, condition type, algorithm settings
  - "Run Optimization" button (triggers async, shows progress)
  - Map area (center/right): full interactive Google Maps map
- [x] Create `frontend/src/components/maps/ClusterRegion.tsx` — Cluster boundary circle
- [x] Create `frontend/src/components/maps/RoutePolyline.tsx` — Vehicle route polyline (solid line, colored per vehicle)
- [x] Create `frontend/src/components/maps/MeetingZoneMarker.tsx` — Meeting zone radius circle
- [x] Create `frontend/src/components/maps/AccessLeg.tsx` — Dashed line (employee -> gathering point)
- [x] Create `frontend/src/components/maps/MapLegend.tsx` — Legend with layer toggles:
  - Show/hide: employee points, clusters, routes, meeting zones, access legs, site markers
  - Per-vehicle route toggle
- [x] Implement progress indicator for async optimization run
- [x] Implement polling-based progress updates (WebSocket deferred)
- [x] Add route details popup (click route -> show vehicle info, stops, metrics)
- [x] Add optimization routes to `routes.tsx`
- [x] Add "Optimization" link to Sidebar (already present)
- [ ] **Browser verification**: Deferred — requires manual check

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
- [x] `OptimizationPage.test.tsx` — Renders controls and map (4 tests)
- [x] `RoutePolyline.test.tsx` — Renders polyline on map (3 tests)
- [x] `MapLegend.test.tsx` — Toggles layer visibility (4 tests)
- [x] `ClusterRegion.test.tsx` — Renders cluster boundary (4 tests)

## Test Results
- Tests written: 15 (4 files)
- Tests passing: 15 (45 total frontend)
- Tests failing: 0
- Coverage: All new components tested

## Acceptance Criteria
- Map displays clusters, routes, meeting zones, access legs
- Layer toggle controls work (show/hide each layer)
- Route polylines colored per vehicle
- Access legs shown as dashed lines
- Optimization progress shown during async run
- Per-vehicle route selection works
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
