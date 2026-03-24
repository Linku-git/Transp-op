# Session 15 — Modal Analysis Model & API

## Phase: 1 — MVP Core (Module C)
## Prerequisites: [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-14|Session 14]] | Next: [[sessions/session-16|Session 16]]

## Complexity: Medium

## Objective
Implement the EmployeeModal model and API endpoints for transport usage data and modal distribution statistics.

---

## Tasks

- [ ] Create `backend/app/models/modal.py` — EmployeeModal model (all fields: primary_mode, alternative_mode, distance_km, travel_time, frequency, interest, pickup preferences, volunteer driver, etc.)
- [ ] Create Alembic migration for employee_modal table (unique on employee_id)
- [ ] Create `backend/app/schemas/modal.py` — Pydantic schemas:
  - `ModalCreate` — All modal fields with enum validation for modes
  - `ModalUpdate` — Optional fields
  - `ModalResponse` — Full modal data with employee name
  - `ModalStats` — Aggregated distribution data
  - `MobilityScore` — Per-employee/group score
- [ ] Define transport mode enum: vehicule_particulier, covoiturage, deux_roues_motorise, deux_roues_non_motorise, transport_public, auto_stop, navette_entreprise, autre
- [ ] Create `backend/app/api/v1/modal.py` — Endpoints:
  - GET `/employees/{id}/modal` — Get modal data for employee
  - PUT `/employees/{id}/modal` — Create/update modal data (upsert)
  - DELETE `/employees/{id}/modal` — Delete modal data
  - GET `/modal/stats` — Global modal distribution (count per mode, per site)
  - GET `/modal/shift-analysis` — Modal shift analysis (disruption impact)
  - GET `/modal/mobility-scores` — Mobility scores per employee/group/site
- [ ] Implement modal distribution statistics (pie chart data: mode -> count -> percentage)
- [ ] Implement shift analysis (how many switch modes under disruption)
- [ ] Register modal router
- [ ] Create `backend/tests/test_modal.py`

## Files to Create/Modify
- `backend/app/models/modal.py` (create)
- `backend/app/schemas/modal.py` (create)
- `backend/app/api/v1/modal.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_modal.py` (create)

## Tests
- [ ] `test_create_modal` — PUT creates modal data
- [ ] `test_update_modal` — PUT updates existing modal data
- [ ] `test_get_modal` — GET returns modal data with employee info
- [ ] `test_delete_modal` — DELETE removes modal data
- [ ] `test_modal_stats` — Returns correct mode distribution
- [ ] `test_modal_stats_per_site` — Filters by site
- [ ] `test_shift_analysis` — Returns disruption modal shift data
- [ ] `test_mobility_scores` — Returns scores per employee
- [ ] `test_invalid_mode` — Invalid transport mode returns 422

## Acceptance Criteria
- Modal data CRUD works (upsert pattern)
- Transport mode enums validated
- Statistics endpoints return correct aggregations
- Modal shift analysis shows weather-dependent patterns
- All 9 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
