# Transpop — Complete Database Schema

> PostgreSQL 15+ with PostGIS extension
> ORM: SQLAlchemy 2.0 + GeoAlchemy2
> Migrations: Alembic
>
> See also: [[ARCHITECTURE]] | [[API_ENDPOINTS]] | [[agents]]

## Table Overview

| Group | Tables | Session |
|-------|--------|---------|
| Auth & Multi-Tenant | Tenant, User, Role, Permission, RolePermission | [[sessions/session-04\|04]] |
| Core — Sites | Site | [[sessions/session-06\|06]] |
| Core — Employees | Employee, EmployeeModal, EmployeeLeave | [[sessions/session-09\|09]], [[sessions/session-12\|12]], [[sessions/session-15\|15]] |
| Core — Vehicles | Vehicle | [[sessions/session-20\|20]] |
| Core — Constraints | Constraint, Settings | [[sessions/session-29\|29]] |
| Optimization | Cluster, Route, Optimization, Scenario | [[sessions/session-18\|18]], [[sessions/session-22\|22]], [[sessions/session-23\|23]], [[sessions/session-27\|27]] |
| Weather | WeatherForecast | [[sessions/session-26\|26]] |
| Financial | FinancialScenario, TCOEntry, ROICalculation, VehicleReference | [[sessions/session-31\|31]] |
| Content | Content, ContentDelivery, TrainingModule, Survey, SurveyResponse | [[sessions/session-67\|67]], [[sessions/session-69\|69]], [[sessions/session-72\|72]] |
| RTI | StopRiskScore, VehiclePosition, RTIEvent, RTIConfig | [[sessions/session-57\|57]], [[sessions/session-58\|58]] |
| Security | SecurityQuestionnaire, SecurityScore, EmergencyAlert | [[sessions/session-61\|61]], [[sessions/session-62\|62]] |
| SIRH | SIRHConnection, SyncLog, SyncConflict | [[sessions/session-77\|77]] |
| Mobile | TripBooking, DeviceRegistration, PushNotification | [[sessions/session-54\|54]] |
| Operator | Operator, SizingPlanExport | [[sessions/session-82\|82]] |
| Reporting | GeneratedReport, KPISnapshot | [[sessions/session-42\|42]], [[sessions/session-44\|44]] |

**Total: 38 tables**

---

## Group 1: Auth & Multi-Tenant

### Tenant
```sql
CREATE TABLE tenant (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(100) UNIQUE NOT NULL,
    config          JSONB DEFAULT '{}',      -- branding, defaults, feature flags
    data_region     VARCHAR(50) DEFAULT 'eu-west',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

### User
```sql
CREATE TABLE "user" (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    role_id         UUID NOT NULL REFERENCES role(id),
    employee_id     UUID REFERENCES employee(id),  -- nullable, for Salarie role
    mfa_enabled     BOOLEAN DEFAULT false,
    mfa_secret      VARCHAR(255),                   -- encrypted
    last_login_at   TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tenant_id, email)
);
```

### Role
```sql
CREATE TABLE role (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    name            VARCHAR(50) NOT NULL,  -- drh, daf, salarie, operateur, admin
    permissions     JSONB DEFAULT '[]',
    is_system_role  BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);
