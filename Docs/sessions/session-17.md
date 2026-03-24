# Session 17 — Mobility Scores & Shadow Zones

## Phase: 1 — MVP Core (Module C)
## Prerequisites: [[sessions/session-15|Session 15]]

> Previous: [[sessions/session-16|Session 16]] | Next: [[sessions/session-18|Session 18]]

## Complexity: Medium

## Objective
Implement mobility scoring algorithm and shadow zone identification.

---

## Tasks

- [ ] Create `backend/app/services/mobility_scoring.py` — Scoring engine:
  - Per-employee mobility score (0-100) based on: distance, mode, interest, constraints
  - Per-group score (site, team, shift) — average of employee scores
  - Per-time-slot score — availability by hour
- [ ] Implement shadow zone identification:
  - Employees with no satisfactory transport solution
  - Criteria: distance > threshold, no public transit, no company transport opt-in
  - Return list with map coordinates
- [ ] Create `backend/app/services/modal_analytics.py` — Advanced analytics:
  - Weather-dependent modal analysis (how many switch modes in rain)
  - Disruption modal identification (which modes lose riders)
  - Carpool contribution potential (volunteer driver seats vs demand by corridor)
- [ ] Enhance `/modal/mobility-scores` endpoint with group/site aggregation
- [ ] Enhance `/modal/shift-analysis` with detailed disruption data
- [ ] Add shadow zones to employee summary endpoint
- [ ] Create `backend/tests/test_mobility_scoring.py`

## Files to Create/Modify
- `backend/app/services/mobility_scoring.py` (create)
- `backend/app/services/modal_analytics.py` (create)
- `backend/app/api/v1/modal.py` (modify)
- `backend/tests/test_mobility_scoring.py` (create)

## Tests
- [ ] `test_employee_score_calculation` — Correct score for known input
- [ ] `test_group_score_aggregation` — Correct average per site
- [ ] `test_shadow_zone_identification` — Correctly identifies shadow zones
- [ ] `test_weather_modal_shift` — Correct shift counts
- [ ] `test_carpool_potential` — Correct seat supply vs demand
- [ ] `test_zero_mobility_score` — Employee with no options scores 0

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
