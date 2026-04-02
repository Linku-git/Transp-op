# Session 35 — Financial Dashboard Frontend — TCO

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-32|Session 32]]
## Complexity: Medium
> Previous: [[sessions/session-34|Session 34]] | Next: [[sessions/session-36|Session 36]]

## Objective
Build the frontend TCO calculator page and financial dashboard displaying TCO comparison cards, evolution charts, motorization comparison, and fleet-level aggregation.

---

## Tasks

- [x] Create `frontend/src/pages/financial/FinancialDashboardPage.tsx` — Main financial dashboard page with tab navigation (TCO, ROI, Compare)
- [x] Create `frontend/src/pages/financial/TCOCalculatorPage.tsx` — TCO calculator page:
  - Fleet composition form (select vehicle types, quantities, motorization)
  - Duration slider (1-10 years)
  - Calculate button calling POST `/financial/tco/calculate`
- [x] Create `frontend/src/components/financial/TCOComparisonCards.tsx`:
  - Cards per vehicle spec showing TCO, breakdown, lowest highlighted
- [x] Create `frontend/src/components/financial/TCOEvolutionChart.tsx`:
  - Recharts LineChart showing TCO evolution over years with tooltips
- [x] Create `frontend/src/components/financial/MotorizationTable.tsx`:
  - Comparison table per vehicle type, cheapest row highlighted
- [x] Create `frontend/src/components/financial/VehicleTCOBreakdown.tsx`:
  - Stacked BarChart with purchase, maintenance, energy, residual segments
- [x] Create `frontend/src/components/financial/FleetAggregation.tsx`:
  - Fleet-level summary card: total fleet TCO, vehicle count, average cost
- [x] Create `frontend/src/api/financial.ts` + `frontend/src/types/financial.ts` — API client and TypeScript types
- [x] Add financial routes to `frontend/src/routes.tsx`
- [x] Create `frontend/src/pages/financial/__tests__/FinancialTCO.test.tsx`
- [ ] **Browser verification**: pending (manual check)

## Files Created/Modified
- `frontend/src/types/financial.ts` (created) — TCO TypeScript interfaces
- `frontend/src/api/financial.ts` (created) — API client functions
- `frontend/src/components/financial/TCOComparisonCards.tsx` (created)
- `frontend/src/components/financial/TCOEvolutionChart.tsx` (created)
- `frontend/src/components/financial/MotorizationTable.tsx` (created)
- `frontend/src/components/financial/VehicleTCOBreakdown.tsx` (created)
- `frontend/src/components/financial/FleetAggregation.tsx` (created)
- `frontend/src/pages/financial/TCOCalculatorPage.tsx` (created)
- `frontend/src/pages/financial/FinancialDashboardPage.tsx` (created)
- `frontend/src/routes.tsx` (modified) — added /financial, /financial/tco routes
- `frontend/src/i18n/fr.json` (modified) — financial translations
- `frontend/src/i18n/en.json` (modified) — financial translations
- `frontend/src/pages/financial/__tests__/FinancialTCO.test.tsx` (created) — 7 tests

## Tests
- [x] `test_tco_calculator_renders` — TCO calculator page renders with form inputs
- [x] `test_tco_form_submission` — Form submits and displays results
- [x] `test_tco_comparison_cards` — Cards render with correct values
- [x] `test_tco_evolution_chart` — Chart renders with SVG
- [x] `test_motorization_table` — Table shows all motorizations
- [x] `test_vehicle_breakdown` — Per-vehicle breakdown renders
- [x] `test_fleet_aggregation` — Fleet summary displays correct totals

## Test Results
- Tests written: 7
- Tests passing: 7
- Tests failing: 0

## Acceptance Criteria
- TCO calculator page allows fleet composition input and triggers calculation
- TCO comparison cards display all 3 investment models side by side
- Evolution chart renders year-by-year TCO with interactive tooltips
- Motorization table compares all 4 fuel types
- Per-vehicle breakdown and fleet aggregation are consistent
- All 7 tests pass
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