```

### Permission
```sql
CREATE TABLE permission (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource        VARCHAR(100) NOT NULL,  -- sites, employees, optimization, financial, content, security, admin
    action          VARCHAR(50) NOT NULL,   -- read, write, delete, supervise, emit
    UNIQUE(resource, action)
);
```

### RolePermission
```sql
CREATE TABLE role_permission (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id         UUID NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    permission_id   UUID NOT NULL REFERENCES permission(id) ON DELETE CASCADE,
    UNIQUE(role_id, permission_id)
);
```

---

## Group 2: Core — Sites

### Site
```sql
CREATE TABLE site (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenant(id),
    code                VARCHAR(20) UNIQUE NOT NULL,   -- e.g., S01
    name                VARCHAR(255) NOT NULL,
    address             TEXT NOT NULL,
    city                VARCHAR(100) NOT NULL,
    lat                 DOUBLE PRECISION NOT NULL,
    lng                 DOUBLE PRECISION NOT NULL,
    geom                GEOMETRY(Point, 4326),         -- PostGIS point
    num_shifts          INTEGER NOT NULL DEFAULT 1,    -- 1-3
    shift_1_entry       TIME,
    shift_1_exit        TIME,
    shift_2_entry       TIME,
    shift_2_exit        TIME,
    shift_3_entry       TIME,
    shift_3_exit        TIME,
    working_days        VARCHAR(100) DEFAULT 'Lundi-Vendredi',
    days_per_week       INTEGER DEFAULT 5,
    contact_name        VARCHAR(100),
    contact_phone       VARCHAR(50),
    access_notes        TEXT,
    parking_notes       TEXT,
    zfe_zone            BOOLEAN DEFAULT false,
    security_profile    VARCHAR(20) DEFAULT 'normal',  -- normal, elevated, critical
    timezone            VARCHAR(50) DEFAULT 'Europe/Paris',
    observations        TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_site_tenant ON site(tenant_id);
CREATE INDEX idx_site_geom ON site USING GIST(geom);
```

---

## Group 3: Core — Employees

### Employee
```sql
CREATE TABLE employee (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenant(id),
    matricule               VARCHAR(50) NOT NULL,
    first_name              VARCHAR(100) NOT NULL,
    last_name               VARCHAR(100) NOT NULL,
    site_id                 UUID NOT NULL REFERENCES site(id),
    shift_time              VARCHAR(50),           -- e.g., Matin, Apres-midi, Nuit
    address                 TEXT,
    quartier                VARCHAR(100),
    city                    VARCHAR(100),
    lat                     DOUBLE PRECISION,
    lng                     DOUBLE PRECISION,
    geom                    GEOMETRY(Point, 4326),
    preferred_pickup_address TEXT,
    preferred_pickup_lat    DOUBLE PRECISION,
    preferred_pickup_lng    DOUBLE PRECISION,
    is_pmr                  BOOLEAN DEFAULT false,
    function_role           VARCHAR(100),
    phone                   VARCHAR(50),
    department              VARCHAR(100),
    transport_required      BOOLEAN DEFAULT true,
    current_transport_mode  VARCHAR(50),
    opt_in_company_transport VARCHAR(20) DEFAULT 'Non',  -- Oui, Non, Sous conditions
    has_private_car         BOOLEAN DEFAULT false,
    volunteer_driver        BOOLEAN DEFAULT false,
    carpool_seats           INTEGER DEFAULT 0,
    active                  BOOLEAN DEFAULT true,
    sirh_external_id        VARCHAR(100),
    hire_date               DATE,
    end_date                DATE,
    created_at              TIMESTAMPTZ DEFAULT now(),
    updated_at              TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tenant_id, matricule)
);
CREATE INDEX idx_employee_tenant ON employee(tenant_id);
CREATE INDEX idx_employee_site ON employee(site_id);
CREATE INDEX idx_employee_geom ON employee USING GIST(geom);
CREATE INDEX idx_employee_active ON employee(active);
```

### EmployeeModal
```sql
CREATE TABLE employee_modal (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id                 UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    primary_mode                VARCHAR(50) NOT NULL,
    alternative_mode            VARCHAR(50),
    distance_km                 DECIMAL(8,2),
    travel_time_min             INTEGER,
    frequency                   VARCHAR(50),      -- Quotidien, 3-4 fois/semaine, Occasionnel
    interest_company_transport  VARCHAR(30),       -- Oui, Non, Sous conditions
    reason_current_mode         TEXT,
    departure_time              TIME,
    accepts_common_pickup       BOOLEAN DEFAULT true,
    max_pickup_distance_meters  INTEGER DEFAULT 500,
    has_private_car             BOOLEAN DEFAULT false,
    volunteer_driver            BOOLEAN DEFAULT false,
    carpool_seats_available     INTEGER DEFAULT 0,
    max_detour_minutes          INTEGER,
    bonus_opt_in                BOOLEAN DEFAULT false,
    observations                TEXT,
    created_at                  TIMESTAMPTZ DEFAULT now(),
    updated_at                  TIMESTAMPTZ DEFAULT now(),
    UNIQUE(employee_id)
);
```

### EmployeeLeave
```sql
CREATE TABLE employee_leave (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID NOT NULL REFERENCES employee(id) ON DELETE CASCADE,
    leave_type      VARCHAR(50) NOT NULL,  -- vacation, sick, unpaid, formation, mission, other
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_leave_employee ON employee_leave(employee_id);
CREATE INDEX idx_leave_dates ON employee_leave(start_date, end_date);
```

---

## Group 4: Core — Vehicles

### Vehicle
```sql
CREATE TABLE vehicle (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenant(id),
    type                VARCHAR(50) NOT NULL,       -- Minibus, Midibus, Bus standard, etc.
    brand_model         VARCHAR(100),
    capacity            INTEGER NOT NULL,
    year                INTEGER,
    owner_type          VARCHAR(50),                -- proprietaire, loueur, sous-traitant
    monthly_cost_mad    DECIMAL(12,2),
    monthly_km          DECIMAL(10,2),
    condition           VARCHAR(20) DEFAULT 'Bon',  -- Bon, Moyen, Mauvais
    site_id             UUID REFERENCES site(id),
    is_pmr_accessible   BOOLEAN DEFAULT false,
    fuel_consumption    DECIMAL(6,2),               -- L/100km
    cost_per_km         DECIMAL(8,4),
    motorization        VARCHAR(30),                -- diesel, hybrid, electric, hydrogen, gnv
    length_meters       DECIMAL(5,2),
    zfe_compliant       BOOLEAN DEFAULT false,
    observations        TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_vehicle_tenant ON vehicle(tenant_id);
CREATE INDEX idx_vehicle_site ON vehicle(site_id);
```

---

## Group 5: Core — Constraints & Settings

### Constraint
```sql
CREATE TABLE constraint_param (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    key             VARCHAR(100) NOT NULL,
    value           TEXT NOT NULL,
    description     TEXT,
    category        VARCHAR(50) NOT NULL,  -- duree, accessibilite, budget, saisonnalite, securite, rti, zfe
    created_at      TIMESTAMPTZ DEFAULT now(),
    UNIQUE(tenant_id, key)
);
```

### Settings
```sql
CREATE TABLE settings (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id                   UUID UNIQUE NOT NULL REFERENCES tenant(id),
    meeting_radius_meters       INTEGER DEFAULT 500,
    max_walking_distance_meters INTEGER DEFAULT 800,
    max_route_duration_minutes  INTEGER DEFAULT 90,
    fuel_cost_per_liter         DECIMAL(6,2) DEFAULT 12.0,
    company_lat                 DOUBLE PRECISION,
    company_lng                 DOUBLE PRECISION,
    company_name                VARCHAR(255),
    rti_max_wait_seconds        INTEGER DEFAULT 90,
    night_mode_start            TIME DEFAULT '20:00',
    night_mode_end              TIME DEFAULT '06:30',
    min_night_group_size        INTEGER DEFAULT 3,
    updated_at                  TIMESTAMPTZ DEFAULT now()
);
```

---

## Group 6: Optimization

### Optimization
```sql
CREATE TABLE optimization (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    site_id         UUID REFERENCES site(id),       -- null for global
    condition_type  VARCHAR(30) DEFAULT 'normal',    -- normal, rain, strike, peak, night, transit_failure
    status          VARCHAR(20) DEFAULT 'pending',   -- pending, running, completed, failed
    params          JSONB DEFAULT '{}',
    metrics         JSONB DEFAULT '{}',
    target_date     DATE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_optimization_tenant ON optimization(tenant_id);
```

### Cluster
```sql
CREATE TABLE cluster (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    optimization_id     UUID NOT NULL REFERENCES optimization(id) ON DELETE CASCADE,
    site_id             UUID NOT NULL REFERENCES site(id),
    centroid_lat        DOUBLE PRECISION NOT NULL,
    centroid_lng        DOUBLE PRECISION NOT NULL,
    centroid_geom       GEOMETRY(Point, 4326),
    employee_count      INTEGER DEFAULT 0,
    pmr_count           INTEGER DEFAULT 0,
    security_risk_level VARCHAR(20) DEFAULT 'low',  -- low, medium, high
    employee_ids        UUID[] DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_cluster_optimization ON cluster(optimization_id);
```

### Route
```sql
CREATE TABLE route (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    optimization_id     UUID NOT NULL REFERENCES optimization(id) ON DELETE CASCADE,
    vehicle_id          UUID REFERENCES vehicle(id),
    site_id             UUID NOT NULL REFERENCES site(id),
    ordered_stops       JSONB NOT NULL DEFAULT '[]',
    total_distance_km   DECIMAL(10,2),
    total_time_minutes  DECIMAL(8,2),
    polyline            TEXT,                -- encoded polyline
    geom                GEOMETRY(LineString, 4326),
    rti_compliance_pct  DECIMAL(5,2),
    created_at          TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_route_optimization ON route(optimization_id);
```

### Scenario
```sql
CREATE TABLE scenario (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id               UUID NOT NULL REFERENCES tenant(id),
    site_id                 UUID REFERENCES site(id),
    baseline_optimization_id UUID REFERENCES optimization(id),
    name                    VARCHAR(255),
    condition_type          VARCHAR(30) NOT NULL DEFAULT 'normal',  -- normal, rain, strike, peak, night, transit_failure
    demand_multiplier       DECIMAL(4,2) DEFAULT 1.0,
    custom_params           JSONB DEFAULT '{}',
    estimated_metrics       JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_scenario_tenant ON scenario(tenant_id);
CREATE INDEX idx_scenario_site ON scenario(site_id);
```

---

## Group 7: Weather

### WeatherForecast
```sql
CREATE TABLE weather_forecast (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id             UUID NOT NULL REFERENCES site(id),
    date                DATE NOT NULL,
    condition_summary   VARCHAR(100),
    precipitation_mm    DECIMAL(6,2),
    temp_min_c          DECIMAL(5,2),
    temp_max_c          DECIMAL(5,2),
    wind_kph            DECIMAL(6,2),
    fetched_at          TIMESTAMPTZ DEFAULT now(),
    source              VARCHAR(50),
    UNIQUE(site_id, date, source)
);
```

---

## Group 8: Financial Engineering

### FinancialScenario
```sql
CREATE TABLE financial_scenario (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenant(id),
    name                VARCHAR(255) NOT NULL,
    investment_model    VARCHAR(30) NOT NULL,  -- capex, mise_a_disposition, opex
    duration_years      INTEGER NOT NULL DEFAULT 5,
    fleet_composition   JSONB DEFAULT '{}',
    params              JSONB DEFAULT '{}',
    results             JSONB DEFAULT '{}',
    created_by          UUID REFERENCES "user"(id),
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
```

### TCOEntry
```sql
CREATE TABLE tco_entry (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    financial_scenario_id   UUID NOT NULL REFERENCES financial_scenario(id) ON DELETE CASCADE,
    vehicle_type            VARCHAR(50) NOT NULL,
    motorization            VARCHAR(30),
    quantity                INTEGER NOT NULL DEFAULT 1,
    purchase_price          DECIMAL(14,2),
    annual_maintenance_cost DECIMAL(12,2),
    energy_cost_per_km      DECIMAL(8,4),
    annual_km               DECIMAL(12,2),
    residual_value          DECIMAL(14,2),
    infrastructure_cost     DECIMAL(14,2),
    tco_per_vehicle         DECIMAL(14,2),
    tco_total               DECIMAL(14,2)
);
```

### ROICalculation
```sql
CREATE TABLE roi_calculation (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    financial_scenario_id   UUID NOT NULL REFERENCES financial_scenario(id) ON DELETE CASCADE,
    baseline_absence_rate   DECIMAL(5,4),
    target_absence_rate     DECIMAL(5,4),
    headcount               INTEGER,
    daily_cost              DECIMAL(10,2),
    replacement_cost        DECIMAL(12,2),
    turnover_rate_before    DECIMAL(5,4),
    turnover_rate_after     DECIMAL(5,4),
    training_hour_cost      DECIMAL(8,2),
    engagement_rate         DECIMAL(5,4),
    annual_travel_hours     DECIMAL(8,2),
    roi_absenteeism         DECIMAL(14,2),
    roi_retention           DECIMAL(14,2),
    roi_journey             DECIMAL(14,2),
    roi_fleet_optimization  DECIMAL(14,2),
    roi_total               DECIMAL(14,2),
    payback_months          DECIMAL(6,1)
);
```

### VehicleReference
```sql
CREATE TABLE vehicle_reference (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type                    VARCHAR(50) NOT NULL,  -- minibus, midibus, bus_standard, grand_bus, vehicule_leger
    capacity_min            INTEGER,
    capacity_max            INTEGER,
    motorizations_available JSONB DEFAULT '[]',
    recommended_use         TEXT,
    reference_tco_5y        JSONB DEFAULT '{}',    -- per motorization
    length_meters           DECIMAL(5,2),
    zfe_compliant           BOOLEAN DEFAULT true
);
```

---

## Group 9: Content & Journey Valorization

### Content
```sql
CREATE TABLE content (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id           UUID NOT NULL REFERENCES tenant(id),
    title               VARCHAR(255) NOT NULL,
    body                TEXT,
    content_type        VARCHAR(30) NOT NULL,  -- news, training, safety, survey
    media_url           TEXT,
    target_sites        JSONB,                 -- array of site_ids, null = all
    target_departments  JSONB,
    target_shifts       JSONB,
    published_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    created_by          UUID REFERENCES "user"(id),
    is_active           BOOLEAN DEFAULT true,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
```

### ContentDelivery
```sql
CREATE TABLE content_delivery (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id          UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    employee_id         UUID NOT NULL REFERENCES employee(id),
    delivered_at        TIMESTAMPTZ DEFAULT now(),
    viewed_at           TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    quiz_score          DECIMAL(5,2),
    time_spent_seconds  INTEGER DEFAULT 0
);
CREATE INDEX idx_delivery_content ON content_delivery(content_id);
CREATE INDEX idx_delivery_employee ON content_delivery(employee_id);
```

### TrainingModule
```sql
CREATE TABLE training_module (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id          UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    lms_external_id     VARCHAR(255),
    duration_minutes    INTEGER,
    is_mandatory        BOOLEAN DEFAULT false,
    certification_name  VARCHAR(255)
);
```

### Survey
```sql
CREATE TABLE survey (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id          UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    questions           JSONB NOT NULL DEFAULT '[]',
    response_count      INTEGER DEFAULT 0,
    is_anonymous        BOOLEAN DEFAULT true
);
```

### SurveyResponse
```sql
CREATE TABLE survey_response (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id           UUID NOT NULL REFERENCES survey(id) ON DELETE CASCADE,
    employee_id         UUID REFERENCES employee(id),  -- nullable if anonymous
    responses           JSONB NOT NULL,
    submitted_at        TIMESTAMPTZ DEFAULT now()
);
```

---

## Group 10: RTI (Real-Time Information)

### StopRiskScore
```sql
CREATE TABLE stop_risk_score (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id                 UUID NOT NULL REFERENCES site(id),
    location_lat            DOUBLE PRECISION NOT NULL,
    location_lng            DOUBLE PRECISION NOT NULL,
    geom                    GEOMETRY(Point, 4326),
    stop_name               VARCHAR(255),
    isolation_score         DECIMAL(3,2) DEFAULT 0,   -- 0-1
    lighting_score          DECIMAL(3,2) DEFAULT 0,   -- 0-1
    tc_frequency_score      DECIMAL(3,2) DEFAULT 0,   -- 0-1
    night_risk_multiplier   DECIMAL(3,2) DEFAULT 1.0,
    employee_perception_avg DECIMAL(3,2) DEFAULT 0,
    composite_risk_score    DECIMAL(3,2) DEFAULT 0,   -- 0-1
    is_critical             BOOLEAN DEFAULT false,
    last_assessed_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_stop_risk_site ON stop_risk_score(site_id);
CREATE INDEX idx_stop_risk_geom ON stop_risk_score USING GIST(geom);
```

### VehiclePosition
```sql
CREATE TABLE vehicle_position (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id          UUID NOT NULL REFERENCES vehicle(id),
    route_id            UUID REFERENCES route(id),
    lat                 DOUBLE PRECISION NOT NULL,
    lng                 DOUBLE PRECISION NOT NULL,
    heading             DECIMAL(5,2),
    speed_kph           DECIMAL(6,2),
    timestamp           TIMESTAMPTZ DEFAULT now(),
    next_stop_eta_seconds INTEGER
);
CREATE INDEX idx_vpos_vehicle ON vehicle_position(vehicle_id);
CREATE INDEX idx_vpos_timestamp ON vehicle_position(timestamp);
```

### RTIEvent
```sql
CREATE TABLE rti_event (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stop_id             UUID NOT NULL REFERENCES stop_risk_score(id),
    route_id            UUID NOT NULL REFERENCES route(id),
    scheduled_arrival   TIMESTAMPTZ NOT NULL,
    actual_arrival      TIMESTAMPTZ,
    wait_time_seconds   INTEGER,
    compliant           BOOLEAN,        -- <=90s
    date                DATE NOT NULL
);
CREATE INDEX idx_rti_event_date ON rti_event(date);
```

### RTIConfig
```sql
CREATE TABLE rti_config (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id                 UUID UNIQUE NOT NULL REFERENCES site(id),
    max_wait_seconds        INTEGER DEFAULT 90,
    compliance_target_pct   DECIMAL(5,2) DEFAULT 95.0,
    buffer_vehicle_count    INTEGER DEFAULT 0,
    night_mode_start        TIME DEFAULT '20:00',
    night_mode_end          TIME DEFAULT '06:30'
);
```

---

## Group 11: Security

### SecurityQuestionnaire
```sql
CREATE TABLE security_questionnaire (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id             UUID NOT NULL REFERENCES employee(id),
    submitted_at            TIMESTAMPTZ DEFAULT now(),
    questionnaire_version   INTEGER DEFAULT 1,
    overall_safety_rating   INTEGER,           -- 1-5
    responses               JSONB DEFAULT '{}',
    vulnerable_stops        JSONB DEFAULT '[]', -- [{lat, lng, description}]
    night_concerns          TEXT
);
CREATE INDEX idx_secq_employee ON security_questionnaire(employee_id);
```

### SecurityScore
```sql
CREATE TABLE security_score (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id             UUID UNIQUE NOT NULL REFERENCES employee(id),
    score                   INTEGER,            -- 0-100, higher = safer
    risk_level              VARCHAR(20),        -- low, medium, high, critical
    last_calculated_at      TIMESTAMPTZ DEFAULT now(),
    contributing_factors    JSONB DEFAULT '{}'
);
```

### EmergencyAlert
```sql
CREATE TABLE emergency_alert (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id             UUID NOT NULL REFERENCES employee(id),
    triggered_at            TIMESTAMPTZ DEFAULT now(),
    location_lat            DOUBLE PRECISION,
    location_lng            DOUBLE PRECISION,
    alert_type              VARCHAR(30),        -- emergency_button, system_trigger
    responders_notified     JSONB DEFAULT '[]',
    resolved_at             TIMESTAMPTZ,
    resolution_notes        TEXT
);
```

---

## Group 12: SIRH Sync

### SIRHConnection
```sql
CREATE TABLE sirh_connection (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    provider        VARCHAR(50) NOT NULL,   -- sap, workday, talentsoft, sage
    config          JSONB DEFAULT '{}',     -- encrypted credentials, endpoints
    sync_frequency  VARCHAR(20) DEFAULT 'daily',
    last_sync_at    TIMESTAMPTZ,
    status          VARCHAR(20) DEFAULT 'active'  -- active, error, disabled
);
```

### SyncLog
```sql
CREATE TABLE sync_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sirh_connection_id  UUID NOT NULL REFERENCES sirh_connection(id),
    started_at          TIMESTAMPTZ DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    records_created     INTEGER DEFAULT 0,
    records_updated     INTEGER DEFAULT 0,
    records_failed      INTEGER DEFAULT 0,
    errors              JSONB DEFAULT '[]',
    status              VARCHAR(20) DEFAULT 'running'  -- running, success, partial, failed
);
```

### SyncConflict
```sql
CREATE TABLE sync_conflict (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_log_id     UUID NOT NULL REFERENCES sync_log(id),
    employee_id     UUID REFERENCES employee(id),
    field_name      VARCHAR(100),
    platform_value  TEXT,
    sirh_value      TEXT,
    resolution      VARCHAR(30) DEFAULT 'pending',  -- pending, platform_wins, sirh_wins, manual
    resolved_at     TIMESTAMPTZ,
    resolved_by     UUID REFERENCES "user"(id)
);
```

---

## Group 13: Mobile & Operator

### TripBooking
```sql
CREATE TABLE trip_booking (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID NOT NULL REFERENCES employee(id),
    route_id        UUID REFERENCES route(id),
    pickup_stop_id  UUID REFERENCES stop_risk_score(id),
    booking_date    DATE NOT NULL,
    shift           VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'booked',  -- booked, confirmed, cancelled, completed, no_show
    booked_at       TIMESTAMPTZ DEFAULT now(),
    cancelled_at    TIMESTAMPTZ
);
CREATE INDEX idx_trip_employee ON trip_booking(employee_id);
CREATE INDEX idx_trip_date ON trip_booking(booking_date);
```

### DeviceRegistration
```sql
CREATE TABLE device_registration (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES "user"(id),
    device_token    VARCHAR(500) NOT NULL,
    platform        VARCHAR(10) NOT NULL,   -- ios, android
    app_version     VARCHAR(20),
    registered_at   TIMESTAMPTZ DEFAULT now(),
    is_active       BOOLEAN DEFAULT true
);
```

### PushNotification
```sql
CREATE TABLE push_notification (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES "user"(id),
    type            VARCHAR(30) NOT NULL,   -- rti_alert, route_change, weather, content, emergency
    title           VARCHAR(255),
    body            TEXT,
    data            JSONB DEFAULT '{}',
    sent_at         TIMESTAMPTZ DEFAULT now(),
    delivered_at    TIMESTAMPTZ,
    read_at         TIMESTAMPTZ
);
```

### Operator
```sql
CREATE TABLE operator (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    name            VARCHAR(255) NOT NULL,
    type            VARCHAR(30),            -- via, swvl, local, internal
    api_config      JSONB DEFAULT '{}',
    contact_name    VARCHAR(100),
    contact_email   VARCHAR(255),
    contact_phone   VARCHAR(50),
    is_active       BOOLEAN DEFAULT true
);
```

### SizingPlanExport
```sql
CREATE TABLE sizing_plan_export (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    optimization_id UUID NOT NULL REFERENCES optimization(id),
    operator_id     UUID NOT NULL REFERENCES operator(id),
    exported_at     TIMESTAMPTZ DEFAULT now(),
    format          VARCHAR(10),            -- json, xml, pdf
    file_url        TEXT,
    status          VARCHAR(20) DEFAULT 'draft'  -- draft, sent, acknowledged
);
```

---

## Group 14: Reporting

### GeneratedReport
```sql
CREATE TABLE generated_report (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    report_type     VARCHAR(50) NOT NULL,
    params          JSONB DEFAULT '{}',
    file_url        TEXT,
    format          VARCHAR(10),            -- pdf, xlsx, csv, geojson
    generated_at    TIMESTAMPTZ DEFAULT now(),
    generated_by    UUID REFERENCES "user"(id)
);
```

### KPISnapshot
```sql
CREATE TABLE kpi_snapshot (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant(id),
    site_id         UUID REFERENCES site(id),
    snapshot_date   DATE NOT NULL,
    kpi_type        VARCHAR(50) NOT NULL,
    value           JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_kpi_date ON kpi_snapshot(snapshot_date);
CREATE INDEX idx_kpi_type ON kpi_snapshot(kpi_type);
```

---

## Entity Relationship Summary

```
Tenant 1──* User
Tenant 1──* Site
Tenant 1──* Employee
Tenant 1──* Vehicle
Tenant 1──* Settings (1:1)
Tenant 1──* Role

Role  *──* Permission (via RolePermission)
User  *──1 Role
User  *──1 Employee (optional)

Site  1──* Employee
Site  1──* Vehicle
Site  1──* StopRiskScore
Site  1──* RTIConfig (1:1)
Site  1──* WeatherForecast

Employee 1──1 EmployeeModal
Employee 1──* EmployeeLeave
Employee 1──* SecurityQuestionnaire
Employee 1──1 SecurityScore
Employee 1──* TripBooking
Employee 1──* ContentDelivery
Employee 1──* EmergencyAlert

Optimization 1──* Cluster
Optimization 1──* Route
Optimization 1──* Scenario (baseline)
Route *──1 Vehicle

FinancialScenario 1──* TCOEntry
FinancialScenario 1──* ROICalculation

Content 1──* ContentDelivery
Content 1──1 TrainingModule
Content 1──1 Survey
Survey  1──* SurveyResponse

SIRHConnection 1──* SyncLog
SyncLog 1──* SyncConflict

Operator 1──* SizingPlanExport
Optimization 1──* SizingPlanExport
```

---
## Related Documentation
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API endpoints consuming these tables
- [[FRONTEND_PAGES]] — Web pages displaying this data
- [[MOBILE_PAGES]] — Mobile screens
- [[PROGRESS]] — Implementation status
- [[ROADMAP]] — Development timeline
- [[agents]] — Development workflow
