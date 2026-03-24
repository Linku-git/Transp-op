# Session 28 — Scenario Comparison Frontend

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-24|Session 24]], [[sessions/session-27|Session 27]]

> Previous: [[sessions/session-27|Session 27]] | Next: [[sessions/session-29|Session 29]]

## Complexity: Medium

## Objective
Build scenario management and comparison frontend with side-by-side metrics and map toggle.

---

## Tasks

- [ ] Create `frontend/src/api/scenarios.ts` — API client functions
- [ ] Create `frontend/src/types/scenario.ts` — TypeScript interfaces
- [ ] Create `frontend/src/pages/scenarios/ScenarioListPage.tsx` — Table of saved scenarios with actions
- [ ] Create `frontend/src/pages/scenarios/ScenarioComparePage.tsx`:
  - Select 2-3 scenarios from dropdown
  - Side-by-side comparison table (vehicles, occupancy, distance, cost, CO2)
  - Before/after delta metrics with color (green=improvement, red=worse)
  - Map toggle between scenarios
  - Recommendations text
  - RTI compliance comparison
- [ ] Create `frontend/src/components/optimization/WeatherWidget.tsx`:
  - 3-day forecast display per site
  - Condition icons
  - "Create Rain Scenario" one-click button
- [ ] Add weather widget to OptimizationPage
- [ ] Add scenario routes to navigation

## Files to Create/Modify
- `frontend/src/api/scenarios.ts` (create)
- `frontend/src/types/scenario.ts` (create)
- `frontend/src/pages/scenarios/ScenarioListPage.tsx` (create)
- `frontend/src/pages/scenarios/ScenarioComparePage.tsx` (create)
- `frontend/src/components/optimization/WeatherWidget.tsx` (create)
- `frontend/src/pages/optimization/OptimizationPage.tsx` (modify — add weather widget)
- `frontend/src/routes.tsx` (modify)

## Tests
- [ ] `ScenarioComparePage.test.tsx` — Renders comparison table
- [ ] `WeatherWidget.test.tsx` — Displays forecast data

## Acceptance Criteria
- Scenario list shows all saved scenarios
- Comparison page shows side-by-side metrics
- Delta values color-coded (green/red)
- Map toggles between scenario visualizations
- Weather widget shows 3-day forecast
- One-click scenario creation from weather

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
