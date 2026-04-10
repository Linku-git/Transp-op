# Transpop — Development Progress Tracker

> See also: [[README]] | [[ROADMAP]] | [[agents]]

> Last updated: 2026-04-10

## Summary

| Phase | Sessions | Status | Completion |
|-------|----------|--------|------------|
| Phase 0 — Cadrage & Setup | 01-05 | COMPLETE | 5/5 |
| Phase 1 — MVP Core (Modules A-D) | 06-30 | COMPLETE | 25/25 |
| Phase 2 — Financial & Reporting | 31-44 | COMPLETE | 14/14 |
| **Replit Deployment & Refinement** | **R01** | **COMPLETE** | **✅** |
| Phase 3 — Mobile MVP | 45-56 | **COMPLETE** | **12/12** |
| Phase 4 — Security & RTI | 57-66 | **COMPLETE** | **10/10** |
| Phase 5 — Journey Valorization | 67-76 | **COMPLETE** | **10/10** |
| Phase 6 — Enterprise Integrations | 77-86 | **COMPLETE** | **10/10** |
| Phase 7 — Stabilization & Scale | 87-92 | IN PROGRESS | 5/6 |
| Phase 8 — SOTREG Modules (M1-M8) | 93-127 | IN PROGRESS | 7/35 |
| **Total (core sessions)** | **127** | | **98/127** |

---

## Phase 0 — Cadrage & Setup

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 01 | [[sessions/session-01\|Monorepo Setup & Docker]] | COMPLETE | 2026-04-01 | All services running: PostgreSQL 15 + PostGIS 3.4, Redis 7, OSRM, FastAPI |
| 02 | [[sessions/session-02\|Backend FastAPI Skeleton]] | COMPLETE | 2026-04-01 | Config, DB, Base model, health endpoint, Alembic, 4 tests passing |
| 03 | [[sessions/session-03\|Frontend React Scaffold]] | COMPLETE | 2026-04-01 | Vite + TS strict + TailwindCSS v4 + design system, 7 UI components, 8 tests |
| 04 | [[sessions/session-04\|Auth & RBAC Foundation]] | COMPLETE | 2026-04-01 | JWT auth, 5 roles, RBAC middleware, user/role/tenant CRUD, 15 tests |
| 05 | [[sessions/session-05\|CI/CD & Test Infrastructure]] | COMPLETE | 2026-04-01 | GitHub Actions CI, ruff, mypy, Prettier, pre-commit, 23 tests green |

