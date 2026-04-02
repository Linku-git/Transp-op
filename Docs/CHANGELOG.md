# Transpop — Changelog

> All notable changes to this project are documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
> See also: [[PROGRESS]] | [[ROADMAP]]

---

## [Session-35] — 2026-04-02
### Added
- TypeScript interfaces for TCO calculation types (`frontend/src/types/financial.ts`)
- Financial API client: `calculateTCO`, `getVehicleReferences` (`frontend/src/api/financial.ts`)
- 5 financial chart/table components: TCOComparisonCards (vehicle cards with lowest highlight), TCOEvolutionChart (Recharts LineChart), MotorizationTable (comparison with green cheapest row), VehicleTCOBreakdown (stacked BarChart), FleetAggregation (summary card)
- TCOCalculatorPage (`/financial/tco`): fleet composition form, duration slider, calculate button, results display with all 5 components
- FinancialDashboardPage (`/financial`): tab navigation for TCO/ROI/Comparateur (ROI and Comparateur as placeholders)
- Routes for `/financial` and `/financial/tco` with lazy loading
- i18n translations for financial section (fr + en)
- 7 tests in `frontend/src/pages/financial/__tests__/FinancialTCO.test.tsx`

### Changed
- `frontend/src/routes.tsx` — Added financial routes

---

## [Session-34] — 2026-04-02
### Added
- Investment model comparator engine: CAPEX (own fleet), Mise a Disposition (rental), OPEX (full outsource) — each computing total cost, annual cost, cost per employee, cost per trip (`backend/app/services/investment_comparator.py`)
- Recommendation logic: heuristic based on fleet size/duration, overridden by >20% cost difference
- Sensitivity analysis: fuel price delta (±50%), headcount delta (±50%), fill rate (50-100%) — recomputes all 3 models and returns deltas vs baseline
- Pydantic schemas: `InvestmentCompareRequest/Response`, `SensitivityRequest/Response`, `InvestmentModelResult`, `SensitivityDelta`
- POST `/financial/compare` — side-by-side comparison with recommendation
- POST `/financial/compare/sensitivity` — sensitivity analysis endpoint
- 11 tests in `backend/tests/test_investment_comparator.py` (9 unit + 2 integration)

### Changed
- `backend/app/schemas/financial.py` — Added 8 comparison/sensitivity schemas
- `backend/app/api/v1/financial.py` — Added 2 compare endpoints, imported `Decimal`

---

## [Session-33] — 2026-04-02
### Added
- ROI calculator engine with 4 levers: absenteeism (rate × daily_cost × headcount × 220 working days), retention (turnover reduction × replacement cost), fleet optimization (current vs optimized fleet cost), journey productivity (travel hours × engagement × training cost) (`backend/app/services/roi_calculator.py`)
- Payback period in months: `(total_investment / annual_roi_total) × 12`
- ROI percentage: `(roi_total / total_investment) × 100`
- Edge case handling: zero investment returns 0% ROI, negative savings clamped to 0
- Pydantic schemas: `ROICalculateRequest` (13 input params), `ROICalculateResponse` (10 output fields + stored_id)
- POST `/financial/roi/calculate` endpoint with optional `scenario_id` to persist results in `ROICalculation` table
- 9 tests in `backend/tests/test_roi_calculator.py` (7 unit + 2 integration, including DB persistence)

### Changed
- `backend/app/schemas/financial.py` — Added 2 ROI calculation schemas
- `backend/app/api/v1/financial.py` — Added ROI calculate endpoint with DB persistence

---

## [Session-32] — 2026-04-02
### Added
- TCO calculator engine with core formula: `TCO = Purchase + (Maintenance × Duration) + (Energy/km × Annual_km × Duration) − Residual` (`backend/app/services/tco_calculator.py`)
- Per-vehicle and fleet-level TCO aggregation with quantity support
- Motorization comparison: computes TCO for all available motorizations per vehicle type, sorted cheapest-first
- Year-by-year evolution (1-10 years) showing monotonically increasing cumulative fleet TCO
- Default cost parameters per motorization with vehicle type multipliers (vehicule_leger through grand_bus)
- Custom cost override support — any default parameter can be overridden per vehicle in the fleet
- Pydantic schemas: `TCOCalculateRequest`, `TCOCalculateResponse`, `TCOFleetResult`, `TCOYearlyPoint`, `TCOMotorizationComparison`
- POST `/financial/tco/calculate` endpoint returning fleet TCO, evolution, and motorization comparisons
- 8 tests in `backend/tests/test_tco_calculator.py` (7 unit + 1 integration)

