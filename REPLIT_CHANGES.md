# Replit Agent Changes Log

> This file documents all changes made by Replit Agent for Claude Code to review.
> Do NOT delete this file. Claude Code will process it in the next session.

## Summary
- Total files modified: 35+
- Total new files created: 12+
- Categories: Replit initialization, environment config, host/proxy setup, seed data, Google Maps migration, Pydantic v2 fixes, TS build fixes, optimization sections rebuilt, modal analysis real data, KPI dashboard fix, deployment configuration, production port fix

---

## Changes

### [2026-04-08] Deployment: Port fixed to ${PORT:-8080} for Cloud Run
- **Files:** `start_production.sh`
- **What:** Changed hard-coded `--port 8000` to `--port "${PORT:-8080}"`. Cloud Run (used by both Autoscale and Reserved VM on Replit) injects a `PORT` environment variable set to 8080; the old hard-coded 8000 caused health check failures.
- **Before:** `exec uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **After:** `APP_PORT="${PORT:-8080}"; exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}"`
- **Risk:** Low

### [2026-04-08] Deployment: Switch to Reserved VM target
- **Files:** `.replit`
- **What:** Changed `deploymentTarget` from `autoscale` to `"vm"`. Autoscale restricts to a single port; this app needs Redis (6379) and multiple services.
- **Before:** `deploymentTarget = "autoscale"`
- **After:** `deploymentTarget = "vm"`
- **Risk:** Low

### [2026-04-08] Fix: KPI dashboard URL missing /api/v1 prefix
- **Files:** `frontend/src/api/kpis.ts`
- **What:** The `getDashboardKpis()` function was calling `/kpis/dashboard` (missing the `/api/v1` prefix). The Vite proxy routes `/api` → `http://localhost:8000`, so the URL must be `/api/v1/kpis/dashboard` to resolve correctly.
- **Before:** `get('/kpis/dashboard')`
- **After:** `get('/api/v1/kpis/dashboard')`
- **Risk:** Low

### [2026-04-08] Fix: Google Maps region set to Morocco (MA)
- **Files:** `frontend/src/components/maps/MapView.tsx`, `frontend/src/components/maps/MapPicker.tsx`
- **What:** Added `region="MA"` to the `APIProvider` component in both files so Google Maps biases geocoding and rendering toward Morocco including Western Sahara.
- **Risk:** Low

### [2026-04-03] Deployment: build.sh and start_production.sh created
- **Files:** `build.sh` (new), `start_production.sh` (new), `package.json` (root)
- **What:**
  - `build.sh`: runs `cd frontend && npm install && npm run build` then `pip install -r backend/requirements.txt`
  - `start_production.sh`: builds DATABASE_URL from Replit env vars, optionally starts Redis, runs Alembic migrations, starts uvicorn on `${PORT:-8080}`
  - Root `package.json` build script added for alternative invocation
- **Why:** Production deployment on Replit Reserved VM requires a build step and a separate run command
- **Risk:** Low

### [2026-04-03] Fix: Production TypeScript build errors resolved
- **Files:** `frontend/tsconfig.json`, multiple frontend source files
- **What:** Resolved all pre-existing TypeScript errors that prevented `npm run build` from succeeding:
  - Fixed `recharts` formatter types
  - Removed unused variables
  - Added `@types/google.maps` for `google.maps` namespace
  - Excluded test files from `tsconfig.json`
- **Risk:** Low

### [2026-04-03] Feature: Optimization sections rebuilt (3 pages)
- **Files:** `frontend/src/pages/optimization/StopsAnalysisSection.tsx`, `FleetOptimizerSection.tsx`, `RouteViewerSection.tsx`
- **Files (backend):** `backend/app/api/v1/transport_optimization.py` (new)
- **What:** See `Docs/sessions/session-replit.md` §7 for full detail
- **Risk:** Medium (new endpoints + rebuilt UI)

### [2026-04-03] Feature: Multi-configuration plans + 591-row seed
- **Files:** `backend/alembic/versions/h3i4j5k6l7m8_add_configuration_plan.py`, `backend/app/api/v1/configuration_plans.py`, `backend/seed_configuration.py`, `frontend/src/pages/fleet/ConfigurationTransportPage.tsx`
- **What:** `configuration_plan` table added; `configuration_transport` redesigned with 19 real columns; 591 rows seeded from attached XLSX; frontend page with 19-column grid and filters
- **Risk:** Medium

### [2026-04-03] Fix: Sidebar collapse/expand
- **Files:** `frontend/src/components/layout/AppLayout.tsx`, `frontend/src/components/layout/Sidebar.tsx`
- **What:** Collapsible sidebar (persisted in localStorage); collapses to 56px icon-only rail with tooltips
- **Risk:** Low

### [2026-04-03] Fix: Map filter panel moved outside map
- **Files:** `frontend/src/pages/map/UnifiedMapPage.tsx`
- **What:** Side-by-side layout — collapsible filter panel (288px/56px) + full-width map. No overlays on map.
- **Risk:** Low

