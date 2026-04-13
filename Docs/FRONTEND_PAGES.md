# Transpop — Frontend Web Pages (React + TypeScript)

> See also: [[API_ENDPOINTS]] | [[MOBILE_PAGES]] | [[ARCHITECTURE]] | [[agents]]

## Page Architecture

### Layout
- **AppLayout** — Sidebar + Header + Content area
  - Sidebar: Navigation menu (role-based visibility)
  - Header: User profile, tenant name, language toggle, notifications
  - Content: Route-based page rendering

### Route Structure

```
/                           -> Dashboard (role-based redirect)
/login                      -> LoginPage
/dashboard                  -> OperationsDashboard
/dashboard/hr               -> HRDashboard
/dashboard/rse              -> RSEDashboard
/dashboard/financial        -> FinancialDashboard
/dashboard/rti              -> RTIMonitoringDashboard
/dashboard/security         -> SecurityDashboard
/sites                      -> SiteListPage
/sites/new                  -> SiteCreatePage
/sites/:id                  -> SiteDetailPage
/sites/:id/edit             -> SiteEditPage
/employees                  -> EmployeeListPage
/employees/new              -> EmployeeCreatePage
/employees/:id              -> EmployeeDetailPage
/employees/:id/edit         -> EmployeeEditPage
/employees/map              -> EmployeeMapPage
/modal-analysis             -> ModalAnalysisPage
/vehicles                   -> VehicleListPage
/vehicles/new               -> VehicleCreatePage
/vehicles/:id/edit          -> VehicleEditPage
/optimization               -> OptimizationPage
/optimization/:id           -> OptimizationResultPage
/optimization/history       -> OptimizationHistoryPage
/scenarios                  -> ScenarioListPage
/scenarios/compare          -> ScenarioComparePage
/financial                  -> FinancialScenarioListPage
/financial/new              -> FinancialScenarioCreatePage
/financial/:id              -> FinancialScenarioDetailPage
/financial/tco              -> TCOCalculatorPage
/financial/roi              -> ROICalculatorPage
/financial/comparator       -> InvestmentComparatorPage
/content                    -> ContentListPage
/content/new                -> ContentCreatePage
/content/:id                -> ContentDetailPage
/content/:id/edit           -> ContentEditPage
/content/analytics          -> ContentAnalyticsPage
/reports                    -> ReportListPage
/reports/generate           -> ReportGeneratorPage
/settings                   -> SettingsPage
/settings/constraints       -> ConstraintsPage
/import                     -> ExcelImportPage
/admin/users                -> UserManagementPage
/admin/tenants              -> TenantManagementPage
/admin/sirh                 -> SIRHConnectionsPage
/admin/sirh/sync            -> SIRHSyncDashboardPage
/admin/operators            -> OperatorManagementPage
/admin/api-keys             -> APIKeyManagementPage
/sotreg                     -> DiagnosticDashboardPage
/sotreg/lignes              -> LigneListPage
/sotreg/lignes/new          -> LigneFormPage
/sotreg/lignes/:id/edit     -> LigneFormPage (edit mode)
/sotreg/technologies        -> TechnologiesDashboardPage
/sotreg/infrastructure      -> InfrastructureDashboardPage
/sotreg/finance             -> AdvancedFinanceDashboardPage
/sotreg/roadmap             -> RoadmapDashboardPage
/sotreg/scoring             -> ScoringDashboardPage
/sotreg/operations          -> OperationsDashboardPage
/sotreg/ml                  -> MLDashboardPage
/admin/roles                -> RoleManagementPage
```

---

## Pages by Module

### Authentication (Session 04)

#### LoginPage `/login`
- SSO login button (Auth0/Keycloak)
- Email/password fallback
- MFA challenge dialog
- "Forgot password" link
- Language selector (FR/EN)

---

### Operations Dashboard (Sessions 24-25)

#### OperationsDashboard `/dashboard`
- **KPI Cards Row:** Total vehicles, avg occupancy, total distance, fuel cost, CO2 saved
- **Interactive Map (Leaflet):**
  - Site markers (color-coded)
  - Employee points (toggle)
  - Cluster regions (toggle)
  - Route polylines with vehicle colors (toggle)
  - Meeting zones with radius (toggle)
  - Access legs: dashed employee->gathering point (toggle)
  - Risk stop overlay (toggle)
  - ZFE zone boundaries (toggle)
  - Legend with layer toggles
