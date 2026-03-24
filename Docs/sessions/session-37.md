# Session 37 — Cost-per-Trip & Breakeven Analysis

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-32|Session 32]]
## Complexity: Medium
> Previous: [[sessions/session-36|Session 36]] | Next: [[sessions/session-38|Session 38]]

## Objective
Build cost-per-trip calculations (per available seat, per occupied seat, per employee) and breakeven analysis determining the minimum number of employees for the transport solution to be cheaper than kilometric allowance.

---

## Tasks

- [ ] Create `backend/app/services/cost_analysis.py` — Cost analysis engine:
  - **Cost per available seat**: Annual route cost / (capacity x working days x 2 trips/day)
  - **Cost per occupied seat**: Annual route cost / (average occupancy x working days x 2 trips/day)
  - **Annual cost per transported employee**: Total annual transport cost / number of transported employees
  - **Breakeven point**: minimum number of employees where transport cost < kilometric allowance
    - Formula: `N_breakeven = Annual_Transport_Cost / Annual_Kilometric_Allowance_per_Employee`
    - Where kilometric allowance = average distance x cost per km x working days x 2
- [ ] Implement PRD example calculation:
  - 50-seat bus at 120,000 EUR/year
  - Cost per available seat: 120,000 / (50 x 220 x 2) = 5.45 EUR
  - At 80% fill rate: cost per occupied seat = 5.45 / 0.80 = 6.82 EUR
- [ ] Create Pydantic request/response schemas for cost analysis
- [ ] Create POST `/financial/cost-analysis` endpoint in `backend/app/api/v1/financial.py`:
  - Accepts route cost, vehicle capacity, fill rate, working days, kilometric allowance rate
  - Returns cost per available seat, cost per occupied seat, annual cost per employee, breakeven point
- [ ] Create `frontend/src/components/financial/CostAnalysisPanel.tsx`:
  - Input form for route cost, capacity, fill rate
  - Results display: cost per seat metrics, breakeven point
  - Breakeven chart showing cost curves intersection
- [ ] Create `frontend/src/components/financial/BreakevenChart.tsx`:
  - Line chart: transport cost (flat) vs kilometric allowance (linear with N employees)
  - Intersection point highlighted as breakeven
  - Shaded regions: cheaper vs more expensive zone
- [ ] Create `backend/tests/test_cost_analysis.py`
- [ ] Create `frontend/src/tests/cost-analysis.test.tsx`

## Files to Create/Modify
- `backend/app/services/cost_analysis.py` (create)
- `backend/app/api/v1/financial.py` (modify)
- `backend/app/schemas/financial.py` (modify)
- `frontend/src/components/financial/CostAnalysisPanel.tsx` (create)
- `frontend/src/components/financial/BreakevenChart.tsx` (create)
- `backend/tests/test_cost_analysis.py` (create)
- `frontend/src/tests/cost-analysis.test.tsx` (create)

## Tests
- [ ] `test_cost_per_available_seat` — 120K/year, 50-seat bus = 5.45 EUR per seat
- [ ] `test_cost_per_occupied_seat` — At 80% fill rate = 6.82 EUR per occupied seat
- [ ] `test_annual_cost_per_employee` — Total cost divided by transported employees
- [ ] `test_breakeven_calculation` — Breakeven point matches expected N employees
- [ ] `test_breakeven_edge_cases` — Zero fill rate, zero cost, single employee
- [ ] `test_cost_analysis_endpoint` — POST endpoint returns valid response
- [ ] `test_cost_analysis_panel_renders` — Frontend panel renders with inputs and results
- [ ] `test_breakeven_chart_renders` — Breakeven chart shows intersection point

## Acceptance Criteria
- Cost per available seat and occupied seat match PRD example (5.45 EUR, 6.82 EUR)
- Breakeven calculation correctly identifies minimum employee count
- API endpoint accepts configurable parameters and returns all cost metrics
- Frontend displays cost metrics and breakeven chart with clear intersection
- All 8 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
