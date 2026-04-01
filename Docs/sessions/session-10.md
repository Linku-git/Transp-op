# Session 10 — Employee Frontend Pages

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-09|Session 09]] | Next: [[sessions/session-11|Session 11]]

## Complexity: Medium

## Objective
Build employee management frontend: list with filters, create/edit forms, detail view.

---

## Tasks

- [x] Create `frontend/src/api/employees.ts` — API client functions
- [x] Create `frontend/src/types/employee.ts` — Employee TypeScript interfaces
- [x] Create `frontend/src/stores/employeeStore.ts` — Zustand store
- [x] Create `frontend/src/pages/employees/EmployeeListPage.tsx` — DataTable with columns: matricule, name, site, shift, PMR badge, transport mode, opt-in status
- [x] Add filters: site dropdown, shift dropdown, PMR toggle, department, active/inactive
- [x] Add search bar (name/matricule)
- [x] Create `frontend/src/pages/employees/EmployeeCreatePage.tsx` — Form:
  - Personal info (matricule, name, phone)
  - Site + shift dropdowns (site loads shifts dynamically)
  - Address with auto-geocode button
  - PMR toggle
  - Transport profile (current mode, opt-in, has car, volunteer, carpool seats)
- [x] Create `frontend/src/pages/employees/EmployeeEditPage.tsx` — Pre-filled form
- [x] Create `frontend/src/pages/employees/EmployeeDetailPage.tsx` — Profile card, mini-map (home + site), transport info
- [x] Add employee routes to `routes.tsx`
- [x] Add "Employees" link to Sidebar
- [x] Handle loading, error, and empty states

## Files to Create/Modify
- `frontend/src/api/employees.ts` (create)
- `frontend/src/types/employee.ts` (create)
- `frontend/src/stores/employeeStore.ts` (create)
- `frontend/src/pages/employees/EmployeeListPage.tsx` (create)
- `frontend/src/pages/employees/EmployeeCreatePage.tsx` (create)
- `frontend/src/pages/employees/EmployeeEditPage.tsx` (create)
- `frontend/src/pages/employees/EmployeeDetailPage.tsx` (create)
- `frontend/src/routes.tsx` (modify)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

## Tests
- [x] `EmployeeListPage.test.tsx` — Renders table, filters work
- [x] `EmployeeCreatePage.test.tsx` — Form validates, submit calls API
- [x] `EmployeeDetailPage.test.tsx` — Displays profile with site info

## Acceptance Criteria
- Employee list shows all employees with proper columns
- All filters work (site, shift, PMR, department, active)
- Create form dynamically loads shifts from selected site
- Edit page pre-fills all fields
- Detail page shows mini-map with home and site markers

## Test Results
- Tests written: 3 (EmployeeListPage, EmployeeCreatePage, EmployeeDetailPage)
- Tests passing: 20 frontend (3 new + 17 prior)
- Tests failing: 0

## Notes
- Extracted shared EmployeeForm component used by Create and Edit pages (same pattern as SiteForm)
- EmployeeDetailPage uses CircleMarker with two colors: teal for employee home, navy for site location
- EmployeeListPage reads `site_id` from URL search params to support deep-linking from SiteDetailPage
- EmployeeForm includes conditional carpool_seats field shown only when volunteer_driver is toggled on
- Added 70+ i18n keys in `employees` namespace for both FR and EN

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
