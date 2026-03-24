# Session 58 — RTI Backend System

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-57|Session 57]]
## Complexity: High
> Previous: [[sessions/session-57|Session 57]] | Next: [[sessions/session-59|Session 59]]

## Objective
Build the core Real-Time Information backend system with vehicle position tracking via GPS and Redis, ETA calculations, compliance metrics, and WebSocket-based live position broadcasting.

---

## Tasks
- [ ] Create `VehiclePosition` model with fields:
  - `vehicle_id` — foreign key to vehicle
  - `lat` / `lng` — current coordinates
  - `geom` — PostGIS geometry point
  - `heading` — float, direction of travel
  - `speed` — float, current speed
  - `recorded_at` — timestamp of GPS reading
  - `created_at` — timestamp of DB insert
- [ ] Create `RTIEvent` model with fields:
  - `vehicle_id` — foreign key to vehicle
  - `stop_id` — foreign key to stop
  - `event_type` — enum (arrival, departure, delay, breakdown)
  - `scheduled_at` — expected arrival time
  - `actual_at` — actual arrival time
  - `wait_duration_seconds` — computed wait time
  - `created_at` — timestamp
- [ ] Create Alembic migrations for both models
- [ ] Implement `POST /rti/vehicle-position` — receive GPS tracker update, store in Redis (current position) and DB (history)
- [ ] Implement `GET /rti/vehicle-position/{vehicle_id}` — return current position from Redis cache
- [ ] Implement `GET /rti/stop/{stop_id}/eta` — calculate ETA for next vehicle arriving at stop based on current positions and route geometry
- [ ] Implement `GET /rti/compliance` — return RTI compliance metrics (percentage of trips where wait time <= 90 seconds)
- [ ] Implement WebSocket endpoint `ws://localhost:8000/ws/rti/{vehicle_id}` — broadcast real-time position updates to connected clients
- [ ] Implement compliance tracking: log an `RTIEvent` for each stop arrival with scheduled vs actual times
- [ ] Redis integration for low-latency position lookups

## Files to Create/Modify
- `backend/app/models/vehicle_position.py`
- `backend/app/models/rti_event.py`
- `backend/app/schemas/vehicle_position.py`
- `backend/app/schemas/rti_event.py`
- `backend/app/api/endpoints/rti.py`
- `backend/app/api/websockets/rti.py`
- `backend/app/services/rti_service.py`
- `backend/app/services/eta_calculator.py`
- `backend/alembic/versions/xxx_create_vehicle_position.py`
- `backend/alembic/versions/xxx_create_rti_event.py`
- `backend/app/api/router.py` (register new endpoints and WebSocket)

## Tests
- [ ] Test position update stores data in both Redis and DB
- [ ] Test current position retrieval from Redis returns latest data
- [ ] Test ETA calculation returns reasonable estimate based on vehicle position and route
- [ ] Test compliance metric correctly computes percentage of trips within 90-second threshold
- [ ] Test RTIEvent is logged on each stop arrival
- [ ] Test WebSocket connection receives position broadcasts
- [ ] Test WebSocket disconnection is handled gracefully
- [ ] Test concurrent position updates from multiple vehicles

## Acceptance Criteria
- VehiclePosition and RTIEvent models exist with all specified fields and migrations
- GPS position updates are stored in Redis for real-time access and DB for history
- ETA endpoint returns calculated arrival time for next vehicle at a given stop
- Compliance endpoint returns percentage of trips meeting the 90-second wait threshold
- WebSocket endpoint broadcasts live position updates to subscribed clients
- RTIEvent records are created for each stop arrival for compliance tracking
- All tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
- [[DATABASE_SCHEMA]]
- [[API_ENDPOINTS]]
- [[FRONTEND_PAGES]]
