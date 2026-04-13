# Transpop — Product Requirements Document (PRD v4.0)

> **Version:** 4.0 — Updated 2026-04-08 to reflect all Replit deployment and refinement changes
> **Previous version:** v3.0 (pre-Replit, sessions 1-44 planned)
> **Status:** Sessions 1-44 + Replit phase complete. Live on Replit Reserved VM.
>
> See also: [[ARCHITECTURE]] | [[DATABASE_SCHEMA]] | [[API_ENDPOINTS]] | [[FRONTEND_PAGES]] | [[PROGRESS]]

---

## 1. Product Overview

### 1.1 Product Identity

| Field | Value |
|-------|-------|
| **Codename** | Transpop |
| **Full Name** | Plateforme d'Orchestration Mobilité RH |
| **Type** | Enterprise SaaS — B2B |
| **Market** | HR Transport Management — Morocco / North Africa / MENA |
| **Target** | Large enterprises (500–5000+ employees) with company transport needs |
| **Languages** | French (primary), Arabic (future), English |

### 1.2 Elevator Pitch

Transpop is an intelligent HR mobility orchestration platform that gives enterprises a **fully dimensioned, financially optimized, and secured transport model**. Unlike operational tools (SWVL, Via), Transpop intervenes **before exploitation** — delivering diagnostic, route-planning, financial engineering, and journey valorization.

A DRH launches a new industrial site. In 10 minutes, Transpop:
1. Clusters 1,200 employee addresses into geographic zones
2. Assigns the right vehicle type (AUTOCAR/MINIBUS/MINICAR) to each cluster
3. Calculates the optimal route per vehicle
4. Produces a 5-year TCO + ROI comparison (own fleet vs leasing)
5. Exports a PDF for the DAF and a sizing plan for the operator

### 1.3 Current Status (as of 2026-04-08)

| Phase | Status | Details |
|-------|--------|---------|
| Phases 0–2 (Sessions 1–44) | ✅ COMPLETE | Full web platform built and tested |
| Replit Deployment (R01) | ✅ LIVE | Reserved VM, 1200 employees, 106 vehicles |
| Phase 3 — Mobile (Sessions 45–56) | ✅ COMPLETE | Flutter app for employees |
| Phase 4 — Security & RTI (Sessions 57–66) | ✅ COMPLETE | Stop risk scoring, RTI, emergency alerts |
| Phase 5 — Journey Valorization (Sessions 67–76) | ✅ COMPLETE | Content, surveys, LMS, engagement |
| Phase 6 — Enterprise Integrations (Sessions 77–86) | ✅ COMPLETE | SIRH, operators, ERP, payments |
| Phase 7 — Stabilization & Scale (Sessions 87–92) | 🔄 IN PROGRESS | Performance, security, RGPD, a11y (5/6) |
| Phase 8 — SOTREG Modules M1–M8 (Sessions 93–127) | 🔜 NOT STARTED | Advanced optimization, ML, real-time ops |

---

## 2. User Profiles

### 2.1 DRH — Directeur/trice des Ressources Humaines
- **Interface:** Web Dashboard
- **Primary tasks:** Configure mobility policy, validate transport sizing, oversee employee data, manage sites and shifts
- **Key screens:** Operations Dashboard, Employee Map, Optimization Hub, Scenario Comparison, Settings
- **RBAC role:** `drh`

### 2.2 DAF — Directeur/trice Administratif/ve et Financier/ère
- **Interface:** Web Dashboard
- **Primary tasks:** Analyze TCO/ROI, compare investment models, export financial data to ERP
- **Key screens:** Financial Dashboard (TCO + ROI), Investment Comparator, DAF Export
- **RBAC role:** `daf`

### 2.3 Salarié — Employee
- **Interface:** Flutter Mobile App _(Phase 3 — not yet built)_
- **Primary tasks:** Book/cancel trips, view real-time vehicle tracking (RTI), receive push notifications, consume learning content during journey
- **Key screens:** Home, Trip Booking, RTI Map, Profile, CO2 Impact
- **RBAC role:** `salarie`

### 2.4 Opérateur — Transport Operator
- **Interface:** Web Dashboard (read-only portal) _(Phase 6)_
- **Primary tasks:** View sizing plans, confirm vehicle assignments
- **RBAC role:** `operateur`

### 2.5 Admin — Platform Administrator
- **Interface:** Web Admin Panel
- **Primary tasks:** Manage users, tenants, SIRH integrations, API keys, RGPD compliance
- **RBAC role:** `admin`

---

## 3. Architecture (Current, Live)

