# Session 61 — Security Questionnaire Model & API

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-09|Session 09]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08

## Tasks
- [x] SecurityQuestionnaire model (employee, version, rating 1-5, responses JSONB, vulnerable_stops, night_concerns, trigger_type)
- [x] Alembic migration n9o0p1q2r3s4 with indexes
- [x] POST /security/questionnaire — submit with auto-version increment
- [x] GET /security/questionnaire/{employee_id} — latest + history
- [x] POST /security/questionnaire/trigger-reassessment — incident-triggered
- [x] ReassessmentScheduler: quarterly/semi-annual/annual intervals, due detection

## Files Created (6)
- `backend/app/models/security_questionnaire.py`
- `backend/app/schemas/security_questionnaire.py`
- `backend/app/api/v1/security_questionnaire.py`
- `backend/app/services/reassessment_scheduler.py`
- `backend/alembic/versions/n9o0p1q2r3s4_create_security_questionnaire.py`
- `backend/tests/test_security_questionnaire.py`

## Tests
- Tests written: 18 | Tests passing: 18 | Tests failing: 0
- Total: 363 (263 mobile + 91 backend + 9 frontend)