## Phase 1 — MVP Core: Modules A-D

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 06 | [[sessions/session-06\|Site Model & CRUD API]] | COMPLETE | 2026-04-01 | PostGIS model, 7 CRUD endpoints, pagination, filters, 13 tests |
| 07 | [[sessions/session-07\|Site Frontend Pages]] | COMPLETE | 2026-04-01 | List/create/edit/detail pages, MapPicker, Zustand store, 4 tests |
| 08 | [[sessions/session-08\|Site Dashboard & Shifts UI]] | COMPLETE | 2026-04-01 | Badge, SiteSummaryCards, ShiftConfigPanel, enhanced detail page, 3 tests |
| 09 | [[sessions/session-09\|Employee Model & CRUD API]] | COMPLETE | 2026-04-01 | 30+ field model, 8 endpoints, CSV upload, geocoding, 13 tests |
| 10 | [[sessions/session-10\|Employee Frontend Pages]] | COMPLETE | 2026-04-01 | List/create/edit/detail pages, dual-marker map, 6 filters, 3 tests |
| 11 | [[sessions/session-11\|Employee Map View & Bulk Actions]] | COMPLETE | 2026-04-01 | Full-screen map, site-colored markers, bulk CSV export/delete, 2 tests |
| 12 | [[sessions/session-12\|Employee Leave Model & API]] | COMPLETE | 2026-04-01 | Leave model, 5 CRUD endpoints, overlap detection, 8 tests |
| 13 | [[sessions/session-13\|Excel Import Engine]] | COMPLETE | 2026-04-01 | 6-sheet parser, upsert, preview, validation, 3 endpoints, 13 tests |
| 14 | [[sessions/session-14\|Excel Import Frontend]] | COMPLETE | 2026-04-01 | Upload/preview/import UI, FileUpload, Tabs, ProgressBar, 5 tests |
| 15 | [[sessions/session-15\|Modal Analysis Model & API]] | COMPLETE | 2026-04-01 | Modal model, upsert CRUD, stats/scores, 6 endpoints, 9 tests |
| 16 | [[sessions/session-16\|Modal Analysis Frontend]] | COMPLETE | 2026-04-01 | PieChart/BarChart/Histogram, 5 dashboard cards, site filter, 3 tests |
| 17 | [[sessions/session-17\|Mobility Scores & Shadow Zones]] | COMPLETE | 2026-04-01 | Scoring engine (0-100), shadow zones, weather/disruption analytics, carpool potential, 6 tests |
| 18 | [[sessions/session-18\|Clustering Engine]] | COMPLETE | 2026-04-01 | DBSCAN/KMeans/hierarchical, PMR-aware, configurable params, 11 tests |
| 19 | [[sessions/session-19\|Meeting Zone Optimization]] | COMPLETE | 2026-04-01 | OSRM client, road-snap, PMR accessibility, walking constraints, 7 tests |
| 20 | [[sessions/session-20\|Vehicle Model & Fleet API]] | COMPLETE | 2026-04-01 | Vehicle CRUD, 5 filters, fleet summary by type/condition/motor/site, 11 tests |
| 21 | [[sessions/session-21\|Vehicle Assignment Algorithm]] | COMPLETE | 2026-04-01 | Bin-packing assignment, split/merge, PMR/ZFE constraints, volunteer drivers, 9 tests |
| 22 | [[sessions/session-22\|Route Optimization (OSRM + CVRP)]] | COMPLETE | 2026-04-01 | OR-Tools CVRP, OSRM table/route, two-leg model, ETA per stop, 10 tests |
| 23 | [[sessions/session-23\|Full Optimization Pipeline]] | COMPLETE | 2026-04-01 | E2E pipeline, Celery task, Redis progress, leave filtering, metrics (fuel/CO2/time), 8 tests |
| 24 | [[sessions/session-24\|Optimization Map (Leaflet)]] | COMPLETE | 2026-04-01 | Interactive map, 5 map components, layer controls, route popups, progress indicator, 15 tests |
| 25 | [[sessions/session-25\|Optimization Analytics Panel]] | COMPLETE | 2026-04-02 | MetricsPanel, RouteList, ClusterTable, GaugeChart, result/history pages, 35 tests |
| 26 | [[sessions/session-26\|Weather API Integration]] | COMPLETE | 2026-04-02 | WeatherForecast model, Open-Meteo service (free, no key), 4 endpoints, 5 tests |
| 27 | [[sessions/session-27\|Scenario Simulation Backend]] | COMPLETE | 2026-04-02 | Scenario model, scenario engine, 5 endpoints, comparison deltas, 6 tests |
| 28 | [[sessions/session-28\|Scenario Comparison Frontend]] | COMPLETE | 2026-04-02 | ScenarioListPage, ScenarioComparePage, WeatherWidget, 8 API client functions, 40 tests |
| 29 | [[sessions/session-29\|Settings & Constraints CRUD]] | COMPLETE | 2026-04-02 | OptimizationSettings + ConstraintParam models, 7 endpoints, SettingsPage + ConstraintsPage, 22 tests |
| 30 | [[sessions/session-30\|Export Engine (PDF, Excel, CSV, GeoJSON)]] | COMPLETE | 2026-04-02 | ExportEngine service, 5 endpoints, Celery tasks, 22 tests |

