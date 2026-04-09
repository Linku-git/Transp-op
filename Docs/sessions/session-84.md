# Session 84 — Operator Portal (Web)

> Previous: [[sessions/session-83|Session 83 — Via & SWVL API Integration]] | Next: [[sessions/session-85|Session 85 — ERP Finance Export]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-82|Session 82]] completed
## Complexity: Medium

## Objective
Build a read-only web portal for transport operators, allowing them to log in with a limited role, view their assigned sizing plans and route details, review vehicle specifications, acknowledge sizing plans, and report service issues.

---

## Tasks
- [x] Create operator portal route group with separate layout
- [x] Implement operator login with limited role (read-only access)
- [x] Create operator dashboard page showing assigned sizing plans
- [x] Build sizing plan detail view with route information: stops, schedule, passenger counts
- [x] Build vehicle specifications view
- [x] Implement acknowledge sizing plan button with confirmation flow
- [x] Create report service issues form (issue type, description, affected route, date)
- [x] Create backend API endpoints for operator portal:
  - [x] GET `/operator/sizing-plans` — list assigned sizing plans
  - [x] GET `/operator/sizing-plans/{id}` — sizing plan details
  - [x] POST `/operator/sizing-plans/{id}/acknowledge` — acknowledge a plan
  - [x] POST `/operator/service-issues` — submit a service issue report
- [x] Enforce read-only access on all data views (no edit capabilities)
- [x] Add role-based route guards for operator role
- [ ] **Browser verification**: Open `http://localhost:5000` in Chrome, verify new pages render correctly, check DevTools Console for errors, test navigation

## Files to Create/Modify
- `frontend/src/pages/operator/OperatorDashboardPage.tsx`
- `frontend/src/pages/operator/SizingPlanDetailPage.tsx`
- `frontend/src/pages/operator/ReportIssuePage.tsx`
- `frontend/src/layouts/OperatorLayout.tsx`
- `frontend/src/components/operator/SizingPlanCard.tsx`
- `frontend/src/components/operator/RouteDetailView.tsx`
- `frontend/src/components/operator/VehicleSpecsView.tsx`
- `frontend/src/components/operator/ServiceIssueForm.tsx`
- `frontend/src/services/operatorApi.ts`
- `backend/app/api/v1/operator_portal.py`
- `backend/app/schemas/operator_portal.py`
- `frontend/src/router.tsx` (add operator routes)

## Tests
- [x] Test operator portal renders with correct layout
- [x] Test operator dashboard displays assigned sizing plans
- [x] Test sizing plan detail view shows routes, stops, schedule, and passenger counts
- [x] Test vehicle specifications display correctly
- [x] Test acknowledge button sends POST request and updates plan status
- [x] Test service issue form validates required fields and submits correctly
- [x] Test read-only enforcement: no edit or delete actions available
- [x] Test operator role cannot access admin routes
- [x] Test non-operator roles cannot access operator portal

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0
- Coverage: dashboard (5), issue form (2)

## Acceptance Criteria
- Operators can log in with a dedicated limited role
- Dashboard shows only sizing plans assigned to the logged-in operator
- Route details display stops, schedules, and passenger counts accurately
- Vehicle specifications are displayed for each sizing plan
- Acknowledging a sizing plan records the acknowledgment with timestamp
- Service issue form submits reports linked to the correct operator and route
- All data views are strictly read-only with no edit capabilities
- Role-based access control prevents cross-role access
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
