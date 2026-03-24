# Session 31 — Financial Models & API

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-02|Session 02]]
## Complexity: Medium
> Previous: [[sessions/session-30|Session 30]] | Next: [[sessions/session-32|Session 32]]

## Objective
Create the SQLAlchemy models, Alembic migrations, Pydantic schemas, and CRUD API endpoints for financial scenarios, TCO entries, ROI calculations, and the vehicle reference catalog.

---

## Tasks

- [ ] Create `backend/app/models/financial.py` — SQLAlchemy models:
  - `FinancialScenario` — scenario metadata (name, description, duration, status, created_by)
  - `TCOEntry` — total cost of ownership line items (vehicle_type, motorization, purchase_cost, maintenance_annual, energy_cost_per_km, annual_km, residual_value, duration_years)
  - `ROICalculation` — ROI results per scenario (lever, value, assumptions JSON)
  - `VehicleReference` — vehicle catalog (type, capacity, motorizations, default costs)
- [ ] Create Alembic migration for all financial tables
- [ ] Create `backend/app/schemas/financial.py` — Pydantic schemas:
  - `FinancialScenarioCreate`, `FinancialScenarioRead`, `FinancialScenarioUpdate`
  - `TCOEntryCreate`, `TCOEntryRead`
  - `ROICalculationCreate`, `ROICalculationRead`
  - `VehicleReferenceRead`
- [ ] Create `backend/app/crud/financial.py` — CRUD operations for all financial models
- [ ] Create `backend/app/api/v1/financial.py` — API endpoints:
  - POST/GET/PUT/DELETE `/financial/scenarios`
  - POST/GET `/financial/scenarios/{id}/tco-entries`
  - GET `/financial/vehicles` — vehicle reference catalog
- [ ] Register financial router in API v1
- [ ] Seed `VehicleReference` catalog with 5 vehicle types from PRD:
  - `minibus` (20 seats)
  - `midibus` (30 seats)
  - `bus_standard` (50 seats)
  - `grand_bus` (70 seats)
  - `vehicule_leger` (9 seats)
- [ ] Create `backend/tests/test_financial_models.py`

## Files to Create/Modify
- `backend/app/models/financial.py` (create)
- `backend/alembic/versions/xxx_add_financial_tables.py` (create)
- `backend/app/schemas/financial.py` (create)
- `backend/app/crud/financial.py` (create)
- `backend/app/api/v1/financial.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/app/db/seed_vehicles.py` (create)
- `backend/tests/test_financial_models.py` (create)

## Tests
- [ ] `test_create_financial_scenario` — Create and retrieve a scenario
- [ ] `test_update_financial_scenario` — Update scenario fields
- [ ] `test_delete_financial_scenario` — Delete scenario and cascade
- [ ] `test_create_tco_entry` — Create TCO entry linked to scenario
- [ ] `test_schema_validation` — Pydantic rejects invalid data (negative costs, missing fields)
- [ ] `test_vehicle_catalog_seeded` — All 5 vehicle types present after seeding
- [ ] `test_vehicle_catalog_endpoint` — GET `/financial/vehicles` returns full catalog

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
