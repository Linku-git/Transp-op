# Session 09 — Employee Model & CRUD API

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-06|Session 06]]

> Previous: [[sessions/session-08|Session 08]] | Next: [[sessions/session-10|Session 10]]

## Complexity: High

## Objective
Implement the Employee database model with geocoding integration and full CRUD API including bulk CSV upload.

---

## Tasks

- [ ] Create `backend/app/models/employee.py` — Employee model (all fields: matricule, name, site_id FK, shift, address, lat/lng, geom, PMR, transport mode, volunteer driver, etc.)
- [ ] Create Alembic migration for employee table with indexes (tenant, site, geom, active)
- [ ] Create `backend/app/schemas/employee.py` — Pydantic schemas:
  - `EmployeeCreate` — Required fields, inline transport_profile
  - `EmployeeUpdate` — Optional fields
  - `EmployeeResponse` — Full data with site name
  - `EmployeeListResponse` — Paginated with filters
  - `EmployeeSummary` — Counts by site, PMR breakdown
- [ ] Create `backend/app/services/geocoding.py` — Geocoding service:
  - Address to GPS (Nominatim/Google Geocoding)
  - Batch geocoding for imports
  - Reverse geocoding (GPS to address)
- [ ] Create `backend/app/api/v1/employees.py` — Endpoints:
  - GET `/employees` — List with filters (site_id, is_pmr, quartier, shift_time, department, active)
  - GET `/employees/{id}` — Get single
  - POST `/employees` — Create (auto-geocode if lat/lng missing, create PostGIS point)
  - PUT `/employees/{id}` — Update
  - DELETE `/employees/{id}` — Soft-delete (set active=false)
  - POST `/employees/upload` — Bulk CSV upload with validation
  - POST `/employees/geocode` — Geocode all employees missing GPS
  - GET `/employees/summary` — Summary with site/PMR breakdowns
- [ ] Implement tenant_id filtering on all queries
- [ ] Implement unique constraint on (tenant_id, matricule)
- [ ] Register employee router
- [ ] Create `backend/tests/test_employees.py`

## Files to Create/Modify
- `backend/app/models/employee.py` (create)
- `backend/app/schemas/employee.py` (create)
- `backend/app/services/geocoding.py` (create)
- `backend/app/api/v1/employees.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_employees.py` (create)

## Tests
- [ ] `test_create_employee` — POST creates with all fields
- [ ] `test_create_employee_duplicate_matricule` — Returns 409
- [ ] `test_create_employee_invalid_site` — Returns 404 (site not found)
- [ ] `test_list_employees` — Paginated list
- [ ] `test_filter_by_site` — Filters by site_id
- [ ] `test_filter_by_pmr` — Filters PMR employees
- [ ] `test_filter_by_shift` — Filters by shift_time
- [ ] `test_get_employee` — Returns single employee with site info
- [ ] `test_update_employee` — PUT updates fields
- [ ] `test_soft_delete_employee` — Sets active=false, still in DB
- [ ] `test_csv_upload` — Bulk creates from CSV
- [ ] `test_csv_upload_validation_errors` — Returns row-level errors
- [ ] `test_employee_summary` — Returns correct breakdowns
- [ ] `test_geocode_from_address` — Auto-fills lat/lng from address
- [ ] `test_postgis_geometry` — Geom column populated

## Acceptance Criteria
- All CRUD operations work with proper validation
- Soft-delete preserves data (active=false)
- CSV bulk upload handles valid and invalid rows
- Geocoding fills GPS from address
- PostGIS geometry auto-created
- All 15 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
