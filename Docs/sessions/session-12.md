# Session 12 — Employee Leave Model & API

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-11|Session 11]] | Next: [[sessions/session-13|Session 13]]

## Complexity: Low

## Objective
Implement the EmployeeLeave model and CRUD API for managing employee leave/vacation periods.

---

## Tasks

- [x] Create `backend/app/models/leave.py` — EmployeeLeave model (employee_id FK, leave_type, start_date, end_date, notes)
- [x] Create Alembic migration for employee_leave table
- [x] Create `backend/app/schemas/leave.py` — Pydantic schemas (LeaveCreate, LeaveUpdate, LeaveResponse)
- [x] Create `backend/app/api/v1/leaves.py` — Endpoints:
  - POST `/leaves` — Create leave period
  - GET `/leaves` — List with filters (employee_id, site_id, date_from, date_to)
  - GET `/leaves/{id}` — Get single leave
  - PUT `/leaves/{id}` — Update leave
  - DELETE `/leaves/{id}` — Delete leave
- [x] Add leave_type enum validation: vacation, sick, unpaid, formation, mission, other
- [x] Add date validation (end_date >= start_date)
- [x] Register leaves router
- [x] Create `backend/tests/test_leaves.py`

## Files to Create/Modify
- `backend/app/models/leave.py` (create)
- `backend/app/schemas/leave.py` (create)
- `backend/app/api/v1/leaves.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_leaves.py` (create)

## Tests
- [x] `test_create_leave` — Creates leave with valid data
- [x] `test_create_leave_invalid_dates` — end_date < start_date returns 422
- [x] `test_create_leave_invalid_type` — Unknown type returns 422
- [x] `test_list_leaves_filter_employee` — Filters by employee_id
- [x] `test_list_leaves_filter_date_range` — Filters by date range
- [x] `test_update_leave` — Updates successfully
- [x] `test_delete_leave` — Deletes successfully
- [x] `test_overlapping_leave_check` — Handles overlapping periods

## Acceptance Criteria
- CRUD operations work for leaves
- Leave types are validated against allowed values
- Date range filtering works correctly
- Overlapping period detection works
- All 8 tests pass

## Test Results
- Tests written: 8
- Tests passing: 49 (8 new + 41 prior backend)
- Tests failing: 0

## Notes
- Overlap detection uses `start_date <= new_end AND end_date >= new_start` with self-exclusion on update
- Hard delete (not soft-delete) for leaves — they're temporal records, not entities
- Leave list supports site_id filter via employee join (useful for site-level absence views)

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
