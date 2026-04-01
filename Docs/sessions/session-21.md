# Session 21 — Vehicle Assignment Algorithm

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-18|Session 18]], [[sessions/session-20|Session 20]]

> Previous: [[sessions/session-20|Session 20]] | Next: [[sessions/session-22|Session 22]]

## Complexity: High

## Objective
Implement vehicle-to-cluster assignment using bin-packing, including cluster split/merge and PMR-aware matching.

---

## Tasks

- [x] Create `backend/app/services/vehicle_assignment.py`:
  - Bin-packing: assign clusters to vehicles by capacity
  - Prefer existing fleet vehicles (from Vehicle table)
  - Split large clusters that exceed vehicle capacity
  - Merge small clusters that are geographically close
  - PMR matching: clusters with PMR employees must get PMR-accessible vehicles
  - ZFE compliance: sites in ZFE zones only get compliant vehicles
  - Minimize empty seats (maximize occupancy)
- [x] Create `backend/app/api/v1/vehicle_assignments.py` — Endpoints:
  - POST `/vehicle-assignments/assign` — Assign vehicles to clusters
  - POST `/vehicle-assignments/split-cluster/{id}` — Split oversized cluster
  - POST `/vehicle-assignments/merge-clusters` — Merge selected clusters
- [x] Implement optimization goals:
  - Minimize number of vehicles
  - Maximize occupancy rate
  - Respect PMR and ZFE constraints
- [x] Integrate volunteer drivers as supplemental capacity
- [x] Register vehicle assignment router
- [x] Create `backend/tests/test_vehicle_assignment.py`

## Files to Create/Modify
- `backend/app/services/vehicle_assignment.py` (create)
- `backend/app/api/v1/vehicle_assignments.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_vehicle_assignment.py` (create)

## Tests
- [x] `test_basic_assignment` — Clusters assigned to vehicles
- [x] `test_capacity_respected` — No vehicle exceeds capacity
- [x] `test_cluster_split` — Large cluster split into valid sub-clusters
- [x] `test_cluster_merge` — Small clusters merged
- [x] `test_pmr_matching` — PMR clusters get PMR vehicles
- [x] `test_zfe_compliance` — ZFE sites get compliant vehicles
- [x] `test_minimize_vehicles` — Fewer vehicles used when possible
- [x] `test_volunteer_integration` — Volunteer drivers supplement fleet
- [x] `test_no_vehicles_available` — Returns recommendation for needed vehicles

## Test Results
- Tests written: 9
- Tests passing: 9
- Tests failing: 0
- Coverage: Service layer fully covered

## Acceptance Criteria
- Assignment respects vehicle capacity constraints
- PMR and ZFE constraints enforced
- Split/merge operations produce valid clusters
- Occupancy rate maximized
- All 9 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
