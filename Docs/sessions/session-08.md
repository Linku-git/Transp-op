# Session 08 — Site Dashboard & Shifts UI

## Phase: 1 — MVP Core (Module A)
## Prerequisites: [[sessions/session-07|Session 07]]

> Previous: [[sessions/session-07|Session 07]] | Next: [[sessions/session-09|Session 09]]

## Complexity: Low

## Objective
Add site summary dashboard view with employee/vehicle/PMR counts, and polish the shift configuration UI.

---

## Tasks

- [ ] Enhance `SiteDetailPage.tsx` with summary cards: employee count, vehicle count, PMR employee count, active shifts
- [ ] Create `frontend/src/components/sites/ShiftConfigPanel.tsx` — Visual shift timeline (horizontal bars per shift with entry/exit times)
- [ ] Create `frontend/src/components/sites/SiteSummaryCards.tsx` — Reusable KPI cards (count + label + icon)
- [ ] Add mini-map to SiteDetailPage showing site location marker
- [ ] Add quick action links: "View Employees", "View Vehicles" (link to filtered lists)
- [ ] Add ZFE badge and security profile badge to site detail
- [ ] Create `frontend/src/components/ui/Badge.tsx` — Status badges (active, ZFE, PMR, security levels)
- [ ] Handle the `/sites/{id}/summary` API call for real counts

## Files to Create/Modify
- `frontend/src/components/sites/ShiftConfigPanel.tsx` (create)
- `frontend/src/components/sites/SiteSummaryCards.tsx` (create)
- `frontend/src/components/ui/Badge.tsx` (create)
- `frontend/src/pages/sites/SiteDetailPage.tsx` (modify)

## Tests
- [ ] `SiteSummaryCards.test.tsx` — Renders correct counts
- [ ] `ShiftConfigPanel.test.tsx` — Renders shift bars with correct times
- [ ] `Badge.test.tsx` — Renders all badge variants

## Acceptance Criteria
- Site detail page shows live employee/vehicle/PMR counts
- Shift configuration displays as visual timeline
- ZFE and security badges display correctly
- Quick links navigate to filtered employee/vehicle lists

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
