# Session 62 — Security Scoring Engine

> Previous: [[sessions/session-61|Session 61 — Security Questionnaire Model & API]] | Next: [[sessions/session-63|Session 63 — Security-Constrained Pooling]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-61|Session 61]] completed
## Complexity: Medium

## Objective
Build a security scoring engine that computes per-employee safety scores from questionnaire responses and commute patterns, with group aggregation and time-slot-based security heat maps including night mode stop identification.

---

## Tasks
- [ ] Create `SecurityScore` model with fields:
  - `id` — primary key
  - `employee_id` — foreign key to employee
  - `score` — integer (0-100), computed security score
  - `risk_level` — enum (low, medium, high, critical)
  - `contributing_factors` — JSON, breakdown of score components
  - `computed_at` — timestamp of last computation
  - `created_at` / `updated_at` — timestamps
- [ ] Create Alembic migration for SecurityScore
- [ ] Create `backend/app/services/security_scoring.py`:
  - Per-employee scoring from questionnaire responses + commute pattern analysis
  - Factors: questionnaire rating, vulnerable stop count, night commute exposure, isolation score of assigned stops
  - Per-group aggregation by site, team, and shift
  - Per-time-slot security heat map generation
  - Night mode stop identification (20h00-6h30) with elevated risk weighting
- [ ] Implement `GET /security/scores` — list security scores with filters (site_id, risk_level, team, shift)
- [ ] Implement `GET /security/scores/{employee_id}` — get detailed security score for specific employee
  - Include contributing factors breakdown
  - Include risk level classification

## Files to Create/Modify
- `backend/app/models/security_score.py`
- `backend/app/schemas/security_score.py`
- `backend/app/api/endpoints/security_scores.py`
- `backend/app/services/security_scoring.py`
- `backend/alembic/versions/xxx_create_security_score.py`
- `backend/app/api/router.py` (register new endpoints)

## Tests
- [ ] Test scoring algorithm produces correct score from known questionnaire + commute inputs
- [ ] Test risk level classification thresholds (low/medium/high/critical)
- [ ] Test contributing factors JSON contains expected breakdown
- [ ] Test group aggregation by site returns correct average scores
- [ ] Test group aggregation by team and shift
- [ ] Test time-slot security heat map identifies high-risk time windows
- [ ] Test night mode stop identification flags stops used between 20h00-6h30
- [ ] Test GET /security/scores returns filtered results
- [ ] Test GET /security/scores/{employee_id} returns detailed score

## Acceptance Criteria
- SecurityScore model exists with all specified fields and migration
- Security scoring service computes per-employee scores from questionnaire and commute data
- Group aggregation works across site, team, and shift dimensions
- Time-slot heat map identifies high-risk periods
- Night mode stops (20h00-6h30) are correctly identified and weighted
- API endpoints return filtered and detailed security score data
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