### Changed
- `backend/app/schemas/financial.py` — Added 8 TCO calculation schemas
- `backend/app/api/v1/financial.py` — Added TCO calculate endpoint

---

## [Session-31] — 2026-04-02
### Added
- FinancialScenario, TCOEntry, ROICalculation, VehicleReference SQLAlchemy models (`backend/app/models/financial.py`)
- Alembic migration for 4 financial tables (`backend/alembic/versions/c3d4e5f6a7b8_add_financial_tables.py`)
- Pydantic v2 schemas with validation: investment model types, vehicle types, positive costs, rate ranges (`backend/app/schemas/financial.py`)
- 8 API endpoints under `/financial/`: scenario CRUD (5), TCO entries (2), vehicle reference catalog (1) (`backend/app/api/v1/financial.py`)
- Vehicle reference seed script with 5 PRD vehicle types (minibus, midibus, bus_standard, grand_bus, vehicule_leger), idempotent, runs at app startup (`backend/app/db/seed_vehicles.py`)
- 7 tests in `backend/tests/test_financial_models.py` covering scenario CRUD, TCO entries, schema validation, vehicle catalog

### Changed
- `backend/app/api/v1/__init__.py` — Registered financial router with tags=["financial"]
- `backend/app/models/__init__.py` — Added 4 financial model exports
- `backend/app/main.py` — Added lifespan hook to seed vehicle references on startup

---

## [Session-30] — 2026-04-02
### Added
- ExportEngine service with 5 format generators: PDF, Excel, CSV stops, CSV employees, GeoJSON (`backend/app/services/export_engine.py`)
- PDF driver sheets using reportlab: cover page with metrics summary, per-route driver sheets with ordered stops tables, PMR indicators highlighted in blue with bold red text
- Multi-sheet Excel workbook using openpyxl: "Resume" summary sheet, per-site sheet with clusters/routes/employees sections, PMR rows highlighted in yellow
- CSV stop order export: route_number, stop_order, employee details, PMR flags, ETA, cumulative distance
- CSV employee assignments export: employee details with cluster/route/vehicle assignments
- GeoJSON FeatureCollection: route LineStrings (from polyline or stops), stop Points with PMR properties, cluster centroid Points
- 5 API endpoints under `/export/` prefix: GET pdf, excel, csv/stops, csv/employees, geojson — all require `optimization_id` query param (`backend/app/api/v1/exports.py`)
- Celery task wrapper for large async exports with Redis progress tracking, 120s timeout (`backend/app/tasks/export_tasks.py`)
- Google encoded polyline decoder helper for GeoJSON route geometry
- `reportlab>=4.4.3` dependency added to requirements.txt
- 22 tests in `backend/tests/test_exports.py` covering all formats + PMR indicators + polyline decoder

### Changed
- `backend/app/api/v1/__init__.py` — Registered exports router with tags=["exports"]

---

## [Session-29] — 2026-04-02
### Added
- OptimizationSettings SQLAlchemy model with tenant-scoped one-row-per-tenant pattern (UniqueConstraint on tenant_id), fields: meeting_radius_meters, max_walking_distance_meters, max_route_duration_seconds, fuel_cost_per_liter, fuel_consumption_l_per_100km, co2_kg_per_liter, rti_threshold_minutes, night_mode_start, night_mode_end, min_night_group_size (`backend/app/models/settings.py`)
- ConstraintParam SQLAlchemy model with UniqueConstraint on (tenant_id, key), fields: key, value, category, description, is_active (`backend/app/models/settings.py`)
- Alembic migration for optimization_settings and constraint_param tables (`backend/alembic/versions/b2c3d4e5f6a7_add_settings_tables.py`)
- Pydantic v2 schemas for settings and constraints CRUD (`backend/app/schemas/settings.py`)
- 2 settings API endpoints: GET `/settings` (get-or-create default), PUT `/settings` (partial update) (`backend/app/api/v1/settings.py`)
- 5 constraints API endpoints: GET `/constraints` (category filter), POST `/constraints`, PUT `/constraints/{id}`, DELETE `/constraints/{id}`, POST `/constraints/bulk` (`backend/app/api/v1/constraints.py`)
- Settings TypeScript interfaces (`frontend/src/types/settings.ts`)
- Settings API client with 7 functions (`frontend/src/api/settings.ts`)
- SettingsPage (`/settings`): form with range sliders for distance/duration, number inputs for costs, time inputs for night mode (`frontend/src/pages/settings/SettingsPage.tsx`)
- ConstraintsPage (`/settings/constraints`): data table with category filter, inline add/edit/delete, bulk import (`frontend/src/pages/settings/ConstraintsPage.tsx`)
- 6 backend tests in `test_settings.py` (150 total passing)
- 16 frontend tests across 2 test files (6 SettingsPage + 10 ConstraintsPage)

