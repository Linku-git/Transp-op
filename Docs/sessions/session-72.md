# Session 72 — Survey/Poll System

> Previous: [[sessions/session-71|Session 71 — Mobile Micro-Training Player]] | Next: [[sessions/session-73|Session 73 — Mobile Survey Interface]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-67|Session 67]] completed
## Complexity: Medium

## Objective
Build the backend survey and poll system supporting multiple question types, anonymous responses, and response aggregation.

---

## Tasks
- [ ] Create Survey model with fields: content_id, questions (JSON), response_count, is_anonymous
- [ ] Create SurveyResponse model with fields: survey_id, employee_id (nullable), responses (JSON), submitted_at
- [ ] Generate Alembic migrations for Survey and SurveyResponse tables
- [ ] Implement POST `/surveys/{id}/respond` endpoint
- [ ] Support question types: single choice, multiple choice, text, rating (1-5), slider
- [ ] Implement anonymous survey support (nullable employee_id)
- [ ] Implement response aggregation (counts, averages, distributions)
- [ ] Validate responses against question schema

## Files to Create/Modify
- `backend/app/models/survey.py`
- `backend/app/models/survey_response.py`
- `backend/app/schemas/survey.py`
- `backend/app/api/endpoints/surveys.py`
- `backend/app/services/survey_service.py`
- `backend/alembic/versions/xxx_create_survey_tables.py`
- `backend/app/api/router.py`

## Tests
- [ ] Test survey creation with various question types
- [ ] Test response submission with valid answers
- [ ] Test anonymous survey handling (employee_id is null)
- [ ] Test response count increments on submission
- [ ] Test response aggregation returns correct counts, averages, and distributions
- [ ] Test validation rejects invalid response formats
- [ ] Test duplicate response prevention for non-anonymous surveys

## Acceptance Criteria
- Survey model stores questions as structured JSON with type metadata
- SurveyResponse model accepts all question types: single choice, multiple choice, text, rating, slider
- Anonymous surveys do not record employee identity
- Response aggregation provides counts, averages, and distributions per question
- POST `/surveys/{id}/respond` validates responses against the question schema
- Response count on the survey increments with each valid submission

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
