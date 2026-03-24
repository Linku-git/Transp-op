# Session 32 — TCO Calculator Engine

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-31|Session 31]]
## Complexity: High
> Previous: [[sessions/session-31|Session 31]] | Next: [[sessions/session-33|Session 33]]

## Objective
Build the Total Cost of Ownership (TCO) calculator engine supporting per-vehicle and fleet-level TCO, motorization comparison, and configurable duration evolution.

---

## Tasks

- [ ] Create `backend/app/services/tco_calculator.py` — TCO engine:
  - Core TCO formula: `TCO = Purchase + (Annual_Maintenance x Duration) + (Energy_Cost_per_km x Annual_km x Duration) - Residual_Value`
  - Per-vehicle TCO calculation given vehicle type, motorization, and duration
  - Fleet-level TCO aggregation (sum of per-vehicle TCOs for a fleet composition)
  - Motorization comparison: compute TCO for diesel, hybrid, electric, hydrogen side by side
  - TCO evolution over configurable duration (1-10 years), returning year-by-year breakdown
  - Use `VehicleReference` defaults with optional overrides
- [ ] Create POST `/financial/tco/calculate` endpoint in `backend/app/api/v1/financial.py`:
  - Accepts fleet composition, motorization, duration, and optional cost overrides
  - Returns per-vehicle TCO, fleet TCO, year-by-year evolution, motorization comparison
- [ ] Create Pydantic request/response schemas for TCO calculation
- [ ] Create `backend/tests/test_tco_calculator.py`

## Files to Create/Modify
- `backend/app/services/tco_calculator.py` (create)
- `backend/app/api/v1/financial.py` (modify)
- `backend/app/schemas/financial.py` (modify)
- `backend/tests/test_tco_calculator.py` (create)

## Tests
- [ ] `test_tco_single_vehicle_known_values` — Known input produces expected TCO output
- [ ] `test_tco_formula_components` — Each formula component (purchase, maintenance, energy, residual) calculated correctly
- [ ] `test_tco_diesel_vs_electric` — Electric has higher purchase but lower energy cost over 10 years
- [ ] `test_tco_motorization_comparison` — All 4 motorizations computed and returned
- [ ] `test_tco_fleet_aggregation` — Fleet of mixed vehicles sums correctly
- [ ] `test_tco_evolution_over_years` — Year-by-year breakdown for 1-10 years is monotonically increasing
- [ ] `test_tco_with_custom_overrides` — Override default costs and verify output changes
- [ ] `test_tco_endpoint_response` — POST endpoint returns valid response structure

## Acceptance Criteria
- TCO formula matches PRD specification exactly
- Per-vehicle and fleet-level calculations are consistent
- Motorization comparison returns all 4 types with correct relative ordering
- Year-by-year evolution covers configurable duration (1-10 years)
- Custom cost overrides are applied correctly
- All 8 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
