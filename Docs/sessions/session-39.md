# Session 39 — HR Dashboard KPIs Backend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-09|Session 09]], [[sessions/session-15|Session 15]], [[sessions/session-23|Session 23]]
## Complexity: Medium
> Previous: [[sessions/session-38|Session 38]] | Next: [[sessions/session-40|Session 40]]

## Objective
Build the backend analytics service and API endpoint that powers the HR dashboard with mobility coverage, absenteeism correlation, retention impact, and shadow zone metrics.

---

## Tasks
- [x] Create `backend/app/services/hr_analytics.py` service module
- [x] Implement mobility coverage calculation by site, shift, team (department)
- [x] Implement mobility score evolution from completed optimization runs
- [x] Build absenteeism correlation (transport interest groups vs leave days)
- [x] Build retention impact estimation (departed with/without transport, savings estimate)
- [x] Implement shadow zone identification (distance >30km or no modal data)
- [x] Create GET `/kpis/hr` endpoint returning all HR metrics
- [x] Write tests for each metric calculation

## Files to Create/Modify
- `backend/app/services/hr_analytics.py`
- `backend/app/routers/kpis.py` (or new router for HR KPIs)
- `backend/tests/test_hr_analytics.py`

## Tests
- [x] Test mobility coverage returns correct percentages per site, shift, department
- [x] Test mobility score evolution returns time-series data
- [x] Test absenteeism correlation produces valid groups with rates
- [x] Test retention impact returns cost comparison figures
- [x] Test shadow zone identification correctly flags employees
- [x] Test GET `/kpis/hr` endpoint returns all 5 metric sections

## Test Results
- Tests written: 6
- Tests passing: 6
- Tests failing: 0

## Files Created/Modified
- `backend/app/services/hr_analytics.py` (created) — 5 analytics functions + compute_hr_kpis
- `backend/app/api/v1/kpis.py` (created) — GET /kpis/hr endpoint
- `backend/app/api/v1/__init__.py` (modified) — registered kpis router
- `backend/tests/test_hr_analytics.py` (created) — 6 tests

## Acceptance Criteria
- GET `/kpis/hr` returns a complete payload with mobility coverage, mobility score evolution, absenteeism correlation, retention impact, and shadow zones
- Mobility coverage is broken down by site, shift, team, and time slot
- Absenteeism correlation links transport issues to absence rates with statistical backing
- Retention impact provides a cost comparison between replacement and mobility solutions
- Shadow zones list employees and locations lacking adequate transport options
- All metric calculations have passing unit tests

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
