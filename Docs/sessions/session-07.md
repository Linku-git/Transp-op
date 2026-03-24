# Session 07 — Site Frontend Pages

## Phase: 1 — MVP Core (Module A)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-06|Session 06]]

> Previous: [[sessions/session-06|Session 06]] | Next: [[sessions/session-08|Session 08]]

## Complexity: Medium

## Objective
Build the site management frontend pages: list, create, edit with map-based GPS picker.

---

## Tasks

- [ ] Create `frontend/src/api/sites.ts` — API client functions (list, get, create, update, delete)
- [ ] Create `frontend/src/types/site.ts` — Site TypeScript interfaces
- [ ] Create `frontend/src/stores/siteStore.ts` — Zustand store for sites
- [ ] Create `frontend/src/pages/sites/SiteListPage.tsx` — DataTable with columns: code, name, city, shifts, ZFE badge, security profile, actions
- [ ] Add search bar (filter by name/code) to SiteListPage
- [ ] Add filter dropdowns (city, ZFE) to SiteListPage
- [ ] Add "Add Site" button linking to create page
- [ ] Create `frontend/src/pages/sites/SiteCreatePage.tsx` — Form with all site fields:
  - Code, name, address, city
  - GPS coordinates (manual input + map picker)
  - Shift configuration (1-3 shifts with time pickers)
  - ZFE toggle, security profile dropdown
  - Contact name, phone
  - Notes fields
- [ ] Create `frontend/src/components/maps/MapPicker.tsx` — Click-to-place GPS coordinate picker using Leaflet
- [ ] Create `frontend/src/pages/sites/SiteEditPage.tsx` — Pre-filled form (reuse SiteCreatePage form)
- [ ] Create `frontend/src/pages/sites/SiteDetailPage.tsx` — Read-only view with mini-map
- [ ] Add site routes to `routes.tsx`
- [ ] Add "Sites" link to Sidebar navigation
- [ ] Handle loading, error, and empty states for all pages

## Files to Create/Modify
- `frontend/src/api/sites.ts` (create)
- `frontend/src/types/site.ts` (create)
- `frontend/src/stores/siteStore.ts` (create)
- `frontend/src/pages/sites/SiteListPage.tsx` (create)
- `frontend/src/pages/sites/SiteCreatePage.tsx` (create)
- `frontend/src/pages/sites/SiteEditPage.tsx` (create)
- `frontend/src/pages/sites/SiteDetailPage.tsx` (create)
- `frontend/src/components/maps/MapPicker.tsx` (create)
- `frontend/src/routes.tsx` (modify)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

## Tests
- [ ] `SiteListPage.test.tsx` — Renders table with mock data
- [ ] `SiteCreatePage.test.tsx` — Form renders all fields, submit calls API
- [ ] `MapPicker.test.tsx` — Renders map, click updates coordinates
- [ ] `SiteDetailPage.test.tsx` — Displays site info

## Acceptance Criteria
- Site list page shows all sites with correct columns
- Search and filters work
- Create form validates required fields
- Map picker allows GPS coordinate selection
- Shift time pickers work for 1-3 shifts
- Edit page pre-fills data correctly
- Navigation between pages works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