- **Analytics Panel (right side):**
  - Modal distribution pie chart (per site dropdown)
  - Occupancy rate bar chart
  - Per-site breakdown table
  - PMR stats card
  - Fleet utilization gauge
- **Weather Widget:** 3-day forecast per selected site
- **Quick Actions:** Run optimization, Import data, Export report

---

### HR Dashboard (Sessions 39-40)

#### HRDashboardPage `/dashboard/hr` ✅ Session 40
- MobilityAlerts: critical (coverage <60%) and warning (shadow zones >10%) banners
- Coverage summary card (big number) + 3 HeatmapTables (by site/shift/department)
- HeatmapTable: reusable color-coded table (red <50%, amber 50-75%, green >75%)
- Mobility score evolution LineChart (date vs score)
- Absenteeism correlation ScatterPlot (reusable Recharts scatter)
- RetentionImpactCard: savings estimate, turnover rate, departure breakdown bar
- ShadowZonesList: employees beyond 30km threshold with location details
- Components: `HeatmapTable`, `ScatterPlot`, `RetentionImpactCard`, `ShadowZonesList`, `MobilityAlerts`

---

### RSE/Environment Dashboard (Session 41)

#### RSEDashboardPage `/dashboard/rse` ✅ Session 41
- 3 summary cards: CO2 saved, private vehicles avoided, ZFE compliance %
- CO2TrendLine: Recharts line chart (green trend over time)
- Modal distribution PieChart + ZFEComplianceGauge (SVG semicircle)
- ModalShiftComparison: before/after grouped bar chart
- DPEF export button (downloads PDF from POST /kpis/rse/dpef)
- Components: `CO2TrendLine`, `ZFEComplianceGauge`, `ModalShiftComparison`

---

### Financial Dashboard (Sessions 35-36)

#### FinancialDashboard `/dashboard/financial`
- TCO comparison cards (3 models side-by-side)
- ROI waterfall chart (4 levers)
- Payback period interactive slider
- Cost-per-trip gauge (actual vs target)
- Investment comparator table
- Export to ERP button

---

### RTI Monitoring Dashboard (Session 60)

#### RTIMonitoringDashboard `/dashboard/rti`
- RTI compliance gauge (live percentage)
- Stop wait time heatmap
- Risk stop map with real-time vehicle positions
- RTI violation alert list
- Historical compliance trend (line chart)

---

### Security Dashboard (Session 64)

#### SecurityDashboard `/dashboard/security`
- Security score distribution chart
- Map overlay: risk-scored stops (green/orange/red)
- Night shift coverage indicator
- Incident history timeline
- Emergency alert log

---

### Sites (Sessions 06-08)

#### SiteListPage `/sites`
- Data table: code, name, city, shifts, ZFE, security profile, employee count
- Search bar + filters (city, ZFE)
- "Add Site" button
- Bulk actions (export, delete)

#### SiteCreatePage `/sites/new`
- Form: all site fields (code, name, address, GPS, shifts, contacts)
- Map picker for GPS coordinates
- ZFE zone toggle
- Security profile selector
- Shift time configuration (1-3 shifts)

#### SiteDetailPage `/sites/:id`
- Site info card
- Mini-map with site location
- Employee count, vehicle count, PMR count
- Shift schedule display
- Quick links: view employees, view vehicles

#### SiteEditPage `/sites/:id/edit`
- Pre-filled form (same as create)
- Map picker with current location

---

### Employees (Sessions 09-14)

#### EmployeeListPage `/employees`
- Data table: matricule, name, site, shift, PMR, mode, opt-in status
- Filters: site, shift, PMR, department, active/inactive
- Search by name or matricule
- "Add Employee" button
- Bulk CSV upload button

#### EmployeeCreatePage `/employees/new`
- Form: personal info, site/shift, address, transport profile
- Address geocoding (auto-fill GPS from address)
- PMR toggle
- Transport mode selector
- Volunteer driver section (conditional on has_private_car)

#### EmployeeDetailPage `/employees/:id`
- Profile card (name, matricule, site, shift, PMR)
- Mini-map: home location + site location
- Transport modal data card
- Leave periods calendar view
- Trip history (if mobile app active)

