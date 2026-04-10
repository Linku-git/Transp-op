# Database Schema — Transpop

**Database:** PostgreSQL 15 + PostGIS  
**Connection:** `postgresql+asyncpg://postgres:password@helium:5432/heliumdb`  
**Backup:** `transpop_backup_20260408.sql` (root folder, 736 KB)  
**Tenant:** `0cea9745-6aa2-4105-9bdc-341d95999048` (OCP Transpop)  
**Live data:** 1,200 employees · 106 vehicles · 591 config_transport rows · 32,696 km total  
**Last updated:** 2026-04-08 (extracted from live DB)

---

## Table Index

| Table | Size | Columns | Description |
|---|---|---|---|
| [tenant](#tenant) | 48 kB | 8 | Multi-tenant root |
| [site](#site) | 80 kB | 38 | Industrial sites (plants) |
| [user](#user) | 48 kB | 14 | Admin/operator accounts |
| [role](#role) | 32 kB | 7 | RBAC roles |
| [permission](#permission) | 16 kB | 5 | RBAC permissions |
| [role_permission](#role_permission) | 16 kB | 5 | Role ↔ Permission mapping |
| [employee](#employee) | 656 kB | 33 | Employee master data with GPS |
| [employee_modal](#employee_modal) | 32 kB | 20 | Transport preferences survey |
| [employee_leave](#employee_leave) | 64 kB | 8 | Leaves and absences |
| [vehicle](#vehicle) | 128 kB | 23 | Fleet inventory |
| [vehicle_reference](#vehicle_reference) | 32 kB | 11 | Reference catalog per type |
| [point_arret](#point_arret) | 96 kB | 15 | Bus stops / gathering points |
| [configuration_plan](#configuration_plan) | 48 kB | 9 | Transport plan version |
| [configuration_transport](#configuration_transport) | 272 kB | 26 | Detailed circuit rows |
| [optimization](#optimization) | 48 kB | 11 | Optimization run results |
| [optimization_settings](#optimization_settings) | 64 kB | 14 | Optimizer parameters |
| [cluster](#cluster) | 56 kB | 12 | Employee geo-clusters |
| [route](#route) | 96 kB | 12 | Computed routes per vehicle |
| [horaire_travail](#horaire_travail) | 64 kB | 11 | Shift schedule templates |
| [constraint_param](#constraint_param) | 32 kB | 9 | Configurable business rules |
| [kpi_snapshot](#kpi_snapshot) | 168 kB | 8 | Daily KPI cache |
| [km_consommation](#km_consommation) | 48 kB | 15 | Monthly mileage actuals |
| [financial_scenario](#financial_scenario) | 64 kB | 11 | TCO/ROI scenario |
| [tco_entry](#tco_entry) | 40 kB | 15 | TCO line items per vehicle type |
| [roi_calculation](#roi_calculation) | 40 kB | 20 | ROI results per scenario |
| [scenario](#scenario) | 64 kB | 11 | Simulation scenario (what-if) |
| [generated_report](#generated_report) | 48 kB | 10 | Async report metadata |
| [weather_forecast](#weather_forecast) | 64 kB | 12 | Open-Meteo forecasts per site |
| [content_delivery](#content_delivery) | — | 10 | Content engagement tracking per employee |
| [survey](#survey) | — | 10 | Survey/poll definitions with JSONB questions |
| [survey_response](#survey_response) | — | 8 | Survey response submissions |
| [training_module](#training_module) | — | 13 | LMS training module mapping |
| [sirh_connection](#sirh_connection) | — | 11 | SIRH provider connections |
| [sync_log](#sync_log) | — | 11 | Sync execution logs |
| [sync_conflict](#sync_conflict) | — | 9 | Field-level sync conflicts |
| [ligne](#ligne) | — | 22 | SOTREG transport lines (CDC formula) |
| [fleet_context](#fleet_context) | — | 12 | Fleet diagnostics snapshots |
| [od_matrix](#od_matrix) | — | 12 | OD matrix entries (Wilson gravity model) |
| [irve_infrastructure](#irve_infrastructure) | — | 20 | IRVE charging infrastructure records |
| [generated_stop](#generated_stop) | — | 18 | Candidate stops from DBSCAN/manual |
| [depot_plan](#depot_plan) | — | 16 | Depot electrification plans with JSONB costs |
| [avl_metric](#avl_metric) | — | 13 | AVL-based operational KPI metrics |
| [departure_schedule](#departure_schedule) | — | 12 | LTO optimized departure schedules |

---

## tenant

Root entity. One row per company/client.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| name | varchar(255) | ✓ | | Company name |
| code | varchar(100) | ✓ | | **UNIQUE** — e.g. `OCP` |
| config | jsonb | ✓ | `{}` | Tenant config blob |
| data_region | varchar(50) | ✓ | `eu-west` | Data residency |
| is_active | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `tenant_pkey`, `tenant_code_key` (UNIQUE)

---

## site

Industrial plant / deployment site.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| code | varchar(20) | ✓ | | **UNIQUE** |
| name | varchar(255) | ✓ | | |
| address | text | ✓ | | |
| city | varchar(100) | ✓ | | |
| lat | float8 | ✓ | | |
| lng | float8 | ✓ | | |
| geom | geometry(Point,4326) | | | PostGIS point |
| num_shifts | integer | ✓ | 1 | 1–3 shifts |
| shift_1_entry | time | | | |
| shift_1_exit | time | | | |
| shift_1_type | varchar(50) | | | e.g. `matin` |
| shift_1_depart_h2 | time | | | 2nd departure slot |
| shift_1_retour_h2 | time | | | 2nd return slot |
| shift_2_entry | time | | | |
| shift_2_exit | time | | | |
| shift_2_type | varchar(50) | | | |
| shift_2_depart_h2 | time | | | |
| shift_2_retour_h2 | time | | | |
| shift_3_entry | time | | | |
| shift_3_exit | time | | | |
| shift_3_type | varchar(50) | | | |
| shift_3_depart_h2 | time | | | |
| shift_3_retour_h2 | time | | | |
| active_shift_ids | jsonb | ✓ | `[]` | Active shift IDs array |
| working_days | varchar(100) | | `Lundi-Vendredi` | |
| days_per_week | integer | | 5 | |
| contact_name | varchar(100) | | | |
| contact_phone | varchar(50) | | | |
| access_notes | text | | | |
| parking_notes | text | | | |
| zfe_zone | boolean | ✓ | false | Low emission zone |
| security_profile | varchar(20) | ✓ | `normal` | `normal`/`elevated`/`high` |
| timezone | varchar(50) | ✓ | `Europe/Paris` | |
| observations | text | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `site_pkey`, `site_code_key` (UNIQUE), `ix_site_tenant_id`, `idx_site_geom` (GIST), `ix_site_geom` (GIST)

---

## user

Portal accounts (admin, operator, viewer).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| email | varchar(255) | ✓ | | UNIQUE per tenant |
| password_hash | varchar(255) | | | bcrypt |
| first_name | varchar(100) | | | |
| last_name | varchar(100) | | | |
| role_id | uuid | ✓ | | FK → role.id |
| employee_id | uuid | | | FK → employee.id (optional) |
| mfa_enabled | boolean | ✓ | false | |
| mfa_secret | varchar(255) | | | TOTP secret |
| last_login_at | timestamptz | | | |
| is_active | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `user_pkey`, `uq_user_tenant_email` UNIQUE(tenant_id, email)

---

## role

RBAC roles per tenant.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| name | varchar(100) | ✓ | | e.g. `admin` |
| description | text | | | |
| is_system | boolean | ✓ | false | Built-in role flag |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `role_pkey`

---

## permission

RBAC permission actions.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| action | varchar(100) | ✓ | | **UNIQUE** e.g. `vehicles:write` |
| resource | varchar(50) | ✓ | | |
| description | text | | | |
| created_at | timestamptz | ✓ | now() | |

**Indexes:** `permission_pkey`, UNIQUE(action)

---

## role_permission

Many-to-many Role ↔ Permission mapping.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| role_id | uuid | ✓ | | FK → role.id |
| permission_id | uuid | ✓ | | FK → permission.id |
| created_at | timestamptz | ✓ | now() | |

**Indexes:** `role_permission_pkey`, `uq_role_permission` UNIQUE(role_id, permission_id)

---

## employee

Core employee master data with geo-coordinates. **1,200 rows seeded.**

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| matricule | varchar(50) | ✓ | | UNIQUE per tenant |
| first_name | varchar(100) | ✓ | | |
| last_name | varchar(100) | ✓ | | |
| department | varchar(100) | | | |
| function_role | varchar(100) | | | |
| phone | varchar(50) | | | |
| shift_time | varchar(50) | | | `P1`/`P2`/`P3`/`N`/`St` |
| address | text | | | |
| quartier | varchar(100) | | | Neighbourhood |
| city | varchar(100) | | | |
| lat | float8 | | | Home GPS latitude |
| lng | float8 | | | Home GPS longitude |
| geom | geometry(Point,4326) | | | PostGIS home point |
| preferred_pickup_address | text | | | |
| preferred_pickup_lat | float8 | | | |
| preferred_pickup_lng | float8 | | | |
| is_pmr | boolean | ✓ | false | Reduced mobility |
| transport_required | boolean | ✓ | true | |
| current_transport_mode | varchar(50) | | | |
| opt_in_company_transport | varchar(20) | ✓ | `Non` | `Oui`/`Non` |
| has_private_car | boolean | ✓ | false | |
| volunteer_driver | boolean | ✓ | false | Carpooling driver |
| carpool_seats | integer | ✓ | 0 | |
| active | boolean | ✓ | true | |
| sirh_external_id | varchar(100) | | | SIRH sync key |
| hire_date | date | | | |
| end_date | date | | | |
| point_arret_id | uuid | | | FK → point_arret.id |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `employee_pkey`, `uq_employee_tenant_matricule` UNIQUE(tenant_id, matricule), `ix_employee_tenant_id`, `ix_employee_site_id`, `ix_employee_active`, `idx_employee_geom` (GIST), `ix_employee_geom` (GIST), `ix_employee_point_arret_id`

---

## employee_modal

Transport mode survey per employee (one-to-one with employee).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| employee_id | uuid | ✓ | | FK → employee.id — **UNIQUE** |
| primary_mode | varchar(50) | ✓ | | `company_bus`/`personal_car`/`walk` |
| alternative_mode | varchar(50) | | | |
| distance_km | numeric | | | |
| travel_time_min | integer | | | |
| frequency | varchar(50) | | | |
| interest_company_transport | varchar(30) | | | |
| reason_current_mode | text | | | |
| departure_time | time | | | |
| accepts_common_pickup | boolean | ✓ | true | |
| max_pickup_distance_meters | integer | ✓ | 500 | |
| has_private_car | boolean | ✓ | false | |
| volunteer_driver | boolean | ✓ | false | |
| carpool_seats_available | integer | ✓ | 0 | |
| max_detour_minutes | integer | | | |
| bonus_opt_in | boolean | ✓ | false | |
| observations | text | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `employee_modal_pkey`, UNIQUE(employee_id)

---

## employee_leave

Leaves / absences tracking.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| employee_id | uuid | ✓ | | FK → employee.id |
| leave_type | varchar(50) | ✓ | | `conge_annuel`/`maladie`/etc. |
| start_date | date | ✓ | | |
| end_date | date | ✓ | | |
| notes | text | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `employee_leave_pkey`, `idx_leave_dates` BTREE(start_date, end_date)

---

## vehicle

Fleet inventory. **106 rows seeded.**  
Default rates: AUTOCAR 4.50 MAD/km · MINIBUS 3.20 MAD/km · MINICAR 2.50 MAD/km

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | | | FK → site.id |
| type | varchar(50) | ✓ | | `AUTOCAR`/`MINIBUS`/`MINICAR` |
| brand_model | varchar(100) | | | |
| matricule | varchar(30) | | | License plate |
| capacity | integer | ✓ | | Seating capacity |
| year | integer | | | |
| motorization | varchar(30) | | | `Diesel`/`CNG`/`Electric` |
| owner_type | varchar(50) | | | Ownership category |
| prestataire | varchar(100) | | | Operator company name |
| monthly_cost_mad | numeric | | | MAD/month |
| monthly_km | numeric | | | |
| condition | varchar(20) | ✓ | `Bon` | `Bon`/`Moyen`/`Mauvais` |
| is_pmr_accessible | boolean | ✓ | false | Wheelchair accessible |
| fuel_consumption | numeric | | | L/100km |
| cost_per_km | numeric | | | MAD/km |
| length_meters | numeric | | | |
| zfe_compliant | boolean | ✓ | false | Low emission zone |
| circulation_date | date | | | First registration |
| observations | text | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `vehicle_pkey`, `idx_vehicle_tenant`, `idx_vehicle_site`

---

## vehicle_reference

Standard reference catalog per vehicle type (not fleet-specific).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| type | varchar(50) | ✓ | | `AUTOCAR`/`MINIBUS`/`MINICAR` |
| capacity_min | integer | | | |
| capacity_max | integer | | | |
| motorizations_available | jsonb | | `[]` | Available motorizations array |
| recommended_use | text | | | |
| reference_tco_5y | jsonb | | `{}` | 5-year TCO reference data |
| length_meters | numeric | | | |
| zfe_compliant | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `vehicle_reference_pkey`

---

## point_arret

Bus stops / gathering points on routes.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| name | varchar(200) | ✓ | | |
| address | text | | | |
| city | varchar(100) | | | |
| lat | float8 | ✓ | | |
| lng | float8 | ✓ | | |
| geom | geometry(Point,4326) | | | PostGIS point |
| quartier | varchar(100) | | | |
| is_active | boolean | ✓ | true | |
| capacity | integer | | | Max passengers |
| security_risk | varchar(20) | ✓ | `low` | `low`/`medium`/`high` |
| observations | text | | | |
| created_at | timestamptz | ✓ | now() | |

**Indexes:** `point_arret_pkey`, `idx_point_arret_site`, `idx_point_arret_geom` (GIST)

---

## configuration_plan

Versioned transport plan container. One plan flagged `is_current=true` at a time.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| name | varchar(200) | ✓ | | |
| description | text | | | |
| is_active | boolean | ✓ | true | |
| is_current | boolean | ✓ | false | Only one true at a time |
| source | varchar(50) | | | `upload`/`optimizer` |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `configuration_plan_pkey`, `ix_configuration_plan_tenant`

---

## configuration_transport

Individual circuit rows within a plan. **591 rows seeded** (imported from Excel).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| plan_id | uuid | ✓ | | FK → configuration_plan.id |
| site_id | uuid | | | FK → site.id |
| prestataire | varchar(100) | ✓ | | Transport operator |
| conducteur | varchar(200) | | | Driver name |
| mle_vehicule | varchar(50) | | | Vehicle registration |
| type_vehicule | varchar(50) | | | `AUTOCAR`/`MINIBUS`/`MINICAR` |
| type_moteur | varchar(50) | | | Engine type |
| poste | varchar(20) | | | Internal circuit code |
| shift | varchar(10) | | | `P1`/`P2`/`P3`/`N`/`St` |
| secteur | varchar(100) | | | Zone/sector |
| entite | varchar(200) | | | Business unit |
| aller_retour | varchar(10) | | | `ALLER`/`RETOUR` |
| heure_depart | varchar(25) | | | Departure time (string) |
| point_depart | varchar(200) | | | Origin stop name |
| point_arrivee | varchar(200) | | | Destination stop name |
| heure_arrivee | varchar(25) | | | Arrival time (string) |
| arrets_circuit | varchar(500) | | | Intermediate stops string |
| duree_trajet_min | integer | | | Trip duration minutes |
| km | numeric(8,2) | | | Distance km |
| rot | numeric(6,2) | | | Number of rotations |
| t_km | numeric(8,2) | | | Total km (km × rot) |
| is_active | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `configuration_transport_pkey`, `ix_configuration_transport_tenant`, `ix_configuration_transport_plan`, `ix_configuration_transport_poste`

---

## optimization

Optimization run metadata and aggregated results.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| status | varchar(20) | ✓ | `pending` | `pending`/`running`/`completed`/`failed` |
| algorithm | varchar(50) | | | `kmeans`/`vrp`/`greedy` |
| total_vehicles | integer | | | |
| total_distance_km | numeric | | | |
| total_cost_mad | numeric | | | |
| results_summary | jsonb | | `{}` | Key metrics blob |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `optimization_pkey`, `idx_optimization_tenant`, `idx_optimization_site`

---

## optimization_settings

Optimizer parameters per run.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| max_walking_distance_m | integer | ✓ | 500 | |
| max_detour_pct | numeric | ✓ | 20 | |
| algorithm | varchar(50) | ✓ | `kmeans` | |
| vehicle_types | jsonb | | `[]` | Allowed vehicle types |
| shift_ids | jsonb | | `[]` | Target shifts |
| pmr_dedicated_vehicle | boolean | ✓ | false | |
| zfe_only | boolean | ✓ | false | |
| max_route_duration_min | integer | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `optimization_settings_pkey`

---

## cluster

Geo-clusters of employees produced by the optimizer.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| optimization_id | uuid | ✓ | | FK → optimization.id |
| site_id | uuid | ✓ | | FK → site.id |
| centroid_lat | float8 | ✓ | | |
| centroid_lng | float8 | ✓ | | |
| centroid_geom | geometry(Point,4326) | | | PostGIS centroid |
| employee_count | integer | ✓ | 0 | |
| pmr_count | integer | ✓ | 0 | |
| security_risk_level | varchar(20) | ✓ | `low` | |
| employee_ids | uuid[] | ✓ | `{}` | Array of employee UUIDs |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `cluster_pkey`, `idx_cluster_optimization`, `idx_cluster_centroid_geom` (GIST)

---

## route

Computed vehicle route per optimization run.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| optimization_id | uuid | ✓ | | FK → optimization.id |
| vehicle_id | uuid | | | FK → vehicle.id |
| site_id | uuid | ✓ | | FK → site.id |
| ordered_stops | jsonb | ✓ | `[]` | Ordered stop list with coordinates |
| total_distance_km | numeric | | | |
| total_time_minutes | numeric | | | |
| polyline | text | | | Encoded Google polyline |
| geom | geometry | | | Route line geometry |
| rti_compliance_pct | numeric | | | RTI compliance percentage |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `route_pkey`, `idx_route_optimization`, `idx_route_geom` (GIST)

---

## horaire_travail

Shift schedule templates per site.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| shift_code | varchar(10) | ✓ | | `P1`/`P2`/`P3`/`N` |
| entry_time | time | ✓ | | |
| exit_time | time | ✓ | | |
| days_of_week | jsonb | | `[]` | Active days array |
| effective_from | date | | | |
| is_active | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `horaire_travail_pkey`

---

## constraint_param

Configurable business rules (key-value store per tenant).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| key | varchar(100) | ✓ | | UNIQUE per tenant |
| value | varchar(500) | ✓ | | |
| category | varchar(50) | ✓ | `general` | `general`/`optimizer`/`financial` |
| description | varchar(500) | | | |
| is_active | boolean | ✓ | true | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `constraint_param_pkey`, `uq_constraint_param_tenant_key` UNIQUE(tenant_id, key), `idx_constraint_param_tenant`

---

## kpi_snapshot

Daily KPI cache — pre-aggregated metrics for dashboard performance.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | | | FK → site.id |
| snapshot_date | date | ✓ | | |
| metrics | jsonb | ✓ | `{}` | All KPIs as JSON blob |
| computed_at | timestamptz | ✓ | now() | |
| created_at | timestamptz | ✓ | now() | |

**Indexes:** `kpi_snapshot_pkey`, `idx_kpi_snapshot_date`

---

## km_consommation

Monthly mileage actuals per vehicle.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | | | FK → site.id |
| vehicle_id | uuid | | | FK → vehicle.id |
| period_month | integer | ✓ | | 1–12 |
| period_year | integer | ✓ | | |
| km_planned | numeric | | | |
| km_actual | numeric | | | |
| cost_mad | numeric | | | |
| fuel_liters | numeric | | | |
| notes | text | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `km_consommation_pkey`

---

## financial_scenario

TCO/ROI financial simulation container.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| name | varchar(255) | ✓ | | |
| investment_model | varchar(30) | ✓ | | `achat`/`leasing`/`prestataire` |
| duration_years | integer | ✓ | 5 | |
| fleet_composition | jsonb | | `{}` | Vehicle type mix |
| params | jsonb | | `{}` | Input parameters |
| results | jsonb | | `{}` | Computed results blob |
| created_by | uuid | | | FK → user.id |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `financial_scenario_pkey`, `idx_financial_scenario_tenant`

---

## tco_entry

TCO line items per vehicle type within a financial scenario.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| financial_scenario_id | uuid | ✓ | | FK → financial_scenario.id |
| vehicle_type | varchar(50) | ✓ | | `AUTOCAR`/`MINIBUS`/`MINICAR` |
| motorization | varchar(30) | | | |
| quantity | integer | ✓ | 1 | |
| purchase_price | numeric | | | MAD |
| annual_maintenance_cost | numeric | | | MAD/year |
| energy_cost_per_km | numeric | | | MAD/km |
| annual_km | numeric | | | |
| residual_value | numeric | | | MAD at end of period |
| infrastructure_cost | numeric | | | MAD |
| tco_per_vehicle | numeric | | | Computed |
| tco_total | numeric | | | Computed |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `tco_entry_pkey`, `idx_tco_entry_financial_scenario`

---

## roi_calculation

ROI outputs per year per financial scenario.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| financial_scenario_id | uuid | ✓ | | FK → financial_scenario.id |
| year | integer | ✓ | | Year 1–N |
| revenue_mad | numeric | | | |
| cost_mad | numeric | | | |
| net_mad | numeric | | | |
| cumulative_net_mad | numeric | | | |
| employee_contribution | numeric | | | |
| savings_vs_baseline | numeric | | | |
| co2_saved_tons | numeric | | | |
| accidents_avoided | numeric | | | |
| absenteeism_reduction_pct | numeric | | | |
| productivity_gain_mad | numeric | | | |
| irr_pct | numeric | | | Internal Rate of Return |
| npv_mad | numeric | | | Net Present Value |
| payback_months | numeric | | | |
| tco_per_employee_mad | numeric | | | |
| cost_per_km_mad | numeric | | | |
| vehicles_needed | integer | | | |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `roi_calculation_pkey`

---

## scenario

What-if simulation scenarios using demand multipliers.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| site_id | uuid | ✓ | | FK → site.id |
| baseline_optimization_id | uuid | | | FK → optimization.id |
| name | varchar(100) | | | |
| condition_type | varchar(30) | ✓ | `normal` | `normal`/`greve`/`intemperie`/`effectif_reduit` |
| demand_multiplier | float8 | ✓ | 1.0 | Applied to employee count |
| custom_params | json | ✓ | `{}` | Override parameters |
| estimated_metrics | json | ✓ | `{}` | Computed scenario metrics |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `scenario_pkey`, `idx_scenario_tenant`, `idx_scenario_site`

---

## generated_report

Async report generation metadata and download links.

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| tenant_id | uuid | ✓ | | FK → tenant.id |
| report_type | varchar(50) | ✓ | | `kpi_monthly`/`fleet_audit`/`roi`/etc. |
| params | jsonb | | `{}` | Generation parameters |
| file_url | text | | | Download URL |
| format | varchar(10) | | | `pdf`/`xlsx` |
| generated_at | timestamptz | ✓ | now() | |
| generated_by | uuid | | | FK → user.id |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `generated_report_pkey`

---

## weather_forecast

Open-Meteo forecast cache per site (no API key required).

| Column | Type | NN | Default | Notes |
|---|---|---|---|---|
| **id** | uuid | ✓ | gen_random_uuid() | **PK** |
| site_id | uuid | ✓ | | FK → site.id |
| date | date | ✓ | | Forecast date |
| condition_summary | varchar(100) | | | e.g. `Partly Cloudy` |
| precipitation_mm | numeric | | | |
| temp_min_c | numeric | | | |
| temp_max_c | numeric | | | |
| wind_kph | numeric | | | |
| fetched_at | timestamptz | ✓ | now() | |
| source | varchar(50) | | | `open-meteo` |
| created_at | timestamptz | ✓ | now() | |
| updated_at | timestamptz | ✓ | now() | |

**Indexes:** `weather_forecast_pkey`, `uq_weather_site_date_source` UNIQUE(site_id, date, source), `idx_weather_forecast_site_id`

---

## PostGIS Geometry Columns

All use SRID 4326 (WGS84). Indexed with GIST for spatial queries.

| Table | Column | Type | Indexes |
|---|---|---|---|
| employee | geom | Point,4326 | `idx_employee_geom`, `ix_employee_geom` |
| site | geom | Point,4326 | `idx_site_geom`, `ix_site_geom` |
| point_arret | geom | Point,4326 | `idx_point_arret_geom` |
| cluster | centroid_geom | Point,4326 | `idx_cluster_centroid_geom` |
| route | geom | generic | `idx_route_geom` |

---

## Foreign Key Graph

```
tenant
  ├── site (tenant_id)
  ├── user (tenant_id) ──→ role
  ├── role (tenant_id) ──→ role_permission ──→ permission
  ├── employee (tenant_id) ──→ site, point_arret
  │     ├── employee_modal (employee_id)
  │     └── employee_leave (employee_id)
  ├── vehicle (tenant_id) ──→ site
  ├── point_arret (tenant_id) ──→ site
  ├── configuration_plan (tenant_id)
  │     └── configuration_transport (plan_id) ──→ site
  ├── optimization (tenant_id) ──→ site
  │     ├── cluster (optimization_id) ──→ site
  │     └── route (optimization_id) ──→ vehicle, site
  ├── optimization_settings (tenant_id) ──→ site
  ├── horaire_travail (tenant_id) ──→ site
  ├── constraint_param (tenant_id)
  ├── kpi_snapshot (tenant_id) ──→ site
  ├── km_consommation (tenant_id) ──→ site, vehicle
  ├── financial_scenario (tenant_id) ──→ user
  │     ├── tco_entry (financial_scenario_id)
  │     └── roi_calculation (financial_scenario_id)
  ├── scenario (tenant_id) ──→ site, optimization
  ├── generated_report (tenant_id) ──→ user
  ├── weather_forecast ──→ site
  ├── content (tenant_id) ──→ user
  └── content_delivery (tenant_id) ──→ content, employee
```

---

## content_delivery

Tracks engagement metrics per content-employee pair. Created in Session 69.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| content_id | uuid | NO | | FK → content.id |
| employee_id | uuid | NO | | FK → employee.id |
| delivered_at | timestamptz | NO | | When content was served |
| viewed_at | timestamptz | YES | | When content was opened |
| completed_at | timestamptz | YES | | When content was fully consumed |
| quiz_score | float | YES | | Quiz result (0-100) |
| time_spent_seconds | int | YES | | Seconds spent consuming content |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** tenant_id, content_id, employee_id, UNIQUE(content_id, employee_id)

---

## survey

Survey/poll definition linked to content. Created in Session 72.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| content_id | uuid | NO | | FK → content.id |
| title | varchar(500) | NO | | Survey title |
| description | varchar(2000) | YES | | Description |
| questions | jsonb | NO | | Array of {id, text, question_type, options, required, min/max} |
| response_count | int | NO | 0 | Auto-incremented on submission |
| is_anonymous | bool | NO | false | Clears employee_id on response |
| is_active | bool | NO | true | Closes survey when false |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Question types:** single_choice, multiple_choice, text, rating (1-5), slider (0-100)
**Indexes:** tenant_id, content_id, is_active

## survey_response

Individual survey response. Created in Session 72.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| survey_id | uuid | NO | | FK → survey.id |
| employee_id | uuid | YES | | FK → employee.id (null for anonymous) |
| responses | jsonb | NO | | Array of {question_id, value} |
| submitted_at | timestamptz | NO | | Submission timestamp |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** tenant_id, survey_id, employee_id

---

## training_module

Maps content to external LMS training modules. Created in Session 74.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| content_id | uuid | NO | | FK → content.id |
| lms_provider | varchar(50) | NO | | cornerstone/360learning/talentlms |
| lms_external_id | varchar(255) | NO | | External course/program ID |
| duration_minutes | int | YES | | Training duration |
| is_mandatory | bool | NO | false | Mandatory training flag |
| certification_name | varchar(500) | YES | | Certification awarded |
| lms_metadata | jsonb | YES | | Provider-specific metadata |
| last_synced_at | timestamptz | YES | | Last sync timestamp |
| is_active | bool | NO | true | |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** tenant_id, content_id, lms_provider, UNIQUE(tenant_id, lms_provider, lms_external_id)

---

## Group 16 — SOTREG

> Source: CDC Technique SOTREG v5.0 Final — OCP Transport Personnel. See [[sessions/session-93]], [[sessions/session-94]].

### ligne

Transport line definition with CDC formula km_annual = D x R x J. Created in Session 93.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| code | varchar(20) | NO | | UNIQUE — line identifier |
| name | varchar(255) | NO | | Line display name |
| site_id | uuid | YES | | FK → site.id |
| origin_lat | float | NO | | Origin latitude |
| origin_lng | float | NO | | Origin longitude |
| dest_lat | float | NO | | Destination latitude |
| dest_lng | float | NO | | Destination longitude |
| origin_geom | geometry(POINT,4326) | YES | | PostGIS origin point |
| dest_geom | geometry(POINT,4326) | YES | | PostGIS destination point |
| distance_km | float | NO | | One-way distance D (km) |
| rotations_per_day | int | NO | | Daily rotations R |
| operating_days_per_year | int | NO | | Operating days J |
| km_annual | float | YES | | Computed: D x R x J |
| vehicle_type | varchar(50) | YES | | Bus/minibus/van/etc. |
| motorization | varchar(30) | YES | | diesel/electric/hybrid/gnc |
| passenger_count_avg | int | YES | | Average passenger count |
| shift_type | varchar(50) | YES | | Associated shift |
| service_type | varchar(20) | YES | | navette/liaison/vip/mixte |
| pente_moyenne_pct | float | YES | | Average slope percentage |
| is_active | bool | NO | true | Active line flag |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** tenant_id, site_id, UNIQUE(tenant_id, code), GIST(origin_geom), GIST(dest_geom)

---

### fleet_context

Fleet diagnostics snapshot aggregated from all lignes. Created in Session 93.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| total_vehicles | int | NO | | Total fleet size |
| total_km_annual | float | NO | | Sum of all ligne km_annual |
| total_tco2_annual | float | NO | | Estimated annual tCO2 |
| average_age_years | float | YES | | Fleet average age |
| pct_diesel | float | YES | | % diesel motorization |
| pct_electric | float | YES | | % electric motorization |
| pct_hybrid | float | YES | | % hybrid motorization |
| currency | varchar(10) | NO | MAD | Financial currency |
| snapshot_date | date | NO | | Snapshot capture date |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** tenant_id, snapshot_date

---

### od_matrix

OD (Origin-Destination) matrix entries computed using Wilson 1967 gravity model: T_ij = k * P_i * P_j * exp(-beta * d_ij). Created in Session 94.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| ligne_id | uuid | NO | | FK → ligne.id (CASCADE) |
| origin_zone | varchar(255) | NO | | Origin zone name |
| destination_zone | varchar(255) | NO | | Destination zone name |
| flow_estimate | float | NO | | Estimated flow T_ij |
| distance_km | float | NO | | Distance between zones |
| gravity_score | float | NO | | Gravity model score |
| beta_used | float | NO | 0.08 | Beta decay parameter |
| computed_at | timestamptz | NO | now() | Computation timestamp |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_od_matrix_tenant_id, ix_od_matrix_ligne_id

### irve_infrastructure

IRVE (Infrastructure de Recharge pour Vehicules Electriques) record. Created in Session 97.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| site_id | uuid | YES | | FK → site.id |
| charger_type | varchar(30) | NO | dc_50kw | ac_7kw, ac_22kw, dc_50kw, dc_150kw |
| charger_count | int | NO | 1 | Number of chargers |
| power_per_charger_kw | float | NO | | Power per charger |
| total_installed_power_kw | float | NO | | Total installed power |
| hardware_cost_mad | float | NO | 0 | Hardware cost MAD |
| installation_cost_mad | float | NO | 0 | Installation cost MAD |
| transformer_cost_mad | float | NO | 0 | Transformer cost MAD |
| grid_connection_cost_mad | float | NO | 0 | Grid connection cost MAD |
| total_capex_mad | float | NO | 0 | Total CAPEX MAD |
| annual_electricity_cost_mad | float | NO | 0 | Annual electricity cost MAD |
| fleet_size | int | YES | | Associated fleet size |
| daily_km_per_vehicle | float | YES | | Daily km per vehicle |
| battery_capacity_kwh | float | YES | | Battery capacity kWh |
| is_active | boolean | NO | true | Active flag |
| currency | varchar(10) | NO | MAD | Currency code |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_irve_infrastructure_tenant_id, ix_irve_infrastructure_site_id

### generated_stop

Candidate stop location generated by DBSCAN clustering or manual entry. Created in Session 99.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| site_id | uuid | YES | | FK → site.id |
| ligne_id | uuid | YES | | FK → ligne.id |
| lat | float | NO | | Latitude |
| lng | float | NO | | Longitude |
| geom | geometry(POINT,4326) | YES | | PostGIS point |
| catchment_radius_m | float | NO | 500 | Catchment radius meters |
| demand_passengers | int | NO | 0 | Passenger demand |
| berth_count | int | NO | 1 | Loading berths |
| capacity_buses_per_hour | float | YES | | HCM 2000 capacity |
| capacity_los | varchar(1) | YES | | LOS grade A-F |
| avg_wait_seconds | float | YES | | Average wait time |
| source | varchar(20) | NO | dbscan | dbscan, manual, imported |
| name | varchar(255) | YES | | Stop name |
| is_active | boolean | NO | true | Active flag |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_generated_stop_tenant_id, ix_generated_stop_site_id, ix_generated_stop_geom (GIST)

### depot_plan

Depot electrification plan with layout areas and JSONB cost breakdown. Created in Session 100.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| site_id | uuid | YES | | FK → site.id |
| name | varchar(255) | YES | | Plan name |
| total_area_m2 | float | NO | | Total depot area |
| charging_area_m2 | float | NO | 0 | Charging zone area |
| parking_area_m2 | float | NO | 0 | Parking zone area |
| maintenance_area_m2 | float | NO | 0 | Maintenance zone area |
| charger_count | int | NO | 0 | Number of chargers |
| charger_type | varchar(30) | NO | dc_50kw | Charger type |
| parking_bays | int | NO | 0 | Number of parking bays |
| fleet_size | int | NO | 0 | Fleet size |
| total_cost_mad | float | NO | 0 | Total cost MAD |
| cost_breakdown | jsonb | YES | | 7-component cost breakdown |
| is_active | boolean | NO | true | Active flag |
| currency | varchar(10) | NO | MAD | Currency code |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_depot_plan_tenant_id, ix_depot_plan_site_id

### avl_metric

AVL-based operational KPI metric record. Created in Session 102.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| ligne_id | uuid | YES | | FK → ligne.id |
| vehicle_id | uuid | YES | | Vehicle UUID (no FK) |
| metric_type | varchar(30) | NO | | otp, headway_cov, load_factor, commercial_speed |
| value | float | NO | | Metric value |
| metric_date | date | NO | | Date of measurement |
| period | varchar(20) | NO | daily | daily, weekly, monthly |
| sample_size | int | YES | | Number of observations |
| meets_target | boolean | YES | | Whether target met |
| details | varchar(500) | YES | | JSON details string |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_avl_metric_tenant_id, ix_avl_metric_ligne_id, ix_avl_metric_vehicle_id, ix_avl_metric_metric_type, ix_avl_metric_date

### departure_schedule

LTO optimized departure schedule from anti-platooning optimization. Created in Session 103.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| id | uuid | NO | gen_random_uuid() | PK |
| tenant_id | uuid | NO | | FK → tenant.id |
| ligne_id | uuid | NO | | FK → ligne.id |
| vehicle_id | uuid | YES | | Vehicle UUID |
| scheduled_departure | timestamptz | NO | | Original departure time |
| optimized_departure | timestamptz | NO | | LTO-adjusted departure time |
| offset_seconds | float | NO | 0 | Adjustment offset |
| schedule_date | date | NO | | Schedule date |
| is_applied | boolean | NO | false | Whether applied to operations |
| optimization_run_id | varchar(50) | YES | | Run identifier |
| created_at | timestamptz | NO | now() | |
| updated_at | timestamptz | NO | now() | |

**Indexes:** ix_departure_schedule_tenant_id, ix_departure_schedule_ligne_id, ix_departure_schedule_date

---

## Alembic Migration State

| Item | Value |
|---|---|
| Migration directory | `backend/alembic/versions/` |
| Auto-applied on startup | Yes — `alembic upgrade head` in `start_production.sh` |
| Current revision | Query: `SELECT version_num FROM alembic_version;` |