### Changed
- `backend/app/api/v1/__init__.py` -- Registered settings and constraints routers
- `backend/app/models/__init__.py` -- Added OptimizationSettings and ConstraintParam imports
- `frontend/src/routes.tsx` -- Added lazy imports and routes for `/settings` and `/settings/constraints`
- `frontend/src/i18n/fr.json` and `en.json` -- Added settings/constraints translations

---

## [Session-28] — 2026-04-02
### Added
- Scenario TypeScript types: Scenario, ScenarioMetrics, MetricDelta, ScenarioComparison, WeatherForecast, ScenarioSuggestion, WeatherSuggestions (`frontend/src/types/scenario.ts`)
- Scenario API client with 8 functions: simulateScenario, listScenarios, getScenario, deleteScenario, compareScenarios, getWeatherForecasts, refreshWeather, getWeatherSuggestions (`frontend/src/api/scenarios.ts`)
- ScenarioListPage (`/scenarios`): data table with condition chips, site filter, checkbox selection for multi-compare, delete actions (`frontend/src/pages/scenarios/ScenarioListPage.tsx`)
- ScenarioComparePage (`/scenarios/compare`): side-by-side metrics comparison with color-coded deltas (green=improvement, red=worse), recommendations panel, URL parameter support (`frontend/src/pages/scenarios/ScenarioComparePage.tsx`)
- WeatherWidget component: 3-day forecast display with condition icons, temp ranges, precipitation, scenario suggestion chips with one-click Apply button (`frontend/src/components/optimization/WeatherWidget.tsx`)
- 40 frontend tests across 3 test files (15 + 15 + 10)

### Changed
- `frontend/src/routes.tsx` — Added lazy imports and routes for `/scenarios` and `/scenarios/compare`
- `frontend/src/components/layout/Sidebar.tsx` — Added "Scenarios" navigation item
- `frontend/src/pages/optimization/OptimizationPage.tsx` — Integrated WeatherWidget below controls, added `transit_failure` to condition options, added `handleWeatherScenario` callback
- `frontend/src/components/optimization/index.ts` — Added WeatherWidget barrel export
- `frontend/src/pages/optimization/__tests__/OptimizationPage.test.tsx` — Fixed test compatibility with WeatherWidget addition

---

## [Session-27] — 2026-04-02
### Added
- Scenario SQLAlchemy model with tenant_id, site_id, baseline_optimization_id FK, condition_type, demand_multiplier, custom_params (JSONB), estimated_metrics (JSONB), name (`backend/app/models/scenario.py`)
- Alembic migration for scenario table with idx_scenario_tenant and idx_scenario_site indexes
- Scenario engine service with demand multipliers (normal=1.0, rain=1.15, strike=1.5, peak=1.3, night=0.8, transit_failure=1.4), metric estimation, and comparison delta calculation (`backend/app/services/scenarios.py`)
- Pydantic schemas: ScenarioRequest, ScenarioResponse, ScenarioComparisonRequest, MetricDelta, ScenarioComparisonResponse with French alias support (pluie, greve_transport, pic_activite, nuit, defaillance_tc) (`backend/app/schemas/scenario.py`)
- 5 API endpoints: POST `/scenarios/simulate`, GET `/scenarios`, GET `/scenarios/{id}`, DELETE `/scenarios/{id}`, POST `/scenarios/compare` (`backend/app/api/v1/scenarios.py`)
- 6 backend tests in `test_scenarios.py` (144 total passing)

### Changed
- `backend/app/schemas/optimization.py` — Added "transit_failure" to CONDITION_TYPES
- `backend/app/models/__init__.py` — Added Scenario import
- `backend/app/api/v1/__init__.py` — Registered scenarios router

---

