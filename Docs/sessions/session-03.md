# Session 03 — Frontend React + TypeScript Scaffold

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-01|Session 01]]

> Previous: [[sessions/session-02|Session 02]] | Next: [[sessions/session-04|Session 04]]

## Complexity: Medium

## Objective
Scaffold the React frontend with Vite, TypeScript strict mode, TailwindCSS, routing, layout shell, and base UI components.

---

## Tasks

- [x] Initialize Vite React TypeScript project: `npm create vite@latest frontend -- --template react-ts`
- [x] Configure TypeScript strict mode in `tsconfig.json`
- [x] Install and configure TailwindCSS
- [x] Install dependencies: `react-router-dom`, `zustand`, `axios`, `recharts`, `@vis.gl/react-google-maps`, `leaflet`, `react-i18next`, `i18next`
- [x] Create `frontend/src/routes.tsx` — Route configuration with lazy loading
- [x] Create `frontend/src/api/client.ts` — Axios instance with base URL, interceptors, auth header
- [x] Create `frontend/src/components/layout/AppLayout.tsx` — Sidebar + Header + Content
- [x] Create `frontend/src/components/layout/Sidebar.tsx` — Navigation menu with role-based items
- [x] Create `frontend/src/components/layout/Header.tsx` — User profile, tenant name, language toggle
- [x] Create `frontend/src/components/ui/Button.tsx` — Primary, secondary, danger, outline variants
- [x] Create `frontend/src/components/ui/Input.tsx` — Text, number, select base component
- [x] Create `frontend/src/components/ui/Card.tsx` — Info card component
- [x] Create `frontend/src/components/ui/DataTable.tsx` — Sortable, paginated table shell
- [x] Create `frontend/src/components/ui/Modal.tsx` — Dialog component
- [x] Create `frontend/src/components/ui/Toast.tsx` — Notification toast
- [x] Create `frontend/src/components/ui/Skeleton.tsx` — Loading skeleton
- [x] Create `frontend/src/stores/authStore.ts` — Zustand auth store (user, token, login/logout)
- [x] Create `frontend/src/types/index.ts` — Base TypeScript interfaces (User, Site, Employee)
- [x] Create `frontend/src/i18n/index.ts` — i18n configuration (FR default, EN)
- [x] Create `frontend/src/i18n/fr.json` — French translations stub
- [x] Create `frontend/src/i18n/en.json` — English translations stub
- [x] Create `frontend/src/pages/dashboard/DashboardPage.tsx` — Placeholder
- [x] Create `frontend/src/pages/LoginPage.tsx` — Placeholder login page
- [x] Create `frontend/Dockerfile` (Node 18, build, serve with nginx)
- [x] Verify `npm run dev` starts dev server at localhost:5000
- [x] Verify layout renders with sidebar and header
- [x] Verify routing works (navigate between placeholder pages)

## Files to Create
- `frontend/src/routes.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Input.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/DataTable.tsx`
- `frontend/src/components/ui/Modal.tsx`
- `frontend/src/components/ui/Toast.tsx`
- `frontend/src/components/ui/Skeleton.tsx`
- `frontend/src/stores/authStore.ts`
- `frontend/src/types/index.ts`
- `frontend/src/i18n/index.ts`
- `frontend/src/i18n/fr.json`
- `frontend/src/i18n/en.json`
- `frontend/src/pages/dashboard/DashboardPage.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/Dockerfile`
- `frontend/tailwind.config.ts`

## Tests
- [x] `AppLayout.test.tsx` — Renders sidebar and header
- [x] `Button.test.tsx` — Renders all variants
- [x] `Card.test.tsx` — Renders title and content
- [x] Routing test — navigates between pages

## Acceptance Criteria
- Dev server starts without errors
- TailwindCSS classes apply correctly
- Layout renders with sidebar navigation
- Routing works between placeholder pages
- i18n loads French by default
- TypeScript strict mode enabled (no `any` types)

## Test Results
- Tests written: 8 (4 test files)
- Tests passing: 8
- Tests failing: 0
- Coverage: N/A

## Notes
- Used TailwindCSS v4 with `@tailwindcss/vite` plugin (CSS-first config via `@theme` in index.css)
- Design system tokens defined as CSS custom properties in `@theme` block
- All components follow "Architectural Conductor" design system: no borders, surface nesting, Manrope/Inter dual fonts
- React Router v7 with lazy-loaded routes for code splitting
- Vite build produces 342KB JS + 22KB CSS (gzipped: ~109KB + ~5KB)
- Vitest configured with jsdom environment and @testing-library/react

## Related Documentation
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
