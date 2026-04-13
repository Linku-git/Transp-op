# Session 124 — Driver Portal (React)

> Previous: [[sessions/session-123|Session 123 — ML Dashboard & Retraining UI]] | Next: [[sessions/session-125|Session 125 — Contractor Dashboard (Dash+Plotly)]]

## Phase: 8 — SOTREG Modules (M1-M8)
## Prerequisites: Sessions 120-121
## Complexity: Medium

## Objective
Build a driver-facing web portal with trip assignments, personal risk score, shift schedule, and vehicle status. The portal uses a simplified navigation layout for the conducteur role and includes LTO-optimized departure times. Role-based portal switching automatically redirects conducteur users to the driver portal on login.

---

## Tasks

- [x] **Create DriverPortalLayout:**
  - Simplified sidebar navigation (5 items max)
  - Driver name, photo, and active vehicle badge in header
  - Notification bell with unread count
  - Responsive design for tablet use in vehicle
- [x] **Create DriverTripsPage:**
  - Today's trip list with stops, scheduled times, passenger counts
  - Active trip highlighted with real-time progress
  - Next stop countdown and ETA
  - Trip status badges: upcoming, in_progress, completed, cancelled
  - Expandable stop list with passenger names (if authorized)
- [x] **Create DriverVehiclePage:**
  - Assigned vehicle details (type, plate, capacity, fuel/battery level)
  - Maintenance alerts with severity and due dates
  - Telemetry summary: speed avg, distance today, fuel consumed
  - Report issue button (opens form)
- [x] **Create DriverRiskPage:**
  - Personal risk score display (gauge chart, 0-100)
  - Risk category badge with color
  - Score history chart (last 30 days trend)
  - Improvement tips based on top risk factors
  - Infraction breakdown: speed, acceleration, braking, geofence, time
- [x] **Create DriverSchedulePage:**
  - Weekly schedule view with LTO-optimized departure times
  - Daily trip assignments with ligne, vehicle, shift
  - Rest period indicators (compliance with driving time rules)
  - Swap request button for shift changes
- [x] **Role-based portal switching:**
  - Detect conducteur role on login/app load
  - Redirect to /driver-portal instead of main dashboard
  - Route guards preventing conducteur from accessing admin pages
  - Shared auth context between portals
- [x] **Tests:**
  - Component render tests for layout and all 4 pages

## Files to Create/Modify
- `frontend/src/layouts/DriverPortalLayout.tsx` (create)
- `frontend/src/pages/driver/DriverTripsPage.tsx` (create)
- `frontend/src/pages/driver/DriverVehiclePage.tsx` (create)
- `frontend/src/pages/driver/DriverRiskPage.tsx` (create)
- `frontend/src/pages/driver/DriverSchedulePage.tsx` (create)
- `frontend/src/api/driver.ts` (create)
- `frontend/src/stores/driverStore.ts` (create)
- `frontend/src/router.tsx` (modify — add driver portal routes and guards)
- `frontend/src/pages/driver/__tests__/DriverTripsPage.test.tsx` (create)
- `frontend/src/pages/driver/__tests__/DriverRiskPage.test.tsx` (create)

## Tests
- [x] DriverPortalLayout renders simplified navigation
- [x] DriverTripsPage renders today's trip list with stops
- [x] DriverTripsPage highlights active trip with progress
- [x] DriverVehiclePage renders vehicle details and telemetry
- [x] DriverRiskPage renders risk gauge with score and category
- [x] DriverRiskPage displays improvement tips
- [x] DriverSchedulePage renders weekly schedule grid
- [x] Role-based redirect sends conducteur to driver portal

## Test Results
- Tests written: 8
- Tests passing: 8
- Tests failing: 0
- Coverage: all acceptance criteria met

## Acceptance Criteria
- Driver portal has simplified layout appropriate for conducteur role
- Trip assignments display with stops, times, and real-time progress
- Vehicle page shows assigned vehicle details, telemetry, and maintenance
- Risk page displays personal score with history and improvement tips
- Schedule page shows LTO-optimized weekly assignments
- Conducteur role is automatically redirected to driver portal
- Route guards prevent conducteur from accessing admin pages
- All 8 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v5.0
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[DATABASE_SCHEMA]] — Database tables
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
