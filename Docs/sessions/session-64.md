# Session 64 — Security Dashboard Frontend

> Previous: [[sessions/session-63|Session 63 — Security-Constrained Pooling]] | Next: [[sessions/session-65|Session 65 — Mobile Night Mode & Emergency]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-62|Session 62]] completed
## Complexity: Medium

## Objective
Build a security dashboard with score distribution visualization, risk-scored stop map, night shift coverage indicators, incident history, and emergency alert logging.

---

## Tasks
- [ ] Create `SecurityDashboard` page at `/dashboard/security`
- [ ] Implement security score distribution chart:
  - Histogram or bar chart showing distribution of employee security scores
  - Segmented by risk level (low/medium/high/critical)
  - Filterable by site, team, shift
- [ ] Implement map overlay with risk-scored stops:
  - Green markers: low-risk stops (score < 30)
  - Orange markers: medium-risk stops (score 30-70)
  - Red markers: high-risk stops (score > 70)
  - Click on marker for stop details and contributing factors
- [ ] Implement night shift coverage indicator:
  - Visual indicator showing coverage status for night shifts
  - Number of employees on night shifts vs minimum group sizes
  - Highlight under-covered night routes
- [ ] Implement incident history timeline:
  - Chronological timeline of security incidents
  - Filterable by severity, type, and date range
  - Click for incident details
- [ ] Implement emergency alert log table:
  - Table of all emergency alerts (triggered, resolved, pending)
  - Columns: employee, time, location, alert type, status, response time
  - Sortable and filterable
- [ ] Implement `GET /security/risk-map` endpoint:
  - Return all stops with risk scores and coordinates for map rendering
- [ ] Implement `GET /kpis/security` endpoint:
  - Average security score across all employees
  - Distribution by risk level
  - Night shift coverage percentage
  - Incident count by period

## Files to Create/Modify
- `frontend/src/pages/dashboard/SecurityDashboard.tsx`
- `frontend/src/components/security/ScoreDistributionChart.tsx`
- `frontend/src/components/security/RiskStopMap.tsx`
- `frontend/src/components/security/NightShiftCoverage.tsx`
- `frontend/src/components/security/IncidentTimeline.tsx`
- `frontend/src/components/security/EmergencyAlertLog.tsx`
- `frontend/src/api/security.ts`
- `backend/app/api/endpoints/security_risk_map.py`
- `backend/app/api/endpoints/kpis_security.py`
- `backend/app/api/router.py` (register new endpoints)
- `frontend/src/routes.tsx` (add route)

## Tests
- [ ] Test score distribution chart renders with correct segmentation
- [ ] Test risk stop map displays markers with correct colors based on score
- [ ] Test marker click shows stop details
- [ ] Test night shift coverage indicator displays correct status
- [ ] Test incident timeline renders chronologically
- [ ] Test emergency alert log table renders and filters correctly
- [ ] Test GET /security/risk-map returns stops with scores and coordinates
- [ ] Test GET /kpis/security returns expected data structure

## Acceptance Criteria
- Security Dashboard is accessible at /dashboard/security
- Score distribution chart shows employee security scores segmented by risk level
- Map overlay displays risk-scored stops with green/orange/red color coding
- Night shift coverage indicator highlights under-covered routes
- Incident history timeline shows chronological security events
- Emergency alert log table displays all alerts with status and response time
- Backend endpoints return all required data for dashboard components
- All frontend tests pass

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
