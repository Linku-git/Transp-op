# Session 31 — Financial Models & API

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-02|Session 02]]
## Complexity: Medium
> Previous: [[sessions/session-30|Session 30]] | Next: [[sessions/session-32|Session 32]]

## Objective
Create the SQLAlchemy models, Alembic migrations, Pydantic schemas, and CRUD API endpoints for financial scenarios, TCO entries, ROI calculations, and the vehicle reference catalog.

---

## Tasks

- [x] Create `backend/app/models/financial.py` — SQLAlchemy models:
  - `FinancialScenario` — scenario metadata (name, description, duration, status, created_by)
  - `TCOEntry` — total cost of ownership line items (vehicle_type, motorization, purchase_cost, maintenance_annual, energy_cost_per_km, annual_km, residual_value, duration_years)
  - `ROICalculation` — ROI results per scenario (lever, value, assumptions JSON)
  - `VehicleReference` — vehicle catalog (type, capacity, motorizations, default costs)
- [x] Create Alembic migration for all financial tables
- [x] Create `backend/app/schemas/financial.py` — Pydantic schemas:
  - `FinancialScenarioCreate`, `FinancialScenarioResponse`, `FinancialScenarioUpdate`
  - `TCOEntryCreate`, `TCOEntryResponse`
  - `ROICalculationCreate`, `ROICalculationResponse`
  - `VehicleReferenceResponse`
- [x] Create `backend/app/api/v1/financial.py` — API endpoints (CRUD inline, no separate crud file):
  - POST/GET/PUT/DELETE `/financial/scenarios`
  - POST/GET `/financial/scenarios/{id}/tco-entries`
  - GET `/financial/vehicles` — vehicle reference catalog
- [x] Register financial router in API v1
- [x] Seed `VehicleReference` catalog with 5 vehicle types from PRD:
  - `minibus` (15-20 seats)
  - `midibus` (25-35 seats)
  - `bus_standard` (40-55 seats)
  - `grand_bus` (60-80 seats)
  - `vehicule_leger` (5-9 seats)
- [x] Create `backend/tests/test_financial_models.py`

## Files Created/Modified
- `backend/app/models/financial.py` (created) — 4 models
- `backend/alembic/versions/c3d4e5f6a7b8_add_financial_tables.py` (created)
- `backend/app/schemas/financial.py` (created) — 8 schemas
- `backend/app/api/v1/financial.py` (created) — 8 endpoints
- `backend/app/api/v1/__init__.py` (modified) — registered financial router
- `backend/app/db/__init__.py` (created)
- `backend/app/db/seed_vehicles.py` (created) — 5 vehicle types
- `backend/app/models/__init__.py` (modified) — exports 4 new models
- `backend/app/main.py` (modified) — lifespan seed hook
- `backend/tests/test_financial_models.py` (created) — 7 tests

## Tests
- [x] `test_create_financial_scenario` — Create and retrieve a scenario
- [x] `test_update_financial_scenario` — Update scenario fields
- [x] `test_delete_financial_scenario` — Delete scenario and cascade
- [x] `test_create_tco_entry` — Create TCO entry linked to scenario
- [x] `test_list_tco_entries` — List TCO entries for a scenario
- [x] `test_schema_validation` — Pydantic rejects invalid data (negative costs, invalid types)
- [x] `test_vehicle_catalog_endpoint` — GET `/financial/vehicles` returns catalog

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0

## Acceptance Criteria
- All financial SQLAlchemy models migrate cleanly
- CRUD endpoints respond with correct status codes and payloads
- Pydantic schemas enforce valid data (positive costs, valid durations)
- Vehicle reference catalog contains all 5 PRD vehicle types with default costs
- All 7 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
