# Session 61 — Security Questionnaire Model & API

> Previous: [[sessions/session-60|Session 60 — RTI Monitoring Dashboard]] | Next: [[sessions/session-62|Session 62 — Security Scoring Engine]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-09|Session 09]] completed
## Complexity: Medium

## Objective
Create the SecurityQuestionnaire model and API for collecting employee safety perceptions, with versioned submissions, periodic reassessment scheduling, and incident-triggered reassessment capabilities.

---

## Tasks
- [ ] Create `SecurityQuestionnaire` model with fields:
  - `id` — primary key
  - `employee_id` — foreign key to employee
  - `submitted_at` — timestamp of submission
  - `version` — integer, questionnaire version number
  - `overall_safety_rating` — integer (1-5), overall safety perception
  - `responses` — JSON, structured questionnaire answers
  - `vulnerable_stops` — JSON array, stops identified as unsafe by employee
  - `night_concerns` — text, free-form night safety concerns
  - `created_at` / `updated_at` — timestamps
- [ ] Create Alembic migration for SecurityQuestionnaire
- [ ] Implement `POST /security/questionnaire` — submit a new questionnaire response (from mobile app)
  - Validate rating range (1-5)
  - Auto-increment version per employee
  - Store vulnerable stops as JSON array of stop IDs
- [ ] Implement `GET /security/questionnaire/{employee_id}` — retrieve latest questionnaire for an employee
  - Return most recent version
  - Include submission history summary (dates, versions)
- [ ] Implement periodic reassessment logic:
  - Configurable reassessment interval (quarterly, semi-annual, annual)
  - Track last submission date per employee
  - Generate reassessment notifications when interval expires
- [ ] Implement triggered reassessment:
  - After a security incident, trigger reassessment for affected employees
  - Mark reassessment as incident-triggered (vs periodic)

## Files to Create/Modify
- `backend/app/models/security_questionnaire.py`
- `backend/app/schemas/security_questionnaire.py`
- `backend/app/api/endpoints/security_questionnaire.py`
- `backend/app/services/reassessment_scheduler.py`
- `backend/alembic/versions/xxx_create_security_questionnaire.py`
- `backend/app/api/router.py` (register new endpoints)

## Tests
- [ ] Test questionnaire submission creates record with correct fields
- [ ] Test overall_safety_rating validation rejects values outside 1-5
- [ ] Test version auto-increments for same employee
- [ ] Test GET latest returns most recent version for employee
- [ ] Test periodic reassessment detects expired intervals
- [ ] Test incident-triggered reassessment marks affected employees
- [ ] Test submission history summary is included in GET response

## Acceptance Criteria
- SecurityQuestionnaire model exists with all specified fields and migration
- POST endpoint accepts and validates questionnaire submissions
- GET endpoint returns the latest questionnaire with submission history
- Version tracking auto-increments per employee
- Periodic reassessment logic identifies employees due for reassessment
- Incident-triggered reassessment marks affected employees for immediate reassessment
- All tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
