# Session 76 — Value Measurement Engine

> Previous: [[sessions/session-75|Session 75 — Engagement Analytics Dashboard]] | Next: [[sessions/session-77|Session 77 — SIRH Connection Framework]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-69|Session 69]], [[sessions/session-74|Session 74]] completed
## Complexity: Medium

## Objective
Build the valorization engine that calculates the monetary and time value recovered from employee commute training engagement, and integrate it with the ROI dashboard.

---

## Tasks
- [ ] Create `backend/app/services/valorization_engine.py` with value calculation logic
- [ ] Implement training time recovered calculation: commute_hours * engagement_rate
- [ ] Implement monetary value calculation: training_hours * engagement_rate * training_hour_cost
- [ ] Apply key metric baseline: 40min round-trip * 5 days * 50 weeks = 173 annual hours; at 20% engagement = 34 hours recovered
- [ ] Implement GET `/valorization/metrics` endpoint for journey valorization KPIs
- [ ] Implement GET `/kpis/valorization` endpoint for dashboard consumption
- [ ] Integrate with ROI calculator (Module E) via the roi_journey lever
- [ ] Make training_hour_cost and engagement assumptions configurable

## Files to Create/Modify
- `backend/app/services/valorization_engine.py`
- `backend/app/api/endpoints/valorization.py`
- `backend/app/api/endpoints/kpis.py`
- `backend/app/schemas/valorization.py`
- `backend/app/config.py`
- `backend/app/api/router.py`

## Tests
- [ ] Test training time recovered calculation with various commute hours and engagement rates
- [ ] Test monetary value calculation with different training hour costs
- [ ] Test baseline metric: 173 annual hours at 20% engagement yields 34 hours
- [ ] Test GET `/valorization/metrics` returns correct KPIs
- [ ] Test GET `/kpis/valorization` returns dashboard-formatted data
- [ ] Test integration with ROI calculator updates the roi_journey lever correctly
- [ ] Test configurable parameters (training_hour_cost, engagement_rate) affect output

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
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