### 3.1 Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Backend** | Python 3.12 / FastAPI / SQLAlchemy 2.0 async | Pydantic v2 throughout |
| **Database** | PostgreSQL 15 + PostGIS + pg_trgm | Hosted on Replit (helium) |
| **Queue** | Redis 7 + Celery | Redis optional in production |
| **Optimization** | Google OR-Tools + scikit-learn (DBSCAN/KMeans) | |
| **Frontend** | React 19 / TypeScript (strict) / Vite | Port 5000 (dev), 8080 (prod) |
| **UI** | TailwindCSS v4 + "Azure Velocity" design system | Primary: #0058be |
| **Charts** | Recharts | |
| **Maps** | `@vis.gl/react-google-maps` (Google Maps) | Replaced Leaflet. region="MA" |
| **State** | Zustand | |
| **Mobile** | Flutter (Dart) / Riverpod / Firebase FCM | Phase 3 — not yet built |
| **Hosting** | Replit Reserved VM | Cloud Run; PORT=8080 |
| **Build** | `build.sh` (npm build + pip install) | |
| **DB Migrations** | Alembic (19 migrations applied) | |

### 3.2 Key Architecture Decisions Made During Replit Phase

| Decision | Rationale |
|----------|-----------|
| **Leaflet → Google Maps** | User request; `@vis.gl/react-google-maps` package used (not the older `@react-google-maps/api`) |
| **region="MA"** on APIProvider | Morocco + Western Sahara rendering |
| **baseURL: ''** in API client | Replit proxied iframe — relative URLs via Vite proxy `/api`→`localhost:8000` |
| **CORS allow_origins=["*"]** | Replit's origin varies; `allow_credentials=False` required with wildcard |
| **Reserved VM** (not Autoscale) | Autoscale = single port; VM supports Redis + multi-service |
| **PORT=${PORT:-8080}** | Cloud Run injects PORT=8080; never hard-code 8000 in production |
| **Open-Meteo** (no key) | Replaced OpenWeatherMap; free, no API key needed |

### 3.3 Infrastructure Ports

| Service | Dev Port | Prod Port |
|---------|----------|-----------|
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| FastAPI (uvicorn) | 8000 | `${PORT:-8080}` |
| Vite dev server | 5000 | — (served by FastAPI in prod) |

---

## 4. Database — Current State

**41 tables, 19 Alembic migrations, PostgreSQL 15 + PostGIS**

### 4.1 Migrations Applied

| ID | Description | Phase |
|----|-------------|-------|
| `72f2ddb31929` | Auth tables (user, role, tenant) | 0 |
| `6a184bb1915d` | Site table with PostGIS geometry | 1 |
| `dbe84fb4d94d` | Vehicle table | 1 |
| `c372c3416485` | Optimization + Cluster tables | 1 |
| `62f4c8fa5cd7` | Route table | 1 |
| `a1b2c3d4e5f6` | Scenario table | 1 |
| `93e4979d00f3` | EmployeeModal table | 1 |
| `e7053e5ce269` | EmployeeLeave table | 1 |
| `dbc17ef335ab` | WeatherForecast table | 1 |
| `b2c3d4e5f6a7` | OptimizationSettings + ConstraintParam | 1 |
| `c2d3e4f5a6b7` | HoraireTravail table | 1 |
| `c3d4e5f6a7b8` | Financial tables (scenario, tco, roi, vehicle_reference) | 2 |
| `d4e5f6a7b8c9` | GeneratedReport table | 2 |
| `e5f6a7b8c9d0` | KPISnapshot table | 2 |
| `d1e2f3a4b5c6` | Shift type columns on employee | R01 |
| `f1a2b3c4d5e6` | Fleet tables (km_consommation, point_arret, config_transport) | R01 |
| `g2h3i4j5k6l7` | `active_shift_ids` JSONB on site | R01 |
| `h3i4j5k6l7m8` | `configuration_plan` table | R01 |
| `i4j5k6l7m8n9` | `point_arret_id` FK on employee | R01 |

### 4.2 Table Groups

| Group | Tables |
|-------|--------|
| Auth | `tenant`, `user`, `role`, `permission`, `role_permission` |
| Sites | `site` (PostGIS), `shift_type` |
| Employees | `employee` (30+ cols), `employee_leave`, `employee_modal` (legacy) |
| Fleet | `vehicle`, `km_consommation`, `point_arret`, `configuration_transport`, `configuration_plan` |
| Optimization | `optimization_run`, `cluster`, `route`, `vehicle_assignment` |
| Scenarios | `transport_scenario`, `optimization_settings`, `constraint_param` |
| Financial | `financial_scenario`, `tco_entry`, `roi_calculation`, `investment_comparison`, `vehicle_reference` |
| Reporting | `generated_report`, `kpi_snapshot` |
| Weather | `weather_forecast` |
| Scheduling | `horaire_travail` |

### 4.3 Live Demo Data

