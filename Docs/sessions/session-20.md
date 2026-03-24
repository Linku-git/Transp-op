# Session 20 — Vehicle Model & Fleet API

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-06|Session 06]]

> Previous: [[sessions/session-19|Session 19]] | Next: [[sessions/session-21|Session 21]]

## Complexity: Medium

## Objective
Implement the Vehicle model and fleet management CRUD API with fleet summary statistics.

---

## Tasks

- [ ] Create `backend/app/models/vehicle.py` — Vehicle model (all fields: type, brand_model, capacity, year, owner_type, monthly_cost, condition, site_id FK, PMR, fuel_consumption, motorization, ZFE, etc.)
- [ ] Create Alembic migration for vehicle table
- [ ] Create `backend/app/schemas/vehicle.py` — Pydantic schemas:
  - `VehicleCreate` — Required fields with enum validation (condition, motorization)
  - `VehicleUpdate` — Optional fields
  - `VehicleResponse` — Full data with site name
  - `FleetSummary` — Aggregated fleet overview
- [ ] Create `backend/app/api/v1/vehicles.py` — Endpoints:
  - GET `/vehicles` — List with filters (site_id, is_pmr_accessible, condition, motorization, zfe_compliant)
  - POST `/vehicles` — Create vehicle
  - PUT `/vehicles/{id}` — Update vehicle
  - DELETE `/vehicles/{id}` — Delete vehicle
  - GET `/vehicles/fleet-summary` — Fleet overview by site, type, condition, motorization
- [ ] Validate condition enum: Bon, Moyen, Mauvais
- [ ] Validate motorization enum: diesel, hybrid, electric, hydrogen, gnv
- [ ] Register vehicle router
- [ ] Create `backend/tests/test_vehicles.py`

## Files to Create/Modify
- `backend/app/models/vehicle.py` (create)
- `backend/app/schemas/vehicle.py` (create)
- `backend/app/api/v1/vehicles.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_vehicles.py` (create)

## Tests
- [ ] `test_create_vehicle` — Creates with all fields
- [ ] `test_create_vehicle_invalid_condition` — Returns 422
- [ ] `test_create_vehicle_invalid_motorization` — Returns 422
- [ ] `test_list_vehicles` — Returns paginated list
- [ ] `test_filter_by_site` — Filters by site_id
- [ ] `test_filter_by_pmr` — Filters PMR-accessible vehicles
- [ ] `test_filter_by_motorization` — Filters by motorization
- [ ] `test_filter_by_zfe` — Filters ZFE-compliant vehicles
- [ ] `test_update_vehicle` — PUT updates fields
- [ ] `test_delete_vehicle` — DELETE removes vehicle
- [ ] `test_fleet_summary` — Returns correct aggregations per site, type, condition

## Acceptance Criteria
- Vehicle CRUD works with all fields
- Enum validation enforced (condition, motorization)
- Multiple filters work simultaneously
- Fleet summary provides correct aggregations
- All 11 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
