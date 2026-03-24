# Session 29 — Settings & Constraints CRUD

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-02|Session 02]], [[sessions/session-03|Session 03]]

> Previous: [[sessions/session-28|Session 28]] | Next: [[sessions/session-30|Session 30]]

## Complexity: Low

## Objective
Implement settings and constraints management (backend + frontend) for optimization parameters.

---

## Tasks

- [ ] Create `backend/app/models/settings.py` — Settings and Constraint models
- [ ] Create Alembic migration for settings and constraint_param tables
- [ ] Create `backend/app/schemas/settings.py` — Pydantic schemas
- [ ] Create `backend/app/api/v1/settings.py` — Endpoints:
  - GET `/settings` — Get current parameters
  - PUT `/settings` — Update parameters
- [ ] Create `backend/app/api/v1/constraints.py` — Endpoints:
  - GET `/constraints` — List with optional category filter
  - POST `/constraints` — Create constraint
  - PUT `/constraints/{id}` — Update
  - DELETE `/constraints/{id}` — Delete
  - POST `/constraints/bulk` — Bulk import
- [ ] Create `frontend/src/pages/settings/SettingsPage.tsx`:
  - Meeting radius slider
  - Max walking distance slider
  - Max route duration slider
  - Fuel cost input
  - RTI threshold input
  - Night mode hours
  - Min night group size
  - Save button
- [ ] Create `frontend/src/pages/settings/ConstraintsPage.tsx`:
  - Constraints table (key, value, category, description)
  - Inline add/edit/delete
  - Category filter
  - Import from Excel button
- [ ] Register settings and constraints routers
- [ ] Create `backend/tests/test_settings.py`

## Files to Create/Modify
- `backend/app/models/settings.py` (create)
- `backend/app/schemas/settings.py` (create)
- `backend/app/api/v1/settings.py` (create)
- `backend/app/api/v1/constraints.py` (create)
- `frontend/src/pages/settings/SettingsPage.tsx` (create)
- `frontend/src/pages/settings/ConstraintsPage.tsx` (create)
- `backend/tests/test_settings.py` (create)

## Tests
- [ ] `test_get_settings` — Returns current settings
- [ ] `test_update_settings` — Updates and persists
- [ ] `test_create_constraint` — Creates constraint
- [ ] `test_list_constraints_by_category` — Category filter works
- [ ] `test_bulk_import_constraints` — Bulk import works
- [ ] `test_delete_constraint` — Deletes constraint

## Acceptance Criteria
- Settings page displays and saves all parameters
- Constraints CRUD works with category filtering
- Bulk constraint import from template
- All 6 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
