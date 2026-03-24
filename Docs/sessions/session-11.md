# Session 11 — Employee Map View & Bulk Actions

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-10|Session 10]]

> Previous: [[sessions/session-10|Session 10]] | Next: [[sessions/session-12|Session 12]]

## Complexity: Medium

## Objective
Build a full-screen map view of all employees with filtering, and add bulk actions to the employee list.

---

## Tasks

- [ ] Create `frontend/src/pages/employees/EmployeeMapPage.tsx` — Full-screen Leaflet map:
  - Employee markers color-coded by site
  - Click marker -> popup with name, matricule, site, shift, PMR badge
  - Filter overlay (site, shift, PMR dropdowns)
  - Heatmap toggle (employee density)
  - Site location markers (different icon)
- [ ] Create `frontend/src/components/maps/MapView.tsx` — Base Leaflet map wrapper (reusable)
- [ ] Create `frontend/src/components/maps/EmployeeMarker.tsx` — Employee map marker with popup
- [ ] Create `frontend/src/components/maps/SiteMarker.tsx` — Site location marker
- [ ] Add bulk actions to `EmployeeListPage.tsx`:
  - Select multiple employees (checkboxes)
  - Bulk export selected as CSV
  - Bulk soft-delete
  - Bulk reassign to different site
- [ ] Add "Map View" button to EmployeeListPage
- [ ] Add "Employees Map" route to navigation

## Files to Create/Modify
- `frontend/src/pages/employees/EmployeeMapPage.tsx` (create)
- `frontend/src/components/maps/MapView.tsx` (create)
- `frontend/src/components/maps/EmployeeMarker.tsx` (create)
- `frontend/src/components/maps/SiteMarker.tsx` (create)
- `frontend/src/pages/employees/EmployeeListPage.tsx` (modify — add bulk actions)
- `frontend/src/routes.tsx` (modify)

## Tests
- [ ] `EmployeeMapPage.test.tsx` — Renders map with markers
- [ ] `MapView.test.tsx` — Base map initializes correctly
- [ ] Bulk action test — Select multiple, export CSV

## Acceptance Criteria
- Map displays all employees as colored markers
- Markers are color-coded by site
- Click marker shows popup with employee info
- Filters update map markers in real-time
- Bulk actions work (export, delete, reassign)

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
