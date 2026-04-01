# Session 07 — Site Frontend Pages

## Phase: 1 — MVP Core (Module A)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-06|Session 06]]

> Previous: [[sessions/session-06|Session 06]] | Next: [[sessions/session-08|Session 08]]

## Complexity: Medium

## Objective
Build the site management frontend pages: list, create, edit with map-based GPS picker.

---

## Tasks

- [x] Create `frontend/src/api/sites.ts` — API client functions (list, get, create, update, delete)
- [x] Create `frontend/src/types/site.ts` — Site TypeScript interfaces
- [x] Create `frontend/src/stores/siteStore.ts` — Zustand store for sites
- [x] Create `frontend/src/pages/sites/SiteListPage.tsx` — DataTable with columns: code, name, city, shifts, ZFE badge, security profile, actions
- [x] Add search bar (filter by name/code) to SiteListPage
- [x] Add filter dropdowns (city, ZFE) to SiteListPage
- [x] Add "Add Site" button linking to create page
- [x] Create `frontend/src/pages/sites/SiteCreatePage.tsx` — Form with all site fields:
  - Code, name, address, city
  - GPS coordinates (manual input + map picker)
  - Shift configuration (1-3 shifts with time pickers)
  - ZFE toggle, security profile dropdown
  - Contact name, phone
  - Notes fields
- [x] Create `frontend/src/components/maps/MapPicker.tsx` — Click-to-place GPS coordinate picker using Leaflet
- [x] Create `frontend/src/pages/sites/SiteEditPage.tsx` — Pre-filled form (reuse SiteCreatePage form)
- [x] Create `frontend/src/pages/sites/SiteDetailPage.tsx` — Read-only view with mini-map
- [x] Add site routes to `routes.tsx`
- [x] Add "Sites" link to Sidebar navigation
- [x] Handle loading, error, and empty states for all pages

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
- [x] `SiteListPage.test.tsx` — Renders table with mock data
- [x] `SiteCreatePage.test.tsx` — Form renders all fields, submit calls API
- [x] `MapPicker.test.tsx` — Renders map, click updates coordinates
- [x] `SiteDetailPage.test.tsx` — Displays site info

## Acceptance Criteria
- Site list page shows all sites with correct columns
- Search and filters work
- Create form validates required fields
- Map picker allows GPS coordinate selection
- Shift time pickers work for 1-3 shifts
- Edit page pre-fills data correctly
- Navigation between pages works

## Test Results
- Tests written: 4 (SiteListPage, SiteCreatePage, SiteDetailPage, MapPicker)
- Tests passing: 12 frontend (4 new + 8 prior)
- Tests failing: 0
- Coverage: N/A

## Notes
- Extracted shared SiteForm component used by both Create and Edit pages
- Leaflet mocks required for jsdom: mock leaflet, CSS, image imports, and react-leaflet per test file
- MapPicker uses draggable marker + click-to-place + coordinate display
- All pages follow design system: surface nesting, no borders, Manrope/Inter fonts, low-chrome chips for ZFE/security

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
