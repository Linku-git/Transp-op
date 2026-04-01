# Session 17 — Mobility Scores & Shadow Zones

## Phase: 1 — MVP Core (Module C)
## Prerequisites: [[sessions/session-15|Session 15]]

> Previous: [[sessions/session-16|Session 16]] | Next: [[sessions/session-18|Session 18]]

## Complexity: Medium

## Objective
Implement mobility scoring algorithm and shadow zone identification.

---

## Tasks

- [x] Create `backend/app/services/mobility_scoring.py` — Scoring engine:
  - Per-employee mobility score (0-100) based on: distance, mode, interest, constraints
  - Per-group score (site, team, shift) — average of employee scores
  - Per-time-slot score — availability by hour
- [x] Implement shadow zone identification:
  - Employees with no satisfactory transport solution
  - Criteria: distance > threshold, no public transit, no company transport opt-in
  - Return list with map coordinates
- [x] Create `backend/app/services/modal_analytics.py` — Advanced analytics:
  - Weather-dependent modal analysis (how many switch modes in rain)
  - Disruption modal identification (which modes lose riders)
  - Carpool contribution potential (volunteer driver seats vs demand by corridor)
- [x] Enhance `/modal/mobility-scores` endpoint with group/site aggregation
- [x] Enhance `/modal/shift-analysis` with detailed disruption data
- [x] Add shadow zones endpoint (`/modal/shadow-zones`) and carpool potential (`/modal/carpool-potential`)
- [x] Create `backend/tests/test_mobility_scoring.py`

## Files to Create/Modify
- `backend/app/services/mobility_scoring.py` (create)
- `backend/app/services/modal_analytics.py` (create)
- `backend/app/api/v1/modal.py` (modify)
- `backend/tests/test_mobility_scoring.py` (create)

## Tests
- [x] `test_employee_score_calculation` — Correct score for known input
- [x] `test_group_score_aggregation` — Correct average per site
- [x] `test_shadow_zone_identification` — Correctly identifies shadow zones
- [x] `test_weather_modal_shift` — Correct shift counts
- [x] `test_carpool_potential` — Correct seat supply vs demand
- [x] `test_zero_mobility_score` — Employee with no options scores 0

## Test Results
- Tests written: 6
- Tests passing: 6
- Tests failing: 0
- Full suite: 77 passed

## Acceptance Criteria
- Mobility scores correctly reflect employee transport situation
- Shadow zones identified for employees without solutions
- Weather-dependent analysis produces meaningful results
- All 6 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
