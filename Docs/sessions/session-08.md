# Session 08 — Site Dashboard & Shifts UI

## Phase: 1 — MVP Core (Module A)
## Prerequisites: [[sessions/session-07|Session 07]]

> Previous: [[sessions/session-07|Session 07]] | Next: [[sessions/session-09|Session 09]]

## Complexity: Low

## Objective
Add site summary dashboard view with employee/vehicle/PMR counts, and polish the shift configuration UI.

---

## Tasks

- [x] Enhance `SiteDetailPage.tsx` with summary cards: employee count, vehicle count, PMR employee count, active shifts
- [x] Create `frontend/src/components/sites/ShiftConfigPanel.tsx` — Visual shift timeline (horizontal bars per shift with entry/exit times)
- [x] Create `frontend/src/components/sites/SiteSummaryCards.tsx` — Reusable KPI cards (count + label + icon)
- [x] Add mini-map to SiteDetailPage showing site location marker
- [x] Add quick action links: "View Employees", "View Vehicles" (link to filtered lists)
- [x] Add ZFE badge and security profile badge to site detail
- [x] Create `frontend/src/components/ui/Badge.tsx` — Status badges (active, ZFE, PMR, security levels)
- [x] Handle the `/sites/{id}/summary` API call for real counts

## Files to Create/Modify
- `frontend/src/components/sites/ShiftConfigPanel.tsx` (create)
- `frontend/src/components/sites/SiteSummaryCards.tsx` (create)
- `frontend/src/components/ui/Badge.tsx` (create)
- `frontend/src/pages/sites/SiteDetailPage.tsx` (modify)

## Tests
- [x] `SiteSummaryCards.test.tsx` — Renders correct counts
- [x] `ShiftConfigPanel.test.tsx` — Renders shift bars with correct times
- [x] `Badge.test.tsx` — Renders all badge variants

## Acceptance Criteria
- Site detail page shows live employee/vehicle/PMR counts
- Shift configuration displays as visual timeline
- ZFE and security badges display correctly
- Quick links navigate to filtered employee/vehicle lists

## Test Results
- Tests written: 3 (Badge, SiteSummaryCards, ShiftConfigPanel)
- Tests passing: 17 frontend (5 new assertions across 3 files + 12 prior)
- Tests failing: 0

## Notes
- ShiftConfigPanel renders a proportional 24h timeline with overnight shift wrapping
- SiteSummaryCards fetches data via direct getSiteSummary API call (not through store)
- Badge component uses low-chrome design tokens per design system spec
- SiteDetailPage now has full detail: summary cards, shift panel, badges, quick links, notes section

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