#### EmployeeMapPage `/employees/map`
- Full-screen Leaflet map
- All employees as markers (color by site)
- Filter controls overlay (site, shift, PMR)
- Click employee marker -> popup with details
- Heatmap toggle (employee density)

#### ExcelImportPage `/import`
- File upload dropzone (.xlsx)
- Sheet detection + preview (tab per sheet)
- Validation results table (errors by row/column)
- Import button per sheet or "Import All"
- Progress indicator
- Error download as CSV

---

### Modal Analysis (Sessions 15-17)

#### ModalAnalysisPage `/modal-analysis`
- **Modal Distribution:** Pie chart per site (dropdown)
- **Global vs per-site toggle**
- **Shift Potential:** bar chart — employees willing to switch
- **Weather Impact:** chart showing mode switches in rain
- **Carpool Contribution:** seats offered vs demand
- **Distance/Time Histograms**
- **Shadow Zones:** employees without satisfactory transport
- **Mobility Score Table:** per employee, per group

---

### Vehicles (Session 20)

#### VehicleListPage `/vehicles`
- Data table: type, brand, capacity, site, condition, motorization, ZFE
- Filters: site, type, condition, motorization, PMR accessible
- "Add Vehicle" button

#### VehicleCreatePage `/vehicles/new`
- Form: type, brand, capacity, year, owner, cost, condition
- PMR accessible toggle
- Motorization selector
- ZFE compliance toggle
- Site assignment dropdown

---

### Optimization (Sessions 23-25)

#### OptimizationPage `/optimization`
- **Controls Panel:**
  - Site selector (or "All Sites")
  - Target date picker
  - Condition type dropdown (normal, rain, strike, peak, night)
  - Algorithm settings (clustering method, radius)
  - "Run Optimization" button
- **Results (after run):**
  - Interactive map (clusters, routes, meeting zones, access legs)
  - Metrics panel (vehicles, occupancy, distance, time, CO2)
  - Route list with expand/collapse per vehicle
  - Cluster details table

#### OptimizationResultPage `/optimization/:id`
- Full results display (map + metrics + tables)
- Export buttons (PDF, Excel, GeoJSON)
- "Re-run with changes" button

#### OptimizationHistoryPage `/optimization/history`
- Table of past runs (date, site, condition, metrics)
- Compare button (select 2 to compare)

---

### Scenarios (Sessions 27-28)

#### ScenarioListPage `/scenarios`
- Data table: name, site, condition type, demand multiplier, created date, key metrics
- Condition type chips (normal, rain, strike, peak, night, transit_failure)
- Site filter dropdown
- Checkbox selection for multi-scenario comparison
- "Compare Selected" button (enabled when 2+ scenarios selected)
- Delete action per row
- Navigation to ScenarioComparePage with selected scenario IDs

#### ScenarioComparePage `/scenarios/compare`
- Scenario selector dropdowns (select 2-3 scenarios)
- Side-by-side metrics comparison table (vehicles, occupancy, distance, cost, CO2)
- Color-coded delta values (green for improvements, red for worse)
- Recommendations panel with scenario-specific suggestions
- URL query parameter support (`?ids=uuid1,uuid2`) for direct linking
- "Compare" button to trigger comparison

#### WeatherWidget (Component)
- Located in `components/optimization/WeatherWidget.tsx`
- 3-day weather forecast display per selected site
- Condition icons (sun, cloud, rain, snow, etc.)
- Temperature ranges (min/max) and precipitation data
- Scenario suggestion chips based on weather conditions
- One-click "Apply" button to create weather-based scenario
- Integrated into OptimizationPage below the controls panel

---

### Financial Engineering (Sessions 31-38)

#### FinancialScenarioListPage `/financial`
- Table of financial scenarios
- Create new button
- Filters: investment model, date

#### FinancialScenarioCreatePage `/financial/new`
- Investment model selector (CAPEX / mise-a-dispo / OPEX)
- Duration slider (1-10 years)
- Fleet composition builder (add vehicle types + quantities)
- Parameter inputs (fuel price, maintenance, etc.)
- Calculate button

#### TCOCalculatorPage `/financial/tco` ✅ Session 35
- Fleet composition form: add/remove vehicle rows (type, motorization, quantity)
- Duration slider (1-10 years)
- Calculate button → POST `/financial/tco/calculate`
- Results: FleetAggregation card, TCOComparisonCards, TCOEvolutionChart (Recharts LineChart), MotorizationTable, VehicleTCOBreakdown (stacked BarChart)
- Components: `TCOComparisonCards`, `TCOEvolutionChart`, `MotorizationTable`, `VehicleTCOBreakdown`, `FleetAggregation`

