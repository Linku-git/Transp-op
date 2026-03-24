# Session 12 — Employee Leave Model & API

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-11|Session 11]] | Next: [[sessions/session-13|Session 13]]

## Complexity: Low

## Objective
Implement the EmployeeLeave model and CRUD API for managing employee leave/vacation periods.

---

## Tasks

- [ ] Create `backend/app/models/leave.py` — EmployeeLeave model (employee_id FK, leave_type, start_date, end_date, notes)
- [ ] Create Alembic migration for employee_leave table
- [ ] Create `backend/app/schemas/leave.py` — Pydantic schemas (LeaveCreate, LeaveUpdate, LeaveResponse)
- [ ] Create `backend/app/api/v1/leaves.py` — Endpoints:
  - POST `/leaves` — Create leave period
  - GET `/leaves` — List with filters (employee_id, site_id, date_from, date_to)
  - GET `/leaves/{id}` — Get single leave
  - PUT `/leaves/{id}` — Update leave
  - DELETE `/leaves/{id}` — Delete leave
- [ ] Add leave_type enum validation: vacation, sick, unpaid, formation, mission, other
- [ ] Add date validation (end_date >= start_date)
- [ ] Register leaves router
- [ ] Create `backend/tests/test_leaves.py`

## Files to Create/Modify
- `backend/app/models/leave.py` (create)
- `backend/app/schemas/leave.py` (create)
- `backend/app/api/v1/leaves.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_leaves.py` (create)

## Tests
- [ ] `test_create_leave` — Creates leave with valid data
- [ ] `test_create_leave_invalid_dates` — end_date < start_date returns 422
- [ ] `test_create_leave_invalid_type` — Unknown type returns 422
- [ ] `test_list_leaves_filter_employee` — Filters by employee_id
- [ ] `test_list_leaves_filter_date_range` — Filters by date range
- [ ] `test_update_leave` — Updates successfully
- [ ] `test_delete_leave` — Deletes successfully
- [ ] `test_overlapping_leave_check` — Handles overlapping periods

## Acceptance Criteria
- CRUD operations work for leaves
- Leave types are validated against allowed values
- Date range filtering works correctly
- Overlapping period detection works
- All 8 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
