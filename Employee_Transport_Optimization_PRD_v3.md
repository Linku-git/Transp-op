# Transpop — Plateforme d'Orchestration Mobilite RH

## Product Requirements Document (PRD) — Enhanced v3.0

---

| Field | Value |
|-------|-------|
| Reference | PRD-TRANSPOP-2026-v3.0 |
| Date | March 2026 |
| Version | 3.0 — Full CDC integration |
| Status | En cours de validation |
| Confidentiality | Confidentiel — Usage interne uniquement |

**Change Log v2 → v3:**
- Added Module E (Financial Engineering & Fleet Arbitrage)
- Added Module F (Journey Valorization)
- Added RTI (Real-Time Information) guarantee system
- Added Security module (employee vulnerability scoring, emergency features)
- Added RBAC & multi-tenant access control (5 user profiles)
- Added SIRH integrations (SAP, Workday, Talentsoft, Sage)
- Added transport operator integrations (Via, SWVL, GTFS-RT)
- Added Flutter mobile app specification (iOS + Android)
- Added enterprise integrations (ERP Finance, LMS, internal comms, payment)
- Added vehicle sizing engine with motorization recommendations (diesel, hybrid, electric, hydrogen)
- Added ZFE (Zone a Faibles Emissions) compliance
- Added non-functional requirements (performance, scalability, RGPD, accessibility, i18n)
- Added financial model formulas (TCO, ROI, payback)
- Added vehicle reference catalog
- Added competitive positioning (vs SWVL, Via)
- Expanded data model with 10 table groups
- Expanded API reference with 18 endpoint groups
- Expanded export/reporting with 8 report types

---

# PART I — VISION, CONTEXT & STRATEGY

---

# 1. Product Overview

## 1.1 Vision

Transpop is an **intelligent HR mobility orchestration platform** that goes beyond transport optimization. It is the **decisional brain** that intervenes **before any operational exploitation phase**, providing companies with a fully dimensioned, secured, and financially optimized transport model.

The platform speaks the language of **DRH** (HR Directors), **DAF** (Finance Directors), and **RSE** (CSR) — not just transport operations.

It delivers:

- **Diagnostic & collecte** — Individual employee mobility assessment via mobile questionnaire and SIRH integration
- **Pooling intelligent** — Multi-dimensional clustering crossing geography, shifts, and security constraints
- **Sizing & RTI** — Fleet dimensioning with guaranteed <=90 second wait times at critical stops
- **Financial engineering** — CAPEX/OPEX/TCO/ROI analysis for fleet investment arbitrage
- **Journey valorization** — Transforming commute time into productive learning/communication space
- **Scenario simulation** — Weather, disruption, and demand variation modeling
- **Multi-site optimization** — Per-site clustering, routing, and fleet assignment
- **Operator interfacing** — Standardized sizing plan export to transport operators

The platform comprises three client interfaces:
- **Web Dashboard** (React + TypeScript) — Back-office for DRH, DAF, and Admin users
- **Mobile App** (Flutter — iOS & Android) — Employee-facing app for trip booking, RTI, content, and security
- **Operator Portal** (Web) — Read-only interface for transport operators receiving sizing plans

## 1.2 Competitive Positioning

| Dimension | SWVL | Via | Transpop |
|-----------|------|-----|----------|
| Intervention | During exploitation | During exploitation | **Before exploitation** |
| Optimization unit | Vehicle / Line | Network / TC Agency | **Individual / HR Day** |
| Target model | B2C / B2B / B2G | B2G (90% public) | **B2B private enterprises** |
| HR integration | None | None | **Natively integrated** |
| Financial analysis | None | None | **TCO + ROI + CAPEX/OPEX** |
| RTI stop security | Basic tracking | TC network only | **RTI <= 90s guaranteed** |
| Journey valorization | None | None | **Micro-training + corporate content** |

---

# 2. Problem Statement

Companies providing employee transport face:

### Operational Problems (existing)
- Inefficient routes across multiple sites
- Vehicles not filled to capacity
- High fuel costs and long commute times
- Manual planning using spreadsheets with no optimization tools
- No visibility into employee mobility habits (modal distribution)
- No multi-site coordination for fleet management
- No tracking of existing fleet inventory and utilization
- No adaptability to weather, disruptions, or seasonal demand changes
- No leave/vacation integration (inactive employees still counted in plans)
- No incentive framework for employee-owned car contributions
- Data collection relies on unstructured Excel files without validation

### Strategic Problems (new — from CDC)
- **No financial arbitrage tools** — Fleet decisions made without rigorous CAPEX vs OPEX vs TCO analysis
- **No ROI measurement** — No quantification of transport investment returns (absenteeism, retention, productivity)
- **Zero SIRH integration** — No dynamic link to HR systems for recruitments, turnover, seasonal reinforcements
- **No individual security management** — Employee vulnerability at stops untreated, especially during night/early morning shifts
- **No RTI guarantee** — Employees waiting without precise arrival information, exposed during critical hours
- **Commute time wasted** — Travel time treated as dead cost rather than valorizable asset for training/communication
- **No common language** — Mobility data not translated into DRH, DAF, and RSE decision formats
- **No operator standardization** — No structured way to transmit sizing plans to transport operators

---

# 3. Target Users & Personas

## 3.1 DRH / Responsable Mobilite

- **Role:** Configures mobility policy, validates sizing, manages employees, reviews HR dashboards
- **Primary interface:** Web back-office
- **Key needs:** Diagnostic, simulation, KPIs RH, employee data import, content scheduling
- **Access:** Full platform except financial arbitrage (shared with DAF)

## 3.2 DAF / Controle de Gestion

- **Role:** Financial decision-maker, arbitrates fleet investment, validates ROI
- **Primary interface:** Web back-office (financial modules)
- **Key needs:** TCO calculation, ROI analysis, CAPEX/OPEX comparison, cost-per-trip metrics, ERP export
- **Access:** Financial engineering module, read-only simulation, KPIs

## 3.3 Salarie (Employee)

- **Role:** Uses the transport service daily
- **Primary interface:** Flutter mobile app (iOS + Android)
- **Key needs:** RTI (real-time vehicle arrival), trip booking, security features, embedded content (micro-training), night mode
- **Access:** Personal trips, RTI, content consumption, profile management, security reporting

## 3.4 Operateur Transport

- **Role:** Receives and executes the sizing plan
- **Primary interface:** Web operator portal (read-only)
- **Key needs:** Planning, manifeste, real-time updates, route schedules, passenger counts
- **Access:** Sizing plans, route data, schedules (read-only)

## 3.5 Administrateur Plateforme

- **Role:** Manages accounts, integrations, RBAC, API keys, monitoring
- **Primary interface:** Web admin panel
- **Key needs:** SIRH config, API management, logs, RGPD compliance, tenant management
- **Access:** Full administrative access, no operational features

## 3.6 Transport Study Consultant

- **Role:** Conducts feasibility studies using the platform's diagnostic and simulation tools
- **Primary interface:** Web back-office
- **Key needs:** Multi-site analysis, scenario comparison, export reports
- **Access:** Similar to DRH but scoped to study projects

## 3.7 Target Companies

- Factories and industrial zones
- Call centers and BPO companies
- Large offices and corporate campuses
- Smart city transport operators
- Multi-site enterprises
- Companies with night/early morning shifts (security-critical)

---

# 4. Platform Architecture Overview

## 4.1 Web Dashboard — React + TypeScript

- **Framework:** React 18+ with TypeScript (strict mode)
- **Build tool:** Vite
- **Styling:** TailwindCSS
- **Charts:** Recharts
- **Maps:** Leaflet + react-leaflet (or Mapbox GL JS)
- **State management:** Zustand
- **HTTP client:** Axios or fetch
- **Testing:** Vitest + React Testing Library

**Purpose:** Primary back-office for DRH, DAF, Admin. Operations dashboard, optimization controls, financial analysis, reporting, SIRH configuration.

## 4.2 Mobile App — Flutter (iOS + Android)

- **Framework:** Flutter (Dart)
- **Platforms:** iOS 15+ / Android 10+ (API 29+)
- **Maps:** Google Maps for Flutter or Mapbox
- **Push notifications:** Firebase Cloud Messaging (FCM)
- **Offline storage:** Hive or SQLite
- **Authentication:** Auth0 Flutter SDK or Keycloak adapter
- **Real-time:** WebSocket (Socket.io client) for RTI updates

**Purpose:** Employee-facing app for trip booking, real-time vehicle tracking, push alerts, embedded content (micro-training, corporate news), security features, night mode.

## 4.3 Backend API — Python FastAPI

- **Framework:** Python 3.11+, FastAPI
- **ORM:** SQLAlchemy 2.0 + GeoAlchemy2
- **Database:** PostgreSQL 15+ with PostGIS extension
- **Cache & real-time:** Redis + WebSockets
- **Task queue:** Celery + Redis (async simulation, TCO calculation, pooling)
- **Optimization:** Google OR-Tools, scikit-learn (DBSCAN, KMeans)
- **Excel parsing:** openpyxl
- **Financial calculations:** NumPy, pandas
- **Authentication:** Auth0 / Keycloak integration (JWT + OAuth2)
- **API docs:** OpenAPI 3.0 (Swagger auto-generated)
- **Testing:** pytest with fixtures

## 4.4 External Services & Integrations

| Category | Service | Purpose |
|----------|---------|---------|
| Routing | OSRM (self-hosted or demo) | Route calculation, ETA |
| Routing (production) | HERE Maps / Google Maps API | Real-time traffic-aware routing |
| Geocoding | Nominatim / Google Geocoding | Address-to-GPS conversion |
| Public transit | GTFS-RT feeds (RATP, SNCF) | Real-time transit data |
| Weather | OpenWeatherMap / Meteo-France | 3-day forecast per site |
| Traffic | Google Maps Traffic / TomTom | Real-time congestion data |
| SIRH | SAP SuccessFactors, Workday, Talentsoft, Sage RH | Employee data sync |
| LMS | Cornerstone, 360Learning, TalentLMS | Training catalog/completion sync |
| Internal comms | Workplace by Meta, Microsoft Viva | Content feed for Module F |
| ERP Finance | SAP FI, Sage Comptabilite, Cegid | Financial report export |
| Payment | Stripe | Billing, transport pass management |
| Transport passes | Navigo API, Edenred, Swile | Benefits integration |
| Vehicle TCO data | Manufacturer APIs (Renault, Mercedes, MAN, BYD) | Reference maintenance/depreciation |
| Energy costs | ENEDIS, Total Energies | Fuel prices, EV charging tariffs |
| ZFE data | Local authority APIs | Low emission zone boundaries |
| Push notifications | Firebase Cloud Messaging (FCM) | Mobile push alerts |
| Auth | Auth0 / Keycloak | SSO (SAML/OIDC), MFA |

## 4.5 Infrastructure

- **Containers:** Docker + Docker Compose (dev), Kubernetes (production)
- **CI/CD:** GitHub Actions
- **Monitoring:** Datadog or Grafana + Prometheus
- **Storage:** AWS S3 / GCP Cloud Storage (reports, exports, content assets)
- **Hosting:** European cloud servers (RGPD compliance)
- **Infrastructure as Code:** Terraform

---

# PART II — CORE MODULES (ENHANCED)

---

# 5. Module A — Site Management

### Inputs

- Site code (e.g., S01, S02) — unique identifier
- Site name
- Full address
- City
- GPS coordinates (latitude, longitude)
- Number of shifts (1 to 3)
- Shift entry/exit times (per shift)
- Working days (e.g., Lundi-Vendredi)
- Days per week
- Contact name and phone
- Access/parking notes
- ZFE zone flag (Yes/No — is the site in a low emission zone)
- Security profile (normal / elevated / critical)
- Observations

### Capabilities

- Multi-site CRUD (create, read, update, delete)
- Map-based site location picking
- Per-site shift configuration (up to 3 shifts with entry/exit times)
- Site dashboard showing employee count, fleet assigned, PMR count
- Import from Excel template (SITES sheet)
- ZFE compliance indicator per site (affects vehicle recommendations)
- Site security profile setting (impacts pooling algorithm constraints)

---

# 6. Module B — Employee Data Management

## 6.1 Employee Location & Profile

### Inputs