#### ROICalculatorTab (within `/financial` ROI tab) ✅ Session 36
- 11-field form: headcount, daily cost, absence rates, turnover rates, travel hours, engagement, training cost, total investment
- "Calculer ROI" button → POST `/financial/roi/calculate`
- Results: WaterfallChart (4 levers + total), PaybackSlider (color-coded), summary cards (ROI total, %, payback)
- Components: `WaterfallChart`, `PaybackSlider`, `CostPerTripGauge`, `DAFExportButton`

#### InvestmentComparatorTab (within `/financial` Comparator tab) ✅ Session 36
- 4-field form: vehicle count, headcount, annual trips, duration
- "Comparer" button → POST `/financial/compare`
- Results: InvestmentComparatorCards (3 models + recommendation badge)
- Components: `InvestmentComparatorCards`

---

### Content Management (Sessions 67-68, 75)

#### ContentListPage `/content` ✅ Session 68
- Data table: title, type chip (news/training/safety/survey with icons), status badge (draft/published/archived), published date, audience summary
- Filters: content_type dropdown, status dropdown, text search
- Stats bento: total, published, drafts counts
- Pagination with page controls
- Row actions: view, edit, publish/unpublish, delete (hover reveal)
- "Créer du contenu" primary CTA
- Components: inline stats, filter bar, action buttons

#### ContentCreatePage `/content/new` ✅ Session 68
- `ContentForm` shared component with card-based sections
- Title input, TipTap rich text editor (bold, italic, lists, headings toolbar)
- Content type selector (news, training, safety, survey)
- Media URL input with image preview
- `AudienceTargeting` component: site dropdown (from API), department/shift chip inputs
- Expiry date datetime-local picker
- Preview toggle button (shows rendered content inline)
- Validation: title required
- Components: `RichTextEditor`, `AudienceTargeting`, `ContentForm`

#### ContentEditPage `/content/:id/edit` ✅ Session 68
- Same `ContentForm` with `initialData` pre-fill
- Breadcrumb navigation: Contenu > {title} > Modifier
- Loads content from store on mount
- Loading/error/not-found states

#### ContentDetailPage `/content/:id` ✅ Session 68
- Read-only view with title, type badge, status badge
- Rendered HTML body (dangerouslySetInnerHTML)
- Media display (image preview or link)
- Audience targeting display (sites, departments, shifts)
- Date info: created, updated, published, expires
- Publish/unpublish toggle button
- Edit and delete action buttons
- Engagement metrics placeholder (session 69)

#### ContentAnalyticsPage `/content/analytics` ✅ Session 75
- **Overview KPIs (4 cards):** total views, completions, avg quiz score, avg time spent
- **Training Hours Hero Card:** gradient card showing total recovered training hours (seconds→hours)
- **Engagement by Type Chart:** horizontal bar chart with type-colored bars (news, training, safety, survey)
- **Engagement Rates Card:** view rate + completion rate progress bars, delivery/completion totals
- **Content Ranking Table:** sorted by completions, columns: title, type, views, completions, avg score, avg time
- API: `GET /api/v1/content/analytics` → overview + content_ranking + by_type

---

### SOTREG — Diagnostic & Context (Session 95)

#### DiagnosticDashboardPage `/sotreg` ✅ Session 95
- **Fleet KPI Cards (6):** total vehicles, km annuels, tCO₂/an, age moyen, motorisation split (donut), lignes actives
- **ZFE Compliance Card:** lignes in ZFE count, compliance percentage, link to ligne list
- **OD Flow Summary:** total flows, top 5 OD pairs, compute OD button
- **Quick Actions:** link to ligne list, create new ligne
- API: `GET /api/v1/sotreg/context/snapshot`, `GET /api/v1/sotreg/lignes`, `GET /api/v1/sotreg/zfe/lignes`, `GET /api/v1/sotreg/od-matrix`

