# Session 57 — Stop Risk Score Model & Algorithm

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-06|Session 06]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08

## Tasks
- [x] StopRiskScore model with PostGIS geometry, 5 risk factors, composite score, critical flag
- [x] Alembic migration with GIST spatial index on geom column
- [x] Weighted risk scoring algorithm: `w1*Isolation + w2*(1-Lighting) + w3*(1-TC) + w4*Night + w5*(1-Perception)`
- [x] Configurable weights via RiskWeights dataclass (default: 0.25/0.20/0.20/0.20/0.15)
- [x] Critical threshold at 0.7 (configurable)
- [x] GET /rti/risk-stops — list with site_id and is_critical filters
- [x] POST /rti/risk-stops — create with auto-computed composite score
- [x] PUT /rti/risk-stops/{id} — update and recompute score

## Files Created
- `backend/app/models/stop_risk_score.py`
- `backend/app/services/risk_scoring.py`
- `backend/app/schemas/stop_risk_score.py`
- `backend/app/api/v1/rti_risk_stops.py`
- `backend/alembic/versions/k6l7m8n9o0p1_create_stop_risk_score.py`
- `backend/tests/test_risk_scoring.py`

## Tests
- Tests written: 20 | Tests passing: 20 (backend) | Tests failing: 0
- Total project: 299 (263 mobile + 36 backend)
