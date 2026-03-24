# Session 03 — Frontend React + TypeScript Scaffold

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-01|Session 01]]

> Previous: [[sessions/session-02|Session 02]] | Next: [[sessions/session-04|Session 04]]

## Complexity: Medium

## Objective
Scaffold the React frontend with Vite, TypeScript strict mode, TailwindCSS, routing, layout shell, and base UI components.

---

## Tasks

- [ ] Initialize Vite React TypeScript project: `npm create vite@latest frontend -- --template react-ts`
- [ ] Configure TypeScript strict mode in `tsconfig.json`
- [ ] Install and configure TailwindCSS
- [ ] Install dependencies: `react-router-dom`, `zustand`, `axios`, `recharts`, `react-leaflet`, `leaflet`, `react-i18next`, `i18next`
- [ ] Create `frontend/src/routes.tsx` — Route configuration with lazy loading
- [ ] Create `frontend/src/api/client.ts` — Axios instance with base URL, interceptors, auth header
- [ ] Create `frontend/src/components/layout/AppLayout.tsx` — Sidebar + Header + Content
- [ ] Create `frontend/src/components/layout/Sidebar.tsx` — Navigation menu with role-based items
- [ ] Create `frontend/src/components/layout/Header.tsx` — User profile, tenant name, language toggle
- [ ] Create `frontend/src/components/ui/Button.tsx` — Primary, secondary, danger, outline variants
- [ ] Create `frontend/src/components/ui/Input.tsx` — Text, number, select base component
- [ ] Create `frontend/src/components/ui/Card.tsx` — Info card component
- [ ] Create `frontend/src/components/ui/DataTable.tsx` — Sortable, paginated table shell
- [ ] Create `frontend/src/components/ui/Modal.tsx` — Dialog component
- [ ] Create `frontend/src/components/ui/Toast.tsx` — Notification toast
- [ ] Create `frontend/src/components/ui/Skeleton.tsx` — Loading skeleton
- [ ] Create `frontend/src/stores/authStore.ts` — Zustand auth store (user, token, login/logout)
- [ ] Create `frontend/src/types/index.ts` — Base TypeScript interfaces (User, Site, Employee)
- [ ] Create `frontend/src/i18n/index.ts` — i18n configuration (FR default, EN)
- [ ] Create `frontend/src/i18n/fr.json` — French translations stub
- [ ] Create `frontend/src/i18n/en.json` — English translations stub
- [ ] Create `frontend/src/pages/dashboard/DashboardPage.tsx` — Placeholder
- [ ] Create `frontend/src/pages/LoginPage.tsx` — Placeholder login page
- [ ] Create `frontend/Dockerfile` (Node 18, build, serve with nginx)
- [ ] Verify `npm run dev` starts dev server at localhost:5173
- [ ] Verify layout renders with sidebar and header
- [ ] Verify routing works (navigate between placeholder pages)

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
- [ ] `AppLayout.test.tsx` — Renders sidebar and header
- [ ] `Button.test.tsx` — Renders all variants
- [ ] `Card.test.tsx` — Renders title and content
- [ ] Routing test — navigates between pages

## Acceptance Criteria
- Dev server starts without errors
- TailwindCSS classes apply correctly
- Layout renders with sidebar navigation
- Routing works between placeholder pages
- i18n loads French by default
- TypeScript strict mode enabled (no `any` types)

## Related Documentation
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