#### LigneListPage `/sotreg/lignes` ✅ Session 95
- Data table: code, name, service type badge, distance km, rotations/day, km annuels, motorisation, active status
- Filters: service_type dropdown, is_active toggle, text search
- Pagination controls
- Row actions: edit (link), delete (confirm dialog)
- "Nouvelle Ligne" primary CTA
- API: `GET /api/v1/sotreg/lignes`, `DELETE /api/v1/sotreg/lignes/{id}`

#### LigneFormPage `/sotreg/lignes/new` & `/sotreg/lignes/:id/edit` ✅ Session 95
- Create/edit form with 4 sections: Identification, Géographie, Paramètres opérationnels, Véhicule
- Google Maps coordinate picker (click to set origin/destination)
- Computed km_annual display (D × R × J formula)
- Service type and motorisation dropdowns
- Pydantic v2 error handling via extractApiError
- API: `POST /api/v1/sotreg/lignes`, `PUT /api/v1/sotreg/lignes/{id}`, `GET /api/v1/sotreg/lignes/{id}`

#### ZFEMapOverlay (Component) ✅ Session 95
- Google Maps overlay at `components/sotreg/ZFEMapOverlay.tsx`
- Markers: blue (hors ZFE) / red (en ZFE) for each ligne endpoint
- Polylines connecting origin to destination per ligne
- InfoWindow on click: ligne code, ZFE status, zone name, restriction level
- Legend: compliance count, color coding
- Empty state when no ZFE data

#### ODFlowChart (Component) ✅ Session 95
- Recharts horizontal bar chart at `components/sotreg/ODFlowChart.tsx`
- Top 15 OD flows by flow_estimate
- Summary: total flux, OD pair count, average distance
- Empty state when no OD matrix computed

### SOTREG — Technologies & Electrification (Session 98)

#### TechnologiesDashboardPage `/sotreg/technologies` ✅ Session 98
- **4 tabs:** Autonomie, TCO 15 ans, Seuil de Rentabilite, IRVE
- Tab 0: `<RangeCorrectionPanel />` — profile selectors (pente/saison/vitesse), corrected range display
- Tab 1: `<TCO15YearChart />` — Recharts stacked area chart (depreciation/maintenance/energy/financing)
- Tab 2: `<BreakevenChart />` — diesel vs electric line chart with km_seuil intersection
- Tab 3: `<IRVESizingWizard />` + `<ChargingScheduleTimeline />`
- API: POST `/api/v1/sotreg/technologies/range-correction`, `/tco-15year`, `/breakeven`, `/charging-optimization`, `/irve-sizing`

#### RangeCorrectionPanel (Component) ✅ Session 98
- 3 profile dropdowns (pente, saison, vitesse) + nominal range input
- Real-time corrected range display with factor cards and reduction bar

#### TCO15YearChart (Component) ✅ Session 98
- Form: purchase price, maintenance, energy/km, annual km, loan rate, duration
- Recharts stacked AreaChart with 4 cost layers over 15 years

#### BreakevenChart (Component) ✅ Session 98
- Form: diesel/electric CAPEX and OPEX/km
- Recharts LineChart with diesel (red) vs electric (blue) + km_seuil ReferenceLine

#### IRVESizingWizard (Component) ✅ Session 98
- 3-step wizard: Fleet params → Charger selection → Cost results
- Charger count, power, cost breakdown cards

#### ChargingScheduleTimeline (Component) ✅ Session 98
- SOC optimization form (battery, current/target SOC, charger power)
- 24h timeline bar with ONEE TOU windows (creuse/pleine/pointe)
- Cost summary: energy cost, peak demand, demand charge

---

### SOTREG — Infrastructure & Stops (Session 101)

#### InfrastructureDashboardPage `/sotreg/infrastructure` ✅ Session 101
- **3 tabs:** Arrets, Depot, Couts IRVE
- Tab 0: `<StopGeneratorPanel />` + `<StopCapacityTable />` stacked
- Tab 1: `<DepotLayoutViewer />`
- Tab 2: `<IRVECostBreakdown />`
- API: POST `/api/v1/sotreg/stops/generate`, `/stops/capacity`, `/depot/cost-estimate`, `/depot/layout-plan`

#### StopGeneratorPanel (Component) ✅ Session 101
- DBSCAN params (eps_m, min_pts) + generate button
- Google Maps display of generated stops with markers and employee counts

#### StopCapacityTable (Component) ✅ Session 101
- HCM 2000 capacity inputs (berths, dwell time, demand)
- Capacity result with color-coded LOS badge (A-F), utilization bar