## [Session-26] — 2026-04-02
### Added
- WeatherForecast model with unique constraint on (site_id, date, source)
- Weather service: OpenWeatherMap 5-day/3-hour fetch, daily aggregation, upsert, scenario suggestions
- 4 API endpoints: GET `/weather/{site_id}`, POST `/weather/{site_id}/refresh`, POST `/weather/refresh-all`, GET `/weather/{site_id}/suggestions`
- Pydantic schemas: WeatherForecastResponse, WeatherRefreshResponse, WeatherRefreshAllResponse, ScenarioSuggestion, WeatherSuggestionsResponse
- Alembic migration for weather_forecast table
- Config: `weather_api_key`, `weather_api_url` settings
- 5 backend tests with mocked external API (138 total passing)

---

## [Session-25] — 2026-04-02
### Added
- MetricsPanel: 6 KPI cards with inline SVG icons (vehicles, employees, occupancy gauge, distance, fuel cost, CO2)
- RouteList: expandable accordion showing per-vehicle stops with ETA and cumulative distance
- ClusterTable: borderless table with PMR chips and hover highlights
- SiteBreakdown: summary card with condition type chip and computed totals
- GaugeChart: SVG semicircle gauge with clamping, ARIA attributes, configurable size/color
- OptimizationResultPage (`/optimization/:id`): map + tabbed analytics panel + export buttons
- OptimizationHistoryPage (`/optimization/history`): table with status chips, pagination, view links
- 2 new lazy-loaded routes added to routes.tsx
- 35 new frontend tests (4 files)

---

## [Session-24] — 2026-04-01
### Added
- Optimization page (`/optimization`) with split layout: controls panel + Leaflet map
- TypeScript types for optimization entities, metrics, routes, meeting zones, layer visibility
- API client (5 functions) for optimization endpoints
- Zustand store with launch/poll/fetch, layer toggles, route selection
- ClusterRegion map component: circle overlay scaled by employee count
- RoutePolyline: Google encoded polyline decoder, 8-color palette, route popup with metrics
- MeetingZoneMarker: circle marker with PMR accessibility indicator
- AccessLeg: dashed walking path line (employee -> meeting zone)
- MapLegend: glassmorphism floating panel with 6 layer toggles + per-route selector
- Metrics bar: vehicles, employees, occupancy, distance, CO2
- Progress bar with step description for async optimization runs
- 15 new frontend tests (4 files)

---

## [Session-23] — 2026-04-01
### Added
- Full optimization pipeline orchestrator (`backend/app/services/optimization_pipeline.py`)
  - 7-step pipeline: filter → cluster → meeting zones → assign → route → metrics → save
  - Leave-aware employee filtering for target date
  - Metrics calculation: fuel (L), cost (MAD), CO2 (kg), time saved (hrs), occupancy rate
- Celery task wrapper with Redis progress tracking (`backend/app/tasks/optimization_tasks.py`)
  - 6-step progress updates (0%→100%) stored in Redis with 1h TTL
  - Graceful sync fallback when Celery broker unavailable
- 5 optimization pipeline schemas: RunRequest, MetricsResponse, StatusResponse, FullResponse, HistoryItem
- 5 API endpoints: POST `/optimize`, GET `/optimize/{id}`, GET `/optimize/{id}/status`, GET `/optimize/latest/result`, GET `/optimize/history/list`
- 8 unit tests in `test_optimization_pipeline.py`

---

## [Session-22] — 2026-04-01
### Added
- Route SQLAlchemy model with polyline, ordered stops JSONB, distance/time metrics (`backend/app/models/optimization.py`)
- Alembic migration for route table with spatial index
- OSRM table service (`osrm_table`) for NxN distance/time matrices with haversine fallback
- OSRM multi-waypoint route service (`osrm_route_multi`) with polyline and leg parsing
- OR-Tools CVRP solver with capacity dimension, time dimension (90min max), node dropping
- PATH_CHEAPEST_ARC first solution + GUIDED_LOCAL_SEARCH metaheuristic (10s time limit)
- Sequential fallback assignment when OR-Tools unavailable
- Two-leg route model: walking access leg + driving main leg
- ETA calculation per stop with cumulative distance tracking
- Route Pydantic schemas (`RouteResponse`, `RouteStopResponse`, `TwoLegResponse`)
- 2 API endpoints: GET `/routes` (with site/optimization/vehicle filters), GET `/routes/{id}`
- 10 unit tests in `test_routing.py`

---