| Entity | Count |
|--------|-------|
| Employees | 1,200 (all with lat/lng) |
| Vehicles | 106 |
| Configuration Transport rows | 591 (plan: "Configuration Initiale 2024") |
| Total fleet distance | 32,696 km |
| Sites | 4 (Casablanca industrial zones) |
| KPI snapshots | 90 days of trend data |

---

## 5. API — Current Endpoints (130+)

### 5.1 Implemented Routers

| Router | Prefix | Key Endpoints | Session |
|--------|--------|---------------|---------|
| Auth | `/api/v1/auth` | login, logout, refresh, me | 04 |
| Users | `/api/v1/users` | CRUD + roles + tenants | 04 |
| Sites | `/api/v1/sites` | CRUD + summary + export/import CSV | 06, R01 |
| Employees | `/api/v1/employees` | CRUD + CSV upload + geocode + summary (page_size up to 2000) | 09 |
| Employee Modal | `/api/v1/modal` | stats, shift-analysis, mobility-scores, shadow-zones, carpool-potential | 15, R01 |
| Employee Leaves | `/api/v1/employees/{id}/leaves` | CRUD + overlap detection | 12 |
| Excel Import | `/api/v1/excel` | upload, preview, import (6-sheet parser) | 13 |
| Vehicles | `/api/v1/vehicles` | CRUD + fleet summary | 20 |
| Km Consommation | `/api/v1/km-consommation` | CRUD | R01 |
| Points d'Arrêt | `/api/v1/point-arret` | CRUD | R01 |
| Config Transport | `/api/v1/configuration-transport` | CRUD (19 columns) | R01 |
| Config Plans | `/api/v1/configuration-plans` | GET/POST/PATCH/DELETE | R01 |
| Optimization | `/api/v1/optimization` | run, status, results, history, settings | 21–23 |
| Transport Optim | `/api/v1/transport-optimization` | stops, plan analysis/optimize/trips, trip detail | R01 |
| Scenarios | `/api/v1/scenarios` | CRUD + compare + apply | 27 |
| Weather | `/api/v1/weather` | forecast, refresh (Open-Meteo, free) | 26 |
| Financial | `/api/v1/financial` | scenarios, TCO, ROI, comparator | 31–34 |
| KPIs | `/api/v1/kpis` | dashboard, snapshot, trend | 39, 44 |
| Exports | `/api/v1/exports` | PDF, Excel, CSV, GeoJSON | 30 |
| Reports | `/api/v1/reports` | list, generate, history | 42–43 |
| Settings | `/api/v1/settings` | optimization settings + constraints | 29 |
| Vehicle Assignments | `/api/v1/vehicle-assignments` | bin-packing assignment | 21 |
| Health | `/health`, `/api/v1/health` | health check | 02 |

### 5.2 Critical API Notes for Claude Code

- **Base URL:** `baseURL: ''` in axios client — all paths must start with `/api/v1/`
- **Pagination:** `?page=1&page_size=20` → `{data:[], total, page, pages}`
- **Error format:** Pydantic v2 — use `extractApiError(err, fallback)` from `@/lib/apiError.ts`
- **Employees:** max `page_size=2000` to fetch all 1200 in one request
- **CORS:** wildcard, no credentials — all browser origins accepted

---

## 6. Web Platform — Implemented Features (Sessions 1–44 + R01)

### 6.1 Module A — Site Management ✅

**Routes:** `/sites`, `/sites/new`, `/sites/:id`, `/sites/:id/edit`

| Feature | Status |
|---------|--------|
| Site CRUD (name, code, city, PostGIS coordinates) | ✅ |
| MapPicker (Google Maps, draggable marker, region=MA) | ✅ |
| Site summary cards (employees, vehicles, PMR count) | ✅ |
| Shift management per site (active_shift_ids JSONB) | ✅ |
| SiteActiveShiftsPanel on detail page | ✅ |
| CSV Export (`GET /sites/export/csv`) | ✅ |
| CSV Import (`POST /sites/import/csv`, upsert by code) | ✅ |
| Company-wide shift CRUD moved to Paramètres | ✅ |

### 6.2 Module B — Employee Management ✅

**Routes:** `/employees`, `/employees/new`, `/employees/:id`, `/employees/:id/edit`, `/employees/map`

| Feature | Status |
|---------|--------|
| Employee CRUD (30+ fields: name, address, site, shift, transport mode, PMR, etc.) | ✅ |
| Employee map view (Google Maps, site-colored AdvancedMarkers, 1200 employees) | ✅ |
| Filters: site, shift, transport mode, PMR, active, department | ✅ |
| Bulk CSV upload + geocoding | ✅ |
| Employee leave management (CRUD + overlap detection) | ✅ |
| Employee fields: `current_transport_mode`, `opt_in_company_transport`, `has_private_car`, `active`, `shift_time` (P1/P2/P3/N/S) | ✅ |