#### DepotLayoutViewer (Component) ✅ Session 101
- Form: charger count, fleet size, charger type, maintenance toggle
- SVG depot plan with color-coded zones (charging, parking, maintenance)
- Area summary cards

#### IRVECostBreakdown (Component) ✅ Session 101
- Form: charger count, type, contingency slider
- Recharts stacked bar chart with 7 cost components
- Cost component cards grid

### SOTREG — Advanced Finance (Session 108)

#### AdvancedFinanceDashboardPage `/sotreg/finance` ✅ Session 108
- **4 tabs:** VAN & Payback, Portefeuille, CO2, Supernetwork
- Tab 0: `<NPVWaterfallChart />` + `<PaybackTimelineChart />` stacked
- Tab 1: `<EfficientFrontierChart />`
- Tab 2: `<CO2ValorizationPanel />`
- Tab 3: `<SupernetworkFlowDiagram />`

#### NPVWaterfallChart (Component) ✅ Session 108
- Cash flows input + discount rate slider, Recharts waterfall bar chart of present values

#### PaybackTimelineChart (Component) ✅ Session 108
- Cumulative cash flow line chart with zero-crossing ReferenceLine, payback years display

#### CO2ValorizationPanel (Component) ✅ Session 108
- Carbon pricing slider (50-500 MAD/tCO2), motorization selectors, tCO2/MAD output

#### EfficientFrontierChart (Component) ✅ Session 108
- Technology inputs, Recharts scatter with Pareto curve, min-risk/max-return highlights

#### SupernetworkFlowDiagram (Component) ✅ Session 108
- Network link/demand inputs, SVG flow diagram with cost labels, convergence summary

### SOTREG — Roadmap (Session 111)

#### RoadmapDashboardPage `/sotreg/roadmap` ✅ Session 111
- **3 tabs:** Planification, Budget, Jalons
- Tab 0: `<TransitionPlanWizard />` + `<GanttChart />`
- Tab 1: `<BudgetAllocationChart />`
- Tab 2: `<MilestoneTracker />`

#### TransitionPlanWizard (Component) ✅ Session 111
- 3-step wizard: fleet size/budget → scenario type → plan preview

#### GanttChart (Component) ✅ Session 111
- SVG Gantt with phase bars colored by wave (pilot/scale/full)

#### BudgetAllocationChart (Component) ✅ Session 111
- Recharts stacked bars: vehicle_cost + infrastructure_cost per phase

#### MilestoneTracker (Component) ✅ Session 111
- Vertical timeline with year, description, target %, cumulative vehicles

### SOTREG — Scoring & MCDA (Session 114)

#### ScoringDashboardPage `/sotreg/scoring` ✅ Session 114
- **3 tabs:** MCDA, Modal Choice, Reports
- Tab 0: `<MCDAInputForm />` + `<MCDAResultsTable />` + `<RadarComparisonChart />` + `<SensitivitySliders />`
- Tab 1: `<ModalChoicePanel />`
- Tab 2: PDF/Excel download buttons connected to report generation API
- API: POST `/api/v1/sotreg/scoring/mcda`, `/scoring/sensitivity`, `/scoring/modal-choice`, `/scoring/report/pdf/{id}`, `/scoring/report/excel/{id}`

#### MCDAInputForm (Component) ✅ Session 114
- Dynamic alternative management (add/remove rows)
- 6 weight sliders constrained to sum to 1.0 with auto-redistribution on change
- Criteria value inputs per alternative (CAPEX, OPEX, CO2, risk, comfort, maturity)
- CDC default weights button

#### MCDAResultsTable (Component) ✅ Session 114
- Ranked alternatives with horizontal score bars (progress indicators)
- Top-ranked alternative highlighted
- Sortable columns by total score or individual criteria

#### RadarComparisonChart (Component) ✅ Session 114
- Recharts 6-axis radar chart (CAPEX, OPEX, CO2, Risk, Comfort, Maturity)
- Overlapping polygons for selected alternatives with toggleable visibility
- Color-coded legend per alternative

#### SensitivitySliders (Component) ✅ Session 114
- Real-time weight adjustment with instant ranking recomputation
- Visual indicator when ranking reversal occurs (warning badges)
- Reset to CDC default weights button