## [Session-21] — 2026-04-01
### Added
- Vehicle assignment service with best-fit decreasing bin-packing algorithm (`backend/app/services/vehicle_assignment.py`)
- PMR-aware matching: clusters with PMR employees get PMR-accessible vehicles
- ZFE compliance enforcement for low-emission zone sites
- Cluster split (geographic bisection by latitude) for oversized clusters
- Cluster merge (greedy nearest-neighbor with haversine distance) for small clusters
- Volunteer driver integration as supplemental capacity
- Vehicle recommendations for unassigned clusters
- Pydantic v2 schemas for assignment request/response (`backend/app/schemas/vehicle_assignment.py`)
- 3 API endpoints: POST `/vehicle-assignments/assign`, `/vehicle-assignments/split-cluster/{id}`, `/vehicle-assignments/merge-clusters`
- 9 unit tests in `test_vehicle_assignment.py`

---

## [Mini-Changes] — 2026-04-01
### Added
- Frontend dev container in `docker-compose.yml` (node:20-alpine, Vite dev server with hot reload)
- `frontend_node_modules` named volume to isolate container deps from host
- Live Browser Check section in ui-review skill (Chrome console/visual verification)
- Browser test scope in run-tests skill
- Section 11 (Browser Verification) in `agents.md`

### Fixed
- Backend Docker healthcheck URL: `/health` → `/api/v1/health`
- Health-check skill: clarified which services exist vs future (celery/celery-beat)

### Changed
- deploy-local skill: added frontend container verification step
- health-check skill: added `docker compose ps frontend` and log checks

---

## [Session-20] — 2026-04-01
### Added
- Vehicle SQLAlchemy model with 17 fields (`backend/app/models/vehicle.py`)
- Alembic migration for vehicle table
- Pydantic schemas with enum validation: condition (Bon/Moyen/Mauvais), motorization (diesel/hybrid/electric/hydrogen/gnv), owner_type
- 5 API endpoints: GET/POST/PUT/DELETE `/vehicles` + GET `/vehicles/fleet-summary`
- Multi-filter support: site_id, is_pmr_accessible, condition, motorization, zfe_compliant
- Fleet summary aggregations: by type, condition, motorization, site with capacity/PMR/ZFE counts
- 11 tests in `test_vehicles.py`

---

## [Session-19] — 2026-04-01
### Added
- OSRM API client (`backend/app/services/osrm_client.py`) — nearest road snap, walking/driving routes, haversine fallback
- Meeting zone optimizer (`backend/app/services/meeting_zones.py`) — centroid snap-to-road, PMR accessibility check, walking distance constraint validation, per-employee access leg computation
- `POST /clusters/generate-with-zones` — combined clustering + meeting zone optimization endpoint
- Pydantic schemas: AccessLegResponse, MeetingZoneResponse, MeetingZonesResult
- 7 tests (5 unit + 2 OSRM mock integration)

---

## [Session-18] — 2026-04-01
### Added
- Optimization and Cluster SQLAlchemy models with PostGIS centroid geometry (`backend/app/models/optimization.py`)
- Alembic migration for optimization and cluster tables
- Clustering service with 3 algorithms: DBSCAN (haversine), KMeans, hierarchical/Ward (`backend/app/services/clustering.py`)
- Configurable params: eps_meters (50-5000m), min_samples, n_clusters, max_cluster_size
- PMR-aware clustering with pmr_count per cluster
- Auto-split oversized clusters via KMeans sub-clustering
- Pydantic schemas: ClusteringRequest, ClusterResponse, OptimizationResponse, ClusteringResponse (`backend/app/schemas/optimization.py`)
- 3 API endpoints: POST `/clusters/generate`, GET `/clusters`, GET `/clusters/{id}` (`backend/app/api/v1/clusters.py`)
- 11 tests (9 unit + 2 integration) in `test_clustering.py`

---

## [Session-17] — 2026-04-01
### Added
- Mobility scoring engine (`backend/app/services/mobility_scoring.py`) — per-employee score (0-100), group aggregation (site/dept/shift), time-slot bucketing, shadow zone identification
- Modal analytics service (`backend/app/services/modal_analytics.py`) — weather impact analysis, disruption vulnerability, carpool supply vs demand
- `GET /modal/shadow-zones` — identify employees without viable transport solutions
- `GET /modal/carpool-potential` — carpool supply vs demand per site
- 8 new Pydantic response schemas (GroupScore, TimeSlotScore, ShadowZoneEmployee, MobilityScoresResponse, WeatherImpact, DisruptionVulnerability, CarpoolPotential, ShiftAnalysisResponse)
- 6 new tests in `test_mobility_scoring.py`

