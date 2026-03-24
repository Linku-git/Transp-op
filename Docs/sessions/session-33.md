# Session 33 — ROI Calculator Engine

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-31|Session 31]]
## Complexity: High
> Previous: [[sessions/session-32|Session 32]] | Next: [[sessions/session-34|Session 34]]

## Objective
Build the ROI calculator engine implementing the 4 ROI levers from the PRD (absenteeism, retention, fleet optimization, journey productivity) with payback period calculation.

---

## Tasks

- [ ] Create `backend/app/services/roi_calculator.py` — ROI engine:
  - **ROI_absenteeism**: reduction in absenteeism rate x average daily cost x workforce size x working days
  - **ROI_retention**: reduction in turnover x average recruitment cost x workforce size
  - **ROI_fleet_optimization**: fleet cost savings from optimized routing and fill rates
  - **ROI_journey_productivity**: productive hours gained during transport x hourly cost x workforce size
  - **Total ROI**: sum of all 4 levers
  - **Payback Period**: Total Investment / Annual Total ROI (in months)
- [ ] Create Pydantic request/response schemas for ROI calculation:
  - Input: workforce size, average salary, absenteeism rate, turnover rate, transport investment, assumptions per lever
  - Output: per-lever ROI, total ROI, payback period in months, ROI percentage
- [ ] Create POST `/financial/roi/calculate` endpoint in `backend/app/api/v1/financial.py`
- [ ] Store ROI calculation results in `ROICalculation` model linked to scenario
- [ ] Create `backend/tests/test_roi_calculator.py`

## Files to Create/Modify
- `backend/app/services/roi_calculator.py` (create)
- `backend/app/api/v1/financial.py` (modify)
- `backend/app/schemas/financial.py` (modify)
- `backend/tests/test_roi_calculator.py` (create)

## Tests
- [ ] `test_roi_absenteeism_calculation` — Known inputs produce expected absenteeism ROI
- [ ] `test_roi_retention_calculation` — Known inputs produce expected retention ROI
- [ ] `test_roi_fleet_optimization` — Fleet optimization lever calculates correctly
- [ ] `test_roi_journey_productivity` — Journey productivity lever calculates correctly
- [ ] `test_roi_total` — Total ROI equals sum of all 4 levers
- [ ] `test_payback_period` — Payback period in months calculated correctly
- [ ] `test_roi_zero_investment` — Edge case: zero investment returns infinite/undefined payback
- [ ] `test_roi_endpoint_response` — POST endpoint returns valid response structure
- [ ] `test_roi_stored_in_db` — ROI results persisted in ROICalculation table

## Acceptance Criteria
- All 4 ROI lever formulas match PRD specification
- Total ROI correctly aggregates all levers
- Payback period calculated in months with correct formula
- Edge cases handled (zero investment, zero workforce)
- ROI results persisted to database when linked to a scenario
- All 9 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
