# Session 59 — RTI Config & Adaptive Sizing

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-58|Session 58]]
## Complexity: Medium
> Previous: [[sessions/session-58|Session 58]] | Next: [[sessions/session-60|Session 60]]

## Objective
Create a configurable RTI system with per-site settings, adaptive vehicle pool sizing for degraded mode scenarios, dynamic recomposition on workforce changes, and fallback protocols when RTI targets cannot be maintained.

---

## Tasks
- [ ] Create `RTIConfig` model with fields:
  - `site_id` — foreign key to site (unique)
  - `max_wait_seconds` — integer, maximum acceptable wait time (default: 90)
  - `compliance_target_pct` — float, target compliance percentage (default: 95.0)
  - `buffer_vehicle_count` — integer, number of buffer vehicles for degraded mode
  - `night_mode_start` — time, start of night mode hours
  - `night_mode_end` — time, end of night mode hours
  - `created_at` / `updated_at` — timestamps
- [ ] Create Alembic migration for RTIConfig
- [ ] Implement `GET /rti/config/{site_id}` — retrieve RTI configuration for a site
- [ ] Implement `PUT /rti/config/{site_id}` — update RTI configuration for a site
- [ ] Implement adaptive sizing logic:
  - Allocate buffer vehicles for degraded mode (vehicle breakdown, heavy traffic)
  - Calculate required buffer count based on historical breakdown frequency and traffic patterns
  - Activate buffer vehicles when RTI compliance drops below threshold
- [ ] Implement dynamic pool recomposition:
  - Trigger recomposition when employee absences are reported
  - Trigger recomposition when shift changes occur
  - Rebalance vehicle assignments to maintain RTI targets
- [ ] Implement fallback protocol:
  - Monitor real-time compliance against target
  - Trigger TAD (Transport A la Demande) request if RTI cannot be maintained with available fleet
  - Log fallback activation events

## Files to Create/Modify
- `backend/app/models/rti_config.py`
- `backend/app/schemas/rti_config.py`
- `backend/app/api/endpoints/rti_config.py`
- `backend/app/services/adaptive_sizing.py`
- `backend/app/services/pool_recomposition.py`
- `backend/app/services/rti_fallback.py`
- `backend/alembic/versions/xxx_create_rti_config.py`
- `backend/app/api/router.py` (register new endpoints)

## Tests
- [ ] Test RTIConfig CRUD: create, read, update configuration per site
- [ ] Test buffer vehicle allocation calculates correct count based on historical data
- [ ] Test buffer vehicles activate when compliance drops below threshold
- [ ] Test pool recomposition triggers on employee absence
- [ ] Test pool recomposition triggers on shift change
- [ ] Test fallback protocol triggers TAD request when RTI is unsustainable
- [ ] Test fallback events are logged

## Acceptance Criteria
- RTIConfig model exists with all specified fields and per-site uniqueness
- GET/PUT endpoints allow reading and updating site-specific RTI configuration
- Adaptive sizing allocates buffer vehicles and activates them during degraded mode
- Dynamic recomposition rebalances pools on absences and shift changes
- Fallback protocol triggers TAD request when RTI targets cannot be met
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
