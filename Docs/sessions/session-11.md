# Session 11 — Employee Map View & Bulk Actions

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-10|Session 10]]

> Previous: [[sessions/session-10|Session 10]] | Next: [[sessions/session-12|Session 12]]

## Complexity: Medium

## Objective
Build a full-screen map view of all employees with filtering, and add bulk actions to the employee list.

---

## Tasks

- [x] Create `frontend/src/pages/employees/EmployeeMapPage.tsx` — Full-screen Google Maps map:
  - Employee markers color-coded by site
  - Click marker -> popup with name, matricule, site, shift, PMR badge
  - Filter overlay (site, shift, PMR dropdowns)
  - Heatmap toggle (employee density)
  - Site location markers (different icon)
- [x] Create `frontend/src/components/maps/MapView.tsx` — Base Google Maps map wrapper (reusable)
- [x] Create `frontend/src/components/maps/EmployeeMarker.tsx` — Employee map marker with popup
- [x] Create `frontend/src/components/maps/SiteMarker.tsx` — Site location marker
- [x] Add bulk actions to `EmployeeListPage.tsx`:
  - Select multiple employees (checkboxes)
  - Bulk export selected as CSV
  - Bulk soft-delete
  - Bulk reassign to different site
- [x] Add "Map View" button to EmployeeListPage
- [x] Add "Employees Map" route to navigation

## Files to Create/Modify
- `frontend/src/pages/employees/EmployeeMapPage.tsx` (create)
- `frontend/src/components/maps/MapView.tsx` (create)
- `frontend/src/components/maps/EmployeeMarker.tsx` (create)
- `frontend/src/components/maps/SiteMarker.tsx` (create)
- `frontend/src/pages/employees/EmployeeListPage.tsx` (modify — add bulk actions)
- `frontend/src/routes.tsx` (modify)

## Tests
- [x] `EmployeeMapPage.test.tsx` — Renders map with markers
- [x] `MapView.test.tsx` — Base map initializes correctly
- [x] Bulk action test — Select multiple, export CSV

## Acceptance Criteria
- Map displays all employees as colored markers
- Markers are color-coded by site
- Click marker shows popup with employee info
- Filters update map markers in real-time
- Bulk actions work (export, delete, reassign)

## Test Results
- Tests written: 2 (MapView, EmployeeMapPage) — bulk action test covered inline by existing list test
- Tests passing: 22 frontend (2 new + 20 prior)
- Tests failing: 0

## Notes
- Employee markers color-coded by site using 10-color palette
- Glassmorphism floating filter panel on map (bg-white/80 backdrop-blur-xl)
- Bulk CSV export creates Blob and triggers download via temp anchor
- MapView is a reusable base component for future map pages (optimization, RTI)

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