- Matricule (employee ID code) — unique
- Name (first and last)
- Site assignment (linked to site)
- Shift/Poste (linked to site shifts, e.g., Matin, Apres-midi, Nuit)
- Home address (converted to GPS via geocoding)
- Quartier/Zone (neighborhood)
- City
- Preferred pickup point (address or GPS — optional)
- PMR flag (Personne a Mobilite Reduite — reduced mobility: Yes/No)
- Function/Role (optional)
- Phone number (optional)
- Department (optional)
- Transport required (Yes/No)
- Current transport mode (required at creation; used for baseline analytics)
- Opt-in to company transport (Yes/No/Conditional)
- Has personal car (Yes/No)
- Volunteer as driver and pick up colleagues (Yes/No — optional, only if has personal car)
- Seats available for carpool contribution (optional)

### Capabilities

- Multi-sheet Excel import (EFFECTIF sheet from template)
- Bulk upload via CSV (legacy support)
- Manual entry with inline transport profile
- Map-based editing
- Live updates
- Filter by site, shift, PMR status, quartier, department
- Geocoding from address (Nominatim/Google)
- Soft-delete with active/inactive flag

## 6.2 Employee Availability (Leave/Vacation)

### Inputs

- Leave type (vacation, sick, unpaid, formation, mission, other)
- Start date / end date
- Notes (optional)

### Capabilities

- Create/update/delete leave periods per employee
- Optimization runs accept a target date and automatically exclude employees on leave
- Leave-aware analytics (expected demand by day)
- Import from Excel template (ABSENCES sheet — optional)

## 6.3 SIRH Integration & Dynamic Headcount

### Capabilities

- API REST connectors: SAP SuccessFactors, Workday, Talentsoft, Sage RH
- CSV/XLSX fallback for companies without API-enabled SIRH
- Daily synchronization of employee data (delta updates)
- Conflict resolution for data mismatches
- Dynamic headcount management:
  - Upcoming recruitments (pre-register future employees with start date)
  - Planned departures (auto-deactivate on end date)
  - Seasonal reinforcements (temporary employee pools)
- Sync status dashboard with error/conflict reporting

## 6.4 Employee Security Questionnaire

As part of employee onboarding or periodic review, employees complete a security questionnaire via mobile app:

- Stops or time slots where the employee feels vulnerable
- Zones of perceived isolation
- Specific security constraints (e.g., refusal of certain modes)
- Night/early morning commute concerns
- Maximum acceptable walk distance in low-visibility conditions

This data feeds the Security Module (Section 15) and the pooling algorithm.

---

# 7. Module C — Modal Analysis & Usage Tracking

Track and analyze how employees currently commute to identify modal shift potential.

## 7.1 Per-Employee Modal Data

- Current primary transport mode:
  - Vehicule particulier (private car)
  - Covoiturage (carpooling)
  - Deux-roues motorise (motorcycle)
  - Deux-roues non motorise (bicycle)
  - Transport public (bus, tram, train)
  - Auto-stop / transport informel
  - Navette entreprise (company shuttle)
  - Autre (other)
- Alternative mode (used during rain/disruption)
- Home-to-site distance (km)
- Current travel time (minutes)
- Transport frequency:
  - Quotidien (daily)
  - 3-4 fois/semaine
  - Occasionnel
- Interest in company transport (Oui / Non / Sous conditions)
- Reason for current mode choice
- Departure time from home
- Accepts common pickup point? (Oui / Non)
- Max distance to pickup point (meters)
- Has personal car (boolean)
- Willing to contribute as volunteer driver (boolean)
- Carpool seats available (integer)
- Maximum detour tolerance (minutes or km)
- Bonus eligibility / opt-in (boolean)
- Observations

## 7.2 Analytics & Insights

- **Modal distribution** pie chart (per site and global)
- **Modal shift potential:** count of employees willing to switch to company transport
- **Weather-dependent modal analysis:** how many switch modes when it rains
- **Carpool contribution potential:** seats offered by volunteer drivers vs. demand by route corridor
- **Disruption modal identification:** which modes lose riders under disruption
- **Distance/time distribution** histograms
- **Per-site comparison** of modal patterns
- **Mobility score** per employee, per group (site, team, shift), per time slot
- **Shadow zone identification:** employees with no satisfactory transport solution

## 7.3 Import

- From Excel template (USAGES & MODES sheet)
- Linked to employee by matricule

---

# 8. Module D — Optimization Engine

The core computation engine consolidating clustering, meeting zones, vehicle assignment, route optimization, sizing, RTI, and security constraints.

## 8.1 Clustering Engine

