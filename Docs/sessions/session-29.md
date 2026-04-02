# Session 29 — Settings & Constraints CRUD

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-02|Session 02]], [[sessions/session-03|Session 03]]

> Previous: [[sessions/session-28|Session 28]] | Next: [[sessions/session-30|Session 30]]

## Complexity: Low

## Objective
Implement settings and constraints management (backend + frontend) for optimization parameters.

---

## Tasks

- [x] Create `backend/app/models/settings.py` — OptimizationSettings model (tenant-scoped, UniqueConstraint on tenant_id) and ConstraintParam model (key-value, UniqueConstraint on tenant_id+key)
- [x] Create Alembic migration for optimization_settings and constraint_param tables (`backend/alembic/versions/b2c3d4e5f6a7_add_settings_tables.py`)
- [x] Create `backend/app/schemas/settings.py` — Pydantic v2 schemas for settings and constraints CRUD
- [x] Create `backend/app/api/v1/settings.py` — Endpoints:
  - GET `/settings` — Get current parameters (get-or-create default)
  - PUT `/settings` — Update parameters (partial update)
- [x] Create `backend/app/api/v1/constraints.py` — Endpoints:
  - GET `/constraints` — List with optional category filter
  - POST `/constraints` — Create constraint
  - PUT `/constraints/{id}` — Update
  - DELETE `/constraints/{id}` — Delete
  - POST `/constraints/bulk` — Bulk import
- [x] Create `frontend/src/types/settings.ts` — TypeScript interfaces for settings and constraints
- [x] Create `frontend/src/api/settings.ts` — API client (7 functions)
- [x] Create `frontend/src/pages/settings/SettingsPage.tsx`:
  - Meeting radius slider
  - Max walking distance slider
  - Max route duration slider
  - Fuel cost input
  - Fuel consumption input
  - CO2 per liter input
  - RTI threshold input
  - Night mode hours (start/end)
  - Min night group size
  - Save button
- [x] Create `frontend/src/pages/settings/ConstraintsPage.tsx`:
  - Constraints table (key, value, category, description)
  - Inline add/edit/delete
  - Category filter
  - Import from Excel button
- [x] Register settings and constraints routers in `backend/app/api/v1/__init__.py`
- [x] Add model imports in `backend/app/models/__init__.py`
- [x] Add routes in `frontend/src/routes.tsx` for `/settings` and `/settings/constraints`
- [x] Add i18n translations in `frontend/src/i18n/fr.json` and `en.json`
- [x] Create `backend/tests/test_settings.py` — 6 backend tests
- [x] Create `frontend/src/pages/settings/__tests__/SettingsPage.test.tsx` — 6 tests
- [x] Create `frontend/src/pages/settings/__tests__/ConstraintsPage.test.tsx` — 10 tests
- [x] **Browser verification**: Open `http://localhost:5173` in Chrome, verify new pages render correctly, check DevTools Console for errors, test navigation

## Files Created
- `backend/app/models/settings.py`
- `backend/app/schemas/settings.py`
- `backend/app/api/v1/settings.py`
- `backend/app/api/v1/constraints.py`
- `backend/alembic/versions/b2c3d4e5f6a7_add_settings_tables.py`
- `backend/tests/test_settings.py`
- `frontend/src/types/settings.ts`
- `frontend/src/api/settings.ts`
- `frontend/src/pages/settings/SettingsPage.tsx`
- `frontend/src/pages/settings/ConstraintsPage.tsx`
- `frontend/src/pages/settings/__tests__/SettingsPage.test.tsx`
- `frontend/src/pages/settings/__tests__/ConstraintsPage.test.tsx`

## Files Modified
- `backend/app/api/v1/__init__.py` — Registered settings and constraints routers
- `backend/app/models/__init__.py` — Added OptimizationSettings and ConstraintParam imports
- `frontend/src/routes.tsx` — Added /settings and /settings/constraints routes
- `frontend/src/i18n/fr.json` — Added settings translations
- `frontend/src/i18n/en.json` — Added settings translations

## Tests

- [x] `test_get_settings` — Returns current settings (get-or-create)
- [x] `test_update_settings` — Updates and persists
- [x] `test_create_constraint` — Creates constraint
- [x] `test_list_constraints_by_category` — Category filter works
- [x] `test_bulk_import_constraints` — Bulk import works
- [x] `test_delete_constraint` — Deletes constraint

## Test Results
- Backend tests written: 6
- Backend tests passing: 6 (150 total backend tests pass)
- Frontend tests written: 16 (6 SettingsPage + 10 ConstraintsPage)
- Frontend tests passing: 16
- Total new tests: 22
- Coverage: Not measured

## Acceptance Criteria
- [x] Settings page displays and saves all parameters
- [x] Constraints CRUD works with category filtering
- [x] Bulk constraint import from template
- [x] All 6 backend tests pass
- [x] Browser verification passes: no console errors, pages render correctly, navigation works

## Notes
- OptimizationSettings model uses one-row-per-tenant pattern with UniqueConstraint on tenant_id, and get-or-create logic on GET to ensure defaults exist
- ConstraintParam model uses UniqueConstraint on (tenant_id, key) to prevent duplicate keys per tenant
- Settings PUT endpoint supports partial updates (only supplied fields are changed)
- SettingsPage uses range sliders for distance/duration parameters and number inputs for cost fields, with time inputs for night mode hours
- ConstraintsPage includes inline editing, category filter dropdown, and bulk import support
- New DB tables: `optimization_settings` and `constraint_param` (2 tables added)
- New endpoints: 7 total (2 settings + 5 constraints)
- New frontend pages: 2 (SettingsPage, ConstraintsPage)

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[DATABASE_SCHEMA]] — Database schema
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
