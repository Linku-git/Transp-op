# Transpop — Replit Project

## Overview
**Transpop** (Plateforme d'Orchestration Mobilité RH) is an enterprise SaaS platform for HR mobility orchestration. It manages employee transport optimization, route planning, clustering, vehicle assignments, and KPI tracking for large organizations in Morocco.

- **Sessions completed:** 44 core + Replit deployment phase (R01)
- **Platform status:** Live on Replit Reserved VM (deployed ✅)
- **Next phase:** Phase 3 — Flutter Mobile MVP (sessions 45–56)

---

## Architecture

- **Backend:** Python 3.12 / FastAPI / SQLAlchemy 2.0 (async) / PostgreSQL + PostGIS / Redis + Celery / OR-Tools
- **Frontend:** React 19 / TypeScript / Vite / TailwindCSS v4 / Zustand / `@vis.gl/react-google-maps` / Recharts
- **Database:** Replit managed PostgreSQL (host: `helium`, db: `heliumdb`)
- **Deployment:** Replit Reserved VM (`deploymentTarget = "vm"`)

---

## Running the Project (Development)

### Workflows
- **Start application** — Frontend dev server (Vite, port 5000, webview)
- **Backend API** — Redis + FastAPI uvicorn (port 8000, console)

### Manual startup
```bash
# Backend (Redis + uvicorn on port 8000)
bash start_backend.sh

# Frontend (Vite on port 5000)
cd frontend && npm run dev
```

### Health check
```
GET /api/v1/health
→ {"status":"healthy","db":true,"redis":true}
```

---

## Key Configuration

### Database
- **URL (asyncpg):** `postgresql+asyncpg://postgres:password@helium:5432/heliumdb`
- **URL (sync):** `postgresql+psycopg2://postgres:password@helium:5432/heliumdb`
- **Tenant ID:** `0cea9745-6aa2-4105-9bdc-341d95999048`
- **Admin:** `admin@transpop.dev` / `admin123`
- **Migrations:** 19 Alembic migrations applied

### Backend Environment Variables
Set in `start_backend.sh` (dev) and `start_production.sh` (prod):
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@helium:5432/heliumdb` |
| `DATABASE_URL_SYNC` | `postgresql+psycopg2://postgres:password@helium:5432/heliumdb` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `ENVIRONMENT` | `development` / `production` |
| `SECRET_KEY` | Set via Replit secret |
| `PORT` | Injected by Cloud Run/Replit VM (8080 in production) |

### Frontend Environment Variables
| Variable | Value |
|----------|-------|
| `VITE_GOOGLE_MAPS_API_KEY` | Set as Replit secret — powers all map views |

### Vite Config (`frontend/vite.config.ts`)
- Dev server: port `5000`, host `0.0.0.0`, `allowedHosts: true`
- API proxy: `/api` → `http://localhost:8000`
- Dedupe: `['react', 'react-dom']` — prevents double React instance from `@vis.gl/react-google-maps`
- Path alias: `@` → `/src`

### API Client (`frontend/src/api/client.ts`)
- `baseURL: ''` (empty string — uses relative URLs proxied through Vite)
- **All API files MUST use full paths:** `/api/v1/...`
- ❌ Never: `get('/kpis/dashboard')`
- ✅ Always: `get('/api/v1/kpis/dashboard')`

---

## Production Deployment

### Config (`.replit`)
```toml
[deployment]
deploymentTarget = "vm"
run = ["bash", "start_production.sh"]
build = ["bash", "build.sh"]
```

### Build (`build.sh`)
```bash
cd frontend && npm install && npm run build
pip install -r backend/requirements.txt
```

### Run (`start_production.sh`)
- Builds `DATABASE_URL` from Replit env vars (`$PGHOST`, `$PGUSER`, `$PGPASSWORD`, `$PGDATABASE`)
- Starts Redis (optional — failure does not abort)
- Runs Alembic migrations
- Starts uvicorn: `--port "${PORT:-8080}"` (Cloud Run sets PORT=8080)

### Why Reserved VM?
Replit Autoscale = single exposed port only. This app needs Redis (6379) and multiple services → must use Reserved VM. Cloud Run still applies → `${PORT:-8080}` is required.

---

## Database: 41 Tables, 19 Migrations

| Group | Key Tables |
|-------|-----------|
| Auth | `user`, `role`, `tenant`, `user_role` |
| Sites | `site` (PostGIS), `shift_type` |
| Employees | `employee`, `employee_leave` |
| Fleet | `vehicle`, `km_consommation`, `point_arret`, `configuration_transport`, `configuration_plan` |
| Optimization | `optimization_run`, `cluster`, `route`, `vehicle_assignment` |
| Scenarios | `transport_scenario`, `optimization_settings`, `constraint_param` |
| Modal | `employee_modal` (legacy), mobility scoring via Employee fields |
| Financial | `financial_scenario`, `tco_entry`, `roi_calculation`, `investment_comparison` |
| Reporting | `generated_report`, `kpi_snapshot` |
| Weather | `weather_forecast` |

---

## Live Demo Data

| Entity | Count | Details |
|--------|-------|---------|
| Employees | 1,200 | All with lat/lng; 900=company_bus, 65=personal_car |
| Vehicles | 106 | AUTOCAR(54 seats), MINIBUS(25), MINICAR(12) |
| Configuration Transport | 591 | Seeded from XLSX, plan "Configuration Initiale 2024" |
| Total fleet distance | 32,696 km | |
| Sites | 4 | Casablanca: Ain Sebaa, Bouskoura, Moulay Rachid, Ain Chock |
| KPI snapshots | 90 days | Trend data for all sites |

---

## Project Structure

```
backend/
  app/
    main.py              # FastAPI app + SPA static serving + CORS
    config.py            # Settings from env vars
    database.py          # SQLAlchemy async engine
    models/              # SQLAlchemy models (41 tables)
    schemas/             # Pydantic v2 request/response
    api/v1/              # Route handlers (30+ files)
    services/            # Business logic (clustering, routing, tco, roi, mobility_scoring, etc.)
    tasks/               # Celery async tasks
    middleware/           # Auth, RBAC
  tests/                 # pytest tests
  alembic/               # 19 DB migrations
  requirements.txt
  seed_*.py              # Seed scripts (idempotent)

frontend/
  src/
    pages/               # Route-level pages
      dashboard/         # KPI dashboard
      sites/             # Site CRUD + CSV import/export
      employees/         # Employee CRUD + map view
      fleet/             # Vehicles, KmConsommation, PointArret, ConfigurationTransport
      optimization/      # 3-section optimization hub
      modal/             # Modal analysis (real Employee data)
      financial/         # TCO + ROI dashboards
      reports/           # Report generation
      settings/          # OptimizationSettings + ConstraintParams + Shifts
      scenarios/         # Scenario comparison
      map/               # Unified map view
    components/
      ui/                # Button, Card, Modal, Input, Badge, DataTable, etc.
      layout/            # Sidebar (collapsible), Header, AppLayout
      maps/              # MapView, markers, routes (all @vis.gl/react-google-maps)
      charts/            # PieChart, BarChart, GaugeChart, Histogram
    api/                 # Axios API clients (ALL use /api/v1/... full paths)
    lib/
      apiError.ts        # extractApiError() — Pydantic v2 error utility
    stores/              # Zustand state stores
    types/               # TypeScript interfaces
  vite.config.ts         # Port 5000, proxy /api, allowedHosts: true

start_backend.sh         # Dev: Redis + uvicorn on port 8000
start_production.sh      # Prod: migrations + uvicorn on ${PORT:-8080}
build.sh                 # Prod build: frontend + pip install
.replit                  # Replit config: vm deployment, build/run commands
```

---

## Design System: "Azure Velocity"
- **Primary:** `#0058be` (Azure Blue)
- **Font:** Inter
- **Icons:** Material Symbols Outlined
- **Cards:** `bg-white rounded-xl shadow-sm border border-outline-variant/10`
- Full spec: `Docs/DESIGN_SYSTEM.md`

---

## Critical Patterns for New Code

### 1. API Error Handling (Pydantic v2)
```typescript
import { extractApiError } from '@/lib/apiError';

try {
  await createSomething(data);
} catch (err) {
  setError(extractApiError(err, 'Une erreur est survenue'));
}
```

### 2. Google Maps Components
```tsx
import { APIProvider, Map, AdvancedMarker } from '@vis.gl/react-google-maps';

<APIProvider apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY} region="MA">
  <Map defaultCenter={{ lat: 33.5731, lng: -7.5898 }} defaultZoom={11}>
    <AdvancedMarker position={{ lat, lng }} />
  </Map>
</APIProvider>
```

### 3. Full API Paths (mandatory)
```typescript
// ✅ Correct
const res = await apiClient.get('/api/v1/employees?page_size=2000');

// ❌ Wrong — will 404
const res = await apiClient.get('/employees');
```

### 4. Production Port
```bash
# In start_production.sh
APP_PORT="${PORT:-8080}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}"
```

---

## Vehicle Constants
```
AUTOCAR:  capacity=54,  cost_per_km=4.50 MAD
MINIBUS:  capacity=25,  cost_per_km=3.20 MAD
MINICAR:  capacity=12,  cost_per_km=2.50 MAD
```

---

## Replit Changes History
See `REPLIT_CHANGES.md` for a full timestamped log of every change made during the Replit deployment sessions.

See `Docs/sessions/session-replit.md` for the full session notes including what was changed, why, and what's next.

---

## What's Next: Phase 3 — Flutter Mobile App

The next major work block is sessions 45–56: building the employee-facing Flutter mobile app.

Key files to create:
- `mobile/` — new Flutter project directory
- `mobile/lib/main.dart` — app entry point
- `mobile/lib/features/auth/` — login + biometric
- `mobile/lib/features/home/` — home screen
- `mobile/lib/features/trips/` — trip booking + management

The mobile app will connect to the existing FastAPI backend via the `/api/v1/` endpoints. Session 54 adds mobile-specific backend endpoints.

**After mobile is done:** Re-inject the project into Replit for final polishing, QA, and production deployment.
