# Transpop — Replit Project

## Overview
**Transpop** (Plateforme d'Orchestration Mobilité RH) is an enterprise SaaS platform for HR mobility orchestration. It manages employee transport optimization, route planning, clustering, vehicle assignments, and KPI tracking.

## Recent Changes
- **Multi-configuration support + real data seed:** `configuration_plan` table added (migration `h3i4j5k6l7m8`). `configuration_transport` redesigned with 19 real columns matching the XLSX source (conducteur, poste, prestataire, mle_vehicule, type_vehicule, type_moteur, secteur, entite, aller_retour, shift, heure_depart/arrivee, point_depart/arrivee, arrets_circuit, duree_trajet_min, km, rot, t_km). **591 rows seeded** from `attached_assets/config_1775180737219.xlsx` into plan "Configuration Initiale 2024". New API: `GET/POST/PATCH/DELETE /api/v1/configuration-plans`. New frontend page at `/fleet/config` shows plan cards + a full 19-column data grid with filters (prestataire, secteur, shift, A/R, type vehicule) + pagination. `seed_configuration.py` created.
- **Sidebar collapse/expand:** `AppLayout` owns `collapsed` state (persisted in localStorage); `Sidebar` receives `collapsed` + `onToggle` props; collapses to 56px icon-only rail with tooltips; smooth transition via inline `marginLeft`.
- **Map filter panel moved outside map:** `UnifiedMapPage` refactored to side-by-side layout — collapsible filter panel (expanded=288px, collapsed=56px) + map filling remaining width. Legend integrated into expanded panel. No overlays on map anymore.
- **Shifts restructure:** Removed all "Equipes/Horaires" terminology. Company-wide shift management (create/edit/delete) moved to **Paramètres** page. Site create/edit form now has a **Shifts Actifs** selector (read-only table with checkboxes to activate per site). Site detail page shows `SiteActiveShiftsPanel`. `active_shift_ids` (JSONB) column added to `site` table (migration `g2h3i4j5k6l7`). "Horaires de Travail" removed from fleet sidebar navigation.
- **CSV Export/Import (Sites):** `GET /api/v1/sites/export/csv` streams a UTF-8 CSV (headers-only when empty). `POST /api/v1/sites/import/csv` accepts a `.csv` file and upserts by `code` (no duplicates on re-import). Frontend: "Import CSV" + "Export CSV" buttons in SiteListPage header; result/error banners shown after import.

## Architecture
- **Backend:** Python 3.12 / FastAPI / SQLAlchemy 2.0 (async) / PostgreSQL + PostGIS / Redis + Celery / OR-Tools
- **Frontend:** React 19 / TypeScript / Vite / TailwindCSS v4 / Zustand / Google Maps (`@vis.gl/react-google-maps`) / Recharts
- **Database:** Replit managed PostgreSQL (host: helium, db: heliumdb)

## Project Structure
```
backend/        FastAPI application (Python)
frontend/       React web dashboard (TypeScript/Vite)
Docs/           Project documentation (Obsidian vault)
start_backend.sh  Startup script (Redis + uvicorn)
```

## Running the Project

### Workflows
- **Start application** — Frontend (Vite, port 5000, webview)
- **Backend API** — Redis + FastAPI uvicorn (port 8000, console)

### Manual startup
```bash
# Backend (includes Redis)
bash start_backend.sh

# Frontend
cd frontend && npm run dev
```

## Key Configuration

### Backend Environment Variables
Set in `start_backend.sh` (overrides Replit's system DATABASE_URL):
- `DATABASE_URL` — `postgresql+asyncpg://postgres:password@helium:5432/heliumdb`
- `DATABASE_URL_SYNC` — `postgresql+psycopg2://postgres:password@helium:5432/heliumdb`
- `REDIS_URL` — `redis://localhost:6379/0`
- Weather — uses **Open-Meteo** (free, no API key required); live 5-day forecasts fetch automatically via `POST /api/v1/weather/{site_id}/refresh`

### Frontend Environment Variables
- `VITE_GOOGLE_MAPS_API_KEY` — Google Maps API key (already set); powers all map views and optimization maps

### Frontend
- Dev server: port 5000, host 0.0.0.0, all hosts allowed
- API proxy: `/api` → `http://localhost:8000` (via Vite dev server proxy)
- API client base URL: empty string (uses relative URLs)
- Vite dedupe: `['react', 'react-dom']` — prevents multiple React instances from `@vis.gl/react-google-maps`

## Health Check
```
GET /api/v1/health
→ {"status":"healthy","db":true,"redis":true}
```

## Database
- 16 Alembic migrations applied (sessions 1–44 + fleet migration `f1a2b3c4d5e6`)
- Extensions: PostGIS, pg_trgm
- 41 tables across 10 groups
- New fleet tables: `vehicle` (extended), `km_consommation`, `point_arret`, `configuration_transport`

## Fleet Module (XLSX schemas 2–6)
### Backend
- `backend/app/models/vehicle.py` — Vehicle, KmConsommation, PointArret, ConfigurationTransport models
- `backend/app/schemas/vehicle.py` — Pydantic schemas for all 4 entities
- `backend/app/api/v1/vehicles.py` — CRUD for Vehicle (paginated list, get, create, update, delete)
- `backend/app/api/v1/km_consommation.py` — CRUD for Km & Consommation (list, create, update, delete)
- `backend/app/api/v1/point_arret.py` — CRUD for Points d'Arrêt SOTREG
- `backend/app/api/v1/configuration_transport.py` — CRUD for Configuration Transport-Véhicule

### Frontend
- `frontend/src/types/vehicle.ts` — TypeScript types for all 4 entities
- `frontend/src/api/vehicles.ts` — API client for all 4 entity CRUD operations
- Pages: VehicleListPage, VehicleCreatePage, VehicleDetailPage, VehicleEditPage (with shared VehicleForm)
- Fleet pages: KmConsommationPage, PointArretPage, ConfigurationTransportPage (modal CRUD with inline table)
- Routes: `/vehicles`, `/vehicles/new`, `/vehicles/:id`, `/vehicles/:id/edit`, `/fleet/consumption`, `/fleet/stops`, `/fleet/config`
- Sidebar: fleet sub-nav auto-expands under Parc Véhicule when on `/vehicles*` or `/fleet*` paths

## Design System: "Azure Velocity"
- Primary: `#0058be` (Azure Blue)
- Font: Inter
- Icons: Material Symbols Outlined

## Refinement Scope
This is a refinement-only project. Sessions 1–44 are implemented. See `REPLIT_INSTRUCTIONS.md` for constraints and `REPLIT_CHANGES.md` for change log.
