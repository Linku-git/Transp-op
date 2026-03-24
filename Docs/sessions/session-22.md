# Session 22 — Route Optimization (OSRM + CVRP)

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-19|Session 19]], [[sessions/session-21|Session 21]]

> Previous: [[sessions/session-21|Session 21]] | Next: [[sessions/session-23|Session 23]]

## Complexity: High

## Objective
Implement route optimization using Google OR-Tools CVRP solver with OSRM routing for real distances and polylines.

---

## Tasks

- [ ] Create `backend/app/models/route.py` — Route model (or add to optimization.py)
- [ ] Create Alembic migration for route table
- [ ] Create `backend/app/services/routing.py` — Route optimizer:
  - Build distance/time matrix using OSRM (table service)
  - Solve CVRP with Google OR-Tools
  - For each vehicle: optimal pickup order
  - Compute route polylines via OSRM route service
  - Calculate total distance, time, ETA per stop
  - Respect max route duration constraint
- [ ] Enhance `backend/app/services/osrm_client.py`:
  - Table service (distance/time matrix)
  - Route service with polyline decoding
  - Traffic-aware ETA (optional, Google Maps API)
- [ ] Create `backend/app/schemas/route.py` — Route schemas:
  - `RouteResponse` — Route with ordered stops, polyline, distance, time
- [ ] Create `backend/app/api/v1/routes.py` — Endpoints:
  - GET `/routes` — Get routes (site_id, optimization_id, vehicle_id filters)
  - GET `/routes/{id}` — Single route with geometry
- [ ] Implement two-leg model:
  - Access leg: employee -> gathering point (walking)
  - Main leg: gathering point -> site (vehicle route)
- [ ] Register routes router
- [ ] Create `backend/tests/test_routing.py`

## Files to Create/Modify
- `backend/app/models/route.py` (create or modify optimization.py)
- `backend/app/services/routing.py` (create)
- `backend/app/services/osrm_client.py` (modify)
- `backend/app/schemas/route.py` (create)
- `backend/app/api/v1/routes.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_routing.py` (create)

## Tests
- [ ] `test_distance_matrix` — OSRM returns valid matrix
- [ ] `test_cvrp_solver` — OR-Tools produces valid routes
- [ ] `test_route_respects_capacity` — No route exceeds vehicle capacity
- [ ] `test_route_respects_duration` — No route exceeds max duration
- [ ] `test_polyline_generation` — Routes have valid encoded polylines
- [ ] `test_stop_order_optimized` — Stops ordered to minimize distance
- [ ] `test_eta_calculation` — ETA computed per stop
- [ ] `test_two_leg_model` — Access and main legs separate
- [ ] `test_get_routes_endpoint` — API returns routes
- [ ] `test_per_site_routing` — Routes scoped to site

## Acceptance Criteria
- CVRP solver produces optimal routes
- All capacity and duration constraints respected
- Polylines can be rendered on a map
- ETA calculated per stop
- Two-leg model (walking + vehicle) computed
- All 10 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
