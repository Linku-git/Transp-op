# Session 19 — Meeting Zone Optimization

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-18|Session 18]]

> Previous: [[sessions/session-18|Session 18]] | Next: [[sessions/session-20|Session 20]]

## Complexity: Medium

## Objective
Implement meeting zone (gathering point) optimization — calculating optimal pickup locations per cluster.

---

## Tasks

- [x] Create `backend/app/services/meeting_zones.py` — Meeting zone optimizer:
  - Calculate optimal centroid location per cluster
  - Snap to nearest road (using OSRM nearest service)
  - Verify safe parking area (road accessibility check)
  - Verify PMR accessibility for clusters with PMR employees
  - Verify walking distance constraint (all employees within max_walking_distance)
- [x] Implement employee-to-gathering-point assignment:
  - Each employee assigned to exactly one meeting zone
  - Compute walking distance from each employee to their gathering point
  - Verify constraint: walking distance <= max_walking_distance
- [x] Implement access leg computation:
  - Recommended walking path from employee home to gathering point
  - Distance and estimated walking time
- [x] Add meeting zone data to cluster response (POST /clusters/generate-with-zones)
- [x] Create `backend/app/services/osrm_client.py` — OSRM API client:
  - Nearest point on road
  - Walking route between two points
  - Driving route between points
  - Haversine fallback when OSRM unavailable
- [x] Create `backend/tests/test_meeting_zones.py`

## Files to Create/Modify
- `backend/app/services/meeting_zones.py` (create)
- `backend/app/services/osrm_client.py` (create)
- `backend/app/schemas/optimization.py` (modify — add meeting zone fields)
- `backend/tests/test_meeting_zones.py` (create)

## Tests
- [x] `test_centroid_snap_to_road` — Centroid snapped to nearest road
- [x] `test_walking_distance_constraint` — All employees within max distance
- [x] `test_pmr_accessibility` — PMR clusters get accessible zones
- [x] `test_employee_assignment` — Each employee assigned to one zone
- [x] `test_access_leg_calculation` — Walking distance/time computed
- [x] `test_osrm_nearest` — OSRM nearest service integration
- [x] `test_osrm_route` — OSRM route service integration

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0
- Full suite: 95 passed

## Acceptance Criteria
- Meeting zones are road-accessible locations
- All employees within walking distance constraint
- PMR clusters get accessible meeting zones
- Employee-to-zone assignment is 1:1
- OSRM integration works (mock for tests)
- All 7 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