Clusters employees based on:
- Geographic proximity (distance radius, configurable)
- Shift time
- Site assignment (cluster within a site's employees)

### Algorithms

- K-Means
- DBSCAN
- Hierarchical clustering
- Custom distance-based clustering

### Adjustable Parameters

- Meeting radius (200m / 500m / 1km)
- Max walking distance
- Maximum employees per cluster

### Enhancements

- **Per-site clustering** — employees are clustered within their assigned site
- **PMR-aware clustering** — ensure PMR employees are flagged in their cluster for accessible vehicle assignment
- **Security-aware clustering** — integrate security scores into clustering for night shifts (avoid isolated stops, maintain minimum group sizes)

### Output

- Suggested meeting zones (per site)
- Cluster centroid coordinates
- PMR employee count per cluster
- Security risk level per cluster

## 8.2 Meeting Zone Optimization

System calculates:
- Optimal centroid location
- Safe parking area
- Accessible road
- Near main road
- **PMR accessibility** — meeting zones for clusters with PMR employees must be wheelchair-friendly
- **Security assessment** — meeting zones for night shifts must be in well-lit, non-isolated areas
- **Designated gathering point per employee** — each employee is assigned to one meeting zone
- **Employee-to-gathering access leg** — compute the recommended path from each employee location to their gathering point, constrained by max walking distance and safety rules

Future Enhancement:
- Integration with Google Places API for parking areas or bus stops

## 8.3 Vehicle Capacity Assignment

### Inputs — Existing Fleet Inventory

- Vehicle type (e.g., Minibus, Bus, Van)
- Brand/Model (e.g., Toyota Coaster, Mercedes Sprinter)
- Seat capacity
- Year
- Owner/Leaser (proprietaire, loueur, sous-traitant)
- Monthly cost (MAD)
- Monthly km
- Condition (Bon, Moyen, Mauvais)
- Assigned site
- PMR accessible (Yes/No)
- Fuel consumption (L/100km)
- Cost per km
- **Motorization type** (diesel, hybrid, electric, hydrogen, GNV)
- **Vehicle length** (meters — for site access constraint checking)
- **ZFE compliant** (Yes/No)
- Observations

### System Capabilities

- Assign clusters to vehicles (prefer existing fleet)
- Split large clusters
- Merge small clusters
- Minimize empty seats
- Match PMR clusters to PMR-accessible vehicles
- Track fleet utilization (used vs. available vehicles per site)
- Integrate volunteer drivers as supplemental capacity
- **ZFE compliance checking** — flag non-compliant vehicles for ZFE-zone sites

### Optimization Goals

- Minimize number of vehicles
- Maximize occupancy rate
- Reduce total travel distance
- Respect PMR accessibility requirements
- Respect ZFE compliance per site

### Import

- From Excel template (PARC EXISTANT sheet)

### Solvers

- Capacitated Vehicle Routing Problem (CVRP) — Google OR-Tools
- Linear Programming
- Bin-packing with PMR constraints

## 8.4 Route Optimization

For each vehicle:
- Optimal pickup order
- Shortest route to company site
- Traffic-aware routing (optional, via HERE/Google Maps)
- ETA calculation
- Respect max travel duration constraint
- Per-site depot (each site is the destination for its employees)

### Two-Leg Visualization Model

- **Employee -> Gathering point** (dashed line on map, usually walking/short access leg)
- **Gathering point -> Site** (solid line on map, actual vehicle route polyline)

### Volunteer Driver Integration

- Employee-owned car contribution: volunteer drivers pick up colleagues along same corridor
- Configurable detour tolerance and incentive policy

### Routing APIs

- OSRM (development / self-hosted)
- Google Maps API / HERE Maps (production, traffic-aware)
- Mapbox (alternative)

## 8.5 Sizing Engine (NEW — from CDC)

Beyond assigning existing fleet, the sizing engine **recommends the optimal fleet composition** for a given demand profile.

### Vehicle Specification Recommendations

| Type | Capacity | Motorizations | Recommended Use |
|------|----------|---------------|-----------------|
| Minibus | 8-14 seats | Diesel, electric, hybrid | TAD, small dedicated shuttles |
| Midibus | 15-30 seats | Diesel, electric, hydrogen | Medium dedicated shuttles |
| Bus standard | 45-60 seats | Diesel, electric, hydrogen | Fixed lines, high density |
| Grand bus | 80-120 seats | Diesel, GNV (natural gas) | Seasonal peaks, large sites |
| Vehicule leger | 4-8 seats | Electric, thermal | Rural zones, off-peak hours |

### Sizing Criteria

- **Capacity:** Number of seats required per route/cluster
- **Length:** Site access constraints (parking, industrial zones, underground access)
- **Motorization:** RSE/environmental commitments, ZFE compliance, infrastructure availability (charging stations)

### RSE Alignment

- Automatic motorization recommendation integrating company environmental commitments
- ZFE compliance validation for recommended vehicles
- CO2 emission comparison between motorization options

### Mix Recommendation

- Fixed lines (high-density corridors)
- Dedicated shuttles (medium clusters)
- TAD — Transport A la Demande (low-density, on-demand)

### Operator Export

- Standardized sizing plan export to transport operators (Via, SWVL, local operators)
- Format includes: vehicle specs, routes, schedules, passenger counts, PMR requirements

## 8.6 Optimization Model

### Objective Function

Minimize Total Cost =
alpha x Distance
+ beta x Time
+ gamma x Number of Vehicles
+ delta x Fuel Cost
+ epsilon x Incentive Cost (volunteer driver bonuses)
+ zeta x RTI Violation Penalty
+ eta x Security Risk Penalty

Subject to:
- Vehicle capacity constraints
- Maximum walking distance to gathering point
- Shift arrival time constraints
- Route duration limit
- Employee availability (exclude on-leave employees for target date)
- Volunteer driver constraints (opt-in only, seats available, max detour)
- PMR accessibility constraints
- Per-site optimization scope
- Budget constraints (when defined)
- **RTI constraints** (<=90s wait at critical stops)
- **Security constraints** (avoid high-risk stops at night, minimum group sizes)
- **ZFE constraints** (only compliant vehicles for ZFE-zone sites)

### Solvers

- Google OR-Tools (CVRP)
- Pyomo (Linear Programming)
- Genetic Algorithms (complex multi-objective)
- scikit-learn (clustering preprocessing)

## 8.7 RTI-Aware Sizing (NEW — from CDC)

The sizing algorithm integrates the RTI guarantee as a constraint:

- **Target:** Vehicle arrives within 90 seconds of the employee reaching the designated stop
- **Risk stop identification:** Stops scored by isolation level, lighting, public transit frequency
- **Adaptive sizing:** In degraded mode (vehicle breakdown, traffic surge), buffer vehicles are allocated to maintain RTI compliance
- **Measurement:** RTI compliance logged per stop, per trip, per day for KPI reporting
- **Recomposition:** Automatic pool recomposition when employee absences or shift modifications occur

## 8.8 Security-Constrained Pooling (NEW — from CDC)

The pooling algorithm crosses three dimensions (beyond simple geographic proximity):

| Dimension | Variables Analyzed | Objective |
|-----------|-------------------|-----------|
| Geographic proximity | Home addresses, distance to stop, walk time | Create optimized pickup hubs |
| Shift compatibility | Time windows, overlaps, wait tolerance | Maximize fill rate |
| Security criteria | Night hours, vulnerable zones, at-risk profiles | Respect RTI <= 90s |

- Security scores feed into the clustering algorithm as weighted constraints
- Night-hour shifts trigger stricter pooling rules (no isolated stops, larger group minimums)
- Iterative optimization: algorithm simultaneously maximizes fill rate and respects RTI/security constraints
- Automatic recomposition of pools when absences or shift changes occur

---

# 9. Planning Parameters & Constraints

## 9.1 Planning Parameters (Admin can modify)

- Meeting radius
- Vehicle capacity limits
- Maximum walking distance
- Maximum route duration
- Fuel cost per km
- Time penalty weight
- **RTI threshold** (default: 90 seconds)
- **Night hour definition** (default: 20h00-06h30)
- **Minimum group size for night stops** (default: 3)

## 9.2 Operational Constraints (from Excel CONTRAINTES sheet)

- Maximum travel duration acceptable (minutes)
- Working days concerned
- Seasonal variations / known peaks
- Accessibility requirements (PMR)
- Security requirements
- Budget limits
- ZFE compliance requirements
- Custom constraint key-value pairs

### Import

- From Excel template (CONTRAINTES sheet)

Recalculation triggered via: "Recalculate Optimization" button

---

# 10. Excel Data Import (Multi-Sheet Template)

System supports importing a structured Excel template (`.xlsx`) with the following sheets:

| Sheet | Target | Description |
|-------|--------|-------------|
| SITES | Site table | Company sites with shifts, GPS, contacts |
| EFFECTIF | Employee table | Employees with expanded fields |
| USAGES & MODES | EmployeeModal table | Mobility behavior per employee |
| CONTRAINTES | Constraint table | System constraints and parameters |
| PARC EXISTANT | Vehicle table | Existing fleet inventory |
| ABSENCES (optional) | EmployeeLeave table | Leave/vacation periods |
| SYNTHESE | Read-only | Auto-calculated summary (not imported) |

### Features

- Upload single `.xlsx` file
- Parse each sheet with correct header row offsets (rows 2-3)
- Validation per sheet with detailed error reporting (row number, column, error)
- Preview data per sheet before import
- Incremental import (update existing records by code/matricule, add new)
- Required vs. optional field enforcement (columns marked `*` vs `(o)`)
- Support for GPS coordinates from Google Maps format

---

# 11. Scenario Simulation & Conditions

## 11.1 Standard Scenarios

Admin can simulate:
- Increased meeting radius
- Larger buses
- Shift splitting
- Fuel price increase

## 11.2 Weather/Disruption Scenarios (from CDC)

| Scenario | Description | Typical Impact |
|----------|-------------|----------------|
| Jour Normal | Standard load, optimized modal mix | Baseline |
| Meteo Degradee | Rain/bad weather, VP->TC/shuttle modal shift | +20-30% demand |
| Defaillance Reseau TC | Public transit failure, automatic modal shift | +40-60% demand |
| Pic d'effectif | Seasonal recruitment, reinforcements | +15-25% headcount |
| Horaires Decales / Nuit | Security focus, 4h30-6h30 and 20h-23h | Security constraints active |
| Greve TC | Transport strike, TAD activation, dedicated shuttles | +50-80% demand |

### Capabilities

- Set current condition (normal, pluie, greve transport, pic activite)
- Adjust demand multiplier per condition
- Re-run optimization with adjusted parameters
- Compare normal vs. disruption scenarios side-by-side
- **Multi-scenario simultaneous simulation:** compare up to 3 scenarios side-by-side
- **RTI degraded mode testing:** verify RTI compliance holds under each scenario
- **ZFE compliance check:** verify recommended vehicles comply under each scenario

## 11.3 Weather API (Forecast)

- Fetch forecast for the next 3 days (daily) for each site location (lat/lng)
- Store forecast snapshots (per day) for reproducibility
- Display 3-day forecast widget on dashboard and optimization page
- One-click scenario suggestions (e.g., upcoming rain day -> create "rain" scenario with pre-filled multipliers)

### System Outputs

- Comparison table
- Before/after metrics
- Condition-specific recommendations
- RTI compliance status per scenario

---

# PART III — NEW MODULES (CDC SCOPE)

---

# 12. Module E — Financial Engineering & Fleet Arbitrage

This module is the most distinctive feature vs. existing market solutions. It transforms the platform into a **financial decision-support tool** for DAF and DRH.

## 12.1 Investment Model Comparator (E1)

Three investment models can be simulated and compared over a configurable duration:

| Model | Description | Key Indicators |
|-------|-------------|---------------|
| **CAPEX — Flotte propre** | Company buys its own vehicles (full control, capital immobilization) | TCO over 5 years, cost/km, depreciation, maintenance cost, residual value |
| **Mise a disposition** | Company invests in vehicles managed by the platform operator | Shared TCO, economies of scale, redeployment flexibility |
| **OPEX — Externalisation totale** | Full outsourcing to operators (Via, SWVL, TAD) — no capital investment | Cost per trip, monthly recurring cost, max flexibility, supplier dependency |

### Capabilities

- Side-by-side comparison table with configurable parameters
- Duration slider (1-10 years)
- Fleet size and utilization rate inputs
- Sensitivity analysis (what-if sliders for fuel price, headcount, fill rate)

## 12.2 TCO Calculator (E2)

Total Cost of Ownership calculation per vehicle and per fleet:

- **Acquisition cost** — purchase price or lease cost (by motorization: electric, hydrogen, thermal)
- **Exploitation cost** — fuel/energy, maintenance, insurance, tires
- **Infrastructure cost** — charging stations, depot, preventive maintenance facilities
- **Management cost** — drivers, dispatching, fleet management software
- **Residual value** — vehicle value at end of period (impacts net TCO)

### Formulas

```
TCO_vehicle = Purchase + (Annual_Maintenance x Duration) + (Energy_Cost_per_km x Annual_km x Duration) - Residual_Value
TCO_fleet = SUM(TCO_vehicle) + Infrastructure_Cost + Management_Cost
```

### Capabilities

- Per-vehicle TCO breakdown
- Fleet-level TCO aggregation
- Automatic comparison: TCO own fleet vs. OPEX cost for same transport volume
- Motorization comparison (diesel vs. hybrid vs. electric vs. hydrogen)

## 12.3 Real Cost per Trip per Employee (E3)

Granular cost calculation:

- **Cost per available seat:** Total cost / (number of seats x number of annual trips)
- **Cost per occupied seat:** Total cost / (number of seats x fill rate x number of annual trips)
- **Annual cost per transported employee:** benchmark indicator for inter-company comparison
- **Breakeven point:** minimum number of employees to transport for the solution to be cheaper than individual kilometric allowance

### Example Calculation

A 50-seat bus at 120,000 EUR (TCO 5 years) costs 2,400 EUR/seat over 5 years. With 70% fill rate, the real cost per occupied seat is 3,428 EUR, which is less than 1 EUR per trip over 250 working days. This is the quantified argument the platform provides to the DAF.

## 12.4 ROI Calculator (E4)

Return on investment built on four measurable levers:

| ROI Lever | Mechanism | Data Source | Estimated Impact |
|-----------|-----------|-------------|-----------------|
| Absenteeism reduction | Fewer delays/absences from transport failures | DRH (transport absence rate) | -15 to -30% transport absenteeism |
| Talent retention | Secure mobility = competitive advantage in recruitment | RH (recruitment + onboarding cost) | -10 to -20% targeted turnover |
| Fleet optimization | Pooling reduces number of vehicles needed | Module D (fill rate) | +20 to +40% fill rate |
| Journey productivity | Travel time valorized (training, internal comms) | Module F (app engagement rate) | N minutes/day recovered |

### Formulas

```
ROI_absenteeism = (Absence_Rate_Before - After) x Headcount x Daily_Cost
ROI_retention = Avoided_Turnover x Replacement_Cost (6-9 months salary)
ROI_journey = Travel_Hours x Engagement_Rate x Internal_Training_Hour_Cost
Payback_Period = Total_Investment / Annual_Net_Gain (all ROI levers)
```

### Capabilities

- **Dashboard ROI:** automatic synthesis of global ROI, presentable to executive committee
- **Payback simulation:** estimated duration before full return on investment
- **DAF export report:** standardized financial presentation for annual budget arbitrage
- Configurable baseline metrics (current absence rate, turnover rate, training hour cost)

## 12.5 Financial Dashboard

- TCO evolution chart over time (line chart, per model)
- ROI waterfall chart (contribution of each lever)
- Payback period slider (interactive)
- Investment comparator side-by-side cards
- Cost per trip gauge (actual vs. target)
- Export to ERP-compatible format (SAP FI, Sage, Cegid)

## 12.6 Data Model

### FinancialScenario Table

- id
- name
- investment_model (capex / mise_a_disposition / opex)
- duration_years
- fleet_composition (JSON — vehicle types and quantities)
- params (JSON — fuel price, maintenance costs, etc.)
- results (JSON — TCO, cost/seat, cost/trip, ROI)
- created_by (FK -> User)
- created_at

### TCOEntry Table

- id
- financial_scenario_id (FK)
- vehicle_type
- motorization
- quantity
- purchase_price
- annual_maintenance_cost
- energy_cost_per_km
- annual_km
- residual_value
- infrastructure_cost
- tco_per_vehicle
- tco_total

### ROICalculation Table

- id
- financial_scenario_id (FK)
- baseline_absence_rate
- target_absence_rate
- headcount
- daily_cost
- replacement_cost
- turnover_rate_before
- turnover_rate_after
- training_hour_cost
- engagement_rate
- annual_travel_hours
- roi_absenteeism
- roi_retention
- roi_journey
- roi_fleet_optimization
- roi_total
- payback_months

### VehicleReference Table

- id
- type (minibus, midibus, bus_standard, grand_bus, vehicule_leger)
- capacity_min, capacity_max
- motorizations_available (JSON array)
- recommended_use
- reference_tco_5y (per motorization)
- length_meters
- zfe_compliant (boolean)

---

# 13. Module F — Journey Valorization

The commute must no longer be considered dead time. The platform transforms the mobility network into a space for **internal communication and skill development**.

## 13.1 Embedded Content Delivery (F1)

Content types delivered via the Flutter mobile app during commute:

- **Corporate news** — company announcements, HR updates, team news
- **Safety reminders** — procedures, mandatory training renewals, safety consigns
- **Micro-training modules** (5-10 minutes) — videos, quizzes, podcasts
- **Surveys and polls** — internal employee satisfaction, feedback collection
- **Targeted notifications** — per site, per team, per role profile

### Content Management (Web — DRH/Admin)

- Content creation interface (title, body, media attachments, target audience)
- Scheduling (publish date, expiry date)
- Audience targeting (by site, department, shift, role)
- Content categories (news, training, safety, survey)
- Analytics dashboard (views, completions, engagement)

## 13.2 Value Measurement (F2)

- **Engagement rate** on delivered content (views, completions, quiz scores)
- **Training time recovered:** calculation in annual hours per employee
- **LMS integration:** synchronize completed modules with employee training records
- **Monetary value estimate:** training hours x engagement rate x internal training hour cost

### Key Metric

A 40-minute round-trip commute, 5 days/week = **173 annual hours** of potentially valorizable time. Even at 20% engagement, that represents **34 hours** of training or internal communication at zero additional cost.

## 13.3 Content Integrations

- **LMS:** Cornerstone, 360Learning, TalentLMS — training catalog sync, completion tracking
- **Internal comms:** Workplace by Meta, Microsoft Viva — content feed integration
- **CMS headless:** content creation and distribution management

## 13.4 Data Model

### Content Table

- id
- title
- body (rich text / markdown)
- content_type (news, training, safety, survey)
- media_url (optional — video, podcast, image)
- target_sites (JSON array of site_ids, null = all)
- target_departments (JSON array, null = all)
- target_shifts (JSON array, null = all)
- published_at
- expires_at
- created_by (FK -> User)
- is_active (boolean)

### ContentDelivery Table

- id
- content_id (FK -> Content)
- employee_id (FK -> Employee)
- delivered_at
- viewed_at (nullable)
- completed_at (nullable)
- quiz_score (nullable, percentage)
- time_spent_seconds

### TrainingModule Table

- id
- content_id (FK -> Content)
- lms_external_id (for LMS sync)
- duration_minutes
- is_mandatory (boolean)
- certification_name (optional)

### Survey Table

- id
- content_id (FK -> Content)
- questions (JSON array)
- response_count
- is_anonymous (boolean)

### SurveyResponse Table

- id
- survey_id (FK -> Survey)
- employee_id (FK -> Employee, nullable if anonymous)
- responses (JSON)
- submitted_at

---

# 14. RTI (Real-Time Information) Guarantee

The RTI guarantee is a **sizing output, not an app feature**. It is because the sizing was calculated integrating the wait constraint that the promise of <=90 seconds is contractually tenable.

## 14.1 RTI Guarantee Definition

- **Target:** Employee waits no more than 90 seconds at their designated stop after arriving at the scheduled time
- **Scope:** All stops identified as "critical" (based on risk score)
- **Measurement:** RTI compliance percentage = trips where wait <=90s / total trips
- **SLA target:** 95% compliance rate

## 14.2 Risk Stop Identification

Stops are scored on multiple criteria:

- **Isolation level:** Distance from nearest populated area / public transit
- **Lighting:** Available street lighting (data from OpenStreetMap or manual assessment)
- **Public transit frequency:** Nearby TC stops with >15min headways = higher risk
- **Time of day:** Night/early morning (20h-6h30) elevates risk score
- **Employee security questionnaire responses:** subjective vulnerability perception

### Risk Score

```
Risk_Score = w1 x Isolation + w2 x (1 - Lighting) + w3 x (1 - TC_Frequency) + w4 x Night_Flag + w5 x Employee_Perception
```

Stops with Risk_Score above threshold are flagged as "critical" and receive RTI guarantee priority.

## 14.3 Adaptive Sizing

- The sizing algorithm allocates buffer vehicles to maintain RTI compliance even in degraded mode (breakdown, traffic)
- Dynamic recomposition of pools when employees are absent or shifts change
- Fallback protocol: if RTI cannot be maintained, the system triggers a TAD (Transport A la Demande) request

## 14.4 Mobile RTI Display

- Real-time vehicle arrival countdown (updated every <=10 seconds)
- Colored indicator:
  - **Green:** Vehicle arriving on time (<=90s)
  - **Orange:** Slight delay (90-180s)
  - **Red:** Significant delay (>180s)
- Push alert D-2 minutes before vehicle arrival
- Interactive map showing approaching vehicle position and driver identification
- Booking status with modification/cancellation (up to 30 minutes before departure)

## 14.5 Data Model

### StopRiskScore Table

- id
- site_id (FK -> Site)
- location_lat, location_lng
- stop_name
- isolation_score (0-1)
- lighting_score (0-1)
- tc_frequency_score (0-1)
- night_risk_multiplier
- employee_perception_avg (0-1)
- composite_risk_score (0-1)
- is_critical (boolean)
- last_assessed_at

### VehiclePosition Table

- id
- vehicle_id (FK -> Vehicle)
- route_id (FK -> Route)
- lat, lng
- heading
- speed_kph
- timestamp
- next_stop_eta_seconds

### RTIEvent Table

- id
- stop_id (FK -> StopRiskScore)
- route_id (FK -> Route)
- scheduled_arrival
- actual_arrival
- wait_time_seconds
- compliant (boolean — <=90s)
- date

### RTIConfig Table

- id
- site_id (FK -> Site)
- max_wait_seconds (default: 90)
- compliance_target_pct (default: 95)
- buffer_vehicle_count
- night_mode_start, night_mode_end

---

# 15. Security Module

## 15.1 Security Questionnaire

Employee-facing questionnaire (via Flutter mobile app) collecting:

- Stops or time slots where the employee feels vulnerable
- Perceived isolation zones (map-based pin selection)
- Specific constraints (refusal of certain modes, preference for group pickup)
- Night/early morning commute concerns
- Rating of perceived safety at currently assigned stop (1-5 scale)

### Questionnaire Schedule

- Initial onboarding questionnaire (mandatory)
- Periodic reassessment (configurable: quarterly, semi-annual, annual)
- Triggered reassessment after security incident

## 15.2 Security Scoring

- **Per employee:** Individual security risk profile based on questionnaire responses + commute pattern
- **Per group:** Aggregated security profile for site, team, shift
- **Per time slot:** Security heat map by hour of day
- **Night mode stop identification:** Stops flagged as high-risk during 20h-6h30

### Site Security Dashboard (Web)

- Security score distribution chart
- Map overlay showing risk-scored stops
- Night shift coverage indicator
- Incident history timeline

## 15.3 Security Constraints in Optimization

Security scores are integrated into the pooling and routing algorithms:

- High-risk stops avoided during night hours (if alternative exists within walking distance)
- Minimum group size for night shift stops (configurable, default: 3 employees)
- Priority vehicle assignment for night-shift routes (shorter wait times)
- PMR employees at night-shift stops receive priority RTI guarantee

## 15.4 Emergency Features (Mobile App)

- **Discrete emergency button** — visible only during night hours (configurable), one-tap activation
- **Alert routing:** Emergency alert sent to:
  - Site security contact
  - Platform admin
  - Local emergency services (configurable)
- **Location sharing:** Employee's real-time GPS position shared with responders
- **Incident logging:** All emergency activations logged for audit and pattern analysis

## 15.5 Data Model

### SecurityQuestionnaire Table

- id
- employee_id (FK -> Employee)
- submitted_at
- questionnaire_version
- overall_safety_rating (1-5)
- responses (JSON — structured answers)
- vulnerable_stops (JSON array of {lat, lng, description})
- night_concerns (text)

### SecurityScore Table

- id
- employee_id (FK -> Employee)
- score (0-100, higher = safer perception)
- risk_level (low / medium / high / critical)
- last_calculated_at
- contributing_factors (JSON)

### EmergencyAlert Table

- id
- employee_id (FK -> Employee)
- triggered_at
- location_lat, location_lng
- alert_type (emergency_button, system_trigger)
- responders_notified (JSON array)
- resolved_at (nullable)
- resolution_notes (text, nullable)

---

# 16. RBAC & Multi-Tenant Access Control

## 16.1 User Profiles & Permissions Matrix

| Feature | DRH | DAF | Salarie | Operateur | Admin |
|---------|-----|-----|---------|-----------|-------|
| Import employee data | Write | - | - | - | Write |
| Launch simulation | Write | Read | - | - | Write |
| Financial engineering (TCO/ROI) | Write | Write | - | - | Read |
| View sizing plan | Write | Write | - | Read | Write |
| Book a trip | Write | - | Write | - | - |
| RTI real-time access | Supervise | - | Write | Read | Supervise |
| HR KPIs | Write | Read | - | - | Read |
| RSE KPIs | Write | Read | - | - | Read |
| Embedded content (publish) | Write | - | - | - | Write |
| Embedded content (consume) | - | - | Read | - | - |
| Security alerts (receive) | Receive | - | Emit | Receive | Receive |
| User management | - | - | - | - | Write |
| Tenant configuration | - | - | - | - | Write |
| API key management | - | - | - | - | Write |
| SIRH integration config | Write | - | - | - | Write |
| Export reports | Write | Write | - | Read | Write |

## 16.2 Authentication

- **SSO integration:** Auth0 or Keycloak
- **Protocols:** SAML 2.0 and OIDC
- **MFA:** Mandatory for DRH, DAF, and Admin profiles
- **JWT tokens:** Short-lived access tokens + refresh tokens
- **Session management:** Redis-backed session store
- **Password policy:** Min 12 chars, complexity requirements, rotation every 90 days

## 16.3 Multi-Tenant Architecture

- **Tenant isolation:** Complete data separation per company/organization
- **Tenant-level configuration:** Custom branding, default parameters, feature toggles
- **Tenant admin:** Can manage users, roles, and settings within their tenant
- **Cross-tenant analytics:** Platform-level admin can view aggregated anonymized metrics
- **Data residency:** Per-tenant data location configuration (RGPD compliance)

## 16.4 Data Model

### Tenant Table

- id
- name
- code (unique slug)
- config (JSON — branding, defaults, feature flags)
- data_region (eu-west, eu-central)
- is_active
- created_at

### User Table

- id
- tenant_id (FK -> Tenant)
- email (unique within tenant)
- password_hash
- first_name, last_name
- role_id (FK -> Role)
- employee_id (FK -> Employee, nullable — for Salarie role linking)
- mfa_enabled (boolean)
- mfa_secret (encrypted)
- last_login_at
- is_active

### Role Table

- id
- tenant_id (FK -> Tenant)
- name (drh, daf, salarie, operateur, admin)
- permissions (JSON array or FK to Permission table)
- is_system_role (boolean — cannot be deleted)

### Permission Table

- id
- resource (sites, employees, optimization, financial, content, security, admin)
- action (read, write, delete, supervise, emit)

### RolePermission Table

- id
- role_id (FK -> Role)
- permission_id (FK -> Permission)

---

# PART IV — VISUALIZATION & REPORTING

---

# 17. Web Dashboard (React + TypeScript)

## 17.1 Interactive Map (Leaflet / Mapbox)

- Employee points (color-coded by site)
- Clusters with centroid markers
- Meeting zones with radius visualization
- Vehicle routes with polyline rendering
- Company site locations (multiple markers)
- PMR employee indicators (icon badge)
- **Dashed access legs:** employee -> designated gathering point
- **Solid main legs:** gathering point -> site route polyline (per vehicle)
- **Risk stop overlay:** stops color-coded by risk score (green/orange/red)
- **ZFE zone overlay:** low emission zone boundaries on map
- Legend + toggles (show/hide layers: access legs, routes, risk stops, ZFE zones, per-vehicle selection)

## 17.2 Operations Analytics Panel

- Total vehicles used
- Average occupancy rate
- Total distance
- Estimated fuel cost
- CO2 emission estimate
- Time saved
- Modal distribution chart (pie chart per site)
- Per-site breakdown (summary table)
- PMR stats (PMR employees served, accessible vehicles used)
- Fleet utilization (vehicles used / available per site)

## 17.3 HR Dashboard (NEW — D1 from CDC)

- **Mobility coverage** by site, shift, team, and time slot
- **Mobility score evolution** over time (line chart)
- **Absenteeism correlation** — statistical model correlating transport problems with absence rates
- **Retention impact** — estimated cost of replacement vs. cost of mobility solution
- **Shadow zones** — employees without satisfactory transport solution (map + list)
- Alerts on unaddressed mobility gaps

## 17.4 RSE / Environment Dashboard (NEW — D2 from CDC)

- **Private vehicle reduction:** number of individual cars avoided, equivalent CO2 saved
- **Soft/electric modes share** in recommended modal mix
- **DPEF report generation** — automated Declaration de Performance Extra-Financiere
- **ZFE compliance status** — percentage of recommended fleet that is ZFE-compliant
- CO2 emission trends over time

## 17.5 Financial Dashboard (NEW — from Module E)

- TCO comparison cards (CAPEX vs. mise a dispo vs. OPEX)
- ROI waterfall chart
- Payback period interactive slider
- Cost per trip gauge
- Investment model comparison table
- Export button to ERP format

## 17.6 RTI Monitoring Dashboard (NEW)

- Live RTI compliance percentage (gauge)
- Stop wait time heat map
- Risk stop map overlay with real-time vehicle positions
- RTI violation alerts
- Historical compliance trends

## 17.7 Weather Widget

- 3-day forecast per site
- Condition icons with scenario suggestion buttons
- One-click "create rain scenario" from forecast

---

# 18. Mobile App — Flutter (iOS + Android)

## 18.1 Authentication & Onboarding

- Login via SSO (Auth0/Keycloak OIDC)
- First-time onboarding wizard:
  - Transport preferences setup
  - Security questionnaire
  - Notification permissions
  - Location permissions (active-only, never background)
- Profile management (update preferences, modes, constraints)

## 18.2 Home Screen

- **Next departure** — large, central, readable at night
- **Time remaining** countdown with colored indicator (green/orange/red)
- **Quick actions:** Book trip, View map, Emergency button (night only)
- **Content carousel** — latest corporate news / micro-training

## 18.3 Trip Management

- **Booking:** Select date, shift, preferred pickup point
- **Modification:** Change pickup point or time (up to 30 min before departure)
- **Cancellation:** Cancel booking (up to 30 min before departure)
- **Trip history:** Past trips with details (route, duration, CO2 saved)
- **Statistics:** Monthly/annual CO2 savings, trips taken, training completed

## 18.4 Real-Time Tracking (RTI)

- Interactive map showing approaching vehicle in real-time
- Vehicle position updated every <=10 seconds
- Driver identification for dedicated shuttles
- ETA display with colored indicator:
  - Green: On time (<=90s)
  - Orange: Slight delay (90-180s)
  - Red: Significant delay (>180s)
- Route polyline showing vehicle path to pickup point
- Two-leg visualization:
  - Dashed line: employee walking to gathering point
  - Solid line: vehicle route to site

## 18.5 Push Notifications

- **D-2 minutes alert:** Vehicle arriving in 2 minutes
- **Route changes:** Real-time notification of route modifications
- **Weather-triggered scenarios:** Alert when weather changes affect transport
- **Content notifications:** New training module or corporate news available
- **Security alerts:** Emergency response confirmation

## 18.6 Embedded Content (Module F)

- Corporate news feed (scrollable cards)
- Micro-training player (video, audio, quiz)
- Survey / poll interface
- Progress tracking (completed modules, quiz scores)
- Training certificates (from LMS integration)
- Content available offline (pre-downloaded)

## 18.7 Night Mode

- **Automatic activation** based on time (configurable) or manual toggle
- Dark UI theme with high contrast
- Maximum readability for outdoor use
- Low battery consumption optimization
- Emergency button prominently visible

## 18.8 Security Features

- **Discrete emergency button** — visible during night hours, one-tap activation
- Link to local emergency services
- **Security questionnaire** — accessible from profile
- **Incident reporting** — report safety concerns at stops
- Location sharing with responders during emergency

## 18.9 Profile & Preferences

- Transport mode preferences
- Maximum walking distance setting
- Notification preferences (granular control)
- Language preference (FR / EN)
- Volunteer driver toggle (if has personal car)
- Carpool seats available
- PMR flag
- Opt-in/out of company transport

## 18.10 Offline Mode

- Last booked trip details cached locally
- Downloaded content (training modules, news) available offline
- Offline trip info: pickup point, time, vehicle info, gathering point map
- Auto-sync when connectivity restored

## 18.11 Technical Requirements

- iOS 15+ (iPhone 8 and above)
- Android 10+ (API 29+)
- Cold start: < 3 seconds on 4G network
- Geolocation: active mode only (never background collection)
- WCAG 2.1 AA accessibility
- Screen reader support (VoiceOver / TalkBack)
- Adjustable text size

---

# 19. Export & Reporting

## 19.1 Operational Exports (existing)

- **PDF driver sheets** — per site, per route, with PMR indicators
- **Excel cluster list** — with per-site sheets
- **CSV stop order** — ordered stops with PMR data
- **GeoJSON route export** — FeatureCollection for GIS tools

## 19.2 Modal Analysis Report

- PDF/Excel with modal distribution charts
- Shift potential analysis
- Weather impact assessment
- Per-site modal comparison

## 19.3 Fleet Utilization Report

- Vehicle usage per site
- Condition status distribution
- PMR vehicle coverage
- Utilization rate trends

## 19.4 Volunteer Driver / Bonus Report

- Eligible trips per driver
- Passengers picked up
- Compensation totals
- Detour analysis

## 19.5 Financial Reports (NEW — Module E)

- **TCO report** — per-vehicle and fleet-level TCO breakdown
- **ROI report** — four-lever ROI analysis with payback timeline
- **Investment comparator export** — CAPEX/mise-a-dispo/OPEX side-by-side
- **DAF export** — ERP-compatible format (SAP FI, Sage, Cegid)

## 19.6 RSE / DPEF Report (NEW)

- Automated DPEF-compliant environmental report
- CO2 emission reduction metrics
- Modal shift data
- ZFE compliance status
- Soft/electric modes share

## 19.7 Sizing Plan Export to Operators (NEW)

- Standardized format for transport operators
- Vehicle specifications (type, capacity, motorization, PMR)
- Route details (stops, schedule, passenger counts)
- Service requirements (frequency, RTI targets)

## 19.8 HR Mobility Report (NEW)

- Per-site mobility coverage
- Mobility score evolution
- Absenteeism / retention correlation data
- Shadow zone identification
- Employee satisfaction trends (from surveys)

---

# PART V — INTEGRATIONS

---

# 20. Routing & Geocoding APIs

## 20.1 OSRM (OpenStreetMap Routing Machine)

- Primary routing engine for development and self-hosted deployment
- Route calculation, distance, duration, polyline encoding
- Free, no API key required

## 20.2 HERE Maps / Google Maps Platform

- Production routing with real-time traffic awareness
- Traffic-aware ETA calculation for RTI system
- Matrix routing for multi-stop optimization

## 20.3 Nominatim / Google Geocoding

- Address-to-GPS coordinate conversion
- Reverse geocoding for map-based location picking
- Batch geocoding for CSV/Excel imports

## 20.4 GTFS-RT (General Transit Feed Specification — Realtime)

- Public transit real-time data feeds (RATP, SNCF, Open Data)
- Used for modal analysis (public transit availability scoring)
- Risk stop assessment (nearby TC frequency data)

---

# 21. SIRH Integrations

## 21.1 Supported Systems

| SIRH | Protocol | Authentication | Data |
|------|----------|----------------|------|
| SAP SuccessFactors | REST API | OAuth 2.0 | Employees, sites, departments, shifts |
| Workday | REST API | OAuth 2.0 | Employees, positions, schedules |
| Talentsoft | REST API | API Key | Employees, training records |
| Sage RH | REST API | API Key | Employees, payroll data |

## 21.2 CSV/XLSX Fallback

For companies without API-enabled SIRH:
- CSV import with configurable column mapping
- XLSX import via the standard Excel template
- Manual data entry via web forms

## 21.3 Sync Protocol

- **Frequency:** Daily synchronization (configurable schedule)
- **Method:** Delta updates (only changed records)
- **Conflict resolution:** Configurable strategy (SIRH wins, platform wins, manual review)
- **Dynamic headcount management:**
  - Upcoming recruitments (pre-register with start date)
  - Planned departures (auto-deactivate on end date)
  - Seasonal reinforcements (temporary pools with expiry)
- **Sync dashboard:** Status, error log, conflict queue

---

# 22. Transport Operator Integrations

## 22.1 Via Transportation API

- Integration with ViaViewer, Remix, and microtransit modules
- Sizing plan transmission in Via-compatible format
- Schedule and capacity data exchange

## 22.2 SWVL API

- B2B fleet management integration
- Route and capacity data exchange
- Booking synchronization (future)

## 22.3 GTFS-RT for Public Transit

- Real-time feeds from public transit networks
- Used for multi-modal analysis and fallback routing
- Disruption detection (service alerts)

## 22.4 Standardized Sizing Plan Export

- Platform-agnostic format (JSON/XML) for any operator
- Includes: vehicle specs, routes, schedules, passenger counts, PMR requirements, RTI targets
- Versioned exports with change tracking

---

# 23. External Data Integrations

## 23.1 Weather API

- **Provider:** OpenWeatherMap or Meteo-France
- **Data:** 3-day daily forecast per site (condition, precipitation, temperature, wind)
- **Usage:** Scenario simulation triggers, demand multiplier suggestions
- **Storage:** Forecast snapshots stored locally for reproducibility

## 23.2 Traffic API

- **Provider:** Google Maps Traffic API or TomTom
- **Data:** Real-time congestion data for route optimization
- **Usage:** Traffic-aware ETA for RTI, route duration adjustment

## 23.3 ZFE Data

- **Source:** Local authority APIs / Open Data
- **Data:** Zone boundaries, vehicle restriction rules
- **Usage:** Vehicle recommendation compliance checking

## 23.4 Energy Cost APIs

- **Fuel prices:** Real-time diesel/petrol prices for TCO calculations
- **EV charging tariffs:** ENEDIS, Total Energies tariff data
- **Usage:** Financial engineering module (Module E) cost accuracy

## 23.5 Vehicle Manufacturer TCO Data

- Reference maintenance and depreciation data per vehicle model
- Source: manufacturer APIs (Renault, Mercedes, MAN, BYD)
- Usage: Pre-populated TCO defaults in financial module

---

# 24. Enterprise System Integrations

## 24.1 ERP Finance Export

- **Target systems:** SAP FI, Sage Comptabilite, Cegid
- **Export format:** CSV, XML, or API push (system-dependent)
- **Data:** TCO reports, ROI analyses, cost-per-trip summaries, investment comparator results
- **Frequency:** On-demand export or scheduled monthly push

## 24.2 LMS Integration

- **Supported LMS:** Cornerstone, 360Learning, TalentLMS
- **Sync direction:** Bidirectional
  - Import: Training catalog (available courses, modules)
  - Export: Completion records (modules completed during commute via Module F)
- **Protocol:** REST API with webhook notifications

## 24.3 Internal Communications

- **Platforms:** Workplace by Meta, Microsoft Viva, custom intranet
- **Integration:** Content feed pull for Module F (corporate news, announcements)
- **Direction:** Import only (platform consumes content, does not publish back)

## 24.4 Payment & Benefits

- **Stripe:** Billing management, transport pass purchases (future)
- **Navigo API:** Ile-de-France transit pass integration
- **Edenred / Swile:** NAT (Avantage Nature Transport) benefits integration

---

# PART VI — DATA MODEL

---

# 25. Complete Data Model

## 25.1 Core Tables (existing, enhanced)

### Site Table

- id
- code (unique, e.g., S01)
- name
- address
- city
- lat, lng
- num_shifts
- shift_1_entry, shift_1_exit
- shift_2_entry, shift_2_exit
- shift_3_entry, shift_3_exit
- working_days
- days_per_week
- contact_name, contact_phone
- access_notes, parking_notes
- zfe_zone (boolean)
- security_profile (normal / elevated / critical)
- timezone (string, e.g., "Europe/Paris")
- observations

### Employee Table

- id
- tenant_id (FK -> Tenant)
- matricule (unique employee code)
- first_name, last_name
- site_id (FK -> Site)
- shift_time
- address
- quartier, city
- lat, lng
- preferred_pickup_address
- preferred_pickup_lat, preferred_pickup_lng
- is_pmr (boolean)
- function_role
- phone
- department
- active (boolean)
- sirh_external_id (for SIRH sync)
- hire_date, end_date (for dynamic headcount)

### EmployeeModal Table

- id
- employee_id (FK -> Employee)
- primary_mode
- alternative_mode
- distance_km
- travel_time_min
- frequency
- interest_company_transport
- reason_current_mode
- departure_time
- accepts_common_pickup (boolean)
- max_pickup_distance_meters
- has_private_car (boolean)
- volunteer_driver (boolean)
- carpool_seats_available (integer)
- max_detour_minutes (integer)
- bonus_opt_in (boolean)
- observations

### Vehicle Table

- id
- tenant_id (FK -> Tenant)
- type
- brand_model
- capacity
- year
- owner_type (proprietaire, loueur, sous-traitant)
- monthly_cost_mad
- monthly_km
- condition (Bon, Moyen, Mauvais)
- site_id (FK -> Site)
- is_pmr_accessible (boolean)
- fuel_consumption (L/100km)
- cost_per_km
- motorization (diesel, hybrid, electric, hydrogen, gnv)
- length_meters
- zfe_compliant (boolean)
- observations

### Constraint Table

- id
- tenant_id (FK -> Tenant)
- key (unique identifier)
- value
- description
- category (duree, accessibilite, budget, saisonnalite, securite, rti, zfe)

### Cluster Table

- id
- optimization_id (FK)
- site_id (FK -> Site)
- centroid_lat, centroid_lng
- employee_count
- pmr_count
- security_risk_level (low / medium / high)

### Route Table

- id
- optimization_id (FK)
- vehicle_id (FK -> Vehicle)
- site_id (FK -> Site)
- ordered_stops (JSON)
- total_distance_km
- total_time_minutes
- polyline
- rti_compliance_pct

### Optimization Table

- id
- tenant_id (FK -> Tenant)
- site_id (FK -> Site, nullable for global)
- condition_type (normal, rain, strike, peak, night)
- status
- params (JSON)
- metrics (JSON)
- target_date
- created_at

### EmployeeLeave Table

- id
- employee_id (FK -> Employee)
- leave_type (vacation, sick, unpaid, formation, mission, other)
- start_date, end_date
- notes

### WeatherForecast Table

- id
- site_id (FK -> Site)
- date (YYYY-MM-DD)
- condition_summary
- precipitation_mm
- temp_min_c, temp_max_c
- wind_kph
- fetched_at
- source

### Settings Table

- id
- tenant_id (FK -> Tenant)
- meeting_radius_meters
- max_walking_distance_meters
- max_route_duration_minutes
- fuel_cost_per_liter
- company_lat, company_lng, company_name
- rti_max_wait_seconds (default: 90)
- night_mode_start, night_mode_end
- min_night_group_size (default: 3)

## 25.2 Financial Engineering Tables (NEW)

See Section 12.6 for detailed schemas:
- FinancialScenario
- TCOEntry
- ROICalculation
- VehicleReference

## 25.3 Journey Valorization Tables (NEW)

See Section 13.4 for detailed schemas:
- Content
- ContentDelivery
- TrainingModule
- Survey
- SurveyResponse

## 25.4 RTI Tables (NEW)

See Section 14.5 for detailed schemas:
- StopRiskScore
- VehiclePosition
- RTIEvent
- RTIConfig

## 25.5 Security Tables (NEW)

See Section 15.5 for detailed schemas:
- SecurityQuestionnaire
- SecurityScore
- EmergencyAlert

## 25.6 RBAC & Multi-Tenant Tables (NEW)

See Section 16.4 for detailed schemas:
- Tenant
- User
- Role
- Permission
- RolePermission

## 25.7 SIRH Sync Tables (NEW)

### SIRHConnection Table

- id
- tenant_id (FK -> Tenant)
- provider (sap, workday, talentsoft, sage)
- config (JSON — encrypted credentials, endpoint URLs)
- sync_frequency (daily, hourly, manual)
- last_sync_at
- status (active, error, disabled)

### SyncLog Table

- id
- sirh_connection_id (FK)
- started_at, completed_at
- records_created, records_updated, records_failed
- errors (JSON array)
- status (success, partial, failed)

### SyncConflict Table

- id
- sync_log_id (FK)
- employee_id (FK -> Employee)
- field_name
- platform_value, sirh_value
- resolution (pending, platform_wins, sirh_wins, manual)
- resolved_at, resolved_by

## 25.8 Mobile App Tables (NEW)

### TripBooking Table

- id
- employee_id (FK -> Employee)
- route_id (FK -> Route, nullable — assigned after optimization)
- pickup_stop_id (FK -> StopRiskScore, nullable)
- booking_date
- shift
- status (booked, confirmed, cancelled, completed, no_show)
- booked_at
- cancelled_at (nullable)

### DeviceRegistration Table

- id
- user_id (FK -> User)
- device_token (FCM token)
- platform (ios, android)
- app_version
- registered_at
- is_active (boolean)

### PushNotification Table

- id
- user_id (FK -> User)
- type (rti_alert, route_change, weather, content, emergency)
- title, body
- data (JSON — deep link, action)
- sent_at
- delivered_at (nullable)
- read_at (nullable)

## 25.9 Operator Tables (NEW)

### Operator Table

- id
- tenant_id (FK -> Tenant)
- name
- type (via, swvl, local, internal)
- api_config (JSON — endpoint, credentials)
- contact_name, contact_email, contact_phone
- is_active

### SizingPlanExport Table

- id
- optimization_id (FK -> Optimization)
- operator_id (FK -> Operator)
- exported_at
- format (json, xml, pdf)
- file_url
- status (draft, sent, acknowledged)

## 25.10 Reporting Tables (NEW)

### GeneratedReport Table

- id
- tenant_id (FK -> Tenant)
- report_type (operational, modal, fleet, financial_tco, financial_roi, rse_dpef, sizing_plan, hr_mobility, volunteer)
- params (JSON — filters, date range, site scope)
- file_url
- format (pdf, xlsx, csv, geojson)
- generated_at
- generated_by (FK -> User)

### KPISnapshot Table

- id
- tenant_id (FK -> Tenant)
- site_id (FK -> Site, nullable for global)
- snapshot_date
- kpi_type (mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score)
- value (JSON — structured KPI data)

---

# PART VII — API REFERENCE

---

# 26. API Design Principles

- **Base URL:** `http://localhost:8000/api/v1`
- **Versioning:** URL-based (`/api/v1/`, `/api/v2/`)
- **Authentication:** JWT Bearer tokens (issued by Auth0/Keycloak)
- **Authorization:** RBAC-checked per endpoint via middleware
- **Pagination:** `?page=1&page_size=20` with `total`, `page`, `pages` in response
- **Error format:** `{"detail": "message", "code": "ERROR_CODE", "field": "field_name"}`
- **Rate limiting:** 1000 req/min for web, 500 req/min for mobile, 100 req/min for operators
- **Content type:** `application/json` (default), `multipart/form-data` (file uploads)
- **API docs:** Auto-generated OpenAPI 3.0 / Swagger at `/docs`

---

# 27. API Endpoints by Module

## 27.1 Sites API

- `GET /sites` — List all sites with filters (city, zfe_zone)
- `GET /sites/{id}` — Get single site
- `GET /sites/code/{code}` — Get site by code
- `POST /sites` — Create new site
- `PUT /sites/{id}` — Update site
- `DELETE /sites/{id}` — Delete site
- `GET /sites/{id}/summary` — Get site summary (employee count, vehicle count, PMR, security profile)

## 27.2 Employees API

- `GET /employees` — List with filters (site_id, is_pmr, quartier, shift_time, department, active)
- `GET /employees/{id}` — Get single employee
- `POST /employees` — Create employee (accepts inline transport_profile)
- `PUT /employees/{id}` — Update employee
- `DELETE /employees/{id}` — Soft-delete employee
- `POST /employees/upload` — Bulk CSV upload
- `POST /employees/geocode` — Geocode addresses
- `GET /employees/summary` — Summary with site and PMR breakdowns

## 27.3 Employee Modal API

- `GET /employees/{id}/modal` — Get transport data for employee
- `PUT /employees/{id}/modal` — Create/update modal data
- `DELETE /employees/{id}/modal` — Delete modal data
- `GET /modal/stats` — Global modal distribution statistics
- `GET /modal/shift-analysis` — Modal shift analysis (disruption impact)
- `GET /modal/mobility-scores` — Mobility scores per employee/group/site

## 27.4 Employee Leave API

- `POST /leaves` — Create leave period
- `GET /leaves` — List leaves with filters (employee_id, site_id, date_from, date_to)
- `GET /leaves/{id}` — Get single leave
- `PUT /leaves/{id}` — Update leave
- `DELETE /leaves/{id}` — Delete leave

## 27.5 Vehicles API

- `GET /vehicles` — List vehicles (site_id, is_pmr_accessible, condition, motorization, zfe_compliant filters)
- `POST /vehicles` — Create vehicle
- `PUT /vehicles/{id}` — Update vehicle
- `DELETE /vehicles/{id}` — Delete vehicle
- `GET /vehicles/fleet-summary` — Fleet overview by site, type, condition, motorization

## 27.6 Constraints API

- `GET /constraints` — List constraints with optional category filter
- `POST /constraints` — Create constraint
- `PUT /constraints/{id}` — Update constraint
- `DELETE /constraints/{id}` — Delete constraint
- `POST /constraints/bulk` — Bulk import constraints

## 27.7 Excel Import API

- `POST /import/excel` — Upload and import full Excel template
- `POST /import/excel/preview` — Preview data without importing
- `POST /import/excel/sheet` — Import single sheet

## 27.8 Optimization API

- `POST /optimize` — Run optimization (site_id, condition_type, target_date, rti_enabled)
- `GET /optimize/{optimization_id}` — Get result with per-site metrics
- `GET /optimize/{optimization_id}/status` — Get progress
- `GET /optimize/latest/result` — Most recent optimization
- `GET /optimize/history/list` — Past runs

## 27.9 Clustering API

- `POST /clusters/generate` — Run clustering (site_id, algorithm, params)
- `GET /clusters` — Get saved clusters (site_id filter)
- `GET /clusters/{id}` — Get single cluster with employees

## 27.10 Vehicle Assignment API

- `POST /vehicle-assignments/assign` — Assign vehicles to clusters (PMR-aware)
- `POST /vehicle-assignments/split-cluster/{cluster_id}` — Split cluster
- `POST /vehicle-assignments/merge-clusters` — Merge clusters

## 27.11 Routes API

- `GET /routes` — Get routes (site_id, optimization_id, vehicle_id filters)
- `GET /routes/{id}` — Get single route with geometry

## 27.12 Weather API

- `GET /weather/{site_id}` — Get stored forecasts
- `POST /weather/{site_id}/refresh` — Refresh from provider
- `POST /weather/refresh-all` — Refresh all sites
- `GET /weather/{site_id}/suggestions` — Scenario suggestions from forecast

## 27.13 Scenarios API

- `POST /scenarios/simulate` — Run scenario with modified params
- `GET /scenarios` — List all scenarios
- `GET /scenarios/{scenario_id}` — Get single scenario
- `DELETE /scenarios/{scenario_id}` — Delete scenario
- `POST /scenarios/compare` — Compare 2+ scenarios

## 27.14 Financial Engineering API (NEW)

- `POST /financial/scenarios` — Create financial scenario
- `GET /financial/scenarios` — List financial scenarios
- `GET /financial/scenarios/{id}` — Get scenario with results
- `PUT /financial/scenarios/{id}` — Update scenario
- `DELETE /financial/scenarios/{id}` — Delete scenario
- `POST /financial/tco/calculate` — Calculate TCO for a fleet composition
- `POST /financial/roi/calculate` — Calculate ROI with baseline metrics
- `POST /financial/compare` — Compare investment models side-by-side
- `GET /financial/vehicle-references` — Get vehicle reference catalog
- `POST /financial/export/daf` — Export DAF-compatible report

## 27.15 Journey Valorization API (NEW)

- `POST /content` — Create content item
- `GET /content` — List content (type, site, status filters)
- `GET /content/{id}` — Get content item
- `PUT /content/{id}` — Update content
- `DELETE /content/{id}` — Delete content
- `POST /content/{id}/publish` — Publish content
- `GET /content/feed` — Get personalized content feed (for mobile app)
- `GET /content/{id}/engagement` — Get engagement metrics
- `GET /content/analytics` — Aggregate engagement analytics
- `POST /surveys/{id}/respond` — Submit survey response
- `GET /training/completions` — Training completion records
- `POST /training/sync-lms` — Trigger LMS synchronization
- `GET /valorization/metrics` — Journey valorization KPIs (hours recovered, monetary value)

## 27.16 RTI API (NEW)

- `POST /rti/vehicle-position` — Update vehicle position (from GPS tracker)
- `GET /rti/vehicle-position/{vehicle_id}` — Get current vehicle position
- `GET /rti/stop/{stop_id}/eta` — Get ETA for next vehicle at stop
- `GET /rti/compliance` — Get RTI compliance metrics
- `GET /rti/risk-stops` — List risk-scored stops
- `PUT /rti/risk-stops/{id}` — Update risk stop assessment
- `GET /rti/config/{site_id}` — Get RTI config for site
- `PUT /rti/config/{site_id}` — Update RTI config

## 27.17 Security API (NEW)

- `POST /security/questionnaire` — Submit security questionnaire response
- `GET /security/questionnaire/{employee_id}` — Get latest questionnaire
- `GET /security/scores` — Get security scores (site_id, shift filters)
- `GET /security/scores/{employee_id}` — Get individual security score
- `GET /security/risk-map` — Get security risk map data (stops + scores)
- `POST /security/emergency` — Trigger emergency alert
- `GET /security/emergency/history` — Emergency alert history
- `PUT /security/emergency/{id}/resolve` — Resolve emergency alert

## 27.18 RBAC & Auth API (NEW)

- `POST /auth/login` — Login (delegates to Auth0/Keycloak)
- `POST /auth/logout` — Logout
- `POST /auth/refresh` — Refresh token
- `GET /auth/me` — Get current user profile
- `GET /users` — List users (admin only)
- `POST /users` — Create user (admin only)
- `PUT /users/{id}` — Update user
- `DELETE /users/{id}` — Deactivate user
- `GET /roles` — List roles
- `POST /roles` — Create custom role (admin only)
- `PUT /roles/{id}` — Update role permissions
- `GET /tenants` — List tenants (platform admin)
- `POST /tenants` — Create tenant (platform admin)
- `PUT /tenants/{id}` — Update tenant config

## 27.19 SIRH Sync API (NEW)

- `POST /sirh/connections` — Configure SIRH connection
- `GET /sirh/connections` — List SIRH connections
- `PUT /sirh/connections/{id}` — Update connection config
- `DELETE /sirh/connections/{id}` — Remove connection
- `POST /sirh/sync/{connection_id}` — Trigger manual sync
- `GET /sirh/sync/status` — Get sync status and history
- `GET /sirh/sync/conflicts` — List unresolved conflicts
- `PUT /sirh/sync/conflicts/{id}/resolve` — Resolve conflict

## 27.20 Mobile API (NEW)

- `POST /trips/book` — Book a trip
- `PUT /trips/{id}` — Modify booking
- `DELETE /trips/{id}` — Cancel booking
- `GET /trips/my` — Get my trip history
- `GET /trips/upcoming` — Get upcoming booked trips
- `POST /devices/register` — Register device for push notifications
- `DELETE /devices/{token}` — Unregister device
- `GET /mobile/offline-manifest` — Get data package for offline caching

## 27.21 Export & Report API

- `GET /export/pdf` — Generate PDF driver sheets
- `GET /export/excel` — Generate multi-sheet Excel workbook
- `GET /export/csv/stops` — CSV with stop order
- `GET /export/csv/employees` — CSV with employee assignments
- `GET /export/geojson` — GeoJSON FeatureCollection
- `GET /export/modal-report` — Modal analysis report
- `GET /export/fleet-report` — Fleet utilization report
- `GET /export/volunteer-report` — Volunteer driver report
- `POST /export/financial/tco` — TCO report (PDF/Excel)
- `POST /export/financial/roi` — ROI report (PDF/Excel)
- `POST /export/financial/daf` — DAF ERP-compatible export
- `POST /export/rse/dpef` — DPEF environmental report
- `POST /export/sizing-plan` — Operator sizing plan
- `POST /export/hr-mobility` — HR mobility report
- `GET /export/history` — Generated report history

## 27.22 Dashboard KPI API (NEW)

- `GET /kpis/operations` — Operations KPIs (vehicles, occupancy, distance, fuel, CO2)
- `GET /kpis/hr` — HR dashboard KPIs (coverage, mobility score, absenteeism correlation)
- `GET /kpis/rse` — RSE KPIs (CO2 saved, modal shift, ZFE compliance)
- `GET /kpis/rti` — RTI compliance KPIs
- `GET /kpis/security` — Security scores and incident metrics
- `GET /kpis/financial` — Financial KPIs (TCO trends, ROI, cost/trip)
- `GET /kpis/valorization` — Journey valorization KPIs (engagement, hours recovered)
- `POST /kpis/snapshot` — Save KPI snapshot for historical tracking

## 27.23 Settings API

- `GET /settings` — Get current parameters
- `PUT /settings` — Update parameters

## 27.24 Health API

- `GET /` — API welcome message
- `GET /health` — Health check endpoint

---

# PART VIII — NON-FUNCTIONAL REQUIREMENTS

---

# 28. Performance Requirements

| Metric | Target |
|--------|--------|
| API response time | < 300 ms for 95% of requests (excluding simulation) |
| Standard simulation | < 30 seconds for 500 employees |
| Large simulation | < 3 minutes for 5,000 employees |
| TCO / ROI calculation | < 10 seconds for a complete scenario |
| Pooling algorithm | < 60 seconds for 1,000 employees |
| RTI refresh | <= 10 seconds for vehicle position updates |
| Concurrent users | 10,000 active simultaneous users |
| Availability | 99.5% SLA (monthly, excluding planned maintenance) |
| Mobile cold start | < 3 seconds on 4G network |

### Implementation Strategy

- Simulation, TCO, and pooling engines deployed as independent async services with task queue (Celery + Redis)
- Database read replicas for reporting queries
- Redis caching for frequently accessed data (site configs, vehicle catalog)
- WebSocket connections for RTI real-time updates (not polling)

---

# 29. Scalability & Availability

- **Horizontal scaling:** Backend is stateless (JWT auth, Redis sessions)
- **Database:** PostgreSQL with read replicas for analytics queries
- **Task queue:** Celery workers scale independently for async computation
- **CDN:** Static assets and mobile app content served via CDN
- **Auto-scaling:** Kubernetes HPA (Horizontal Pod Autoscaler) based on CPU/memory
- **Health checks:** Liveness and readiness probes for all services
- **Disaster recovery:** Automated database backups, point-in-time recovery

---

# 30. Security & Compliance

## 30.1 Authentication & Authorization

- SSO via Auth0 or Keycloak (SAML 2.0 + OIDC)
- MFA mandatory for DRH, DAF, and Admin roles
- JWT tokens with short expiry (15 min access, 7 day refresh)
- RBAC middleware checking permissions per endpoint

## 30.2 Data Encryption

- **In transit:** TLS 1.3 for all communications
- **At rest:** AES-256 encryption for sensitive data
- **Secrets management:** Vault or AWS Secrets Manager for API keys, credentials

## 30.3 RGPD Compliance

- **Geolocation:** Active mode only, never background collection
- **Retention:** Location data: 30 days maximum in active database
- **AIPD:** Data Protection Impact Assessment required before deployment
- **Consent:** Explicit employee consent for geolocation and security questionnaire
- **Right to access:** Employee can export their data
- **Right to deletion:** Employee data deletable on request (with audit trail)
- **Data portability:** Export in standard format (JSON, CSV)
- **DPO:** Designated Data Protection Officer required
- **IRP notification:** Employee representatives informed before deployment
- **Audit logging:** All access and modifications logged with user, timestamp, action

## 30.4 API Security

- Rate limiting per role (1000/500/100 req/min)
- Input validation (Pydantic models)
- CORS configuration (whitelist origins)
- CSRF protection for session-based endpoints
- SQL injection prevention (ORM parameterized queries)
- XSS prevention (output encoding)
- File upload validation (type, size limits)

## 30.5 Penetration Testing

- Mandatory pentest before production deployment
- Critical bug fix SLA: 4 hours
- Security patch SLA: 48 hours after CVE disclosure

---

# 31. Accessibility & Internationalization

## 31.1 Accessibility

- **Standard:** WCAG 2.1 Level AA compliance (web and mobile)
- **Web:** Semantic HTML, ARIA labels, keyboard navigation, focus management
- **Mobile:** VoiceOver (iOS) and TalkBack (Android) support, adjustable text size
- **Color contrast:** Minimum 4.5:1 ratio for normal text, 3:1 for large text
- **Screen reader:** All interactive elements labeled, status updates announced

## 31.2 Internationalization

- **Languages:** French (primary), English (secondary)
- **Architecture:** i18n framework from day one (react-i18next for web, flutter_localizations for mobile)
- **Date/time:** Locale-aware formatting
- **Numbers/currency:** Locale-aware formatting (MAD, EUR, USD configurable)
- **Timezone:** Per-site timezone configuration
- **Future:** Arabic RTL support if needed for MENA deployment

---

# PART IX — BUSINESS & OPERATIONS

---

# 32. User Flows

## 32.1 DRH Flow

1. Login (SSO) -> Dashboard
2. Import/configure sites (from Excel or SIRH)
3. Import employees (from Excel, CSV, or SIRH sync)
4. Import modal usage data (from Excel or questionnaire)
5. Import/create fleet inventory (from Excel or manual)
6. Set constraints and parameters
7. (Optional) Manage leaves/vacations
8. Select site -> Click "Optimize" (choose target date, condition)
9. Review map and dashboard (clusters, routes, meeting zones)
10. Set disruption condition -> Re-optimize
11. Compare scenarios
12. Schedule embedded content (Module F)
13. Export reports and sizing plans

## 32.2 DAF Flow

1. Login (SSO with MFA) -> Financial Dashboard
2. Create financial scenario (select investment model)
3. Configure fleet composition and parameters
4. Run TCO calculation
5. Run ROI calculation (input baseline metrics)
6. Compare CAPEX vs. mise-a-dispo vs. OPEX
7. Simulate payback period
8. Export DAF report to ERP
9. Review HR and RSE KPIs (read-only)

## 32.3 Employee (Mobile) Flow

1. Download Flutter app -> Login (SSO)
2. Complete onboarding (preferences, security questionnaire, permissions)
3. Daily: Open app -> View next departure with RTI countdown
4. (Optional) Book/modify/cancel trip
5. Receive D-2min push alert -> Walk to gathering point
6. View approaching vehicle on map
7. During commute: Consume embedded content (news, training, surveys)
8. Complete micro-training modules
9. (Night mode) Use discrete emergency button if needed
10. Review trip history and CO2 savings

## 32.4 Operator Flow

1. Login (web portal) -> View assigned sizing plans
2. Review vehicle specifications, routes, schedules
3. Acknowledge sizing plan
4. Access real-time passenger count data
5. Report service issues

## 32.5 Admin Flow

1. Login (MFA) -> Admin panel
2. Configure tenant (branding, defaults, feature flags)
3. Manage users and roles
4. Configure SIRH connections
5. Configure operator integrations
6. Monitor sync status and errors
7. Review audit logs
8. Manage API keys
9. RGPD compliance monitoring

---

# 33. Business Model

## 33.1 SaaS Pricing Tiers

### Base Tier — Transport Optimization

- Site management + employee data + optimization engine
- Web dashboard (operations map + analytics)
- Excel import
- Basic exports (PDF, CSV)
- **Pricing:** Based on employee count and sites
  - 1 site, up to 100 employees: $199/month
  - 3 sites, up to 500 employees: $599/month

### Professional Tier — + Financial & Reporting

- Everything in Base +
- Module E (Financial Engineering — TCO, ROI, investment comparator)
- Enhanced exports (7-sheet Excel, modal report, fleet report, financial reports)
- SIRH integration (1 connector)
- HR and RSE dashboards
- **Pricing:**
  - Up to 5 sites, 1,000 employees: $1,499/month
  - Up to 10 sites, 3,000 employees: $2,999/month

### Enterprise Tier — Full Platform

- Everything in Professional +
- Flutter mobile app (iOS + Android) for employees
- RTI guarantee system
- Security module (questionnaire, scoring, emergency)
- Module F (Journey Valorization — content, training, LMS)
- Operator API integrations
- Multi-tenant support
- Unlimited SIRH connectors
- ERP finance export
- Custom SLA
- **Pricing:** Custom, based on total employees and deployment scope
  - 10+ sites, 2,000+ employees: Starting $4,999/month
  - Enterprise (10,000+ employees): Custom pricing

### On-Premise / Private Cloud

- Full platform deployed on client infrastructure
- Custom pricing based on deployment complexity

---

# 34. Implementation Phases

### Phase 0 — Cadrage & UX (4 weeks)

- Functional validation, wireframes, design system
- Infrastructure setup (Docker, CI/CD, databases)
- RBAC foundation

### Phase 1 — MVP Core (14 weeks)

- **Modules A-D:** Site management, employee data, modal analysis, optimization engine
- **Web dashboard:** Operations map, analytics panel, basic exports
- **Corresponds to:** Existing sessions 01-25 (already completed)

### Phase 2 — Financial & Reporting (14 weeks)

- **Module E:** Financial engineering (TCO, ROI, investment comparator)
- **Enhanced reporting:** HR dashboard, RSE dashboard, financial exports, DPEF
- **DAF user flow**

### Phase 3 — Mobile MVP (10 weeks)

- **Flutter app:** Authentication, trip booking, RTI display, push notifications, profile management
- **Backend:** Mobile API, trip booking, device registration, push notification service
- **Basic RTI:** Vehicle position updates, ETA calculation

### Phase 4 — Security & RTI (8 weeks)

- **Security module:** Questionnaire, scoring, risk stop assessment, emergency button
- **Full RTI:** Adaptive sizing, compliance tracking, risk stop management
- **Night mode** (mobile)
- **Security-constrained pooling**

### Phase 5 — Journey Valorization (8 weeks)

- **Module F:** Content management (web), content consumption (mobile)
- **LMS integration**
- **Engagement tracking and value measurement**

### Phase 6 — Enterprise Integrations (8 weeks)

- **SIRH sync** (SAP, Workday, Talentsoft, Sage)
- **Operator APIs** (Via, SWVL, sizing plan export)
- **ERP finance export** (SAP FI, Sage, Cegid)
- **Payment integration** (Stripe, Navigo)

### Phase 7 — Stabilization & Scale (4 weeks)

- Performance optimization (10K concurrent users target)
- Load testing
- Penetration testing
- SLA hardening (99.5%)
- RGPD audit and compliance validation
- App Store / Google Play publication

**Total estimated timeline:** ~70 weeks (17.5 months)

---

# APPENDICES

---

# Appendix A — Financial Model Formulas

All formulas are transparent and auditable by the DAF. Default hypotheses are configurable per client.

| Formula | Calculation |
|---------|-------------|
| **TCO per vehicle** | Purchase_Price + (Annual_Maintenance x Duration) + (Energy_Cost_per_km x Annual_km x Duration) - Residual_Value |
| **Cost per available seat** | Annual_TCO / (Seats x Annual_Trips) |
| **Cost per occupied seat** | Annual_TCO / (Seats x Fill_Rate x Annual_Trips) |
| **ROI absenteeism** | (Absence_Rate_Before - After) x Headcount x Daily_Cost |
| **ROI retention** | Avoided_Turnover x Replacement_Cost (6-9 months salary) |
| **ROI journey valorization** | Travel_Hours x Engagement_Rate x Internal_Training_Hour_Cost |
| **Payback period** | Total_Investment / Annual_Net_Gain (all ROI levers cumulated) |

---

# Appendix B — Vehicle Reference Catalog

| Type | Capacity | Motorizations Available | Recommended Use |
|------|----------|------------------------|-----------------|
| Minibus | 8-14 seats | Diesel, electric, hybrid | TAD, small dedicated shuttles |
| Midibus | 15-30 seats | Diesel, electric, hydrogen | Medium dedicated shuttles |
| Bus standard | 45-60 seats | Diesel, electric, hydrogen | Fixed lines, high density |
| Grand bus | 80-120 seats | Diesel, GNV (natural gas) | Seasonal peaks, large sites |
| Vehicule leger | 4-8 seats | Electric, thermal | Rural zones, off-peak hours |

---

# Appendix C — RBAC Permissions Matrix

| Resource | Action | DRH | DAF | Salarie | Operateur | Admin |
|----------|--------|-----|-----|---------|-----------|-------|
| Sites | Read | Yes | Yes | Own site | Assigned | Yes |
| Sites | Write | Yes | No | No | No | Yes |
| Employees | Read | Yes | No | Self | No | Yes |
| Employees | Write | Yes | No | Self (prefs) | No | Yes |
| Optimization | Run | Yes | No | No | No | Yes |
| Optimization | Read results | Yes | Yes | No | Assigned | Yes |
| Financial scenarios | Read | Yes | Yes | No | No | Yes |
| Financial scenarios | Write | Yes | Yes | No | No | Yes |
| Content (Module F) | Publish | Yes | No | No | No | Yes |
| Content (Module F) | Read | No | No | Yes | No | No |
| Trips | Book | Yes | No | Yes | No | No |
| RTI | View | Supervise | No | Yes | Yes | Supervise |
| Security questionnaire | Submit | No | No | Yes | No | No |
| Security scores | Read | Yes | No | No | No | Yes |
| Emergency alerts | Emit | No | No | Yes | No | No |
| Emergency alerts | Receive | Yes | No | No | Yes | Yes |
| Users | Manage | No | No | No | No | Yes |
| Tenants | Manage | No | No | No | No | Platform Admin |
| SIRH connections | Configure | Yes | No | No | No | Yes |
| Reports | Generate | Yes | Yes | No | Read | Yes |
| Settings | Modify | Yes | No | No | No | Yes |
| Audit logs | View | No | No | No | No | Yes |

---

# Appendix D — RGPD Compliance Checklist

- [ ] Registre des traitements maintained for each data processing activity
- [ ] AIPD (Data Protection Impact Assessment) completed for geolocation processing
- [ ] DPO (Data Protection Officer) designated by client
- [ ] Data processor agreement (Article 28 RGPD) signed with development provider
- [ ] Privacy by Design applied from architecture phase
- [ ] Retention policy: location data max 30 days in active database
- [ ] Geolocation: active mode only (never background collection)
- [ ] IRP (employee representatives) informed before deployment
- [ ] Employee consent mechanism implemented (explicit opt-in for geolocation)
- [ ] Right to access: employee data export functionality
- [ ] Right to rectification: employee can update personal data
- [ ] Right to deletion: employee data deletable on request (with audit trail)
- [ ] Right to portability: export in standard format (JSON, CSV)
- [ ] Data breach notification procedure documented (<72h to CNIL)
- [ ] Security audit (pentest) completed before production
- [ ] All API calls to external services reviewed for data transmission compliance
- [ ] Cookie consent implemented (web dashboard)
- [ ] Privacy policy published (public URL — required for App Store / Google Play)

---

# Appendix E — Integration API Specifications

| Integration | Auth Method | Rate Limit | Data Direction | Error Handling |
|-------------|-----------|------------|----------------|----------------|
| SAP SuccessFactors | OAuth 2.0 | Per contract | Import | Retry 3x, exponential backoff |
| Workday | OAuth 2.0 | Per contract | Import | Retry 3x, exponential backoff |
| Talentsoft | API Key | 1000/hour | Import | Retry 3x, queue on failure |
| Sage RH | API Key | 500/hour | Import | Retry 3x, queue on failure |
| OpenWeatherMap | API Key | 60/min (free) | Import | Cache last result, fallback |
| Google Maps | API Key | Per quota | Import | Fallback to OSRM |
| HERE Maps | API Key | Per quota | Import | Fallback to OSRM |
| OSRM | None (self-hosted) | Unlimited | Import | Retry 3x |
| Auth0 | OAuth 2.0 | Per plan | Bidirectional | Token refresh, re-auth |
| Firebase FCM | Server key | 500k/day | Export (push) | Retry with backoff |
| Stripe | API Key | 100/sec | Bidirectional | Idempotent retry |
| Cornerstone LMS | OAuth 2.0 | Per contract | Bidirectional | Queue sync conflicts |
| 360Learning | API Key | Per contract | Bidirectional | Queue sync conflicts |

---

# Appendix F — Excel Template Specification

Seven-sheet Excel template (`Collecte_Donnees_Transport_Personnel_v2.xlsx`):

### SITES Sheet

| Column | Field | Required | Description |
|--------|-------|----------|-------------|
| A | Code Site | * | Unique site identifier (e.g., S01) |
| B | Nom du site | * | Site name |
| C | Adresse complete | * | Full address |
| D | Ville | * | City |
| E | Latitude | * | GPS latitude |
| F | Longitude | * | GPS longitude |
| G | Nombre de postes | * | Number of shifts (1-3) |
| H | Poste 1 — Entree | * | Shift 1 entry time |
| I | Poste 1 — Sortie | * | Shift 1 exit time |
| J | Poste 2 — Entree | (o) | Shift 2 entry time |
| K | Poste 2 — Sortie | (o) | Shift 2 exit time |
| L | Poste 3 — Entree | (o) | Shift 3 entry time |
| M | Poste 3 — Sortie | (o) | Shift 3 exit time |
| N | Jours travailles | * | Working days |
| O | Jours/semaine | * | Days per week |
| P | Contact | (o) | Contact name |
| Q | Telephone | (o) | Contact phone |
| R | Acces/parking | (o) | Access notes |
| S | Observations | (o) | Notes |

### EFFECTIF Sheet

| Column | Field | Required |
|--------|-------|----------|
| A | Matricule | * |
| B | Nom | * |
| C | Prenom | * |
| D | Code Site | * |
| E | Poste | * |
| F | Adresse domicile | * |
| G | Quartier/Zone | (o) |
| H | Ville | * |
| I | Latitude | (o) — geocoded if missing |
| J | Longitude | (o) — geocoded if missing |
| K | PMR | * (Oui/Non) |
| L | Fonction | (o) |
| M | Telephone | (o) |
| N | Departement | (o) |
| O | Mode transport actuel | * |
| P | Opt-in transport entreprise | * (Oui/Non/Sous conditions) |
| Q | Vehicule personnel | * (Oui/Non) |
| R | Conducteur volontaire | (o) (Oui/Non) |
| S | Places covoiturage | (o) |

### USAGES & MODES Sheet

| Column | Field | Required |
|--------|-------|----------|
| A | Matricule | * |
| B | Mode principal | * |
| C | Mode alternatif | (o) |
| D | Distance km | * |
| E | Temps trajet min | * |
| F | Frequence | * |
| G | Interet transport entreprise | * |
| H | Raison mode actuel | (o) |
| I | Heure depart domicile | (o) |
| J | Accepte point commun | * (Oui/Non) |
| K | Distance max point pickup (m) | (o) |
| L | Vehicule personnel | * (Oui/Non) |
| M | Conducteur volontaire | (o) (Oui/Non) |
| N | Places dispo covoiturage | (o) |
| O | Detour max (min) | (o) |
| P | Opt-in bonus | (o) (Oui/Non) |
| Q | Observations | (o) |

### CONTRAINTES Sheet

| Column | Field | Required |
|--------|-------|----------|
| A | Cle | * |
| B | Valeur | * |
| C | Description | (o) |
| D | Categorie | * (duree, accessibilite, budget, saisonnalite, securite, rti, zfe) |

### PARC EXISTANT Sheet

| Column | Field | Required |
|--------|-------|----------|
| A | Type vehicule | * |
| B | Marque/Modele | (o) |
| C | Capacite (places) | * |
| D | Annee | (o) |
| E | Proprietaire/Loueur | * |
| F | Cout mensuel (MAD) | (o) |
| G | Km mensuel | (o) |
| H | Etat | * (Bon/Moyen/Mauvais) |
| I | Code Site | * |
| J | Accessible PMR | * (Oui/Non) |
| K | Conso carburant (L/100km) | (o) |
| L | Cout/km | (o) |
| M | Motorisation | (o) (diesel, hybride, electrique, hydrogene, gnv) |
| N | Longueur (m) | (o) |
| O | Conforme ZFE | (o) (Oui/Non) |
| P | Observations | (o) |

### ABSENCES Sheet (optional)

| Column | Field | Required |
|--------|-------|----------|
| A | Matricule | * |
| B | Type absence | * (conge, maladie, formation, mission, autre) |
| C | Date debut | * |
| D | Date fin | * |
| E | Notes | (o) |

### SYNTHESE Sheet

Read-only auto-calculated summary. Not imported.

---

# Appendix G — Optimization Model Mathematical Specification

## Decision Variables

- x_ij = 1 if employee i is assigned to vehicle j, 0 otherwise
- y_j = 1 if vehicle j is used, 0 otherwise
- z_ik = 1 if employee i is assigned to gathering point k, 0 otherwise
- r_jl = 1 if vehicle j visits stop l, 0 otherwise
- s_jlm = 1 if vehicle j travels from stop l to stop m, 0 otherwise

## Objective Function

```
Minimize:
  alpha * SUM(d_lm * s_jlm)           [total distance]
+ beta * SUM(t_lm * s_jlm)            [total time]
+ gamma * SUM(y_j)                      [number of vehicles]
+ delta * SUM(f_j * d_lm * s_jlm)     [fuel cost]
+ epsilon * SUM(incentive_v)            [volunteer driver bonuses]
+ zeta * SUM(max(0, w_k - RTI_max))    [RTI violation penalty]
+ eta * SUM(risk_k * night_k)          [security risk penalty]
```

## Constraints

```
1. Capacity:     SUM_i(x_ij) <= C_j * y_j                  for all vehicles j
2. Assignment:   SUM_j(x_ij) = 1                            for all employees i (not on leave)
3. Walking:      dist(home_i, gathering_k) <= W_max          for all i where z_ik = 1
4. Duration:     SUM_lm(t_lm * s_jlm) <= T_max              for all vehicles j
5. Shift:        arrival_time(j, site) <= shift_entry - buffer for all vehicles j
6. PMR:          if employee i is PMR and x_ij = 1, then vehicle j must be PMR-accessible
7. ZFE:          if site(j) is in ZFE, then vehicle j must be ZFE-compliant
8. RTI:          wait_time(k) <= RTI_max_seconds              for all critical stops k
9. Security:     if night_shift AND stop_k is critical, then group_size(k) >= MIN_GROUP
10. Volunteer:   if driver_v is volunteer, detour(v) <= max_detour_v
11. Budget:      SUM(cost_j * y_j) <= Budget_max              when budget defined
12. Leave:       x_ij = 0 for all employees i on leave on target_date
```

---

# Appendix H — Competitive Positioning

| Capability | SWVL | Via | Transpop |
|------------|------|-----|----------|
| Individual diagnostic | No | No | **Yes — mobile questionnaire + SIRH** |
| Financial sizing (TCO/ROI) | No | No | **Yes — Module E** |
| Security scoring at stops | No | No | **Yes — risk scores + RTI guarantee** |
| Journey valorization | No | No | **Yes — Module F (micro-training)** |
| Multi-site optimization | Partial | Yes | **Yes — per-site with global view** |
| SIRH integration | No | No | **Yes — SAP, Workday, Talentsoft, Sage** |
| Operator API standardization | Proprietary | Proprietary | **Yes — standardized sizing plan export** |
| RBAC multi-profile | Basic | Basic | **Yes — 5 profiles with granular permissions** |
| PMR accessibility | Basic | Basic | **Yes — model-level + vehicle-level + routing** |
| Weather/disruption simulation | No | Basic | **Yes — multi-scenario with forecasting** |
| ZFE compliance | No | No | **Yes — vehicle + route + site** |
| Mobile app (employee) | Consumer app | Agency app | **Yes — Flutter iOS/Android** |
| Night mode + emergency | No | No | **Yes — discrete button + responder alert** |
| RGPD by design | Partial | Partial | **Yes — full compliance architecture** |
| On-demand transport (TAD) | Yes | Yes | **Yes — fallback mode in sizing** |

---

# End of Enhanced PRD v3.0