### 6.3 Module C — Modal Analysis ✅

**Routes:** `/modal-analysis`

| Feature | Status |
|---------|--------|
| Transport mode distribution (PieChart + BarChart) | ✅ |
| Shift-based analysis | ✅ |
| Mobility scoring engine (0–100, uses Employee fields directly) | ✅ |
| Shadow zones detection (employees >X km from any stop) | ✅ |
| Carpool potential analysis | ✅ |
| All 5 endpoints use real Employee data (not empty employee_modal table) | ✅ |

### 6.4 Module D — Optimization Engine ✅

**Routes:** `/optimization`, `/optimization/stops`, `/optimization/fleet`, `/optimization/routes`

| Feature | Status |
|---------|--------|
| Employee clustering (DBSCAN / KMeans / hierarchical) | ✅ |
| Meeting zone optimization (PMR-aware, walking constraints) | ✅ |
| Vehicle assignment (bin-packing, split/merge, PMR/ZFE) | ✅ |
| Route optimization (OR-Tools CVRP + OSRM) | ✅ |
| Full async pipeline (Celery task, Redis progress) | ✅ |
| **Optimization Hub (3 sections rebuilt in R01):** | ✅ |
| — StopsAnalysisSection: KPI strip + BarChart + map + AI suggestions (MERGE/REMOVE/RELOCATE/ADD) | ✅ |
| — FleetOptimizerSection: mode toggle wizard, VRP-greedy new config, KPI results | ✅ |
| — RouteViewerSection: DirectionsService, chunked waypoints, error banners | ✅ |
| Scenario comparison (3 transport scenarios) | ✅ |
| Weather integration (Open-Meteo, scenario suggestions) | ✅ |

### 6.5 Module E — Financial Engineering ✅

**Routes:** `/financial`, `/financial/tco`, `/financial/roi`, `/financial/comparator`

| Feature | Status |
|---------|--------|
| Financial scenario CRUD | ✅ |
| TCO Calculator (fleet/motorization/evolution) | ✅ |
| ROI Calculator (4 levers: cost savings, absenteeism, retention, ZFE) | ✅ |
| Payback analysis with slider | ✅ |
| Investment model comparator (CAPEX/MaD/OPEX + sensitivity analysis) | ✅ |
| WaterfallChart, GaugeChart, BarChart for TCO/ROI | ✅ |
| DAF Export (SAP FI / Sage / Cegid CSV+XML, PDF+Excel) | ✅ |
| Cost-per-trip + breakeven analysis | ✅ |

### 6.6 HR Dashboard & RSE ✅

**Routes:** `/dashboard/hr`, `/dashboard/rse`

| Feature | Status |
|---------|--------|
| Mobility coverage KPIs | ✅ |
| Absenteeism + retention analysis | ✅ |
| HeatmapTable, ScatterPlot, RetentionCard | ✅ |
| Shadow zones + mobility alerts | ✅ |
| CO2 / modal / ZFE dashboard | ✅ |
| DPEF export | ✅ |

### 6.7 Reporting ✅

**Routes:** `/reports`, `/reports/generate`

| Feature | Status |
|---------|--------|
| Report list + generator page | ✅ |
| 4 report types (PDF + Excel) | ✅ |
| DB persistence (GeneratedReport model) | ✅ |
| KPI snapshot system (daily Celery task, 6 KPI types, trend queries) | ✅ |

### 6.8 Fleet Module ✅

**Routes:** `/vehicles`, `/fleet/consumption`, `/fleet/stops`, `/fleet/config`

| Feature | Status |
|---------|--------|
| Vehicle CRUD (106 vehicles seeded) | ✅ |
| Km & Consommation tracking | ✅ |
| Points d'Arrêt SOTREG management | ✅ |
| Configuration Transport (19 columns, 591 rows from XLSX) | ✅ |
| Configuration Plans (plan selector, multi-configuration support) | ✅ |
| 19-column data grid with filters (prestataire, secteur, shift, A/R, type vehicule) | ✅ |

### 6.9 Shared UX Improvements (R01) ✅

| Feature | Status |
|---------|--------|
| Sidebar collapse/expand (56px icon-only rail, localStorage-persisted) | ✅ |
| Map filter panel side-by-side layout (no overlays on map) | ✅ |
| Pydantic v2 error rendering (`extractApiError`) on all form pages | ✅ |
| Excel Import (6-sheet parser: employees, vehicles, stops, config, fuel, shifts) | ✅ |
| Settings page (optimization settings + constraints + company-wide shifts) | ✅ |

---

## 7. Vehicle Constants (Business Rules)