## Phase 2 — Financial & Reporting

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 31 | [[sessions/session-31\|Financial Models & API]] | COMPLETE | 2026-04-02 | 4 models, 8 endpoints, 5 vehicle refs seeded, 7 tests |
| 32 | [[sessions/session-32\|TCO Calculator Engine]] | COMPLETE | 2026-04-02 | TCO service, fleet/motorization/evolution, 8 tests |
| 33 | [[sessions/session-33\|ROI Calculator Engine]] | COMPLETE | 2026-04-02 | 4 ROI levers, payback, DB persistence, 9 tests |
| 34 | [[sessions/session-34\|Investment Model Comparator]] | COMPLETE | 2026-04-02 | CAPEX/MaD/OPEX comparison, sensitivity analysis, 11 tests |
| 35 | [[sessions/session-35\|Financial Dashboard — TCO]] | COMPLETE | 2026-04-02 | TCO calculator page, 5 chart/table components, dashboard tabs, 7 tests |
| 36 | [[sessions/session-36\|Financial Dashboard — ROI]] | COMPLETE | 2026-04-02 | WaterfallChart, PaybackSlider, CostPerTripGauge, InvestmentComparatorCards, DAFExportButton, 7 tests |
| 37 | [[sessions/session-37\|Cost-per-Trip & Breakeven]] | COMPLETE | 2026-04-02 | Cost per seat, breakeven analysis, chart, 8 tests |
| 38 | [[sessions/session-38\|DAF Export (ERP Format)]] | COMPLETE | 2026-04-02 | SAP FI/Sage/Cegid CSV/XML, TCO/ROI PDF+Excel, 10 tests |
| 39 | [[sessions/session-39\|HR Dashboard KPIs Backend]] | COMPLETE | 2026-04-02 | Mobility coverage, absenteeism, retention, shadow zones, 6 tests |
| 40 | [[sessions/session-40\|HR Dashboard Frontend]] | COMPLETE | 2026-04-02 | HeatmapTable, ScatterPlot, RetentionCard, ShadowZones, MobilityAlerts, 8 tests |
| 41 | [[sessions/session-41\|RSE/Environment Dashboard]] | COMPLETE | 2026-04-02 | CO2/modal/ZFE backend+frontend, DPEF export, 13 tests |
| 42 | [[sessions/session-42\|Enhanced Reporting Engine]] | COMPLETE | 2026-04-02 | GeneratedReport model, 4 report types (PDF+Excel), DB persistence, 7 tests |
| 43 | [[sessions/session-43\|Report Generation Frontend]] | COMPLETE | 2026-04-02 | ReportList + Generator pages, history endpoint, 6 tests |
| 44 | [[sessions/session-44\|KPI Snapshot System]] | COMPLETE | 2026-04-02 | KPISnapshot model, 6 KPI types, Celery task, trend queries, 7 tests |

---

## Replit Deployment & Refinement Phase

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| R01 | [[sessions/session-replit\|Replit Deployment & Refinement]] | COMPLETE | 2026-04-02 → 2026-04-08 | Infrastructure setup, Google Maps migration, seed data (1200 employees/106 vehicles/591 config rows), Pydantic v2 fixes, optimization sections rebuilt, modal analysis real data, production deployment on Reserved VM |

**Key outcomes of Replit session:**
- Platform is **live** on Replit Reserved VM (deployed)
- All 19 Alembic migrations applied; real demo data loaded
- All maps migrated from Leaflet → `@vis.gl/react-google-maps`
- Pydantic v2 error rendering fixed platform-wide
- 3 optimization sections rebuilt with real data and UX improvements
- Dashboard shows real data: 1200 employees, 106 vehicles, 32,696 km total distance
- Production build fixed (TS errors resolved, `build.sh` + `start_production.sh` created)

---

