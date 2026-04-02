# Session 28 — Scenario Comparison Frontend

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-24|Session 24]], [[sessions/session-27|Session 27]]

> Previous: [[sessions/session-27|Session 27]] | Next: [[sessions/session-29|Session 29]]

## Complexity: Medium

## Objective
Build scenario management and comparison frontend with side-by-side metrics and map toggle.

---

## Tasks

- [x] Create `frontend/src/api/scenarios.ts` — API client functions
- [x] Create `frontend/src/types/scenario.ts` — TypeScript interfaces
- [x] Create `frontend/src/pages/scenarios/ScenarioListPage.tsx` — Table of saved scenarios with actions
- [x] Create `frontend/src/pages/scenarios/ScenarioComparePage.tsx`:
  - Select 2-3 scenarios from dropdown
  - Side-by-side comparison table (vehicles, occupancy, distance, cost, CO2)
  - Before/after delta metrics with color (green=improvement, red=worse)
  - Map toggle between scenarios
  - Recommendations text
  - RTI compliance comparison
- [x] Create `frontend/src/components/optimization/WeatherWidget.tsx`:
  - 3-day forecast display per site
  - Condition icons
  - "Create Rain Scenario" one-click button
- [x] Add weather widget to OptimizationPage
- [x] Add scenario routes to navigation
- [x] **Browser verification**: Open `http://localhost:5173` in Chrome, verify new pages render correctly, check DevTools Console for errors, test navigation

## Files to Create/Modify
- `frontend/src/api/scenarios.ts` (create)
- `frontend/src/types/scenario.ts` (create)
- `frontend/src/pages/scenarios/ScenarioListPage.tsx` (create)
- `frontend/src/pages/scenarios/ScenarioComparePage.tsx` (create)
- `frontend/src/components/optimization/WeatherWidget.tsx` (create)
- `frontend/src/pages/optimization/OptimizationPage.tsx` (modify — add weather widget)
- `frontend/src/routes.tsx` (modify)

## Tests
- [x] `ScenarioListPage.test.tsx` — 15 tests (table rendering, condition chips, site filter, checkbox selection, compare navigation, delete actions)
- [x] `ScenarioComparePage.test.tsx` — 15 tests (side-by-side metrics, color-coded deltas, recommendations panel, URL parameter support)
- [x] `WeatherWidget.test.tsx` — 10 tests (3-day forecast display, condition icons, temp ranges, precipitation, scenario suggestion chips, Apply button)

## Acceptance Criteria
- Scenario list shows all saved scenarios
- Comparison page shows side-by-side metrics
- Delta values color-coded (green/red)
- Map toggles between scenario visualizations
- Weather widget shows 3-day forecast
- One-click scenario creation from weather
- Browser verification passes: no console errors, pages render correctly, navigation works

## Test Results
- Tests written: 40
- Tests passing: 40
- Tests failing: 0
- Full suite: 114 passing (6 pre-existing timeout failures unrelated to this session)

## Browser Verification
- ScenarioListPage renders correctly with data table, condition chips, filters
- ScenarioComparePage renders with scenario selectors and compare button
- WeatherWidget renders on OptimizationPage when site is selected
- No console errors
- Navigation works between all pages

## Notes
- Added `transit_failure` condition type to OptimizationPage dropdown to match Session 27 backend addition
- WeatherWidget integrated below controls on OptimizationPage with `handleWeatherScenario` callback for one-click scenario creation from weather suggestions
- ScenarioListPage supports checkbox selection of 2+ scenarios for bulk comparison navigation
- ScenarioComparePage supports URL query parameters (`?ids=uuid1,uuid2`) for direct linking
- Barrel export added to `frontend/src/components/optimization/index.ts` for WeatherWidget

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
