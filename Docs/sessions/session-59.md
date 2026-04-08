# Session 59 — RTI Config & Adaptive Sizing

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-58|Session 58]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08

## Tasks
- [x] RTIConfig model (max_wait_seconds, compliance_target_pct, buffer_vehicle_count, night_mode_start/end)
- [x] Alembic migration m8n9o0p1q2r3 with unique constraint (tenant_id, site_id)
- [x] GET/PUT /rti/config/{site_id} — per-site RTI configuration
- [x] GET /rti/adaptive-sizing/{site_id} — sizing recommendation
- [x] Adaptive sizing: buffer calculation from breakdown rate + traffic factor
- [x] Pool recomposition: triggers for absence, shift change, breakdown, compliance drop
- [x] Fallback protocol: buffer activation → TAD request decision tree

## Files Created (8)
- `backend/app/models/rti_config.py`
- `backend/app/schemas/rti_config.py`
- `backend/app/api/v1/rti_config.py`
- `backend/app/services/adaptive_sizing.py`
- `backend/app/services/pool_recomposition.py`
- `backend/app/services/rti_fallback.py`
- `backend/alembic/versions/m8n9o0p1q2r3_create_rti_config.py`
- `backend/tests/test_rti_config.py`

## Tests
- Tests written: 20 | Tests passing: 20 | Tests failing: 0
- Total: 333 (263 mobile + 70 backend)
