# Session 36 — Financial Dashboard Frontend — ROI

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-35|Session 35]], [[sessions/session-33|Session 33]]
## Complexity: Medium
> Previous: [[sessions/session-35|Session 35]] | Next: [[sessions/session-37|Session 37]]

## Objective
Build the frontend ROI visualization components including the waterfall chart for ROI levers, payback period slider, cost-per-trip gauge, investment comparator cards, and DAF export button.

---

## Tasks

- [ ] Create `frontend/src/components/financial/WaterfallChart.tsx`:
  - Waterfall chart showing 4 ROI levers contributing to total ROI
  - Bars: absenteeism, retention, fleet optimization, journey productivity, total
  - Color-coded (green for gains, cumulative total bar)
  - Tooltip with lever details and assumptions
- [ ] Create `frontend/src/components/financial/PaybackSlider.tsx`:
  - Interactive slider adjusting investment amount
  - Real-time payback period recalculation (in months)
  - Visual indicator: green (<12 months), yellow (12-24), red (>24)
- [ ] Create `frontend/src/components/financial/CostPerTripGauge.tsx`:
  - Gauge/dial component showing actual cost per trip vs target
  - Color zones: below target (green), at target (yellow), above target (red)
  - Display numeric values for actual, target, and delta
- [ ] Create `frontend/src/components/financial/InvestmentComparatorCards.tsx`:
  - Side-by-side cards for CAPEX, mise a disposition, OPEX
  - Each card: total cost, annual cost, cost per employee, pros/cons summary
  - Highlight recommended model with badge
- [ ] Create `frontend/src/components/financial/DAFExportButton.tsx`:
  - Export button triggering POST `/financial/export/daf`
  - Format selector dropdown (CSV, XML, PDF, Excel)
  - Loading state during export generation
  - Download file on completion
- [ ] Integrate ROI components into `FinancialDashboard.tsx` ROI tab
- [ ] Create `frontend/src/tests/financial-roi.test.tsx`

## Files to Create/Modify
- `frontend/src/components/financial/WaterfallChart.tsx` (create)
- `frontend/src/components/financial/PaybackSlider.tsx` (create)
- `frontend/src/components/financial/CostPerTripGauge.tsx` (create)
- `frontend/src/components/financial/InvestmentComparatorCards.tsx` (create)
- `frontend/src/components/financial/DAFExportButton.tsx` (create)
- `frontend/src/pages/FinancialDashboard.tsx` (modify)
- `frontend/src/tests/financial-roi.test.tsx` (create)

## Tests
- [ ] `test_waterfall_chart_renders` — Waterfall chart renders with 4 levers and total
- [ ] `test_waterfall_chart_values` — Bar heights match ROI lever values
- [ ] `test_payback_slider_interaction` — Slider adjusts payback period in real time
- [ ] `test_payback_color_indicator` — Color changes based on payback threshold
- [ ] `test_cost_per_trip_gauge` — Gauge renders with actual vs target values
- [ ] `test_investment_comparator_cards` — 3 cards render with correct model data
- [ ] `test_daf_export_button` — Export button triggers API call and downloads file

## Acceptance Criteria
- Waterfall chart clearly shows contribution of each ROI lever to total
- Payback slider provides real-time feedback with color-coded thresholds
- Cost-per-trip gauge displays actual vs target with visual zones
- Investment comparator cards enable side-by-side model comparison
- DAF export button generates and downloads files in selected format
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
