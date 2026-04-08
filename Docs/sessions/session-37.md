# Session 37 — Cost-per-Trip & Breakeven Analysis

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-32|Session 32]]
## Complexity: Medium
> Previous: [[sessions/session-36|Session 36]] | Next: [[sessions/session-38|Session 38]]

## Objective
Build cost-per-trip calculations (per available seat, per occupied seat, per employee) and breakeven analysis determining the minimum number of employees for the transport solution to be cheaper than kilometric allowance.

---

## Tasks

- [x] Create `backend/app/services/cost_analysis.py` — Cost analysis engine with all formulas
- [x] Implement PRD example: 50-seat bus at 120K/year = 5.45 EUR/seat, 6.81 at 80% fill
- [x] Create Pydantic schemas: CostAnalysisRequest, CostAnalysisResponse, BreakevenPoint
- [x] Create POST `/financial/cost-analysis` endpoint
- [x] Create `frontend/src/components/financial/CostAnalysisPanel.tsx` — form + 4 metric cards
- [x] Create `frontend/src/components/financial/BreakevenChart.tsx` — Recharts LineChart with transport/allowance curves
- [x] Create `backend/tests/test_cost_analysis.py` — 6 tests
- [x] Create `frontend/src/pages/financial/__tests__/CostAnalysis.test.tsx` — 2 tests
- [ ] **Browser verification**: pending (manual check)

## Files Created/Modified
- `backend/app/services/cost_analysis.py` (created) — 6 functions
- `backend/app/api/v1/financial.py` (modified) — POST /financial/cost-analysis
- `backend/app/schemas/financial.py` (modified) — 3 schemas
- `frontend/src/components/financial/CostAnalysisPanel.tsx` (created)
- `frontend/src/components/financial/BreakevenChart.tsx` (created)
- `frontend/src/types/financial.ts` (modified) — cost analysis types
- `frontend/src/api/financial.ts` (modified) — calculateCostAnalysis
- `backend/tests/test_cost_analysis.py` (created) — 6 tests
- `frontend/src/pages/financial/__tests__/CostAnalysis.test.tsx` (created) — 2 tests

## Tests
- [x] `test_cost_per_available_seat` — 120K/year, 50-seat bus = 5.45 EUR per seat
- [x] `test_cost_per_occupied_seat` — At 80% fill rate = 6.81 EUR per occupied seat
- [x] `test_annual_cost_per_employee` — 120K / 40 employees = 3,000 EUR
- [x] `test_breakeven_calculation` — 73 employees breakeven
- [x] `test_breakeven_edge_cases` — Zero fill rate, zero cost, zero employees
- [x] `test_cost_analysis_endpoint` — POST returns correct structure + PRD values
- [x] `test_cost_analysis_panel_renders` — Panel renders with form inputs
- [x] `test_breakeven_chart_renders` — Chart renders with SVG

## Test Results
- Tests written: 8
- Tests passing: 8
- Tests failing: 0

## Acceptance Criteria
- Cost per available seat and occupied seat match PRD example (5.45 EUR, 6.82 EUR)
- Breakeven calculation correctly identifies minimum employee count
- API endpoint accepts configurable parameters and returns all cost metrics
- Frontend displays cost metrics and breakeven chart with clear intersection
- All 8 tests pass
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