## Phase 3 — Mobile MVP

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 45 | [[sessions/session-45\|Flutter Project Setup]] | COMPLETE | 2026-04-08 | Flutter 3.38.5, 111 deps, 12 source files, 22 tests, GoRouter + Riverpod + Material 3 |
| 46 | [[sessions/session-46\|Mobile Auth Flow]] | COMPLETE | 2026-04-08 | JWT auth, dio interceptor, auto-refresh, SplashScreen, LoginScreen, 50 total tests |
| 47 | [[sessions/session-47\|Onboarding Wizard]] | COMPLETE | 2026-04-08 | 4-step PageView wizard, transport prefs, security questionnaire, permissions, 83 total tests |
| 48 | [[sessions/session-48\|Home Screen]] | COMPLETE | 2026-04-08 | NextDepartureCard with live countdown, QuickActions, ContentCarousel, night mode emergency, 112 total tests |
| 49 | [[sessions/session-49\|Trip Booking Screens]] | COMPLETE | 2026-04-08 | DatePicker, ShiftSelector, PickupPicker, BookingSummary, TripBookingScreen, 142 total tests |
| 50 | [[sessions/session-50\|Trip Management]] | COMPLETE | 2026-04-08 | TripsScreen (tabs), TripDetail, TripHistory with stats, cancel dialog, 163 total tests |
| 51 | [[sessions/session-51\|RTI Display & Vehicle Tracking]] | COMPLETE | 2026-04-08 | RTITrackingScreen, FullMapScreen, WebSocket+polling, ETA countdown, 191 total tests |
| 52 | [[sessions/session-52\|Push Notification Service]] | COMPLETE | 2026-04-08 | FCM service, 5 notification types, NotificationListScreen, token register, 206 total tests |
| 53 | [[sessions/session-53\|Profile & Preferences Screen]] | COMPLETE | 2026-04-08 | ProfileScreen, EditProfile, Preferences, 8 menu items, logout, 223 total tests |
| 54 | [[sessions/session-54\|Mobile API Backend]] | COMPLETE | 2026-04-08 | 3 models, 8 endpoints, migration, 30-min rule, offline manifest, 239 total tests |
| 55 | [[sessions/session-55\|Trip Statistics & CO2 Screen]] | COMPLETE | 2026-04-08 | StatisticsScreen, 5 chart widgets, CO2 calculator, share impact card, 259 total tests |
| 56 | [[sessions/session-56\|Offline Mode]] | COMPLETE | 2026-04-08 | Hive+SQLite storage, CacheManager, OfflineQueue, ConnectivityService, ManifestSync, 279 total tests |

## Phase 4 — Security & RTI

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 57 | [[sessions/session-57\|Stop Risk Score Model & Algorithm]] | COMPLETE | 2026-04-08 | PostGIS model, weighted scoring algorithm, 3 API endpoints, 20 backend tests |
| 58 | [[sessions/session-58\|RTI Backend System]] | COMPLETE | 2026-04-08 | VehiclePosition, RTIEvent, ETA calculator, Redis+DB, WebSocket, compliance, 14 tests |
| 59 | [[sessions/session-59\|RTI Config & Adaptive Sizing]] | COMPLETE | 2026-04-08 | RTIConfig model, adaptive sizing, pool recomposition, fallback protocol, 20 tests |
| 60 | [[sessions/session-60\|RTI Monitoring Dashboard]] | COMPLETE | 2026-04-08 | Dashboard page, 5 RTI components, compliance gauge, trend chart, KPI endpoint |
| 61 | [[sessions/session-61\|Security Questionnaire]] | COMPLETE | 2026-04-08 | SecurityQuestionnaire model, versioned submissions, reassessment scheduler, 18 tests |
| 62 | [[sessions/session-62\|Security Scoring Engine]] | COMPLETE | 2026-04-08 | Weighted scoring, risk classification, night heatmap, group aggregation, 22 tests |
| 63 | [[sessions/session-63\|Security-Constrained Pooling]] | COMPLETE | 2026-04-08 | 3-dimension pooling, night constraints, critical stop avoidance, priority vehicle, 18 tests |
| 64 | [[sessions/session-64\|Security Dashboard Frontend]] | COMPLETE | 2026-04-08 | Dashboard page, 5 security components, risk map, KPI endpoints, 9 frontend tests |
| 65 | [[sessions/session-65\|Mobile Night Mode & Emergency]] | COMPLETE | 2026-04-08 | Night mode service, EmergencyScreen, SecurityQuestionnaire, NightModeToggle |
| 66 | [[sessions/session-66\|Emergency Alert System]] | COMPLETE | 2026-04-08 | EmergencyAlert model, routing, location sharing, 3 API endpoints, 18 tests |