### Changed
- `GET /modal/mobility-scores` — now returns group_scores and timeslot_scores alongside individual scores
- `GET /modal/shift-analysis` — enhanced with disruption vulnerability and weather impact data, added site_id filter
- Scoring algorithm rewritten: base=0 with weighted factors (distance, mode, interest, flexibility) replacing old base=50 approach

---

## [Session-16] — 2026-04-01
### Added
- ModalAnalysisPage — 5 dashboard cards: distribution pie chart, shift potential bar, distance histogram, mobility scores, shift analysis
- Reusable Recharts components: PieChart, BarChart, Histogram with design system tokens
- Modal API client and TypeScript types (`frontend/src/api/modal.ts`, `types/modal.ts`)
- Site filter dropdown for per-site analysis
- i18n translations (16 keys in `modal` namespace)
- 3 component tests with Recharts mocking

### Changed
- Sidebar — added "Analyse Modale" navigation link
- routes.tsx — added /modal-analysis route

---

## [Session-15] — 2026-04-01
### Added
- EmployeeModal SQLAlchemy model with 17 data columns, unique(employee_id) constraint (`backend/app/models/modal.py`)
- Alembic migration for employee_modal table
- Pydantic schemas with transport mode enum validation, stats/score models (`backend/app/schemas/modal.py`)
- 6 API endpoints: CRUD upsert for employee modal, distribution stats, shift analysis, mobility scores (`backend/app/api/v1/modal.py`)
- 9 test cases covering upsert, stats, scores, and mode validation

---

## [Session-14] — 2026-04-01
### Added
- ExcelImportPage — multi-step flow (upload -> preview -> import) with per-sheet tabs
- FileUpload — drag-and-drop component with .xlsx validation and loading state
- Tabs — horizontal tab navigation with badge counts
- ProgressBar — animated progress indicator with 3 variants
- SheetPreview — auto-column data table with truncation
- ValidationErrors — grouped error display with row/column references
- Import API client (preview, import, single-sheet) with FormData upload
- 5 component tests

### Changed
- Sidebar — added Import navigation link
- routes.tsx — added /import route

---

## [Session-13] — 2026-04-01
### Added
- ExcelImportService — multi-sheet parser for 6-sheet template (SITES, EFFECTIF, USAGES, CONTRAINTES, PARC, ABSENCES) with upsert, validation, preview mode (`backend/app/services/excel_parser.py`)
- Response schemas for import results (`backend/app/schemas/excel_import.py`)
- 3 API endpoints: full import, preview, single-sheet import (`backend/app/api/v1/excel_import.py`)
- 13 test cases with programmatic Excel fixture generation

---

## [Session-12] — 2026-04-01
### Added
- EmployeeLeave SQLAlchemy model with employee FK (CASCADE), date indexes (`backend/app/models/leave.py`)
- Alembic migration for employee_leave table
- Pydantic schemas with leave_type enum and date range validation (`backend/app/schemas/leave.py`)
- 5 CRUD endpoints with date range filtering, site_id filter via join, overlap detection (`backend/app/api/v1/leaves.py`)
- 8 test cases covering CRUD, validation, date filtering, and overlap conflict detection

---

## [Session-11] — 2026-04-01
### Added
- EmployeeMapPage — Full-screen Leaflet map with site-colored employee markers, glassmorphism filter panel, legend
- MapView, EmployeeMarker, SiteMarker — Reusable map components
- Bulk actions on EmployeeListPage: checkbox selection, CSV export, bulk soft-delete
- 2 component tests (MapView, EmployeeMapPage)

### Changed
- EmployeeListPage — Added selection state, bulk action bar, map view button

---

## [Session-10] — 2026-04-01
### Added
- Employee TypeScript types, API client (8 functions), Zustand store (`frontend/src/types/employee.ts`, `api/employees.ts`, `stores/employeeStore.ts`)
- EmployeeListPage — DataTable with 6 filters (site, shift, PMR, department, active, search), pagination, PMR/opt-in badges
- Shared EmployeeForm — 4 sections (identity, assignment, location/MapPicker, mobility with conditional carpool)
- EmployeeCreatePage, EmployeeEditPage (pre-filled), EmployeeDetailPage (dual-marker map + transport profile)
- i18n translations (70+ keys in `employees` namespace for FR/EN)
- 3 component tests

