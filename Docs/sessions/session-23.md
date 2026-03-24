# Session 23 — Full Optimization Pipeline

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-18|Session 18]], [[sessions/session-19|Session 19]], [[sessions/session-21|Session 21]], [[sessions/session-22|Session 22]]

> Previous: [[sessions/session-22|Session 22]] | Next: [[sessions/session-24|Session 24]]

## Complexity: High

## Objective
Orchestrate the full optimization pipeline: clustering -> meeting zones -> vehicle assignment -> routing, with async execution via Celery.

---

## Tasks

- [ ] Create `backend/app/services/optimization_pipeline.py` — Pipeline orchestrator:
  1. Load employees for site (exclude on-leave for target_date)
  2. Run clustering algorithm
  3. Calculate meeting zones
  4. Assign vehicles to clusters
  5. Optimize routes
  6. Calculate metrics (total distance, time, vehicles, occupancy, fuel, CO2)
  7. Save results to database
- [ ] Create `backend/app/tasks/optimization_tasks.py` — Celery task:
  - `run_optimization` async task
  - Progress reporting via Redis (status updates)
- [ ] Create `backend/app/schemas/optimization.py` — Full schemas:
  - `OptimizationRequest` — site_id, condition_type, target_date, algorithm, params
  - `OptimizationResponse` — Full results with clusters, routes, metrics
  - `OptimizationStatus` — Progress status
- [ ] Create/update `backend/app/api/v1/optimization.py` — Endpoints:
  - POST `/optimize` — Launch optimization (returns task_id)
  - GET `/optimize/{id}` — Get result with metrics
  - GET `/optimize/{id}/status` — Get progress
  - GET `/optimize/latest/result` — Most recent optimization
  - GET `/optimize/history/list` — Past runs
- [ ] Implement leave-aware filtering (exclude employees on leave for target_date)
- [ ] Implement metrics calculation:
  - Total vehicles used
  - Average occupancy rate
  - Total distance (km)
  - Estimated fuel cost
  - CO2 estimate
  - Time saved vs individual transport
- [ ] Add WebSocket endpoint for real-time progress (`ws://localhost:8000/ws/optimization/{id}`)
- [ ] Register optimization router
- [ ] Create `backend/tests/test_optimization_pipeline.py`

## Files to Create/Modify
- `backend/app/services/optimization_pipeline.py` (create)
- `backend/app/tasks/optimization_tasks.py` (create)
- `backend/app/api/v1/optimization.py` (create)
- `backend/app/schemas/optimization.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_optimization_pipeline.py` (create)

## Tests
- [ ] `test_full_pipeline` — End-to-end optimization produces valid results
- [ ] `test_leave_exclusion` — Employees on leave excluded
- [ ] `test_metrics_calculation` — Correct distance, time, occupancy, fuel, CO2
- [ ] `test_celery_task` — Async task completes and stores results
- [ ] `test_optimization_status` — Status endpoint returns progress
- [ ] `test_optimization_history` — History lists past runs
- [ ] `test_latest_result` — Returns most recent optimization
- [ ] `test_multi_site_optimization` — Each site optimized independently

## Acceptance Criteria
- Full pipeline runs end-to-end producing valid clusters, routes, and metrics
- Async execution via Celery with progress tracking
- Leave-aware employee filtering works
- Metrics correctly calculated
- All 8 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