#### ModalChoicePanel (Component) ✅ Session 114
- Mode attribute inputs (cost, time, comfort per mode)
- McFadden logit probability display as horizontal bars
- Dynamic update on attribute change

### SOTREG — Real-Time Operations (Session 122)

#### OperationsDashboardPage `/sotreg/operations` ✅ Session 122
- **60/40 grid layout:** LiveFleetMap (60%) + side panels (40%)
- **Real-time data** via SocketIO connection with auto-reconnect
- **Zustand store** (`operationsStore`) for real-time state management
- **Sidebar entry:** "Temps Reel" nav item visible to admin, drh, responsable_exploitation roles
- Components: `LiveFleetMap`, `DemandForecastChart`, `DriverRiskHeatmap`, `RouteOptimizationPanel`, `AlertFeed`
- Hook: `useSocketIO` for connection lifecycle and room management

#### LiveFleetMap (Component) ✅ Session 122
- Google Maps with SocketIO-driven vehicle markers
- Glassmorphism overlays for vehicle info popups (speed, heading, ETA, passengers)
- Route polylines for active trips (color-coded by ligne)
- Geofence polygons with enter/exit highlighting
- Animated marker transitions for smooth position updates
- Cluster markers when zoomed out (>50 vehicles in view)

#### DemandForecastChart (Component) ✅ Session 122
- Recharts AreaChart showing 48-hour demand forecast
- Confidence band (upper/lower bounds) as shaded area
- Actual demand overlay when historical data available
- Ligne selector dropdown to switch forecast view
- Ramadan indicator on timeline when applicable

#### DriverRiskHeatmap (Component) ✅ Session 122
- Color-coded driver list sorted by risk score
- Risk category badges: green (low), yellow (medium), orange (high), red (critical)
- Click-to-expand showing risk breakdown by infraction type
- Filter by risk category and ligne assignment

#### RouteOptimizationPanel (Component) ✅ Session 122
- Solver strategy selector: OR-Tools CVRP / Clarke-Wright / Genetic Algorithm
- Parameter inputs per strategy (e.g., GA population size, CW savings threshold)
- Run optimization button with progress indicator
- Before/after comparison metrics (distance, time, cost)

#### AlertFeed (Component) ✅ Session 122
- Scrolling list of real-time alerts from SocketIO
- Alert types: geofence_alert, route_deviation, maintenance, speed
- Severity color coding (info/warning/critical)
- Click-to-locate: centers map on alert vehicle
- Auto-scroll with pause on hover

### SOTREG — ML Operations (Session 123)

#### MLDashboardPage `/sotreg/ml` ✅ Session 123
- **3 tabs:** Models, Features, Retraining
- Tab 0: `<ModelRegistryTable />` + `<ModelMetricsChart />`
- Tab 1: `<FeatureImportanceChart />`
- Tab 2: `<RetrainingPanel />` + `<PredictionMonitor />`
- API: `GET /api/v1/sotreg/ml/models`, `POST /api/v1/sotreg/ml/models/{id}/promote`, `POST /api/v1/sotreg/ml/models/{id}/retire`, `POST /api/v1/sotreg/ml/retrain`, `GET /api/v1/sotreg/ml/retrain/{id}/status`, `GET /api/v1/sotreg/ml/features/{model}`, `GET /api/v1/sotreg/ml/predictions/{model}`

#### ModelRegistryTable (Component) ✅ Session 123
- List all registered ML models (LSTM demand, RandomForest driver risk, IsolationForest maintenance)
- Columns: name, version, status, key metrics
- Status badges: training (blue), ready (amber), promoted (green), retired (gray)
- Promote and retire action buttons per model row

#### ModelMetricsChart (Component) ✅ Session 123
- Recharts LineChart showing metric evolution across model versions
- Supports MAE, RMSE, accuracy, F1 metrics
- Version selector to compare specific versions
- Threshold reference line for acceptable metric range

#### FeatureImportanceChart (Component) ✅ Session 123
- Horizontal BarChart for RandomForest and IsolationForest feature importances
- Sorted descending by importance value
- Color gradient from primary blue (high) to gray (low)
- Model selector to switch between RF and IF features

#### RetrainingPanel (Component) ✅ Session 123
- Trigger retraining button per model type
- Progress indicator with Celery task status polling
- Auto-promote toggle with improvement threshold input
- Retraining history log with timestamps and outcomes