## Phase 5 — Journey Valorization

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 67 | [[sessions/session-67\|Content Model & CRUD API]] | COMPLETE | 2026-04-08 | Content model, CRUD API, audience targeting, publish/unpublish, 12 tests |
| 68 | [[sessions/session-68\|Content Management Frontend]] | COMPLETE | 2026-04-08 | 4 CRUD pages, TipTap rich text editor, audience targeting, 26 frontend tests |
| 69 | [[sessions/session-69\|Content Delivery & Engagement]] | COMPLETE | 2026-04-08 | ContentDelivery model, feed personalization, engagement tracking, 18 tests |
| 70 | [[sessions/session-70\|Mobile Content Feed]] | COMPLETE | 2026-04-09 | ContentFeedScreen with tabs, ContentDetailScreen, offline caching, 27 tests |
| 71 | [[sessions/session-71\|Mobile Micro-Training Player]] | COMPLETE | 2026-04-09 | TrainingPlayerScreen, video_player, quiz with scoring, offline cache, 28 tests |
| 72 | [[sessions/session-72\|Survey/Poll System]] | COMPLETE | 2026-04-09 | Survey+SurveyResponse models, 5 question types, validation, aggregation, 26 tests |
| 73 | [[sessions/session-73\|Mobile Survey Interface]] | COMPLETE | 2026-04-09 | SurveyScreen with 5 question types, offline queue, anonymous support, 25 tests |
| 74 | [[sessions/session-74\|LMS Integration]] | COMPLETE | 2026-04-09 | TrainingModule model, 3 LMS connectors, bidirectional sync, webhooks, 22 tests |
| 75 | [[sessions/session-75\|Engagement Analytics Dashboard]] | COMPLETE | 2026-04-09 | Analytics endpoint + dashboard page, KPIs, ranking table, type chart, 14 tests |
| 76 | [[sessions/session-76\|Value Measurement Engine]] | COMPLETE | 2026-04-09 | Valorization engine, configurable ROI, KPI endpoints, ROI lever, 18 tests |

## Phase 6 — Enterprise Integrations

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 77 | [[sessions/session-77\|SIRH Connection Framework]] | COMPLETE | 2026-04-09 | 3 models, sync engine, conflict resolver, CRUD API, delta updates, 20 tests |
| 78 | [[sessions/session-78\|SAP SuccessFactors Connector]] | COMPLETE | 2026-04-09 | OAuth 2.0, field mapping, delta sync, retry logic, 30 tests |
| 79 | [[sessions/session-79\|Workday Connector]] | COMPLETE | 2026-04-09 | OAuth 2.0, WID refs, effective dating, pagination, 40 tests |
| 80 | [[sessions/session-80\|Talentsoft & Sage Connectors]] | COMPLETE | 2026-04-09 | API Key auth, rate limiting (1000/500 req/h), training+payroll data, 34 tests |
| 81 | [[sessions/session-81\|SIRH Sync Dashboard]] | COMPLETE | 2026-04-09 | Connections page, sync dashboard, conflict queue, wizard, 9 frontend tests |
| 82 | [[sessions/session-82\|Operator Sizing Plan Export]] | COMPLETE | 2026-04-09 | Operator model, sizing export (JSON/XML/PDF), versioning, 20 tests |
| 83 | [[sessions/session-83\|Via & SWVL API Integration]] | COMPLETE | 2026-04-09 | Via + SWVL clients, sizing plan format, data exchange, validation, 22 tests |
| 84 | [[sessions/session-84\|Operator Portal (Web)]] | COMPLETE | 2026-04-09 | Operator portal, plan viewer, acknowledge, issue form, 7 frontend tests |
| 85 | [[sessions/session-85\|ERP Finance Export]] | COMPLETE | 2026-04-09 | SAP FI/Sage/Cegid CSV formatters, DAF export API, 23 tests |
| 86 | [[sessions/session-86\|Payment & Transport Pass]] | COMPLETE | 2026-04-09 | Stripe, Navigo, Edenred, Swile clients, webhook handling, 21 tests |

## Phase 7 — Stabilization & Scale

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 87 | [[sessions/session-87\|Performance Optimization]] | COMPLETE | 2026-04-09 | Redis caching, gzip compression, perf middleware, query optimization, 24 tests |
| 88 | [[sessions/session-88\|Load Testing]] | COMPLETE | 2026-04-09 | Locust framework, 5 scenarios (1K-10K users), data generator, 18 tests |
| 89 | [[sessions/session-89\|Security Hardening & Pentest]] | COMPLETE | 2026-04-09 | OWASP Top 10 audit, security headers, audit logging, 27 tests |
| 90 | [[sessions/session-90\|RGPD Audit & Compliance]] | COMPLETE | 2026-04-09 | Data export/delete, consent, retention cleanup, 13 RGPD articles, 25 tests |
| 91 | [[sessions/session-91\|Accessibility Audit]] | COMPLETE | 2026-04-09 | WCAG 2.1 AA checklist, contrast validation, a11y utils, 35 tests |
| 92 | [[sessions/session-92\|App Store Prep & Final Docs]] | NOT STARTED | | |

