# Session 35 — Financial Dashboard Frontend — TCO

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-32|Session 32]]
## Complexity: Medium
> Previous: [[sessions/session-34|Session 34]] | Next: [[sessions/session-36|Session 36]]

## Objective
Build the frontend TCO calculator page and financial dashboard displaying TCO comparison cards, evolution charts, motorization comparison, and fleet-level aggregation.

---

## Tasks

- [ ] Create `frontend/src/pages/FinancialDashboard.tsx` — Main financial dashboard page with tab navigation (TCO, ROI, Compare)
- [ ] Create `frontend/src/pages/TCOCalculator.tsx` — TCO calculator page:
  - Fleet composition form (select vehicle types, quantities, motorization)
  - Duration slider (1-10 years)
  - Cost override inputs (optional)
  - Calculate button calling POST `/financial/tco/calculate`
- [ ] Create `frontend/src/components/financial/TCOComparisonCards.tsx`:
  - 3 cards side by side for CAPEX, mise a disposition, OPEX
  - Each card shows total TCO, annual cost, cost per km
  - Highlight lowest-cost model
- [ ] Create `frontend/src/components/financial/TCOEvolutionChart.tsx`:
  - Line chart (Recharts) showing TCO evolution over years
  - One line per motorization or per investment model
  - Tooltip with year-by-year values
- [ ] Create `frontend/src/components/financial/MotorizationTable.tsx`:
  - Comparison table: diesel vs hybrid vs electric vs hydrogen
  - Columns: purchase cost, annual maintenance, energy cost, 5-year TCO, 10-year TCO
- [ ] Create `frontend/src/components/financial/VehicleTCOBreakdown.tsx`:
  - Per-vehicle TCO breakdown (stacked bar or donut chart)
  - Components: purchase, maintenance, energy, residual value offset
- [ ] Create `frontend/src/components/financial/FleetAggregation.tsx`:
  - Fleet-level summary card: total fleet TCO, average cost per vehicle, cost per seat
- [ ] Create `frontend/src/hooks/useFinancialApi.ts` — API hooks for financial endpoints
- [ ] Add financial routes to `frontend/src/router.tsx`
- [ ] Create `frontend/src/tests/financial-tco.test.tsx`

## Files to Create/Modify
- `frontend/src/pages/FinancialDashboard.tsx` (create)
- `frontend/src/pages/TCOCalculator.tsx` (create)
- `frontend/src/components/financial/TCOComparisonCards.tsx` (create)
- `frontend/src/components/financial/TCOEvolutionChart.tsx` (create)
- `frontend/src/components/financial/MotorizationTable.tsx` (create)
- `frontend/src/components/financial/VehicleTCOBreakdown.tsx` (create)
- `frontend/src/components/financial/FleetAggregation.tsx` (create)
- `frontend/src/hooks/useFinancialApi.ts` (create)
- `frontend/src/router.tsx` (modify)
- `frontend/src/tests/financial-tco.test.tsx` (create)

## Tests
- [ ] `test_tco_calculator_renders` — TCO calculator page renders with form inputs
- [ ] `test_tco_form_submission` — Form submits and displays results
- [ ] `test_tco_comparison_cards` — 3 cards render with correct values
- [ ] `test_tco_evolution_chart` — Chart renders with correct data points
- [ ] `test_motorization_table` — Table shows all 4 motorizations
- [ ] `test_vehicle_breakdown` — Per-vehicle breakdown shows cost components
- [ ] `test_fleet_aggregation` — Fleet summary displays correct totals

## Acceptance Criteria
- TCO calculator page allows fleet composition input and triggers calculation
- TCO comparison cards display all 3 investment models side by side
- Evolution chart renders year-by-year TCO with interactive tooltips
- Motorization table compares all 4 fuel types
- Per-vehicle breakdown and fleet aggregation are consistent
- All 7 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