#### PredictionMonitor (Component) ✅ Session 123
- Recharts chart showing predicted vs actual values overlay
- Rolling window selector (24h / 7d / 30d)
- Drift detection indicator when accuracy drops below threshold
- Model-specific views: demand forecast MAE, driver risk accuracy

---

### Reports (Sessions 42-43)

#### ReportListPage `/reports`
- Generated report history table
- Download links
- Filters: type, date, format

#### ReportGeneratorPage `/reports/generate`
- Report type selector (operational, modal, fleet, financial, RSE, HR, sizing)
- Parameter configuration (site scope, date range, format)
- Generate button
- Progress indicator

---

### Settings & Admin (Sessions 04, 29)

#### SettingsPage `/settings` (Session 29)
- Meeting radius slider (range input, meters)
- Max walking distance slider (range input, meters)
- Max route duration slider (range input, seconds)
- Fuel cost per liter input (number)
- Fuel consumption L/100km input (number)
- CO2 kg per liter input (number)
- RTI threshold input (minutes)
- Night mode start/end time inputs
- Min night group size input (number)
- Save button with success/error feedback

#### ConstraintsPage `/settings/constraints` (Session 29)
- Data table: key, value, category, description, is_active status
- Category filter dropdown (duree, accessibilite, budget, saisonnalite, securite, rti, zfe)
- Inline add row with form fields
- Inline edit with save/cancel actions
- Delete action per row
- Bulk import from Excel button

#### UserManagementPage `/admin/users`
- User table (name, email, role, last login, MFA)
- Create/edit/deactivate users
- Role assignment

#### TenantManagementPage `/admin/tenants`
- Tenant list (platform admin only)
- Tenant config (branding, features, data region)

#### SIRHConnectionsPage `/admin/sirh`
- Connection list (provider, status, last sync)
- Add connection wizard
- Test connection button

#### SIRHSyncDashboardPage `/admin/sirh/sync`
- Sync history log
- Conflict resolution queue
- Error details

#### RoleManagementPage `/admin/roles` ✅ Session 115
- 9-role display table (admin, drh, daf, salarie, operateur, responsable_parc, responsable_exploitation, prestataire, conducteur)
- Per-role permissions list and module access matrix
- Role description and system/custom badge
- Note: Sidebar navigation items are now filtered based on the current user's role permissions

#### OperatorManagementPage `/admin/operators`
- Operator list (name, type, status)
- Add/edit operator
- API configuration

---

## Shared Components

### UI Components
- `Button` — Primary, secondary, danger, outline variants
- `Input` — Text, number, date, time, select, textarea
- `Modal` — Confirmation, form, info dialogs
- `DataTable` — Sortable, filterable, paginated table
- `Card` — Info card with title, value, icon
- `Badge` — Status badges (active, inactive, PMR, ZFE)
- `Tabs` — Tab navigation
- `Dropdown` — Select menus
- `FileUpload` — Drag-and-drop file upload
- `Toast` — Success/error/info notifications
- `Skeleton` — Loading states
- `EmptyState` — No data illustrations

### Map Components
- `MapView` — Base Leaflet map wrapper
- `SiteMarker` — Site location marker
- `EmployeeMarker` — Employee location marker (color by site)
- `ClusterRegion` — Cluster boundary polygon
- `RoutePolyline` — Vehicle route line
- `MeetingZone` — Circle radius visualization
- `AccessLeg` — Dashed line (employee -> gathering point)
- `RiskStopMarker` — Risk-scored stop (green/orange/red)
- `ZFEOverlay` — Low emission zone boundary
- `MapLegend` — Toggle-able layer legend

### Chart Components
- `PieChart` — Modal distribution, mode share
- `BarChart` — Occupancy rates, comparisons
- `LineChart` — Trends over time (mobility score, CO2)
- `WaterfallChart` — ROI lever breakdown
- `GaugeChart` — Single metric (RTI compliance, ZFE %)
- `HeatmapTable` — Coverage by site/shift
- `ScatterPlot` — Correlation analysis

---
## Related Documentation
- [[API_ENDPOINTS]] — Backend endpoints these pages consume
- [[MOBILE_PAGES]] — Mobile app screens (Flutter)
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database models behind the pages
- [[ROADMAP]] — Development timeline
- [[PROGRESS]] — Implementation status