## Phase 8 — SOTREG Modules (M1-M8)

> Source: CDC Technique SOTREG v5.0 Final — OCP Transport Personnel

### Phase 8a — Diagnostic & Technologies (M1-M3)

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 93 | [[sessions/session-93\|Transport Line Model & Context Service]] | COMPLETE | 2026-04-09 | M1: Ligne model (CDC km_annual=D*R*J), FleetContext model, ContextService, 6 CRUD endpoints, 20 tests |
| 94 | [[sessions/session-94\|ZFE Detection & Gravity Model OD Matrix]] | COMPLETE | 2026-04-09 | M1: ADEME ZFE API + local registry, Wilson 1967 gravity model, OD matrix, geocoding enrichment, 6 endpoints, 35 tests |
| 95 | [[sessions/session-95\|Diagnostic Frontend Dashboard]] | COMPLETE | 2026-04-10 | M1: DiagnosticDashboard, LigneList/Form, ZFEMapOverlay, ODFlowChart, 15 tests |
| 96 | [[sessions/session-96\|Range Correction & 15-Year TCO Model]] | COMPLETE | 2026-04-10 | M2: 3 correction factors, 15y TCO with financing/escalation, breakeven, 35 tests |
| 97 | [[sessions/session-97\|Demand Charge Optimization & IRVE Sizing]] | COMPLETE | 2026-04-10 | M2: SOC=62% Qin 2016, ONEE tariff, IRVE sizing AC/DC, model+migration, 21 tests |
| 98 | [[sessions/session-98\|Technologies Frontend Dashboard]] | COMPLETE | 2026-04-10 | M2: 4-tab dashboard, range/TCO/breakeven/IRVE/charging components, 6 tests |
| 99 | [[sessions/session-99\|Stop Generation & Capacity Model]] | COMPLETE | 2026-04-10 | M3: DBSCAN stop gen, HCM 2000 capacity, LOS A-F, PostGIS model, 27 tests |
| 100 | [[sessions/session-100\|IRVE Cost Calculator & Depot Layout]] | NOT STARTED | | M3: Depot electrification cost, layout planner |
| 101 | [[sessions/session-101\|Infrastructure Frontend Dashboard]] | NOT STARTED | | M3: Stop map, capacity table, depot viewer, cost chart |

### Phase 8b — Performance & Finance (M4-M5)

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 102 | [[sessions/session-102\|AVL-Based KPI Engine]] | NOT STARTED | | M4: OTP >95%, headway COV <0.3, load factor, speed |
| 103 | [[sessions/session-103\|Leave Time Optimization (LTO)]] | NOT STARTED | | M4: Anti-platooning, scipy optimization, departure offsets |
| 104 | [[sessions/session-104\|IoT Telemetry Pipeline & Predictive Maintenance]] | NOT STARTED | | M4: Webhook ingestion, IsolationForest, maintenance alerts |
| 105 | [[sessions/session-105\|Performance Frontend Dashboard]] | NOT STARTED | | M4: OTP gauge, headway chart, telemetry, maintenance |
| 106 | [[sessions/session-106\|NPV & CO2 Externalities Valorization]] | NOT STARTED | | M5: VAN, IRR, CO2 monetization, carbon price MAD |
| 107 | [[sessions/session-107\|Markowitz Portfolio & Supernetwork Equilibrium]] | NOT STARTED | | M5: Mean-variance optimization, Frank-Wolfe algorithm |
| 108 | [[sessions/session-108\|Advanced Finance Frontend Dashboard]] | NOT STARTED | | M5: NPV waterfall, efficient frontier, CO2 panel |
| 109 | [[sessions/session-109\|Celery Tasks & MAD Currency Calibration]] | NOT STARTED | | Cross: Celery beat, MAD calibration, SOTREG seed data |