### [2026-04-03] Feature: Shifts restructure
- **Files:** `backend/alembic/versions/g2h3i4j5k6l7_add_active_shift_ids_to_site.py`, multiple site pages, Sidebar.tsx
- **What:** Removed "Equipes/Horaires" from fleet sidebar; shift management moved to Paramètres; sites have `active_shift_ids` JSONB column; `SiteActiveShiftsPanel` added to site detail page
- **Risk:** Medium

### [2026-04-03] Feature: CSV Export/Import for Sites
- **Files:** `backend/app/api/v1/sites.py`, `frontend/src/pages/sites/SiteListPage.tsx`
- **What:** `GET /api/v1/sites/export/csv` streams UTF-8 CSV; `POST /api/v1/sites/import/csv` upserts by `code`; frontend Import/Export buttons with result banners
- **Risk:** Low

### [2026-04-02] Fix: Modal analysis real data (mobility_scoring.py rewritten)
- **Files:** `backend/app/services/mobility_scoring.py`
- **What:** Rewritten to use `Employee` model fields directly (`current_transport_mode`, `opt_in_company_transport`, `shift_time`, `has_private_car`) instead of querying the empty `employee_modal` table. All 5 modal endpoints now return real data for 1200 employees.
- **Before:** Queried `employee_modal` table (empty)
- **After:** Queries `employee` table directly
- **Risk:** Low

### [2026-04-02] Fix: Pydantic v2 error rendering across all form pages
- **Files:** `frontend/src/lib/apiError.ts` (new), Login, Employee forms, Site forms, Scenario, Constraints, Settings, Vehicle form, Point d'arrêt, Km Consommation pages
- **What:** Created `extractApiError(err, fallback)` utility. Handles Pydantic v2 `detail: string` and `detail: [{type,loc,msg}]` array formats. Applied to all form pages.
- **Risk:** Low

### [2026-04-02] Maps: Replaced all Leaflet/react-leaflet with Google Maps (@vis.gl/react-google-maps)
- **Files:** `frontend/src/components/maps/MapView.tsx`, `MapPicker.tsx`, `EmployeeMarker.tsx`, `SiteMarker.tsx`, `RoutePolyline.tsx`, `ClusterRegion.tsx`, `MeetingZoneMarker.tsx`, `AccessLeg.tsx`
- **Packages added:** `@vis.gl/react-google-maps`, `@types/google.maps`
- **What:** Rewrote all 8 map components to use `@vis.gl/react-google-maps`. All components preserve identical TypeScript props. `APIProvider` has `region="MA"` for Morocco.
- **Risk:** Medium (breaking change to map rendering; all props preserved)

### [2026-04-02] Data: Comprehensive seed data inserted
- **Files:** `backend/app/db/seed_all.py` (new), `seed_vehicles.py`, `seed_configuration.py`, `seed_km_consommation.py`, `seed_point_arret.py`
- **What:** 1200 employees, 106 vehicles, 591 config rows, KPI trend data (90 days), 4 sites, 3 optimization runs, 2 financial scenarios, weather forecasts
- **Risk:** None — idempotent checks prevent duplicate inserts on re-run

### [2026-04-02] Config: Vite allowedHosts corrected to boolean true
- **Files:** `frontend/vite.config.ts`
- **What:** `allowedHosts: 'all'` → `allowedHosts: true` (Vite 8 requires boolean)
- **Risk:** Low

### [2026-04-02] Config: Vite server config updated for Replit environment
- **Files:** `frontend/vite.config.ts`
- **What:** Port `5173`→`5000`, host `0.0.0.0`, proxy `/api`→`http://localhost:8000`, dedupe `['react','react-dom']`
- **Risk:** Low

### [2026-04-02] Config: API client base URL updated to use relative path
- **Files:** `frontend/src/api/client.ts`
- **What:** `baseURL: 'http://localhost:8000'` → `baseURL: ''`
- **Why:** Browser cannot access localhost:8000 in Replit's proxied iframe; relative URLs are proxied through Vite
- **Risk:** Low — **Important:** all API call paths must now include full `/api/v1/...` prefix

### [2026-04-02] Config: Backend CORS settings updated for Replit
- **Files:** `backend/app/main.py`
- **What:** `allow_origins=["http://localhost:5173"]`→`["*"]`, `allow_credentials=True`→`False`
- **Risk:** Low (development/demo environment)

### [2026-04-02] Init: Backend startup script created
- **Files:** `start_backend.sh` (new)
- **What:** Shell script: exports asyncpg DATABASE_URL, starts Redis daemonized, starts uvicorn on port 8000
- **Risk:** Low

### [2026-04-02] Init: Backend .env created for Replit
- **Files:** `backend/.env`
- **What:** Created from `.env.example` with Replit PostgreSQL connection (asyncpg driver, host: helium)
- **Risk:** Low

---

## Infrastructure Setup Performed (April 2026)

- PostgreSQL database: provisioned via Replit (host: helium, db: heliumdb)
- PostGIS extension: enabled
- pg_trgm extension: enabled
- Redis: installed via Nix system packages
- Python packages: installed from `backend/requirements.txt`
- Node packages: installed from `frontend/package.json`
- Database migrations: all 19 Alembic migrations applied
- Backend workflow: running on port 8000 (console)
- Frontend workflow: running on port 5000 (webview)
- Production deployment: Reserved VM, build.sh + start_production.sh, deployed to Replit .app domain
