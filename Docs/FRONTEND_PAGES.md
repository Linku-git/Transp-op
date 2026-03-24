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

#### HRDashboard `/dashboard/hr`
- Mobility coverage by site/shift/team (heatmap table)
- Mobility score evolution (line chart over time)
- Absenteeism correlation scatter plot
- Retention impact card (cost of replacement vs mobility cost)
- Shadow zones list + map overlay
- Unaddressed mobility gap alerts

---

### RSE/Environment Dashboard (Session 41)

#### RSEDashboard `/dashboard/rse`
- Private vehicles avoided counter
- CO2 saved (kg) with trend line
- Soft/electric modes share (pie chart)
- ZFE compliance percentage (gauge)
- DPEF report generation button
- Modal shift before/after comparison

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
- Table of saved scenarios
- Create new scenario button
- Delete/duplicate actions

#### ScenarioComparePage `/scenarios/compare`
- Side-by-side comparison (2-3 scenarios)
- Before/after metrics table
- Map toggle between scenarios
- RTI compliance comparison
- Recommendations text

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

#### TCOCalculatorPage `/financial/tco`
- Per-vehicle TCO form
- Fleet-level aggregation
- Motorization comparison table (diesel vs hybrid vs electric vs hydrogen)
- TCO evolution chart over time

#### ROICalculatorPage `/financial/roi`
- Baseline metrics inputs (absence rate, turnover, training cost)
- Target metrics sliders
- ROI waterfall chart (4 levers)
- Payback period display
- DAF export button

#### InvestmentComparatorPage `/financial/comparator`
- Three-column comparison (CAPEX, mise-a-dispo, OPEX)
- Configurable parameters per model
- Duration slider
- Key indicators comparison table
- Recommendation highlight

---

### Content Management (Sessions 67-68, 75)

#### ContentListPage `/content`
- Table: title, type, status, published date, audience, engagement
- Filters: type (news, training, safety, survey), status
- "Create Content" button

#### ContentCreatePage `/content/new`
- Title, body (rich text editor), type selector
- Media upload (video, image, audio)
- Audience targeting (sites, departments, shifts)
- Schedule: publish date, expiry date
- Preview button

#### ContentAnalyticsPage `/content/analytics`
- Engagement overview (views, completions, avg quiz score)
- Content performance ranking
- Training hours recovered metric
- Monetary value estimate

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

#### SettingsPage `/settings`
- Meeting radius slider
- Max walking distance
- Max route duration
- Fuel cost input
- RTI threshold (default 90s)
- Night mode hours
- Min night group size
- Save button

#### ConstraintsPage `/settings/constraints`
- Constraints table (key, value, category)
- Add/edit/delete inline
- Category filter
- Import from Excel button

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
