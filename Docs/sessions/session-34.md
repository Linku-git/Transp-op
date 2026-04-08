# Session 34 — Investment Model Comparator

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-32|Session 32]], [[sessions/session-33|Session 33]]
## Complexity: Medium
> Previous: [[sessions/session-33|Session 33]] | Next: [[sessions/session-35|Session 35]]

## Objective
Build the investment model comparator that compares CAPEX (own fleet), mise a disposition, and OPEX (full outsource) models side by side, with sensitivity analysis for key cost drivers.

---

## Tasks

- [x] Create `backend/app/services/investment_comparator.py` — Comparator engine:
  - **CAPEX (own fleet)**: vehicle purchase + internal drivers + maintenance + fuel + insurance + depreciation
  - **Mise a disposition**: monthly vehicle rental fee + fuel + management overhead
  - **OPEX (full outsource)**: per-km fee from transport operator, no capital investment
  - Side-by-side comparison with configurable duration (1-10 years)
  - Compute total cost, annual cost, cost per employee, cost per trip for each model
  - Recommend optimal model based on fleet size and duration (with >20% cost override)
- [x] Implement sensitivity analysis:
  - What-if sliders: fuel price (+/-50%), headcount (+/-50%), fill rate (50%-100%)
  - Recompute all 3 models with adjusted parameters
  - Return delta vs baseline for each parameter change
- [x] Create Pydantic request/response schemas for comparison and sensitivity
- [x] Create POST `/financial/compare` endpoint in `backend/app/api/v1/financial.py`
- [x] Create POST `/financial/compare/sensitivity` endpoint for sensitivity analysis
- [x] Create `backend/tests/test_investment_comparator.py`

## Files Created/Modified
- `backend/app/services/investment_comparator.py` (created) — CAPEX/MaD/OPEX + recommendation + sensitivity
- `backend/app/api/v1/financial.py` (modified) — 2 new endpoints
- `backend/app/schemas/financial.py` (modified) — 8 new comparison/sensitivity schemas
- `backend/tests/test_investment_comparator.py` (created) — 11 tests

## Tests
- [x] `test_capex_model_calculation` — CAPEX model produces correct total cost
- [x] `test_mise_a_disposition_calculation` — Mise a disposition model produces correct total cost
- [x] `test_opex_model_calculation` — OPEX model produces correct total cost
- [x] `test_side_by_side_comparison` — All 3 models returned with correct relative costs
- [x] `test_recommendation_small_fleet` — Small fleet recommends OPEX or cheapest model
- [x] `test_recommendation_large_fleet` — Large fleet recommends CAPEX
- [x] `test_sensitivity_fuel_price` — Fuel price increase affects CAPEX/MaD, not OPEX
- [x] `test_sensitivity_headcount` — Headcount change scales cost per employee
- [x] `test_sensitivity_fill_rate` — Lower fill rate increases cost per employee
- [x] `test_compare_endpoint` — POST /financial/compare returns valid response
- [x] `test_sensitivity_endpoint` — POST /financial/compare/sensitivity returns valid response

## Test Results
- Tests written: 11
- Tests passing: 11
- Tests failing: 0

## Acceptance Criteria
- All 3 investment models calculate correctly with configurable duration
- Side-by-side comparison returns consistent and comparable metrics
- Sensitivity analysis adjusts parameters and shows deltas vs baseline
- Model recommendation logic is sound for different fleet sizes
- All 9 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