| Type | Capacity | Cost/km (MAD) | Use Case |
|------|----------|---------------|----------|
| AUTOCAR | 54 seats | 4.50 | Long routes, large clusters |
| MINIBUS | 25 seats | 3.20 | Medium clusters, urban routes |
| MINICAR | 12 seats | 2.50 | Small clusters, tight streets |

---

## 8. Design System — "Azure Velocity"

| Token | Value |
|-------|-------|
| Primary | `#0058be` (Azure Blue) |
| Font | Inter |
| Icons | Material Symbols Outlined |
| Card style | `bg-white rounded-xl shadow-sm border border-outline-variant/10` |
| Button primary | `bg-primary text-white hover:bg-primary/90` |
| Full spec | `Docs/DESIGN_SYSTEM.md` |

---

## 9. Mobile App — Planned (Phase 3, Sessions 45–56)

> **Status:** NOT STARTED. The `mobile/` directory does not yet exist. Sessions 45–56 build it from scratch.

### 9.1 Tech Stack (Planned)
- **Framework:** Flutter (Dart) — iOS 15+ / Android 10+ (API 29+)
- **State:** Riverpod
- **Maps:** Google Maps for Flutter
- **Push:** Firebase FCM
- **Offline:** Hive (key-value) + SQLite (structured queries)
- **Auth:** JWT from the existing FastAPI backend (same `/api/v1/auth/login`)
- **Real-time:** WebSocket for RTI vehicle positions

### 9.2 Screens Planned

| Session | Screen | Description |
|---------|--------|-------------|
| 45 | Flutter Setup | `mobile/` monorepo dir, dependencies, design system |
| 46 | Auth Flow | Login, biometric unlock, JWT refresh |
| 47 | Onboarding Wizard | Transport preference setup (bus/carpool/car) |
| 48 | Home Screen | Today's trip, next stop countdown, alerts |
| 49 | Trip Booking | Schedule view, book/cancel |
| 50 | Trip Management | My trips history, cancellation |
| 51 | RTI + Vehicle Tracking | Real-time map, vehicle ETA |
| 52 | Push Notifications | FCM setup, alert types |
| 53 | Profile & Preferences | Employee settings, language, notifications |
| 54 | Mobile API Backend | FastAPI mobile-specific endpoints |
| 55 | CO2 / Trip Stats | Personal impact dashboard |
| 56 | Offline Mode | Hive + SQLite sync queue |

### 9.3 Backend API Endpoints (to be added in Session 54)
- `GET /api/v1/mobile/trip/today` — today's scheduled trip
- `POST /api/v1/mobile/trip/book` — book a seat
- `DELETE /api/v1/mobile/trip/{id}` — cancel booking
- `GET /api/v1/mobile/trip/history` — past trips
- `GET /api/v1/mobile/rti/vehicle/{id}` — real-time vehicle position
- `GET /api/v1/mobile/profile` — employee profile
- `PUT /api/v1/mobile/profile/preferences` — update transport preferences
- `GET /api/v1/mobile/stats/co2` — personal CO2 savings
- `POST /api/v1/mobile/device` — register FCM token

---

## 10. Planned Phases (Sessions 57–92)

### Phase 4 — Security & RTI (Sessions 57–66)
- Stop risk scoring model (lighting, isolation, historical incidents)
- Real-Time Information (RTI) backend: WebSocket, GPS vehicle tracking
- RTI Monitoring Dashboard (supervisor view)
- Employee security questionnaire + scoring engine
- Security-constrained route optimization
- Mobile night mode + emergency alert system

### Phase 5 — Journey Valorization (Sessions 67–76)
- Content management (articles, videos, micro-training)
- Mobile content feed during trips
- Survey/poll system
- LMS integration (Cornerstone, 360Learning)
- Engagement analytics dashboard

### Phase 6 — Enterprise Integrations (Sessions 77–86)
- SIRH connectors: SAP SuccessFactors, Workday, Talentsoft, Sage
- Operator portal (read-only sizing plan view)
- Via & SWVL API integration
- ERP finance export (SAP FI / Sage / Cegid)
- Payment & transport pass

### Phase 7 — Stabilization & Scale (Sessions 87–92)
- Performance optimization (N+1 queries, caching, load testing)
- Security hardening + pentest
- RGPD audit & compliance (30-day retention, consent management)
- Accessibility audit (WCAG 2.1 AA)
- App Store preparation + final documentation