### Changed
- `frontend/src/routes.tsx` — Added /employees, /employees/new, /employees/:id, /employees/:id/edit

---

## [Session-09] — 2026-04-01
### Added
- Employee SQLAlchemy model with 30+ fields, PostGIS POINT geometry, GIST spatial index, unique (tenant_id, matricule) (`backend/app/models/employee.py`)
- Alembic migration for employee table with all indexes
- Pydantic schemas: EmployeeCreate/Update/Response, EmployeeSummary, CSVUploadResult (`backend/app/schemas/employee.py`)
- 8 API endpoints: list (7 filters + search + pagination), get, create (auto-geocode), update, soft-delete, CSV upload, batch geocode, summary (`backend/app/api/v1/employees.py`)
- Geocoding service via Nominatim with rate limiting (`backend/app/services/geocoding.py`)
- 13 test cases covering CRUD, filters, CSV upload, validation errors, PostGIS

### Changed
- `backend/requirements.txt` — added python-multipart for file uploads

---

## [Session-08] — 2026-04-01
### Added
- Badge component with 5 variants: success, warning, danger, info, neutral (`frontend/src/components/ui/Badge.tsx`)
- SiteSummaryCards — 3-column stat grid for employee/vehicle/PMR counts (`frontend/src/components/sites/SiteSummaryCards.tsx`)
- ShiftConfigPanel — Visual 24h shift timeline with proportional bars (`frontend/src/components/sites/ShiftConfigPanel.tsx`)
- 3 new component tests (Badge variants, summary counts, shift rendering)

### Changed
- SiteDetailPage — Full enhancement with summary API call, badges, shift panel, quick action links, notes section

---

## [Session-07] — 2026-04-01
### Added
- Site API client (`frontend/src/api/sites.ts`) — 7 functions for all CRUD operations
- Site TypeScript types (`frontend/src/types/site.ts`) — Site, SiteCreate, SiteUpdate, SiteSummary, SiteListParams
- Zustand site store (`frontend/src/stores/siteStore.ts`) — state + async actions for sites
- SiteListPage — DataTable with search bar, city/ZFE filters, pagination, action buttons
- SiteCreatePage + SiteForm — Full form with all fields organized in sections
- SiteEditPage — Pre-filled form reusing SiteForm
- SiteDetailPage — Read-only view with mini-map and summary cards
- MapPicker component — Leaflet click-to-place GPS picker with draggable marker
- i18n translations (fr/en) for all site-related strings
- 4 component tests with Leaflet mocking for jsdom

### Changed
- `frontend/src/routes.tsx` — Added /sites, /sites/new, /sites/:id, /sites/:id/edit routes

---

## [Session-06] — 2026-04-01
### Added
- Site SQLAlchemy model with PostGIS POINT geometry column and GIST spatial index (`backend/app/models/site.py`)
- Alembic migration for site table with GeoAlchemy2 geometry support
- Pydantic schemas: SiteCreate (with lat/lng/security_profile validation), SiteUpdate, SiteResponse, SiteSummary, SiteListResponse (`backend/app/schemas/site.py`)
- 7 CRUD API endpoints: list (paginated + city/ZFE filters), get by ID, get by code, create (with PostGIS ST_MakePoint), update (geom recalc), delete, summary (`backend/app/api/v1/sites.py`)
- 13 test cases covering all CRUD operations, validation, filters, and PostGIS geometry

---

## [Session-05] — 2026-04-01
### Added
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) — backend (ruff + mypy + pytest) and frontend (eslint + tsc + vitest)
- Ruff Python linting config (`backend/ruff.toml`) with FastAPI-compatible rules
- Mypy type checking config (`backend/mypy.ini`) with pydantic + sqlalchemy plugins
- Prettier config (`frontend/.prettierrc`) for consistent formatting
- Pre-commit hooks (`.pre-commit-config.yaml`) — ruff + prettier
- Backend scripts (`backend/scripts.sh`) — lint, format, test, seed, migrate commands
- Frontend scripts: `type-check`, `format`, `format:check` in package.json

### Fixed
- 3 B904 lint violations (raise-from-err) in auth middleware and endpoints
- 5 import sorting violations auto-fixed by ruff

---

