# Session 39 — HR Dashboard KPIs Backend

## Phase: 2 — Enhancement
## Prerequisites: [[sessions/session-09|Session 09]], [[sessions/session-15|Session 15]], [[sessions/session-23|Session 23]]
## Complexity: Medium
> Previous: [[sessions/session-38|Session 38]] | Next: [[sessions/session-40|Session 40]]

## Objective
Build the backend analytics service and API endpoint that powers the HR dashboard with mobility coverage, absenteeism correlation, retention impact, and shadow zone metrics.

---

## Tasks
- [ ] Create `backend/app/services/hr_analytics.py` service module
- [ ] Implement mobility coverage calculation by site, shift, team, and time slot
- [ ] Implement mobility score evolution over time (requires KPISnapshot)
- [ ] Build absenteeism correlation model (correlate transport problems with absence rates)
- [ ] Build retention impact estimation (cost of replacement vs mobility solution cost)
- [ ] Implement shadow zone identification (employees without satisfactory transport)
- [ ] Create GET `/kpis/hr` endpoint returning all HR metrics
- [ ] Write tests for each metric calculation

## Files to Create/Modify
- `backend/app/services/hr_analytics.py`
- `backend/app/routers/kpis.py` (or new router for HR KPIs)
- `backend/tests/test_hr_analytics.py`

## Tests
- [ ] Test mobility coverage calculation returns correct percentages per site, shift, team, and time slot
- [ ] Test mobility score evolution returns time-series data from KPISnapshot
- [ ] Test absenteeism correlation model produces valid correlation coefficients
- [ ] Test retention impact estimation returns cost comparison figures
- [ ] Test shadow zone identification correctly flags employees without satisfactory transport
- [ ] Test GET `/kpis/hr` endpoint returns all metrics with correct structure

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
