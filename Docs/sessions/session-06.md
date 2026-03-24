# Session 06 — Site Model & CRUD API

## Phase: 1 — MVP Core (Module A)
## Prerequisites: [[sessions/session-02|Session 02]], [[sessions/session-04|Session 04]]

> Previous: [[sessions/session-05|Session 05]] | Next: [[sessions/session-07|Session 07]]

## Complexity: Medium

## Objective
Implement the Site database model with PostGIS support and full CRUD API endpoints with validation.

---

## Tasks

- [ ] Create `backend/app/models/site.py` — Site model (all fields from DATABASE_SCHEMA.md: code, name, address, city, lat/lng, geom, shifts, ZFE, security_profile, etc.)
- [ ] Create Alembic migration for site table with PostGIS geometry column and spatial index
- [ ] Create `backend/app/schemas/site.py` — Pydantic schemas:
  - `SiteCreate` — Required fields with validation (code unique, lat/lng range, shifts 1-3)
  - `SiteUpdate` — Optional fields
  - `SiteResponse` — Full site data
  - `SiteListResponse` — Paginated list
  - `SiteSummary` — Summary with employee/vehicle counts
- [ ] Create `backend/app/api/v1/sites.py` — Endpoints:
  - GET `/sites` — List with filters (city, zfe_zone), pagination
  - GET `/sites/{id}` — Get by UUID
  - GET `/sites/code/{code}` — Get by site code
  - POST `/sites` — Create (validate unique code, create PostGIS point)
  - PUT `/sites/{id}` — Update (partial update support)
  - DELETE `/sites/{id}` — Delete (check for linked employees first)
  - GET `/sites/{id}/summary` — Employee count, vehicle count, PMR count
- [ ] Add tenant_id filtering (from JWT token) to all queries
- [ ] Register site router in `api/v1/__init__.py`
- [ ] Create `backend/tests/test_sites.py`

## Files to Create/Modify
- `backend/app/models/site.py` (create)
- `backend/app/schemas/site.py` (create)
- `backend/app/api/v1/sites.py` (create)
- `backend/app/models/__init__.py` (modify — add Site import)
- `backend/app/api/v1/__init__.py` (modify — register router)
- `backend/tests/test_sites.py` (create)
- `alembic/versions/xxxx_add_site_table.py` (auto-generated)

## Tests
- [ ] `test_create_site` — POST creates site with all fields, returns 201
- [ ] `test_create_site_duplicate_code` — Returns 409 conflict
- [ ] `test_create_site_invalid_lat` — Returns 422 validation error
- [ ] `test_list_sites` — GET returns paginated list
- [ ] `test_list_sites_filter_city` — Filters by city
- [ ] `test_list_sites_filter_zfe` — Filters by ZFE zone
- [ ] `test_get_site_by_id` — Returns single site
- [ ] `test_get_site_by_code` — Returns site by code
- [ ] `test_get_site_not_found` — Returns 404
- [ ] `test_update_site` — PUT updates fields
- [ ] `test_delete_site` — DELETE removes site
- [ ] `test_delete_site_with_employees` — Returns 409 (has linked employees)
- [ ] `test_site_summary` — Returns correct counts
- [ ] `test_postgis_geometry_created` — Verifies geom column populated

## Acceptance Criteria
- All CRUD operations work correctly
- PostGIS geometry column auto-populated from lat/lng
- Pagination works with `?page=1&page_size=20`
- City and ZFE filters work
- Unique code constraint enforced
- All 14 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