### Phase 8 — SOTREG Modules M1–M8 (Sessions 93–127)
- M1 Diagnostic & Contexte (transport lines, gravity model, ZFE detection)
- M2 Technologies & Motorisations (range correction, 15-year TCO, IRVE sizing)
- M3 Infrastructures & Depots (stop generation, HCM capacity model, depot layout)
- M4 Performance & Maintenance (AVL KPIs, LTO anti-platooning, predictive maintenance)
- M5 Financement avance (NPV, Markowitz portfolio, supernetwork equilibrium)
- M6 Phasage & Roadmap (electrification transition planner, Gantt chart)
- M7 Scoring Global & MCDA (6-criteria weighted sum, McFadden logit)
- M8 Exploitation Temps Reel & ML (Clarke & Wright, GA, LSTM, RandomForest, SocketIO)
- ML Infrastructure (model registry, feature store, retraining pipeline)
- Portals (driver portal, contractor dashboard Dash+Plotly)
- Observability (Prometheus + Grafana + Loki + OpenTelemetry)
- Rasa chatbot & final integration

---

## 11. Critical Notes for Claude Code Resuming Development

### 11.1 Must-Know Patterns

```typescript
// ❌ WRONG — missing /api/v1 prefix
await apiClient.get('/kpis/dashboard')

// ✅ CORRECT — always full path
await apiClient.get('/api/v1/kpis/dashboard')
```

```typescript
// ❌ WRONG — Pydantic v2 detail can be array
setError(err.response?.data?.detail)

// ✅ CORRECT — handles both string and array formats
import { extractApiError } from '@/lib/apiError';
setError(extractApiError(err, 'Une erreur est survenue'))
```

```tsx
// ❌ WRONG — old package
import { GoogleMap } from '@react-google-maps/api'

// ✅ CORRECT — current package
import { APIProvider, Map, AdvancedMarker } from '@vis.gl/react-google-maps'
// APIProvider must have region="MA" on MapView and MapPicker
```

### 11.2 Files to Read First (in order)
1. `CLAUDE.md` — project context, rules, Replit-specific constraints
2. `Docs/sessions/session-replit.md` — complete Replit phase log
3. `Docs/PROGRESS.md` — what's done, what's next
4. `Docs/ARCHITECTURE.md` — system design
5. `Docs/DATABASE_SCHEMA.md` — all 41 tables
6. `Docs/API_ENDPOINTS.md` — all ~130+ endpoints
7. `replit.md` — always-loaded Replit context

### 11.3 Environment Quick Reference

| Context | Value |
|---------|-------|
| Admin login | `admin@transpop.dev` / `admin123` |
| Tenant ID | `0cea9745-6aa2-4105-9bdc-341d95999048` |
| DB host (Replit) | `helium:5432/heliumdb` |
| Dev backend | `http://localhost:8000` |
| Dev frontend | `http://localhost:5000` |
| Prod port | `${PORT:-8080}` (Cloud Run) |
| Google Maps | `VITE_GOOGLE_MAPS_API_KEY` Replit secret |

---

## 12. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-15 | Initial PRD — project scope, modules, user profiles |
| v2.0 | 2026-03-28 | Database schema (38 tables), API endpoints (~125), session plan (92 sessions) |
| v3.0 | 2026-04-01 | Sessions 1–44 planned and documented |
| v4.0 | 2026-04-08 | Sessions 1–44 complete + Replit deployment phase: Google Maps migration, real seed data (1200 employees/106 vehicles), Pydantic v2, optimization sections rebuilt, production on Replit Reserved VM, port/CORS/proxy config documented |
| v5.0 | 2026-04-09 | SOTREG Modules M1–M8 integrated: 35 new sessions (93–127) covering transport line model, 15-year TCO, IRVE sizing, AVL KPIs, predictive maintenance (Isolation Forest), Markowitz portfolio optimization, MCDA scoring, Clarke & Wright + Genetic Algorithm routing, LSTM demand forecasting, RandomForest driver risk scoring, SocketIO real-time streaming, driver/contractor portals, observability stack, Rasa chatbot |

---

## 13. SOTREG Modules (M1–M8)

> **Source:** CDC Technique SOTREG v5.0 Final — Avril 2026
> **Client:** OCP Group — Transport Personnel
> **Scope:** 1,500 vehicles | 80M km/year | 50,000 tCO2/year | Net Zero 2035

### 13.1 Overview