### Phase 8c — Roadmap, Scoring & MCDA (M6-M7)

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 110 | [[sessions/session-110\|Phased Electrification Transition Planner]] | NOT STARTED | | M6: Phase sequencing, budget allocation, milestones |
| 111 | [[sessions/session-111\|Gantt Chart & Roadmap Frontend]] | NOT STARTED | | M6: Interactive Gantt, budget chart, milestone tracker |
| 112 | [[sessions/session-112\|MCDA Scoring Engine]] | NOT STARTED | | M7: 6-criteria weighted sum, normalization, McFadden logit |
| 113 | [[sessions/session-113\|Comparison PDF Report Generator]] | NOT STARTED | | M7: Radar chart, scoring table, sensitivity, Excel export |
| 114 | [[sessions/session-114\|Scoring Frontend Dashboard]] | NOT STARTED | | M7: MCDA interface, radar chart, sensitivity sliders |
| 115 | [[sessions/session-115\|Keycloak Roles & RBAC Extension]] | NOT STARTED | | Cross: 5 to 9 roles, permissions matrix, route guards |

### Phase 8d — ML Infrastructure & Real-Time (M8)

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 116 | [[sessions/session-116\|ML Infrastructure: Model Registry & Feature Store]] | NOT STARTED | | ML: joblib/h5 versioning, feature store, Celery retrain |
| 117 | [[sessions/session-117\|Clarke & Wright Savings Algorithm]] | NOT STARTED | | M8: S_ij savings, greedy merge, strategy="cw" |
| 118 | [[sessions/session-118\|Genetic Algorithm Optimizer]] | NOT STARTED | | M8: OX crossover 0.85, mutation 0.05, 500 gen, strategy="ga" |
| 119 | [[sessions/session-119\|LSTM Demand Forecasting]] | NOT STARTED | | M8/ML: 336 timesteps, is_ramadan, TensorFlow/Keras |
| 120 | [[sessions/session-120\|RandomForest Driver Risk Scoring]] | NOT STARTED | | M8/ML: 8 telematics features, penalty scoring, daily Celery |
| 121 | [[sessions/session-121\|SocketIO Real-Time GPS Streaming]] | NOT STARTED | | M8: <1s latency, 1500+ connections, Redis pub/sub, geofence |
| 122 | [[sessions/session-122\|Real-Time Operations Frontend]] | NOT STARTED | | M8: Live fleet map, demand forecast, driver risk, alerts |
| 123 | [[sessions/session-123\|ML Dashboard & Retraining UI]] | NOT STARTED | | ML: Model registry, metrics, feature importance, retrain |

### Phase 8e — Portals, Chatbot & Integration

| Session | Title | Status | Date | Notes |
|---------|-------|--------|------|-------|
| 124 | [[sessions/session-124\|Driver Portal (React)]] | NOT STARTED | | M8: Trip assignments, risk score, schedule, conducteur role |
| 125 | [[sessions/session-125\|Contractor Dashboard (Dash+Plotly)]] | NOT STARTED | | M8: SLA compliance, financial reconciliation, fleet status |
| 126 | [[sessions/session-126\|Observability Stack]] | NOT STARTED | | Infra: Prometheus, Grafana, Loki, OpenTelemetry |
| 127 | [[sessions/session-127\|Rasa Chatbot & Final Integration]] | NOT STARTED | | Cross: Chatbot, E2E integration test, 9-role verification |

---

## Related Documentation
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database schema
- [[API_ENDPOINTS]] — API endpoints
- [[FRONTEND_PAGES]] — Web pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Timeline & milestones
- [[PRD]] — Product Requirements Document v5.0
- [[sessions/session-replit]] — Replit deployment & refinement notes

---

## Blockers & Issues

_None._

## Technical Debt (from Replit sessions)

| Item | Details | Priority |
|------|---------|----------|
| API path pattern | All `frontend/src/api/*.ts` files must use `/api/v1/...` full paths (baseURL is empty string) | High |
| CORS credentials | `allow_credentials=False` with wildcard origin — needs narrowing for production security | Medium |
| Pydantic v2 everywhere | `extractApiError()` must be used in any new form page | Medium |
| Redis optional | Celery tasks silently disabled in production if Redis is unavailable | Low |
