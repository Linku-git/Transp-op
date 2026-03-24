# Session 27 — Scenario Simulation Backend

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-23|Session 23]], [[sessions/session-26|Session 26]]

> Previous: [[sessions/session-26|Session 26]] | Next: [[sessions/session-28|Session 28]]

## Complexity: Medium

## Objective
Implement scenario simulation: different conditions (rain, strike, peak) with demand multipliers and multi-scenario comparison.

---

## Tasks

- [ ] Create `backend/app/services/scenarios.py` — Scenario engine:
  - Condition types: normal, pluie, greve_transport, pic_activite, nuit, defaillance_tc
  - Demand multipliers per condition
  - Re-run optimization with adjusted parameters
  - Store scenario results for comparison
- [ ] Create `backend/app/schemas/scenario.py` — Pydantic schemas:
  - `ScenarioRequest` — condition_type, demand_multiplier, custom_params
  - `ScenarioResponse` — Results with metrics
  - `ScenarioComparison` — Side-by-side metrics
- [ ] Create `backend/app/api/v1/scenarios.py` — Endpoints:
  - POST `/scenarios/simulate` — Run scenario
  - GET `/scenarios` — List saved scenarios
  - GET `/scenarios/{id}` — Get single scenario
  - DELETE `/scenarios/{id}` — Delete scenario
  - POST `/scenarios/compare` — Compare 2-3 scenarios side-by-side
- [ ] Implement comparison metrics: vehicles delta, cost delta, CO2 delta, RTI compliance
- [ ] Register scenarios router
- [ ] Create `backend/tests/test_scenarios.py`

## Files to Create/Modify
- `backend/app/services/scenarios.py` (create)
- `backend/app/schemas/scenario.py` (create)
- `backend/app/api/v1/scenarios.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_scenarios.py` (create)

## Tests
- [ ] `test_simulate_rain` — Rain scenario increases vehicle demand
- [ ] `test_simulate_strike` — Strike scenario increases demand significantly
- [ ] `test_simulate_peak` — Peak scenario handles extra headcount
- [ ] `test_compare_scenarios` — Comparison returns delta metrics
- [ ] `test_list_scenarios` — Returns saved scenarios
- [ ] `test_delete_scenario` — Deletes scenario

## Acceptance Criteria
- Scenarios produce valid optimization results with adjusted parameters
- Demand multipliers correctly affect vehicle/route counts
- Comparison provides meaningful delta metrics
- All 6 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