SOTREG (Systeme d'Optimisation du Transport REGulier) extends Transpop with 8 specialized modules covering the full lifecycle of corporate fleet management: diagnostic, technology selection, infrastructure sizing, performance monitoring, financial engineering, phased transition planning, multi-criteria scoring, and real-time operations with ML-powered intelligence.

**Academic Foundations:** D1 WMATA/KFH (bus stop guidelines), D2 Wang et al. (M/G/S queuing), D3 MetroNow (OTP KPIs), D4 Liu (Genetic Algorithms for VRP), D5 Chennai (predictive maintenance), D6 Dhaka/OCP (TCO/electrification), D7 Adelaide (4-step transport model), D8 Project Report.

### 13.2 Module M1 — Diagnostic & Contexte

**Foundation:** Transportation Planning 4-step model (McNally 2007), Wilson gravity model (1967)

| Feature | Specification |
|---------|--------------|
| **Ligne model** | Transport line entity: `km_an = D x R x J` (distance x rotations x operating_days). PostgreSQL `GENERATED ALWAYS AS STORED` computed column |
| **Fleet Context** | 1,500 vehicles, total km/year, tCO2/year, motorization split, average age |
| **Gravity model OD** | `T_ij = A_i x O_i x B_j x D_j x f(c_ij)` with exponential deterrence. Furness iterative proportional fitting for balancing |
| **ZFE detection** | ADEME API integration for Zone a Faibles Emissions compliance check |
| **Service types** | navette, liaison, vip, mixte |

### 13.3 Module M2 — Technologies & Motorisations

**Foundation:** ARCHIMEDES (Skarlis et al. 2018), D6 Dhaka/OCP, Qin et al. (2016)

| Feature | Specification |
|---------|--------------|
| **Range correction** | `A_reelle = A_base / (k_pente x k_saison x k_vitesse)`. k_pente in {1.00, 1.15, 1.30, 1.60}, k_saison in {1.00, 1.25, 1.30} |
| **15-year TCO** | `TCO = CAPEX_net + OPEX_total + C_financement`. With energy price escalation and MAD calibration |
| **Electrification breakeven** | `km_seuil = Delta_CAPEX / delta_opex_km` ~ 48,500 km/an. If km_an > km_seuil, electrification is profitable |
| **Demand charge** | Qin 2016: charge to SOC=62% to minimize peak demand. 500 kWh buffer storage at depot |
| **IRVE sizing** | `nb_bornes_50kW = ceil(n_veh_elec / 2)`, `nb_bornes_150kW = ceil(n_veh_elec / 5)`. Grid reinforcement if P_available < P_simultaneous x 0.62 |
| **Technologies** | diesel (250k, 2.28 EUR/km), electric (350k, 1.25 EUR/km), hybrid, GNV, hydrogen |

### 13.4 Module M3 — Infrastructures & Depots

**Foundation:** D1 WMATA/KFH, D2 Wang et al. (HCM 2000), Ren et al. (2019) DBSCAN

| Feature | Specification |
|---------|--------------|
| **Stop generation** | DBSCAN with eps=500m, MinPts=5, haversine distance, Ball-tree indexing. O(n log n) for n=5000 employees |
| **Stop capacity** | HCM 2000 model: `Bs = N_berths x 3600 x (g/C) / [t_c + t_d x (g/C) + Z x c_v x t_d]`. Log-normal service time (K-S validated). LOS grading A-F |
| **IRVE cost** | Installation + transformer upgrade + grid connection + civil works per depot |
| **Depot layout** | Charger positions, parking bays, maintenance area allocation (m2) |

### 13.5 Module M4 — Performance & Maintenance

**Foundation:** D3 MetroNow, Zimmer et al. (2018) LTO, D5 Chennai, Liu et al. (2012) Isolation Forest

| Feature | Specification |
|---------|--------------|
| **OTP** | On-Time Performance > 95%. Window: +/- 2 min from schedule |
| **Headway COV** | Coefficient of variation < 0.3. Beyond 0.3 triggers LTO correction |
| **Load Factor** | nb_passengers / capacity. Alert if LF > 1.0 |
| **Commercial speed** | V_com = D_route / T_service. Target >= 25 km/h urban |
| **LTO** | `t_LTO = t_planned + delta_GPS`, delta in [-t_leeway, +t_break]. Triggered if COV > 0.3 AND \|t_real - t_planned\| > 3 min |
| **Isolation Forest** | n_estimators=200, contamination=0.05. Features: vibration, temperature, pressure, CAN bus, km, age. Score > 0.7 = critical, > 0.4 = medium. Retrain quarterly |
| **IoT telemetry** | Webhook ingestion, rolling feature extraction (1h/24h/7d windows) |

### 13.6 Module M5 — Financement Avance

**Foundation:** D6 Dhaka/OCP, Markowitz (1952), Dong, Zhang & Nagurney (2004)

| Feature | Specification |
|---------|--------------|
| **NPV** | `VAN = -CAPEX + Sum[CF_t / (1+r)^t]`. IRR via Brentq root finding |
| **CO2 externalities** | `G = C_CO2_avoided x carbon_price_MAD + C_health_public` |
| **Markowitz portfolio** | `max_w (w x R - (1-w) x V)` s.t. Sum(w_i) = 1, w_i >= 0. Efficient frontier computation |
| **Supernetwork** | Dong et al. variational inequality: `VI(F*, K*, lambda*)`. Solved by MSA (Method of Successive Averages) |

### 13.7 Module M6 — Phasage & Roadmap

| Feature | Specification |
|---------|--------------|
| **Transition planner** | Sequence fleet conversion across technology waves (pilot/scale/full) with budget constraints |
| **Gantt chart** | Interactive timeline with dependencies, drag-to-reschedule, PNG/SVG/PDF export |
| **Milestone tracking** | Actual vs planned budget and timeline, % completion per phase |
| **Scenario types** | aggressive, moderate, conservative electrification paths |

### 13.8 Module M7 — Scoring Global & MCDA

**Foundation:** ELECTRE (Roy 1968), AHP (Saaty 1980), McFadden (1974) binary logit

| Feature | Specification |
|---------|--------------|
| **Weighted sum** | `S(a) = Sum(w_k x n_k(a_k))` with Sum(w_k) = 1 |
| **Criteria weights** | CAPEX: 0.20, OPEX: 0.20, CO2: 0.25, Risk: 0.15, Comfort: 0.10, Maturity: 0.10 |
| **Normalization** | Inverse: `n_inv(v) = 5 - 4 x (v - v_min) / (v_max - v_min)` for cost criteria. Direct for benefit criteria |
| **Modal choice** | `P(bus) = exp(V_bus) / [exp(V_bus) + exp(V_car)]` where `V = beta_TT x TT + beta_cost x cost + beta_comfort x comfort` |
| **Sensitivity** | Vary each weight +/- 20%, check ranking stability |

### 13.9 Module M8 — Exploitation Temps Reel & ML

**Foundation:** Clarke & Wright (1964), Holland GA (1975), Hochreiter LSTM (1997), Breiman RF (2001)

| Feature | Specification |
|---------|--------------|
| **Clarke & Wright** | `S_ij = d(depot,i) + d(depot,j) - d(i,j)`. Sort descending, greedy merge. O(n^2 log n) |
| **Genetic Algorithm** | OX crossover (0.85), swap mutation (0.05), 500 gen max, stagnation 50 gen, 10% elitism. Population=100 |
| **LSTM demand** | LSTM(64) -> Dropout(0.2) -> LSTM(32) -> Dense(1). Window=336 (7d x 48 x 30min). Features: timestamp sin/cos, day, is_ramadan, weather. MAE loss. Monthly retrain |
| **RF driver risk** | 8 features: speed/accel/brake alerts, geofencing, driving time, speed avg/max, current score. Score=100 - Sum(penalty_k x infractions_k). Weekly retrain |
| **SocketIO GPS** | < 1s latency, Redis pub/sub for scaling, 1500+ concurrent connections. Geofence + route deviation detection |

### 13.10 New Roles (9 total)

| Role | Access | Description |
|------|--------|-------------|
| `admin` | Full | Platform administrator |
| `drh` | M1-M7 read/write | HR director |
| `daf` | M5 read/write, others read | Finance director |
| `salarie` | Mobile app, own data | Employee |
| `operateur` | M8 limited read | Transport operator |
| `responsable_parc` | M2, M3, M4 read/write | Fleet manager (NEW) |
| `responsable_exploitation` | M4, M8 read/write | Operations manager (NEW) |
| `prestataire` | M8 limited read | Contractor (NEW) |
| `conducteur` | Driver portal only | Driver (NEW) |

### 13.11 ML Infrastructure

| Component | Technology |
|-----------|-----------|
| Model registry | joblib (sklearn) + h5 (Keras), versioned, promote/retire |
| Feature store | PostgreSQL table + Redis cache, rolling windows |
| Training pipeline | Celery tasks: daily scoring, weekly RF retrain, monthly LSTM retrain, quarterly IF retrain |
| Serving | Pre-loaded in memory, < 500ms inference |

### 13.12 Additional Services

| Service | Technology | Port |
|---------|-----------|------|
| Contractor dashboard | Dash + Plotly (Python) | 8050 |
| Driver portal | React (integrated in main frontend) | — |
| Chatbot | Rasa 3 (domain.yml, actions.py) | 5005 |
| Observability | Prometheus + Grafana + Loki + OpenTelemetry | 9090/3000/3100 |

### 13.13 SOTREG Roadmap (12 weeks target)

| Sprint | Duration | Modules | Sessions |
|--------|----------|---------|----------|
| S0 — Infrastructure | 1 week | Setup, CI/CD, Keycloak | — |
| Phase 8a — Diagnostic & Technologies | 3 weeks | M1, M2, M3 | 93–101 |
| Phase 8b — Performance & Finance | 3 weeks | M4, M5 | 102–109 |
| Phase 8c — Scoring & Roadmap | 2 weeks | M6, M7, RBAC | 110–115 |
| Phase 8d — ML & Real-Time | 3 weeks | M8, ML Infra | 116–123 |
| Phase 8e — Portals & Integration | 2 weeks | Portals, Observability, Chatbot | 124–127 |
