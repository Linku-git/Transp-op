# Session 23 — Full Optimization Pipeline

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-18|Session 18]], [[sessions/session-19|Session 19]], [[sessions/session-21|Session 21]], [[sessions/session-22|Session 22]]

> Previous: [[sessions/session-22|Session 22]] | Next: [[sessions/session-24|Session 24]]

## Complexity: High

## Objective
Orchestrate the full optimization pipeline: clustering -> meeting zones -> vehicle assignment -> routing, with async execution via Celery.

---

## Tasks

- [x] Create `backend/app/services/optimization_pipeline.py` — Pipeline orchestrator:
  1. Load employees for site (exclude on-leave for target_date)
  2. Run clustering algorithm
  3. Calculate meeting zones
  4. Assign vehicles to clusters
  5. Optimize routes
  6. Calculate metrics (total distance, time, vehicles, occupancy, fuel, CO2)
  7. Save results to database
- [x] Create `backend/app/tasks/optimization_tasks.py` — Celery task:
  - `run_optimization` async task
  - Progress reporting via Redis (status updates)
- [x] Create `backend/app/schemas/optimization.py` — Full schemas:
  - `OptimizationRunRequest` — site_id, condition_type, target_date, algorithm, params
  - `OptimizationFullResponse` — Full results with clusters, routes, metrics
  - `OptimizationStatusResponse` — Progress status
- [x] Create/update `backend/app/api/v1/optimization.py` — Endpoints:
  - POST `/optimize` — Launch optimization (returns task_id)
  - GET `/optimize/{id}` — Get result with metrics
  - GET `/optimize/{id}/status` — Get progress
  - GET `/optimize/latest/result` — Most recent optimization
  - GET `/optimize/history/list` — Past runs
- [x] Implement leave-aware filtering (exclude employees on leave for target_date)
- [x] Implement metrics calculation:
  - Total vehicles used
  - Average occupancy rate
  - Total distance (km)
  - Estimated fuel cost
  - CO2 estimate
  - Time saved vs individual transport
- [x] Add Redis-based progress tracking (WebSocket deferred to later session)
- [x] Register optimization router
- [x] Create `backend/tests/test_optimization_pipeline.py`

## Files to Create/Modify
- `backend/app/services/optimization_pipeline.py` (create)
- `backend/app/tasks/optimization_tasks.py` (create)
- `backend/app/api/v1/optimization.py` (create)
- `backend/app/schemas/optimization.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_optimization_pipeline.py` (create)

## Tests
- [x] `test_full_pipeline` — End-to-end optimization produces valid results
- [x] `test_leave_exclusion` — Employees on leave excluded
- [x] `test_metrics_calculation` — Correct distance, time, occupancy, fuel, CO2
- [x] `test_celery_task_progress_tracking` — Redis progress tracking works
- [x] `test_optimization_status_values` — Status endpoint returns progress
- [x] `test_optimization_history_schema` — History schema validates
- [x] `test_latest_result_schema` — Returns most recent optimization
- [x] `test_multi_site_optimization` — Each site optimized independently

## Test Results
- Tests written: 8
- Tests passing: 8
- Tests failing: 0
- Coverage: Service layer and schemas fully covered

## Notes
- WebSocket endpoint for real-time progress deferred; Redis polling via GET /status is implemented
- Celery task has graceful sync fallback when Celery broker is not running

## Acceptance Criteria
- Full pipeline runs end-to-end producing valid clusters, routes, and metrics
- Async execution via Celery with progress tracking
- Leave-aware employee filtering works
- Metrics correctly calculated
- All 8 tests pass

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
