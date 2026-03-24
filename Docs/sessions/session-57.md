# Session 57 — Stop Risk Score Model & Algorithm

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-06|Session 06]]
## Complexity: Medium
> Previous: [[sessions/session-56|Session 56]] | Next: [[sessions/session-58|Session 58]]

## Objective
Create the StopRiskScore model with a weighted risk scoring algorithm that evaluates stop safety based on isolation, lighting, transport frequency, night conditions, and employee perception, flagging critical stops above a configurable threshold.

---

## Tasks
- [ ] Create `StopRiskScore` model with fields:
  - `site_id` — foreign key to site
  - `lat` / `lng` — geographic coordinates
  - `geom` — PostGIS geometry point
  - `stop_name` — human-readable stop name
  - `isolation_score` — float (0-1), how isolated the stop is
  - `lighting_score` — float (0-1), quality of lighting at stop
  - `tc_frequency_score` — float (0-1), public transport frequency near stop
  - `night_risk_multiplier` — float, multiplier applied during night hours
  - `employee_perception_avg` — float (0-1), average employee-reported safety perception
  - `composite_risk_score` — float, computed weighted risk score
  - `is_critical` — boolean, flagged when composite score exceeds threshold
- [ ] Create Alembic migration with spatial index on `geom` column
- [ ] Implement risk scoring algorithm:
  - `Risk_Score = w1*Isolation + w2*(1-Lighting) + w3*(1-TC_Frequency) + w4*Night_Flag + w5*Employee_Perception`
  - Weights configurable (default: w1=0.25, w2=0.20, w3=0.20, w4=0.20, w5=0.15)
- [ ] Stops with composite risk score above threshold flagged as "critical" (`is_critical = True`)
- [ ] Implement API endpoint `GET /rti/risk-stops` — list all risk-scored stops with optional filters (site_id, is_critical)
- [ ] Implement API endpoint `PUT /rti/risk-stops/{id}` — update risk stop attributes and recompute composite score

## Files to Create/Modify
- `backend/app/models/stop_risk_score.py`
- `backend/app/schemas/stop_risk_score.py`
- `backend/app/api/endpoints/rti_risk_stops.py`
- `backend/app/services/risk_scoring.py`
- `backend/alembic/versions/xxx_create_stop_risk_score.py`
- `backend/app/api/router.py` (register new endpoints)

## Tests
- [ ] Test scoring formula produces correct composite score for known inputs
- [ ] Test critical flag is set when composite score exceeds threshold
- [ ] Test critical flag is not set when composite score is below threshold
- [ ] Test CRUD operations: create, read, update risk stops
- [ ] Test spatial index is created in migration
- [ ] Test weight configuration changes affect scoring output

## Acceptance Criteria
- StopRiskScore model exists with all specified fields and spatial index
- Risk scoring algorithm correctly computes composite scores using the weighted formula
- Stops above the configured threshold are automatically flagged as critical
- GET /rti/risk-stops returns filtered list of risk-scored stops
- PUT /rti/risk-stops/{id} updates attributes and recomputes composite score
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
