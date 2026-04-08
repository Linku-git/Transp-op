# Session 76 — Value Measurement Engine

> Previous: [[sessions/session-75|Session 75 — Engagement Analytics Dashboard]] | Next: [[sessions/session-77|Session 77 — SIRH Connection Framework]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-69|Session 69]], [[sessions/session-74|Session 74]] completed
## Complexity: Medium

## Objective
Build the valorization engine that calculates the monetary and time value recovered from employee commute training engagement, and integrate it with the ROI dashboard.

---

## Tasks
- [x] Create `backend/app/services/valorization_engine.py` with value calculation logic
- [x] Implement training time recovered calculation: commute_hours * engagement_rate
- [x] Implement monetary value calculation: training_hours * engagement_rate * training_hour_cost
- [x] Apply key metric baseline: 40min round-trip * 5 days * 50 weeks = 166.67 annual hours; at 20% engagement = 33.33 hours recovered
- [x] Implement GET `/valorization/metrics` endpoint for journey valorization KPIs
- [x] Implement GET `/kpis/valorization` endpoint for dashboard consumption
- [x] Integrate with ROI calculator (Module E) via the roi_journey lever
- [x] Make training_hour_cost and engagement assumptions configurable

## Files to Create/Modify
- `backend/app/services/valorization_engine.py`
- `backend/app/api/v1/valorization.py`
- `backend/app/api/v1/kpis.py`
- `backend/app/schemas/valorization.py`
- `backend/app/config.py`
- `backend/app/api/v1/__init__.py`

## Tests
- [x] Test training time recovered calculation with various commute hours and engagement rates
- [x] Test monetary value calculation with different training hour costs
- [x] Test baseline metric: 166.67 annual hours at 20% engagement yields 33.33 hours
- [x] Test GET `/valorization/metrics` returns correct KPIs
- [x] Test GET `/kpis/valorization` returns dashboard-formatted data
- [x] Test integration with ROI calculator updates the roi_journey lever correctly
- [x] Test configurable parameters (training_hour_cost, engagement_rate) affect output

## Test Results
- Tests written: 18
- Tests passing: 18
- Tests failing: 0
- Coverage: calculations (8), KPIs (4), ROI lever (3), schemas (3)

## Notes
- Session spec stated 173 annual hours but correct calculation is 40min * 5d * 50wk / 60 = 166.67h (not 173h). Tests verify the correct value.
- Parameters configurable via query params on endpoints AND via VALORIZATION_* environment variables

## Acceptance Criteria
- Valorization engine correctly calculates training time recovered as commute_hours multiplied by engagement_rate
- Monetary value is computed as training_hours multiplied by engagement_rate multiplied by training_hour_cost
- Baseline scenario (40min round-trip, 5 days, 50 weeks, 20% engagement) produces 34 recovered hours
- Valorization metrics endpoint returns time recovered, monetary value, and engagement rate
- KPI endpoint provides data formatted for dashboard widgets
- ROI calculator integrates the roi_journey lever from valorization metrics
- Cost and engagement parameters are configurable without code changes

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