## [Session-04] — 2026-04-01
### Added
- SQLAlchemy models: Tenant, User, Role, Permission, RolePermission (`backend/app/models/auth.py`)
- Alembic migration for all auth tables
- Pydantic v2 schemas for auth requests/responses (`backend/app/schemas/auth.py`)
- JWT auth middleware with OAuth2PasswordBearer (`backend/app/middleware/auth.py`)
- RBAC `require_role()` dependency factory (`backend/app/middleware/rbac.py`)
- Auth endpoints: POST login, POST logout, POST refresh, GET me (`backend/app/api/v1/auth.py`)
- User CRUD endpoints: GET list, POST create, PUT update, DELETE deactivate (`backend/app/api/v1/users.py`)
- Role CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/roles.py`)
- Tenant CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/tenants.py`)
- Password hashing (bcrypt) and JWT encode/decode utilities (`backend/app/utils/security.py`)
- Seed data script: default tenant, 5 system roles, admin user (`backend/app/scripts/seed_data.py`)
- 11 new tests: auth flow (8) + user management (3)

### Changed
- `backend/app/database.py` — `get_db` uses `session.begin()` context, NullPool in test mode
- `backend/requirements.txt` — added bcrypt==4.2.1, pydantic[email]

---

## [Session-03] — 2026-04-01
### Added
- Vite React TypeScript project with strict mode
- TailwindCSS v4 with full design system tokens (`@theme` block in index.css)
- Layout shell: `AppLayout`, `Sidebar` (NavLink-based navigation), `Header` (language toggle, user display)
- 7 base UI components: `Button` (4 variants), `Input`, `Card`, `DataTable` (generic typed), `Modal`, `Toast`, `Skeleton`
- Routing with lazy-loaded pages (`routes.tsx` using `createBrowserRouter`)
- Zustand auth store (`useAuthStore`) with localStorage persistence
- Axios API client with JWT interceptors
- i18n configuration (French default, English fallback) with translation stubs
- Placeholder pages: `DashboardPage`, `LoginPage`
- `frontend/Dockerfile` (multi-stage Node 18 build + nginx serve)
- Vitest test setup with jsdom + React Testing Library
- 8 tests: AppLayout render, Button variants/loading/disabled, Card render, routing navigation

---

## [Session-02] — 2026-04-01
### Added
- `backend/app/config.py` — Pydantic Settings loading from `.env`
- `backend/app/database.py` — SQLAlchemy async engine, session factory, `get_db` dependency
- `backend/app/models/base.py` — `BaseModel` with UUID pk + `TimestampMixin` (created_at, updated_at)
- `backend/app/api/v1/health.py` — Health endpoint checking DB and Redis connectivity
- `backend/app/api/v1/__init__.py` — API v1 router aggregation
- `backend/alembic.ini` + `alembic/env.py` — Async Alembic configured with PostGIS table exclusion
- `backend/tests/conftest.py` — Async test client fixture (httpx + ASGITransport)
- `backend/tests/test_health.py` — 4 tests (root, health, docs, openapi schema)
- `backend/pytest.ini` — Pytest async mode config

### Changed
- `backend/app/main.py` — Added lifespan events, API router inclusion, config-driven settings

---

## [Session-01] — 2026-04-01
### Added
- Monorepo directory structure (`backend/`, `frontend/`, `mobile/`)
- Backend FastAPI skeleton with `app/` package and all sub-modules (models, schemas, api, services, middleware, tasks, utils)
- `backend/requirements.txt` with all core dependencies (FastAPI, SQLAlchemy, GeoAlchemy2, Celery, OR-Tools, scikit-learn)
- `backend/Dockerfile` (Python 3.11 slim with PostGIS system dependencies)
- `backend/.env.example` with all environment variables
- `docker-compose.yml` with 4 services: PostgreSQL 15 + PostGIS 3.4, Redis 7, OSRM, FastAPI backend
- `.env` with default development values
- `frontend/package.json` placeholder scaffold
- Root `README.md` with quick start instructions and access URLs
- Minimal FastAPI app with `/` and `/health` endpoints

---

## [Session-00] — 2026-03-24
### Added
- Claude Code configuration (`.claude/` directory with settings, rules, agents, skills)
- `CLAUDE.md` root context file with `@import` directives
- Obsidian vault enhancements (`INDEX.md`, `CHANGELOG.md`, ADR template)
- `.gitignore` for Python, Node, Flutter, IDE, and secrets
- Git repository initialized
