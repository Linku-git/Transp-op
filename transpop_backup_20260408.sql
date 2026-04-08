--
-- PostgreSQL database dump
--

-- Dumped from database version 16.10
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: cluster; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cluster (
    optimization_id uuid NOT NULL,
    site_id uuid NOT NULL,
    centroid_lat double precision NOT NULL,
    centroid_lng double precision NOT NULL,
    centroid_geom public.geometry(Point,4326),
    employee_count integer DEFAULT 0 NOT NULL,
    pmr_count integer DEFAULT 0 NOT NULL,
    security_risk_level character varying(20) DEFAULT 'low'::character varying NOT NULL,
    employee_ids uuid[] DEFAULT '{}'::uuid[] NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: configuration_plan; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configuration_plan (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    is_current boolean DEFAULT false NOT NULL,
    source character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: configuration_transport; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configuration_transport (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    site_id uuid,
    prestataire character varying(100) NOT NULL,
    shift character varying(10),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    plan_id uuid NOT NULL,
    conducteur character varying(200),
    poste character varying(20),
    mle_vehicule character varying(50),
    type_vehicule character varying(50),
    type_moteur character varying(50),
    secteur character varying(100),
    entite character varying(200),
    aller_retour character varying(10),
    heure_depart character varying(25),
    point_depart character varying(200),
    point_arrivee character varying(200),
    heure_arrivee character varying(25),
    arrets_circuit character varying(500),
    duree_trajet_min integer,
    km numeric(8,2),
    rot numeric(6,2),
    t_km numeric(8,2)
);


--
-- Name: constraint_param; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.constraint_param (
    tenant_id uuid NOT NULL,
    key character varying(100) NOT NULL,
    value character varying(500) NOT NULL,
    category character varying(50) DEFAULT 'general'::character varying NOT NULL,
    description character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: employee; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee (
    tenant_id uuid NOT NULL,
    matricule character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    site_id uuid NOT NULL,
    shift_time character varying(50),
    address text,
    quartier character varying(100),
    city character varying(100),
    lat double precision,
    lng double precision,
    geom public.geometry(Point,4326),
    preferred_pickup_address text,
    preferred_pickup_lat double precision,
    preferred_pickup_lng double precision,
    is_pmr boolean DEFAULT false NOT NULL,
    function_role character varying(100),
    phone character varying(50),
    department character varying(100),
    transport_required boolean DEFAULT true NOT NULL,
    current_transport_mode character varying(50),
    opt_in_company_transport character varying(20) DEFAULT 'Non'::character varying NOT NULL,
    has_private_car boolean DEFAULT false NOT NULL,
    volunteer_driver boolean DEFAULT false NOT NULL,
    carpool_seats integer DEFAULT 0 NOT NULL,
    active boolean DEFAULT true NOT NULL,
    sirh_external_id character varying(100),
    hire_date date,
    end_date date,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    point_arret_id uuid
);


--
-- Name: employee_leave; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_leave (
    employee_id uuid NOT NULL,
    leave_type character varying(50) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    notes text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: employee_modal; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_modal (
    employee_id uuid NOT NULL,
    primary_mode character varying(50) NOT NULL,
    alternative_mode character varying(50),
    distance_km numeric(8,2),
    travel_time_min integer,
    frequency character varying(50),
    interest_company_transport character varying(30),
    reason_current_mode text,
    departure_time time without time zone,
    accepts_common_pickup boolean DEFAULT true NOT NULL,
    max_pickup_distance_meters integer DEFAULT 500 NOT NULL,
    has_private_car boolean DEFAULT false NOT NULL,
    volunteer_driver boolean DEFAULT false NOT NULL,
    carpool_seats_available integer DEFAULT 0 NOT NULL,
    max_detour_minutes integer,
    bonus_opt_in boolean DEFAULT false NOT NULL,
    observations text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: financial_scenario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.financial_scenario (
    tenant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    investment_model character varying(30) NOT NULL,
    duration_years integer DEFAULT 5 NOT NULL,
    fleet_composition jsonb DEFAULT '{}'::jsonb,
    params jsonb DEFAULT '{}'::jsonb,
    results jsonb DEFAULT '{}'::jsonb,
    created_by uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: generated_report; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.generated_report (
    tenant_id uuid NOT NULL,
    report_type character varying(50) NOT NULL,
    params jsonb DEFAULT '{}'::jsonb,
    file_url text,
    format character varying(10),
    generated_at timestamp with time zone DEFAULT now() NOT NULL,
    generated_by uuid,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: horaire_travail; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.horaire_travail (
    id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    site_id uuid,
    type_horaire character varying(100) NOT NULL,
    depart_h1 character varying(10),
    retour_h1 character varying(10),
    depart_h2 character varying(10),
    retour_h2 character varying(10),
    observations text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: km_consommation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.km_consommation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    site_id uuid,
    prestataire character varying(100) NOT NULL,
    vehicle_type character varying(50) NOT NULL,
    vehicle_count_peak integer,
    km_avg numeric(10,2),
    km_min numeric(10,2),
    km_max numeric(10,2),
    seat_count integer,
    fuel_consumption_l100km numeric(6,2),
    monthly_cost_per_vehicle_mad numeric(12,2),
    observations text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: kpi_snapshot; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.kpi_snapshot (
    tenant_id uuid NOT NULL,
    site_id uuid,
    snapshot_date date NOT NULL,
    kpi_type character varying(50) NOT NULL,
    value jsonb NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: optimization; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optimization (
    tenant_id uuid NOT NULL,
    site_id uuid,
    condition_type character varying(30) DEFAULT 'normal'::character varying NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    target_date date,
    completed_at timestamp with time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: optimization_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.optimization_settings (
    tenant_id uuid NOT NULL,
    meeting_radius_meters double precision DEFAULT '500'::double precision NOT NULL,
    max_walking_distance_meters double precision DEFAULT '800'::double precision NOT NULL,
    max_route_duration_seconds integer DEFAULT 5400 NOT NULL,
    fuel_cost_per_liter double precision DEFAULT '12'::double precision NOT NULL,
    fuel_consumption_l_per_100km double precision DEFAULT '15'::double precision NOT NULL,
    co2_kg_per_liter double precision DEFAULT '2.68'::double precision NOT NULL,
    rti_threshold_minutes integer DEFAULT 15 NOT NULL,
    night_mode_start character varying(5) DEFAULT '22:00'::character varying NOT NULL,
    night_mode_end character varying(5) DEFAULT '06:00'::character varying NOT NULL,
    min_night_group_size integer DEFAULT 3 NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.permission (
    resource character varying(100) NOT NULL,
    action character varying(50) NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: point_arret; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.point_arret (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tenant_id uuid NOT NULL,
    site_id uuid,
    code character varying(30) NOT NULL,
    nom character varying(200) NOT NULL,
    adresse text,
    ville character varying(100),
    lat double precision NOT NULL,
    lng double precision NOT NULL,
    prestataire character varying(100),
    is_active boolean DEFAULT true NOT NULL,
    observations text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    correspondance_tb text
);


--
-- Name: roi_calculation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.roi_calculation (
    financial_scenario_id uuid NOT NULL,
    baseline_absence_rate numeric(5,4),
    target_absence_rate numeric(5,4),
    headcount integer,
    daily_cost numeric(10,2),
    replacement_cost numeric(12,2),
    turnover_rate_before numeric(5,4),
    turnover_rate_after numeric(5,4),
    training_hour_cost numeric(8,2),
    engagement_rate numeric(5,4),
    annual_travel_hours numeric(8,2),
    roi_absenteeism numeric(14,2),
    roi_retention numeric(14,2),
    roi_journey numeric(14,2),
    roi_fleet_optimization numeric(14,2),
    roi_total numeric(14,2),
    payback_months numeric(6,1),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role (
    tenant_id uuid NOT NULL,
    name character varying(50) NOT NULL,
    permissions jsonb DEFAULT '[]'::jsonb NOT NULL,
    is_system_role boolean DEFAULT false NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: role_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.role_permission (
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: route; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.route (
    optimization_id uuid NOT NULL,
    vehicle_id uuid,
    site_id uuid NOT NULL,
    ordered_stops jsonb DEFAULT '[]'::jsonb NOT NULL,
    total_distance_km numeric(10,2),
    total_time_minutes numeric(8,2),
    polyline text,
    geom public.geometry(LineString,4326),
    rti_compliance_pct numeric(5,2),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: scenario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scenario (
    tenant_id uuid NOT NULL,
    site_id uuid NOT NULL,
    baseline_optimization_id uuid,
    condition_type character varying(30) DEFAULT 'normal'::character varying NOT NULL,
    demand_multiplier double precision DEFAULT '1'::double precision NOT NULL,
    custom_params json DEFAULT '{}'::json NOT NULL,
    estimated_metrics json DEFAULT '{}'::json NOT NULL,
    name character varying(100),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: site; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.site (
    tenant_id uuid NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    address text NOT NULL,
    city character varying(100) NOT NULL,
    lat double precision NOT NULL,
    lng double precision NOT NULL,
    geom public.geometry(Point,4326),
    num_shifts integer DEFAULT 1 NOT NULL,
    shift_1_entry time without time zone,
    shift_1_exit time without time zone,
    shift_2_entry time without time zone,
    shift_2_exit time without time zone,
    shift_3_entry time without time zone,
    shift_3_exit time without time zone,
    working_days character varying(100) DEFAULT 'Lundi-Vendredi'::character varying,
    days_per_week integer DEFAULT 5,
    contact_name character varying(100),
    contact_phone character varying(50),
    access_notes text,
    parking_notes text,
    zfe_zone boolean DEFAULT false NOT NULL,
    security_profile character varying(20) DEFAULT 'normal'::character varying NOT NULL,
    timezone character varying(50) DEFAULT 'Europe/Paris'::character varying NOT NULL,
    observations text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    shift_1_type character varying(50),
    shift_1_depart_h2 time without time zone,
    shift_1_retour_h2 time without time zone,
    shift_2_type character varying(50),
    shift_2_depart_h2 time without time zone,
    shift_2_retour_h2 time without time zone,
    shift_3_type character varying(50),
    shift_3_depart_h2 time without time zone,
    shift_3_retour_h2 time without time zone,
    active_shift_ids jsonb DEFAULT '[]'::jsonb NOT NULL
);


--
-- Name: tco_entry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tco_entry (
    financial_scenario_id uuid NOT NULL,
    vehicle_type character varying(50) NOT NULL,
    motorization character varying(30),
    quantity integer DEFAULT 1 NOT NULL,
    purchase_price numeric(14,2),
    annual_maintenance_cost numeric(12,2),
    energy_cost_per_km numeric(8,4),
    annual_km numeric(12,2),
    residual_value numeric(14,2),
    infrastructure_cost numeric(14,2),
    tco_per_vehicle numeric(14,2),
    tco_total numeric(14,2),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: tenant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenant (
    name character varying(255) NOT NULL,
    code character varying(100) NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    data_region character varying(50) DEFAULT 'eu-west'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    tenant_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255),
    first_name character varying(100),
    last_name character varying(100),
    role_id uuid NOT NULL,
    employee_id uuid,
    mfa_enabled boolean DEFAULT false NOT NULL,
    mfa_secret character varying(255),
    last_login_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: vehicle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle (
    tenant_id uuid NOT NULL,
    type character varying(50) NOT NULL,
    brand_model character varying(100),
    capacity integer NOT NULL,
    year integer,
    owner_type character varying(50),
    monthly_cost_mad numeric(12,2),
    monthly_km numeric(10,2),
    condition character varying(20) DEFAULT 'Bon'::character varying NOT NULL,
    site_id uuid,
    is_pmr_accessible boolean DEFAULT false NOT NULL,
    fuel_consumption numeric(6,2),
    cost_per_km numeric(8,4),
    motorization character varying(30),
    length_meters numeric(5,2),
    zfe_compliant boolean DEFAULT false NOT NULL,
    observations text,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    matricule character varying(30),
    circulation_date date,
    prestataire character varying(100)
);


--
-- Name: vehicle_reference; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle_reference (
    type character varying(50) NOT NULL,
    capacity_min integer,
    capacity_max integer,
    motorizations_available jsonb DEFAULT '[]'::jsonb,
    recommended_use text,
    reference_tco_5y jsonb DEFAULT '{}'::jsonb,
    length_meters numeric(5,2),
    zfe_compliant boolean DEFAULT true NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: weather_forecast; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weather_forecast (
    site_id uuid NOT NULL,
    date date NOT NULL,
    condition_summary character varying(100),
    precipitation_mm numeric(6,2),
    temp_min_c numeric(5,2),
    temp_max_c numeric(5,2),
    wind_kph numeric(6,2),
    fetched_at timestamp with time zone DEFAULT now() NOT NULL,
    source character varying(50),
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
i4j5k6l7m8n9
\.


--
-- Data for Name: cluster; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cluster (optimization_id, site_id, centroid_lat, centroid_lng, centroid_geom, employee_count, pmr_count, security_risk_level, employee_ids, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: configuration_plan; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.configuration_plan (id, tenant_id, name, description, is_active, is_current, source, created_at, updated_at) FROM stdin;
818abb76-2384-4ff8-b786-c2758ab4d19d	0cea9745-6aa2-4105-9bdc-341d95999048	Configuration Initiale 2024	Configuration de transport initiale importée depuis le fichier de référence (591 lignes)	t	t	seed	2026-04-03 01:52:54.523165+00	2026-04-03 01:52:54.523165+00
\.


--
-- Data for Name: configuration_transport; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.configuration_transport (id, tenant_id, site_id, prestataire, shift, is_active, created_at, updated_at, plan_id, conducteur, poste, mle_vehicule, type_vehicule, type_moteur, secteur, entite, aller_retour, heure_depart, point_depart, point_arrivee, heure_arrivee, arrets_circuit, duree_trajet_min, km, rot, t_km) FROM stdin;
4401a4e6-37f2-4617-907c-b61720a8218b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL GARARI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	05:50	KHOURIBGA	BENI AMIR MINE	06:40	H-T-1-2-10-Z	50	96.00	0.50	48.00
6cf1237f-ea30-4d31-834b-2e32f3d9f1f5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL GARARI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	06:45	BENI AMIR MINE	KHOURIBGA	07:30	A+Q	45	96.00	0.50	48.00
613f6add-7d79-477d-a492-3c75567cca3b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL GARARI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	13:50	KHOURIBGA	BENI AMIR MINE	14:45	H-T-1-2-3-4-5-OK-HANNA2	55	96.00	0.50	48.00
0cbed0ce-8600-47c6-9a71-af73f675726b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL GARARI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	14:45	BENI AMIR MINE	KHOURIBGA	15:30	F-Z-10-1-2-H	45	96.00	0.50	48.00
8766baa0-6399-42a2-82d3-cf50601af76b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL GARARI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	CCI	RETOUR	16:15	CCI	KHOURIBGA	17:00	Q-A	45	92.00	1.00	92.00
96fa7158-b0b4-449b-8f0e-53142f6374a6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SMAALI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	21:50	KHOURIBGA	BENI AMIR MINE	22:40	H-T-1-2-3-4-5-OK	50	96.00	0.50	48.00
368c690b-8ecf-4ce5-b7f2-ce110b11d236	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SMAALI	S1	82199-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	22:45	BENI AMIR MINE	KHOURIBGA	23:30	V+Q	45	96.00	0.50	48.00
b26672a3-9b31-4d2b-ae12-734f5580c4d4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SMAALI	S2	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	05:50	KHOURIBGA	BENI AMIR MINE	06:40	Q-OK-F	50	96.00	0.50	48.00
da681a35-7ead-4a32-9f91-475ec43cf803	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SMAALI	S3	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	06:45	BENI AMIR MINE	KHOURIBGA	07:30	F-Z-10-1-2-H	45	96.00	0.50	48.00
35931105-beda-4010-a12d-95a8691d8893	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AIT ICHOU	S4	56148-A-14	AUTOCAR	MAN	KHOURIBGA	CCI	ALLER	09:10	BOULANOIR	CCI	09:45	CFO-10-Z-F	35	80.00	1.00	80.00
e59b0537-c72c-4f57-82f5-2b27196d697c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AIT ICHOU	S5	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	13:50	KHOURIBGA	BENI AMIR MINE	14:45	Q-5-9-10-F-Z	55	96.00	0.50	48.00
0f1a304b-3976-42a7-bfd3-d6ba90bc8913	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AIT ICHOU	S6	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	14:45	BENI AMIR MINE	KHOURIBGA	15:30	HANA 2- OK-5-4-3-Q	45	96.00	0.50	48.00
ac97ef84-cb09-4502-bb79-379257fcbee8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AIT ICHOU	S7	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	21:50	KHOURIBGA	BENI AMIR MINE	22:30	Q-5-9-10-F-Z	40	96.00	0.50	48.00
3aad2c9d-be06-46ca-96b7-6f194af6d2fc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AIT ICHOU	S8	56148-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	23:45	BENI AMIR MINE	KHOURIBGA	00:30	F-Z-10-1-2-H	45	96.00	0.50	48.00
ac6bc47b-529f-4445-98b1-857429a27e45	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUINE	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	05:50	KHOURIBGA	BENI AMIR LAVERIE	06:30	H-T-1-2-10-Z-F	40	94.00	0.50	47.00
55f729a8-ef50-4b5a-b350-451a9e957787	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUINE	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	06:45	BENI AMIR LAVERIE	KHOURIBGA	07:30	OK-IMARA- 5-4-3-Q	45	94.00	0.50	47.00
1dd5edc9-2e49-4337-b742-1f2f03668ebf	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUINE	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	13:50	KHOURIBGA	BENI AMIR LAVERIE	14:45	H-T-1-2-10-Z-F	55	94.00	0.50	47.00
906026af-121f-4dd8-b018-4f49e245572b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUINE	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	14:45	BENI AMIR LAVERIE	KHOURIBGA	15:30	OK-IMARA-5-4-3-Q	45	94.00	0.50	47.00
458f1316-efad-470c-b624-701ce1c3e0eb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUINE	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	CCI	RETOUR	16:15	CCI	KHOURIBGA	17:00	F-Z-10-1-2-H	45	92.00	1.00	92.00
ab9c2f7a-6a73-4acc-ba84-5d5366621afe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MANDILI	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	21:50	KHOURIBGA	BENI AMIR LAVERIE	22:40	H-T-1-2-3-4-IMARA-OK	50	94.00	0.50	47.00
bb9f7aba-8aa0-481b-aee8-ff6d1c48fb0b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MANDILI	S3	63321-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	22:45	BENI AMIR LAVERIE	KHOURIBGA	23:30	OK-IMARA-Q	45	94.00	0.50	47.00
fdc64a42-baa2-4d5f-a6d5-cd03e72bd411	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MANDILI	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	05:50	KHOURIBGA	BENI AMIR LAVERIE	06:40	Q-IMARA-OK	50	94.00	0.50	47.00
36d8a25c-1ed4-4168-9a93-450f08ae8eb0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MANDILI	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	06:45	BENI AMIR LAVERIE	KHOURIBGA	07:30	F+Z+10+N	45	94.00	0.50	47.00
c27790cb-b2e4-42cd-b084-1e297eff5978	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MANDILI	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	12:00	UB-R6-GROUNI	KHOURIBGA	12:30	\N	30	54.00	1.00	54.00
646c1490-1d70-482b-8ce2-22d98382b75f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELKHIR	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	13:50	KHOURIBGA	BENI AMIR LAVERIE	14:45	Q-5-V-9-10-F-Z	55	94.00	0.50	47.00
657848fc-f6ba-4672-8a85-27010a46613c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELKHIR	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	14:45	BENI AMIR LAVERIE	KHOURIBGA	15:30	F-Z-10-1-2-H	45	94.00	0.50	47.00
64cde5fe-1fd2-4379-b625-dd126caa3e1d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELKHIR	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	CCI	RETOUR	16:15	CCI	BOULANOIR	17:00	10-CFO-BL	45	80.00	1.00	80.00
8f3dd9f6-df1a-4f1b-8e8f-3616effc4976	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELKHIR	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	21:50	KHOURIBGA	BENI AMIR LAVERIE	22:40	Q-5-V-9-10-F-Z	50	94.00	0.50	47.00
15b62de9-f0b4-48f7-b3cd-c730dd32315f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELKHIR	S4	61847-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	22:45	BENI AMIR LAVERIE	KHOURIBGA	23:30	F+Z+10+N	45	94.00	0.50	47.00
e0e9bf4d-9377-4455-a6db-5c5d561449b3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL RHIRHA	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	ALLER	05:50	KHOURIBGA	PARC 7900	06:30	Q-5-OM K+F	40	60.00	1.00	60.00
f028e66b-a834-485c-abe1-94ab98ba6239	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL RHIRHA	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	BENI AMIR MINE	ALLER	07:00	KHOURIBGA	BENI AMIR LAVERIE &MINE	07:45	Q+V	45	96.00	1.00	96.00
c96581c3-54e8-4031-b292-4e41418728a2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL RHIRHA	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	ALLER	13:50	KHOURIBGA	PARC 7900	14:40	Q-5-V	50	60.00	0.50	30.00
022ab425-befc-4254-aba6-2e66c55af0cb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL RHIRHA	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	RETOUR	14:45	PARC 7900	KHOURIBGA	15:30	F+Z+10+N	45	60.00	0.50	30.00
c1ea1825-d28d-4572-8ee4-7177d7070b3a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL RHIRHA	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE (D)	KHOURIBGA	16:30	F-Z-10-1-2 H	45	104.00	1.00	104.00
fabab236-d750-47b0-8b30-50b9e9f857e7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARAS	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	DAOUI	ALLER	21:50	KHOURIBGA	DAOUI	22:40	N-A	50	86.00	0.50	43.00
6d63d6c0-8412-48f1-95d8-191cd6773e6f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARAS	S5	56046-A-14	AUTOCAR	VOLVO	KHOURIBGA	DAOUI	RETOUR	22:45	DAOUI	KHOURIBGA	23:30	10-V-5-Q	45	86.00	0.50	43.00
b4b9c9b6-be6d-4e26-8fb6-fb681e9d080a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARAS	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	05:50	KHOURIBGA	MLIKATE	06:40	Q-5-OM K+F	50	74.00	0.50	37.00
22b25b82-c964-43db-a953-3fe4ee845d96	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARAS	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	06:45	MLIKATE	KHOURIBGA	07:30	F-Z-10-1-2-H	45	74.00	0.50	37.00
cf35b6d4-025c-4016-b3c3-f2430c5847bc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARAS	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	07:30	KHOURIBGA	SIDI CHENNANE	08:15	N-A	45	104.00	1.00	104.00
df2378e0-a088-4e3c-a41d-d18b1dccf1b2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KAMAL	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	T2	RETOUR	14:45	T2	KHOURIBGA	15:30	Z-F-10-11-1-2-H-T	45	110.00	1.00	110.00
55e583ba-534b-4d5a-b48b-9eae7ce92286	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KAMAL	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	16:30	UB-UM3	KHOURIBGA	17:00	V+Q	30	50.00	1.00	50.00
b1860549-e1d8-4df2-90a5-74727dc5f36a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KAMAL	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	21:50	KHOURIBGA	SIDI CHENNANE	22:40	Q+V	50	104.00	0.50	52.00
40acc945-e7b0-4810-b196-2ff746a63587	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KAMAL	S6	82198-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	23:45	SIDI CHENNANE	KHOURIBGA	00:30	Z-F-10-11-1-2-H-T	45	104.00	0.50	52.00
683e8f5a-8e17-42e5-bf96-29f4354e1cc4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AZAGAR	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	CCI	ALLER	09:00	KHOURIBGA	CCI	09:45	H--T--- OMK	45	92.00	1.00	92.00
155e3597-3e5b-4c17-9b18-b299749df139	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AZAGAR	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	12:00	DAOUI	KHOURIBGA	12:30	N-A	30	86.00	1.00	86.00
5cc1024f-e587-41b1-bbee-00ace716d1e7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AZAGAR	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	13:50	KHOURIBGA	SIDI CHENNANE	14:40	H-T-N-10-Z-F	50	104.00	0.50	52.00
0bfc652a-4ed9-473a-bdb8-e6ad6f734c79	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AZAGAR	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	KHOURIBGA	15:30	F-Z-10-9	45	104.00	0.50	52.00
abb1df80-9f5d-4df7-83f2-7ed1e4e9c9dd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AZAGAR	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	15:45	LAVERIE MERA	KHOURIBGA	16:30	Z-F-10-11-1-2-H-T	45	46.00	1.00	46.00
9c8ee334-61a4-4598-a452-4b75e3fb90f1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUBAN	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	21:50	KHOURIBGA	PARC 7900	22:30	Q-5--A	40	60.00	0.50	30.00
3de3a1cd-905c-4047-a83b-24d207c4a926	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUBAN	S7	63325-A-14	AUTOCAR	MAN	KHOURIBGA	PARC 7900	RETOUR	22:45	PARC 7900	KHOURIBGA	23:30	Z-F-10-11-1-2-H-T	45	60.00	0.50	30.00
37a73605-9784-49bc-ac4a-51e411e6903f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUBAN	S8	82195-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (D)	06:40	Q-5-OK	50	104.00	0.50	52.00
832522e8-6746-4231-b9ff-52122f01eb6f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUBAN	S8	82195-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	07:45	SIDI CHENNANE	KHOURIBGA	08:30	Z-F-10-11-1-2-H-T	45	104.00	0.50	52.00
d6d42dea-c709-4cd4-b30f-5664e0272558	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ABADAN	S8	82195-A-13	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	13:50	KHOURIBGA	PARC 7900	14:40	H-T-N-OK	50	60.00	0.50	30.00
a8d48a1d-dfab-415c-9fdc-4d882f315d8d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ABADAN	S8	82195-A-13	AUTOCAR	MAN	KHOURIBGA	PARC 7900	RETOUR	14:45	PARC 7900	KHOURIBGA	15:30	OK-IMARA-5-QODS	45	60.00	0.50	30.00
1f508c64-3c60-470d-9134-165638f159ff	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ABADAN	S8	82195-A-13	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	15:45	LAVERIE MERA	KHOURIBGA	16:30	V-Q	45	46.00	1.00	46.00
0d45c099-aced-479e-9987-51cbc6ff1cfb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ABADAN	S8	82195-A-13	AUTOCAR	MAN	BOUJNIBA	ZONE CENTRALE	ALLER	22:00	BOUJNIBA	LAVERIE MERA & ZONE CENTRALE	22:40	\N	40	50.00	0.50	25.00
e0f40688-6a8b-4f9b-9330-458a1976d19f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ABADAN	S8	82195-A-13	AUTOCAR	MAN	BOUJNIBA	ZONE CENTRALE	ALLER	22:45	LAVERIE MERA & ZONE CENTRALE	BOUJNIBA	23:30	\N	45	50.00	0.50	25.00
e556222d-ae22-410e-9791-68f432ff56c3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GARROUD	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (D)	06:40	H-T-1-2--10	50	104.00	0.50	52.00
7e9904c9-9b1a-4beb-a639-bd4ee2782478	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GARROUD	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	PARC 7900	RETOUR	07:45	PARC 7900	KHOURIBGA	08:30	V-Q	45	60.00	0.50	30.00
1f6a1ed3-7c23-4837-be8d-e76ed187ae13	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GARROUD	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE (D)	KHOURIBGA	15:30	Z-F-10-11-1-2-H-T	45	104.00	1.00	104.00
c609490a-1272-4923-aee0-0526e99085b1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GARROUD	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	RETOUR	15:45	PIPE LINE	KHOURIBGA	16:30	N-A	45	52.00	1.00	52.00
df8cb07f-9ed0-46fa-a9c1-52bd763cfe6c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUNIR	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	21:50	KHOURIBGA	LAVERIE MERA	22:30	H-T-1-2-10-Z-F	40	46.00	0.50	23.00
544f82f1-adb8-485c-b497-70cc2449d4ce	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUNIR	S9	63323-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	22:45	LAVERIE MERA	KHOURIBGA	23:30	Z-F-10-11-1-2-H-T	45	46.00	0.50	23.00
7e19ae0b-59f9-4572-a98d-f225d95b2fe8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUNIR	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (D)	06:40	3 -4-5-V-10	50	104.00	0.50	52.00
60c23d14-9da2-4224-80c8-473a625e2fd5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOUNIR	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	07:45	SIDI CHENNANE	KHOURIBGA	08:30	F-OK-5-Q	45	104.00	0.50	52.00
bcee458c-cfb0-44ef-90ae-9c48b7412720	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HABACHI	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	13:45	KHOURIBGA	SIDI CHENNANE (T)	14:30	NV RIAD 5-O	45	104.00	0.50	52.00
0ddff30a-64fd-4009-90ff-27d51df79fa9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HABACHI	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE (T)	KHOURIBGA	15:30	F-Z-10-1-2-H-T	45	104.00	0.50	52.00
f80b5d29-c74c-44e1-a226-f131d73381c0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HABACHI	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	15:45	UB	KHOURIBGA	16:30	CFO-1-2-H-T	45	50.00	1.00	50.00
23ee5924-8485-4169-bb79-98e3e04ce10e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HABACHI	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	21:50	KHOURIBGA	SIDI CHENNANE	22:40	H-T-1-2-10-Z-F	50	104.00	0.50	52.00
c5d3435d-39c9-4b9d-b243-0d62085dfdcc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HABACHI	S10	56151-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE	KHOURIBGA	23:30	F-Z-10-1-2-H-T	45	104.00	0.50	52.00
790af125-9f6e-4c5a-80be-c2c626112502	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	ALLER	05:50	KHOURIBGA	BENI AMIR MINE	06:40	3-4-5--9-10-F-Z	50	96.00	0.50	48.00
7e8dc99d-bc95-44f3-9d27-6d98adad8d23	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	07:45	BENI AMIR MINE	KHOURIBGA	08:30	V-Q	45	96.00	0.50	48.00
7b96bef0-792b-4234-8ac7-71cb12f2a4a4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	12:00	LAVERIE MERA-PIPE-LABO	KHOURIBGA	12:30	N-A	30	50.00	1.00	50.00
e1ac8dc2-0614-46c6-8787-0fb52ce81419	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	13:50	KHOURIBGA	LAVERIE MERA	14:30	10-F-Z	40	46.00	0.50	23.00
905eea66-c64c-4fa7-a82b-97ed1f7f9a70	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	14:45	LAVERIE MERA	KHOURIBGA	15:30	10-V	45	46.00	0.50	23.00
f060505b-0a8f-43a9-bc33-55abe1f7f995	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AOURAZOUK	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE (T)	KHOURIBGA	16:30	V-Q	45	104.00	1.00	104.00
a1b28869-11db-4249-b107-a6e76e1713de	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ADIL	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	21:50	KHOURIBGA	ZONE CENTRALE	22:40	Q+V	50	50.00	0.50	25.00
0686b065-5c8f-4ea9-9cfb-cfef07b0be30	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ADIL	S11	61846-A-14	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	22:45	ZONE CENTRALE	KHOURIBGA	23:30	V-Q	45	50.00	0.50	25.00
f9636d2a-005a-418c-8f02-0df6cab1b70f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ADIL	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	05:50	KHOURIBGA	BENI AMIR LAVERIE	06:40	3-4-5-V	50	94.00	0.50	47.00
05e765a1-1ad9-4365-a77f-a55d60fbe4f0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ADIL	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	07:45	BENI AMIR LAVERIE	KHOURIBGA	08:30	N-A	45	94.00	0.50	47.00
5cbb6690-f7dc-4a5f-b581-b1e83f3df204	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL JAZOULI	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	13:50	KHOURIBGA	SIDI CHENNANE	14:30	Q-5-OK	40	104.00	0.50	52.00
3a8deb4c-89e8-456c-bf83-2c022d3d1df6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL JAZOULI	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	KHOURIBGA	15:30	F-OK-IMARA-QODS	45	104.00	0.50	52.00
393d6ec4-1f54-4f6d-b897-7772683a40d4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL JAZOULI	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	16:30	UB-UM1	KHOURIBGA	17:00	F-Z-10-1-2-H-T	30	50.00	1.00	50.00
5a3fb62e-7b03-4f97-aed7-50a40a10ef68	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL JAZOULI	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	21:45	KHOURIBGA	SIDI CHENNANE	22:40	NV RIAD 5-3-4-OK-F	55	104.00	0.50	52.00
1d10bac5-9718-4c70-b86c-7969ff40da2a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL JAZOULI	S12	64362-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE	KHOURIBGA	23:45	V-Q	60	104.00	0.50	52.00
e2a273ca-c835-42c4-87f9-2a146698a0a2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GHAOUTI	S13	61858-A-14	AUTOCAR	MAN	BOULANOIR	SIDI CHENNANE	ALLER	06:00	BOULANOIR	SIDI CHENNANE	06:40	\N	40	86.00	0.50	43.00
f1b1b4ad-117f-4eb2-8bd7-41a8d57df965	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GHAOUTI	S13	61858-A-14	AUTOCAR	MAN	BOULANOIR	SIDI CHENNANE	RETOUR	07:45	SIDI CHENNANE	BOULANOIR	08:30	\N	45	86.00	0.50	43.00
4c887346-4ea2-4c7c-b28f-bc7acbb2805f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GHAOUTI	S13	61858-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	12:00	BENI AMIR MINE  & LAVERIE	KHOURIBGA	12:30	N-A	30	96.00	1.00	96.00
b912c62f-276d-49d0-99ae-2ff8d422511e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GHAOUTI	S13	61858-A-14	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE (D)	KHOURIBGA	16:30	OM K-4-3-Q	45	104.00	1.00	104.00
c3cdb9dd-b38e-463b-bd4e-8f80b16bd39a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	FATIH	S13	61858-A-14	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	21:50	KHOURIBGA	MLIKATE	22:30	Q-5-V	40	74.00	0.50	37.00
dcb0d8a0-31b2-43d5-bba6-02708435acbf	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	FATIH	S13	61858-A-14	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	23:45	MLIKATE	KHOURIBGA	00:30	V-5-Q	45	74.00	0.50	37.00
03df33af-f1a4-4931-860b-19a8e8562fa2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	FATIH	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	ALLER	06:00	BOUJNIBA-HATTNE	SIDI CHENNANE (T)	06:40	\N	40	108.00	0.50	54.00
7050a3d9-732a-466e-b325-6dd1b8ce8906	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	FATIH	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	RETOUR	06:45	SIDI CHENNANE (T)	HATTANE-BOUJNIBA	07:30	\N	45	108.00	0.50	54.00
5e874847-156f-4e7d-88aa-d62979682611	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	FATIH	S14	61845-A-14	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	ALLER	08:20	KHOURIBGA	PIPE LINE	09:00	N-A	40	52.00	1.00	52.00
3c208a07-c10c-4c10-af5b-d703e9fd10e6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GALA	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	ALLER	14:00	BOUJNIBA-HATTNE	SIDI CHENNANE (T)	14:40	\N	40	108.00	0.50	54.00
9ad72789-88c1-4002-b1fb-9360c0db5494	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GALA	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE (T)	HATTANE-BOUJNIBA	15:30	\N	45	108.00	0.50	54.00
145fe0b6-4861-476c-86b5-8bc001624332	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GALA	S14	61845-A-14	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	16:30	DAOUI	KHOURIBGA	17:00	N-A	30	86.00	1.00	86.00
86cf5c99-5404-4549-89e4-a17aa009f292	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GALA	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	ALLER	22:00	BOUJNIBA-HATTNE	SIDI CHENNANE (T)	22:40	\N	40	108.00	0.50	54.00
9c459584-efb6-44f2-a5e9-0f7acb3f8843	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	GALA	S14	61845-A-14	AUTOCAR	MAN	BOUJNIBA	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE (T)	HATTANE-BOUJNIBA	23:30	\N	45	108.00	0.50	54.00
a7d5a737-5a65-4fef-8e0b-73a303eccc1f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (T)	06:40	2-3-4-5-V-10-F-Z	50	104.00	0.50	52.00
4a8d1283-95b6-42f5-a261-ac1361b2982d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	07:45	MLIKATE	KHOURIBGA	08:30	N-A	45	74.00	0.50	37.00
9b19f4f8-7cf0-4b37-b5e4-91ad04313565	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	12:00	SIDI CHENNANE	KHOURIBGA	12:30	N-A	30	104.00	1.00	104.00
734adad1-297e-498a-8c45-4aac34de81d3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	13:50	KHOURIBGA	LAVERIE MERA	14:30	H-N-IMARA+OMK-10	40	46.00	0.50	23.00
07a1b8f8-8c40-4f3e-8bba-1b3dab62b28b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	14:45	LAVERIE MERA	KHOURIBGA	15:30	OK-IMARA-4-3-Q	45	46.00	0.50	23.00
6b3179ea-3584-4ea6-88b1-fb8b9b300a9e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUFI	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	16:30	LAVERIE MERA	KHOURIBGA	17:00	F-Z-10-1-2-H-T	30	46.00	1.00	46.00
e02a0dae-1d56-44fd-99b3-86d78179e93f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUMIR	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	21:50	KHOURIBGA	MLIKATE	22:40	H-T-1-2-3-4-5-OK-F	50	74.00	0.50	37.00
b6be9cfb-e12d-45a1-b1e2-046835a4a4ff	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUMIR	S15	82197-A-13	AUTOCAR	MAN	KHOURIBGA	PARC 7900	RETOUR	22:45	PARC 7900	KHOURIBGA	23:30	N-A	45	60.00	0.50	30.00
2f2658b6-deba-4f23-a7e1-5b4b101eb2a6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUMIR	S16	61848-A-14	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	05:50	KHOURIBGA	MLIKATE	06:40	2-3-4-5-V	50	74.00	0.50	37.00
7292be7a-d5ce-481c-af89-33bae630568f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HOUMIR	S16	61848-A-14	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	07:45	BENI AMIR MINE	KHOURIBGA	08:30	F-Z-10-1-2-H-T	45	96.00	0.50	48.00
2bf076a7-ddb1-49d9-bea4-e7bfc180da65	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL BOUHAYATI	S16	61848-A-14	AUTOCAR	MAN	BOUJNIBA	UB	ALLER	13:30	BOUJNIBA	UB	14:00	\N	30	30.00	0.50	15.00
e1410059-81aa-4432-9967-be352166671b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL BOUHAYATI	S16	61848-A-14	AUTOCAR	MAN	BOUJNIBA	UB	RETOUR	14:30	UB	BOUJNIBA	15:00	\N	30	30.00	0.50	15.00
707c34ad-e93f-4410-9b77-de5bc2a8a864	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL BOUHAYATI	S16	61848-A-14	AUTOCAR	MAN	BOULANOIR	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE	BOULANOIR	16:30	\N	45	86.00	1.00	86.00
50ab2935-d477-4915-a2e5-f84551a2e5fc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL BOUHAYATI	S16	61848-A-14	AUTOCAR	MAN	BOUJNIBA	PARC 7900	ALLER	22:00	BOUJNIBA	PARC 7900	22:40	\N	40	84.00	0.50	42.00
00a0682a-cfe8-4ecb-af54-c838c638fca0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL BOUHAYATI	S16	61848-A-14	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	22:45	PARC 7900	BOUJNIBA	23:30	\N	45	84.00	0.50	42.00
686b7019-23ce-4736-a443-84117d05f32b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MASAOUDI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	ALLER	05:50	KHOURIBGA	T2	06:40	H-T-N-5-OK-F	50	110.00	0.50	55.00
ce02b173-867c-4a6c-b182-a358d54a62aa	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MASAOUDI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	06:45	T2	KHOURIBGA	07:30	A-N	45	110.00	0.50	55.00
4f039581-f0be-476f-8b51-fbf8d8fb7301	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MASAOUDI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	ALLER	13:50	KHOURIBGA	T2	14:40	H-T-1-2-3-4-5-A	50	110.00	0.50	55.00
6f66cfe8-5631-4840-a08f-977bf78ec994	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MASAOUDI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	15:45	T2	KHOURIBGA	16:30	V+Q	45	110.00	0.50	55.00
5844435d-daa8-4ad6-bc6e-3946588c2cfa	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL KINANI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	ALLER	21:50	KHOURIBGA	T2	22:40	H-T-1-2-3-4-5-A	50	110.00	0.50	55.00
372059ff-ee3c-4bf2-b804-1f29d38bfdc8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL KINANI	S17	79401-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	23:45	T2	KHOURIBGA	00:30	A-N	45	110.00	0.50	55.00
927548d2-ab9c-4cfc-8338-65d0a5a6e346	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL KINANI	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	ALLER	05:50	KHOURIBGA	T2	06:40	Q-5-6-7-8-9-10	50	110.00	0.50	55.00
249a7feb-1d1a-493d-bb09-a7584b6b46ec	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL KINANI	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	07:45	T2	KHOURIBGA	08:30	10-V-4-3-Q	45	110.00	0.50	55.00
e7984d84-f647-4243-b5b1-fc7220840e52	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAKHEL	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	MLIKATE	ALLER	13:50	KHOURIBGA	MLIKATE	14:40	Q+V	50	74.00	0.50	37.00
c436f608-1e40-42e4-9d85-9dfe21f72cfe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAKHEL	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	MLIKATE	RETOUR	14:45	MLIKATE	KHOURIBGA	15:30	F-Z-10-1-2-H-T	45	74.00	0.50	37.00
3d5482a5-e31b-4cd4-90ff-10432a18e693	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAKHEL	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	RETOUR	15:45	PARC 7900	KHOURIBGA	16:30	F-Z-10-1-2-H-T	45	60.00	1.00	60.00
49733981-f7a0-4c05-b1da-7f38376eb5d1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAKHEL	S18	79143-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	22:45	T2	KHOURIBGA	23:30	A-4-3-QODS	45	110.00	1.00	110.00
8b5b9fa2-5db9-4506-930b-9c490254bdc1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFAKHSI	S19	79142-A-13	AUTOCAR	VOLVO	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (T)	06:40	Q-5-O-M-K-F	50	104.00	0.50	52.00
d1ffe7ab-d848-457b-90e2-8b8568388c8d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFAKHSI	S19	79142-A-13	AUTOCAR	VOLVO	KHOURIBGA	T2	RETOUR	07:45	T2	KHOURIBGA	08:30	10-N-H-T	45	110.00	0.50	55.00
d045f509-facd-4bbd-80fe-888176f9427d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFAKHSI	S19	79142-A-13	AUTOCAR	VOLVO	KHOURIBGA	SIDI CHENNANE	ALLER	13:50	KHOURIBGA	SIDI CHENNANE	14:40	V	50	104.00	0.50	52.00
3e4d31bd-27c5-4a5f-96c3-2476eb843d48	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFAKHSI	S19	79142-A-13	AUTOCAR	VOLVO	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	KHOURIBGA	15:30	7-6-5	45	104.00	0.50	52.00
efb1951a-2201-4c8e-8239-5a32c8d82059	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFAKHSI	S19	79142-A-13	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	RETOUR	15:45	PARC 7900	KHOURIBGA	16:30	IMARA-Q	45	60.00	1.00	60.00
34bb1fbc-0c61-4808-b510-c2c353cd1bba	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BIAD	S19	79142-A-13	AUTOCAR	VOLVO	BOULANOIR	SIDI CHENNANE	ALLER	22:00	BOULANOIR	SIDI CHENNANE	22:40	\N	40	86.00	0.50	43.00
c3e30faa-b417-43e3-97f9-de3cd544a245	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BIAD	S19	79142-A-13	AUTOCAR	VOLVO	BOULANOIR	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE	BOULANOIR	23:30	\N	45	86.00	0.50	43.00
59f31b1d-df82-4747-a47e-3c0d5df07561	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BIAD	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	05:50	KHOURIBGA	MLIKATE	06:40	H-T-1-2-9-Z-F	50	74.00	0.50	37.00
8ff8b752-8ce4-4fa6-bdc9-03b697b86825	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BIAD	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	06:45	MLIKATE	KHOURIBGA	07:30	V-Q	45	74.00	0.50	37.00
8afec71d-6f16-4fa8-aa80-1561bb6c3750	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BIAD	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	CCI	ALLER	09:00	KHOURIBGA	CCI	09:45	Q-A	45	92.00	1.00	92.00
6717a3ec-4110-47ce-9420-3ba4499ad228	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUTAYEB	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	13:50	KHOURIBGA	MLIKATE	14:40	H-T-1-2-9-Z-F	50	74.00	0.50	37.00
ec8f2e67-2cca-49a8-a735-c6d0230b4dc5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUTAYEB	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	14:45	MLIKATE	KHOURIBGA	15:30	F-OK-IMARA-5-Q	45	74.00	0.50	37.00
77de692c-6729-4daf-8775-655fabefece4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUTAYEB	S20	82519-A-14	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	16:30	LAVERIE MERA	KHOURIBGA	17:00	V+Q	30	46.00	1.00	46.00
5a0d80c8-5be4-443a-8019-048308441263	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUTAYEB	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	21:00	KHOURIBGA	LAVERIE MERA-SIDICHENNANE-BENIAMIR	23:30	\N	150	116.00	0.50	58.00
23f80a28-3ef0-42dd-a075-0846b1fece91	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUTAYEB	S20	82519-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	23:45	BENI AMIR LAVERIE	KHOURIBGA	00:30	N-A	45	94.00	0.50	47.00
7f2c4752-2efe-4700-8378-bbe104cf1bae	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAOUISI	S21	82516-A-13	AUTOCAR	MAN	HATTANE	LAVERIE MERA	ALLER	06:00	HATTANE	LAVERIE MERA -ZONE CENTRALE	06:40	\N	40	32.00	0.50	16.00
c41ac98a-3ff8-4d0a-823e-074f942d604f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAOUISI	S21	82516-A-13	AUTOCAR	MAN	HATTANE	LAVERIE MERA	RETOUR	06:45	LAVERIE MERA -ZONE CENTRALE	HATTANE	07:30	\N	45	32.00	0.50	16.00
8a70ab12-293e-45c3-89cc-c802a458c655	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAOUISI	S21	82516-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	13:50	KHOURIBGA	BENI AMIR LAVERIE	14:40	3-4-IMARA+OK	50	94.00	0.50	47.00
8269e553-0753-451d-984e-acd1fa96151f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAOUISI	S21	82516-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	ALLER	14:45	BENI AMIR LAVERIE	KHOURIBGA	15:30	F-Z-10-ALAOUINE	45	94.00	0.50	47.00
61e08c43-8ce2-4592-ae39-49685a97a84a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAOUISI	S21	82516-A-13	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	15:45	ZONE CENTRALE	KHOURIBGA	16:30	F-Z-10-V-5-4-3-Q	45	50.00	1.00	50.00
b102fa9b-632e-4db8-82c5-66c68c3494f8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFINDI	S21	82516-A-13	AUTOCAR	MAN	HATTANE	LAVERIE MERA	ALLER	22:00	HATTANE	LAVERIE MERA -ZONE CENTRALE	22:40	\N	40	46.00	0.50	23.00
a156168e-647e-40e4-bdfb-4579ae0d9877	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFINDI	S21	82516-A-13	AUTOCAR	MAN	HATTANE	LAVERIE MERA	RETOUR	22:45	LAVERIE MERA -ZONE CENTRALE	HATTANE	23:30	\N	45	46.00	0.50	23.00
dc982ad8-b7e9-4be3-b509-901d732a2aa0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFINDI	S21	82516-A-14	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	23:45	MLIKATE	KHOURIBGA	00:30	F-Z-10-1-2-H-T	45	74.00	1.00	74.00
53f6c9c2-433a-4ade-9293-e48a0fd02283	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFINDI	S21	82517-A-13	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	05:50	KHOURIBGA	PARC 7900	06:30	H-T-1-2-9-Z-F	40	60.00	1.00	60.00
7daa65cc-9688-49fd-b5d5-40fc3158e729	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AFINDI	S21	82517-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	07:00	KHOURIBGA	SIDI CHENNANE	07:45	N-A	45	104.00	1.00	104.00
0176f807-99f1-42bf-9901-4f307ceea072	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KASBI	S21	82517-A-13	AUTOCAR	MAN	BOULANOIR	SIDI CHENNANE	ALLER	14:00	BOULANOIR	SIDI CHENNANE	14:40	\N	40	86.00	0.50	43.00
1dbdf7ed-c7ce-441a-a40f-0907e2006ae0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KASBI	S21	82517-A-13	AUTOCAR	MAN	BOULANOIR	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	BOULANOIR	15:30	\N	45	86.00	0.50	43.00
282b89d0-3cce-4310-86ce-8919c36b1324	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KASBI	S21	82517-A-13	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	16:00	UB-UM3	KHOURIBGA	16:30	V-5-Q	30	54.00	1.00	54.00
30467c36-f36c-4a9b-aefb-efd45a0a6be2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KASBI	S21	82517-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE	KHOURIBGA	23:30	A+QODS	45	104.00	1.00	104.00
bd1cdbd9-fb64-4b45-ac25-b221541c12fb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BENAALOU	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	LAVERIE MERA	ALLER	05:50	KHOURIBGA	LAVERIE MERA	06:30	Q-5-V	40	46.00	1.00	46.00
c1ddea48-4c25-412b-a5fa-b94383aa895b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BENAALOU	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	BENI AMIR MINE	ALLER	07:00	KHOURIBGA	BENI AMIR LAVERIE &MINE	07:45	H-T-1-2-9-Z-F	45	96.00	1.00	96.00
faa7f86e-7cb4-4626-a1fd-936c3db0f1e5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BENAALOU	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	DAOUI	ALLER	12:50	KHOURIBGA	LAVERIE DAOUI	13:40	H-T-1-2-9-Z-F	50	86.00	0.50	43.00
9344e202-6e4e-4e47-ad0b-9f7c5d0ac6fd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BENAALOU	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	DAOUI	RETOUR	13:45	LAVERIE DAOUI	KHOURIBGA	14:30	V-5-Q	45	86.00	0.50	43.00
8620bca4-f529-4b45-86bc-0277b25aa6ad	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BENAALOU	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	BENI AMIR MINE	RETOUR	15:45	BENI AMIR MINE	KHOURIBGA	16:30	F-Z-10-1-2-H-T	45	96.00	1.00	96.00
2ac52aa1-72b8-462d-ad87-c8b96118905d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAQUAR	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	ALLER	21:50	KHOURIBGA	PARC 7900	22:40	H-T-1-2-3-4-5-OK	50	60.00	0.50	30.00
154c74a8-0ad1-41b7-a959-5a513dd56e42	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAQUAR	S22	78234-A-13	AUTOCAR	VOLVO	KHOURIBGA	PARC 7900	RETOUR	22:45	PARC 7900	KHOURIBGA	23:30	V-4-3-Q	45	60.00	0.50	30.00
d6c32695-1be9-43b6-81d3-f6976e8b7804	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAQUAR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	05:50	KHOURIBGA	SIDI CHENNANE (T)	06:40	H-T-1-2-10-Z-F	50	104.00	0.50	52.00
34bb4188-1393-4b8f-8fce-a80632386cd0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAQUAR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	06:45	SIDI CHENNANE (T)	KHOURIBGA	07:30	A-N	45	104.00	0.50	52.00
992e0c38-dc60-4465-adcf-44985597a200	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LAQUAR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	12:00	MLIKATE-7900	KHOURIBGA	12:30	A-N	30	80.00	1.00	80.00
cd00735b-dc4d-4261-a572-28281bc1a835	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIBIR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	12:50	KHOURIBGA	LAVERIE DAOUI	13:40	V-5-Q	50	86.00	0.50	43.00
cf4d2396-08b2-4cb4-93ee-435d830b42eb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIBIR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	13:45	LAVERIE DAOUI	KHOURIBGA	14:30	F-Z-10-1-2-H-T	45	86.00	0.50	43.00
9717e1a8-4232-4c79-953a-114079471fd4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIBIR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	15:45	BENI AMIR MINE	KHOURIBGA	16:30	ALAOUINE-V-Qods	45	96.00	1.00	96.00
b149cd47-6cdb-4ead-b19a-207e0d78730b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIBIR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	21:50	KHOURIBGA	ZONE CENTRALE	22:40	N-5-O.K-F	50	50.00	0.50	25.00
1c48ff17-2cf3-4e85-a17d-bdb470cc7cea	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIBIR	S23	82520-A-13	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	22:45	ZONE CENTRALE	KHOURIBGA	23:30	F-Z-10-1-2-H-T	45	50.00	0.50	25.00
e01f2898-a7e4-4f9f-ad64-ff4041cfc419	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	BOUJNIBA	ZONE CENTRALE	ALLER	06:00	BOUJNIBA	LAVERIE MERA -ZONE CENTRALE	06:40	\N	40	50.00	0.50	25.00
61118033-9e6f-4ec6-b3d8-015ee4879efe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42761	P2	467	AUTOCAR	MAN	BOUJNIBA	UB	ALLER	22:30	UB-UM3	BOUJNIBA	23:00	\N	30	15.00	0.50	7.50
849e8834-139f-4203-9d85-ef0a550d30b6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	BOUJNIBA	ZONE CENTRALE	RETOUR	06:45	LAVERIE MERA-ZONE CENTRALE	BOUJNIBA	07:30	\N	45	50.00	0.50	25.00
0fc9b166-95d6-4aff-b92c-4322bc3b8a85	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	KHOURIBGA	BENI AMIR MINE	ALLER	07:30	KHOURIBGA	BENI AMIR LAVERIE &MINE	08:15	N-A	45	96.00	1.00	96.00
1c34a8f1-e33c-4941-acb8-682be39399e6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	BOUJNIBA	ZONE CENTRALE	ALLER	14:00	BOUJNIBA	LAVERIE MERA -ZONE CENTRALE	14:40	\N	40	50.00	0.50	25.00
460bb5bf-6225-4850-b881-983f4ade2e80	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	BOUJNIBA	ZONE CENTRALE	RETOUR	14:45	LAVERIE MERA -ZONE CENTRALE	BOUJNIBA	15:30	\N	45	50.00	0.50	25.00
ab08eea6-d7f2-4df8-a250-9356619ee065	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	KHOURIBGA	DAOUI	RETOUR	15:45	DAOUI	KHOURIBGA	16:30	N-A	45	86.00	1.00	86.00
6103d8df-e58c-4c12-b5f5-b56bc7ae7627	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	KHOURIBGA	LAVERIE MERA	ALLER	21:50	KHOURIBGA	LAVERIE MERA	22:40	Q-5-V	50	46.00	0.50	23.00
4af15a04-8d3c-4161-8b47-ee39b847063e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CHOUHABI	S24	77839-A-13	AUTOCAR	VOLVO	KHOURIBGA	LAVERIE MERA	RETOUR	22:45	LAVERIE MERA	KHOURIBGA	23:30	OK-IMARA-5-Q	45	46.00	0.50	23.00
a56bac18-55b9-4ca6-9eec-6a242cb38953	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	06:00	KHOURIBGA	POULE DAOUI	06:40	\N	40	90.00	0.50	45.00
d6f24f17-f4b4-4d20-8431-6670ac3f2502	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	06:45	POULE DAOUI	KHOURIBGA	07:30	\N	45	90.00	0.50	45.00
20394fec-7896-4c6d-a262-00924490cfac	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	NAVETTE	ALLER	08:00	KHOURIBGA	KHOURIBGA	08:30	F----->VILLAGE	30	2.00	1.00	2.00
ff484d83-c483-478c-92c7-3e7696135d20	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	14:00	KHOURIBGA	POULE DAOUI	14:40	\N	40	90.00	0.50	45.00
5f193f69-3aff-4d07-a18c-7cce3b927a5d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	14:45	POULE DAOUI	KHOURIBGA	15:30	\N	45	90.00	0.50	45.00
24989699-06e8-43ff-8b01-2aca0df0df38	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	22:00	KHOURIBGA	POULE DAOUI	22:40	\N	40	90.00	0.50	45.00
062ac568-5659-468c-a969-10274b6526ab	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SAROUT	S25	84112-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	22:45	POULE DAOUI	KHOURIBGA	23:30	\N	45	90.00	0.50	45.00
57a5d218-ab55-4300-9443-8796ec398ce6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	06:00	KHOURIBGA	POULE FQUIH BEN SALEH	06:40	\N	40	80.00	0.50	40.00
8f79cce2-92a2-4dac-adbb-53347ff219d6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	06:45	POULE FQUIH BEN SALEH	KHOURIBGA	07:30	\N	45	80.00	0.50	40.00
5e1d5804-4e78-42f1-9c5c-16023402f3b3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	14:00	KHOURIBGA	POULE FQUIH BEN SALEH	14:40	\N	40	80.00	0.50	40.00
39641bac-b0f8-4396-92a2-09016114150c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	14:45	POULE FQUIH BEN SALEH	KHOURIBGA	15:30	\N	45	80.00	0.50	40.00
c84ff5a5-9bd3-4dc6-bfad-eaebf8739957	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	ALLER	22:00	KHOURIBGA	POULE FQUIH BEN SALEH	22:40	\N	40	80.00	0.50	40.00
4477f48d-bb51-427a-a121-d19d3a0817fc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KIDDI	S26	84113-A-13	MINIBUS	MERCEDES	KHOURIBGA	POULE	RETOUR	22:45	POULE FQUIH BEN SALEH	KHOURIBGA	23:30	\N	45	80.00	0.50	40.00
edd7f857-4ea2-4f4a-9296-78e25d3c5757	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	ALLER	06:00	OUED ZEM	COZ	06:30	\N	30	16.00	0.50	8.00
4010aaeb-99c6-441c-8a98-d503dee224e6	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	RETOUR	07:00	COZ	OUED ZEM	07:30	\N	30	16.00	0.50	8.00
c40eeb67-6e28-4e12-b5f1-8e5efdff2040	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	NAVETTE	ALLER	07:30	OUED ZEM	OUED ZEM	08:30	\N	60	16.00	1.00	16.00
2807b390-0d4e-45c8-bab1-d18f85f7f872	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	ALLER	14:00	OUED ZEM	COZ	14:30	\N	30	16.00	0.50	8.00
aa2d5378-8174-4c0d-b9c2-7a0257af89e0	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	RETOUR	15:00	COZ	OUED ZEM	15:30	\N	30	16.00	0.50	8.00
313d9174-2036-4ef8-80b0-3f25f039ce8d	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	T2	RETOUR	15:45	T2	OUED ZEM	16:30	\N	45	110.00	1.00	110.00
afa40577-a3dd-4eb4-9a80-1024378325ad	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	DAOUI	RETOUR	18:00	LAVERIE DAOUI	OUED ZEM	18:30	\N	30	70.00	1.00	70.00
434ff866-f726-4338-a55a-33cb28ccecec	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	ALLER	22:00	OUED ZEM	COZ	22:30	\N	30	16.00	0.50	8.00
f56e155a-09e0-467c-a6a4-4858d13e803c	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	COZ	RETOUR	23:00	COZ	OUED ZEM	23:30	\N	30	16.00	0.50	8.00
ddb7d315-cd50-464e-8651-feb68de0f0b5	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HILALI	S27	84114-A-13	MINIBUS	MERCEDES	OUEDZEM	NAVETTE	ALLER	23:30	OUED ZEM	OUED ZEM	00:30	\N	60	2.00	1.00	2.00
e1a39bd3-73b7-42ca-9c53-ec18d53f0b32	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	ALLER	06:00	BOUNJIBA-LAGFAF-BIR MEZOUI	DAOUI  (PTA)	06:30	\N	30	70.00	0.50	35.00
99086eb7-c695-4d2c-b149-831eb252da56	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	RETOUR	06:45	DAOUI  (PTA)	BOUNJIBA-LAGFAF-BIR MEZOUI	07:30	\N	45	70.00	0.50	35.00
b09b2e86-08cf-4c40-9c6e-f9e1dfcac26c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	ZONE CENTRALE	RETOUR	07:45	ZONE CENTRALE	HATTANE-BOUJNIBA	08:30	\N	45	50.00	1.00	50.00
1b609a23-c867-42b0-abc7-f1f1f3cf94de	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	ALLER	14:00	BOUNJIBA-LAGFAF-BIR MEZOUI	DAOUI  (PTA)	14:30	\N	30	70.00	0.50	35.00
3c50631c-a234-4225-b54a-af66304d5fe1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	RETOUR	14:45	DAOUI  (PTA)	BOUNJIBA-LAGFAF-BIR MEZOUI	15:30	\N	45	70.00	0.50	35.00
00af06cd-8ea2-490b-a1ba-3317144a18a2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	ZONE CENTRALE	RETOUR	15:45	ZONE CENTRALE	HATTANE-BOUJNIBA	16:30	\N	45	50.00	1.00	50.00
7096643d-13a0-4809-94fa-0fbb050bc740	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	ALLER	22:00	BOUNJIBA-LAGFAF-BIR MEZOUI	DAOUI  (PTA)	22:30	\N	30	70.00	0.50	35.00
b35a284d-e7cf-49e8-a875-3627bb3909d7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	DAOUI	RETOUR	22:45	DAOUI  (PTA)	BOUNJIBA-LAGFAF-BIR MEZOUI	23:30	\N	45	70.00	0.50	35.00
37dff8f4-92f3-43f8-83fd-28052a49ce6c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SOUSSI	S28	84116-A-13	MINIBUS	MERCEDES	BOUJNIBA	ZONE CENTRALE	RETOUR	23:45	ZONE CENTRALE	HATTANE-BOUJNIBA	00:30	\N	45	50.00	1.00	50.00
ff6904b4-7ae6-4b47-877b-a5a83c579a68	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SRAIDI	S29	84118-A-14	MINIBUS	MERCEDES	KHOURIBGA	UB	ALLER	08:30	KHOURIBGA	UB	09:00	N-A	30	50.00	1.00	50.00
55b01510-4730-4db9-b4c2-6a020f26a8d4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SRAIDI	S29	84118-A-14	MINIBUS	MERCEDES	KHOURIBGA	PIPE LINE	RETOUR	15:30	PIPE LINE & LAVERIE MERA	KHOURIBGA	16:30	N-A	60	50.00	1.00	50.00
177161a5-67b7-41ff-aea3-336ccb9c4943	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	SRAIDI	S29	84118-A-14	MINIBUS	MERCEDES	KHOURIBGA	NAVETTE	ALLER	21:00	KHOURIBGA	KHOURIBGA	00:30	10----->HAY BADR	210	2.00	1.00	2.00
a72f240f-8a22-41ed-91bf-b10636712f80	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAIYA	S30	79806-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:30	KHOURIBGA	KHOURIBGA	08:30	5<----->Q,I	180	2.00	10.00	20.00
0a828f5a-0bf6-4b2f-88fc-7730acc08e65	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAIYA	S30	79806-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:30	KHOURIBGA	KHOURIBGA	16:30	5<----->Q,I	180	2.00	9.00	18.00
7f1aa551-d8a8-4a11-8ab4-beb1b301ab44	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAIYA	S30	79806-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	16:45	KHOURIBGA	KHOURIBGA	17:30	5------->HAY RIAD	45	6.00	1.00	6.00
a3a69224-0b45-4eb7-95b7-52e714b08f74	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAIYA	S30	79806-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:30	KHOURIBGA	KHOURIBGA	00:30	5<----->Q,I	180	2.00	9.00	18.00
d0c3633b-9d8f-4f3c-abfe-f5ddc28382ac	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUHALLA	S31	79637-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:30	KHOURIBGA	KHOURIBGA	08:30	\N	180	3.00	10.00	30.00
25165409-0bd9-469f-a600-5eeeb87502a8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUHALLA	S32	79637-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	3.00	9.00	27.00
9b5ce030-67e3-4f08-925d-041bc7f51a61	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUHALLA	S33	79637-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	3.00	8.00	24.00
71c77c64-f326-4740-af16-b503188f9aad	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:10	Q-FERME	20	6.00	0.50	3.00
288a44ce-3696-4bfc-a5b3-850d722ecd86	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	RETOUR	07:10	KHOURIBGA	KHOURIBGA	07:30	FERME-Q	20	6.00	0.50	3.00
19e0f837-4181-4375-99bf-6af36f103fe3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	LABORATOIRE	ALLER	08:30	KHOURIBGA	LABORATOIRE	09:00	CLUB EQUESTRE	30	30.00	1.00	30.00
787d4169-8346-4e18-b3da-fc10cb651622	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:50	KHOURIBGA	KHOURIBGA	14:10	Q-FERME	20	6.00	0.50	3.00
ea7d6a0a-d80a-4860-8a68-86b4a71dd7f1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	RETOUR	15:10	KHOURIBGA	KHOURIBGA	15:30	FERME-Q	20	6.00	0.50	3.00
3182fb20-ac5a-4331-8623-b8081a398b06	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	16:00	KHOURIBGA	KHOURIBGA	16:30	FERME-VILLAGE	30	2.00	1.00	2.00
a208dbc0-292f-45e4-8649-165849f25ddc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:50	KHOURIBGA	KHOURIBGA	22:10	Q-FERME	20	6.00	0.50	3.00
2bf12ca6-89fb-4a1e-b7a8-8aaff137182b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	RETOUR	23:10	KHOURIBGA	KHOURIBGA	23:30	FERME-Q	20	6.00	0.50	3.00
7e8d5161-48f3-413c-917c-33ef85cc9aa9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BELBARODIA	S34	79826-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	23:30	KHOURIBGA	KHOURIBGA	00:30	10----->HAY RIAD	60	6.00	1.00	6.00
416578d6-5a31-43c0-be12-52b9c9c831a9	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	ALLER	06:00	OUED ZEM	DAOUI  (PTA)	06:30	\N	30	70.00	0.50	35.00
47b581e1-5830-43f2-9df8-6147f940fd97	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	RETOUR	06:45	DAOUI  (PTA)	OUED ZEM	07:15	\N	30	70.00	0.50	35.00
7ab71d01-9898-4086-bccc-989df05b306d	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	07:15	OUED ZEM	OUED ZEM	07:30	\N	15	2.00	1.00	2.00
a64ddbcc-0396-424d-ad1f-94df0b6979aa	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	VS	ALLER	07:30	OUED ZEM	KHOURIBGA	09:00	\N	90	70.00	0.50	35.00
c70c09c3-b8ab-40a1-a633-214c74dd2a99	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	VS	RETOUR	12:00	KHOURIBGA	OUED ZEM	12:30	\N	30	70.00	0.50	35.00
bc582551-f618-4a7a-b0b0-9b61505f26db	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	ALLER	14:00	OUED ZEM	DAOUI  (PTA)	14:30	\N	30	70.00	0.50	35.00
91b4f3dc-83d4-4c1c-b302-b14160965786	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	RETOUR	14:45	DAOUI  (PTA)	OUED ZEM	15:30	\N	45	70.00	0.50	35.00
98db3e8b-fb10-4638-8661-4c6b58807a41	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	ALLER	22:00	OUED ZEM	DAOUI  (PTA)	22:30	\N	30	70.00	0.50	35.00
19989a35-c6c3-46f9-af13-759c9af1665c	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	OUGUIGI	S35	79636-A-13	MINIBUS	HYUNDAI	OUEDZEM	DAOUI	RETOUR	22:45	DAOUI  (PTA)	OUED ZEM	23:15	\N	30	70.00	0.50	35.00
561f2728-8fce-460b-ae12-bed0f08eba10	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARIZ	S36	79644-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:00	KHOURIBGA	KHOURIBGA	08:30	10----->ZITOUNA	210	4.00	9.00	36.00
8e394945-9cfa-4ab7-9dca-776ac858adb8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARIZ	S36	79644-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	12:00	KHOURIBGA	KHOURIBGA	12:30	10----->ZITOUNA	30	4.00	2.00	8.00
6138dfad-8bf6-469e-98d2-6e76aa1a645a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARIZ	S36	79644-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:00	KHOURIBGA	KHOURIBGA	16:30	10----->ZITOUNA	210	4.00	9.00	36.00
717df3b3-b8d9-4203-a604-eb515d64dafd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HARIZ	S36	79644-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	15:10	KHOURIBGA	KHOURIBGA	15:20	10------>JAWHARA	10	2.00	1.00	2.00
eb2805c3-dd27-478c-b2f5-7384b82cb986	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:45	KHOURIBGA	KHOURIBGA	06:00	JAWHARA---->10	15	2.00	1.00	2.00
130ca2b1-3ec5-472f-ad33-c8a59676a5cb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	BOULANOIR	PARC 7900	RETOUR	07:45	MLIKATE-7900	BOULANOIR	08:30	\N	45	70.00	1.00	70.00
060a39b4-6c52-4902-9fbc-f4bc3c2b707c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	RETOUR	12:00	KHOURIBGA	KHOURIBGA	12:30	10---->Q	30	6.00	1.00	6.00
4e047cce-bf48-4025-84dd-ce2d1654872e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:50	KHOURIBGA	KHOURIBGA	14:00	Q---->5	10	5.00	1.00	5.00
c5495ae6-0929-4e6f-a047-347d19b7a695	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	15:10	KHOURIBGA	KHOURIBGA	15:30	FERME-Q	20	6.00	1.00	6.00
77813760-2bdd-4d72-9ff3-5e5a9b8c54b4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	16:00	KHOURIBGA	KHOURIBGA	16:30	10----->Q	30	6.00	1.00	6.00
ebc87534-4a52-4043-9874-12e6b9eb0a29	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHRI	S37	79795-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:00	KHOURIBGA	KHOURIBGA	00:30	10----->ZITOUNA	210	4.00	1.00	4.00
4a0bb6ff-ec26-4c8f-8d8c-3804cce3cc09	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LACHTOUKI	S38	79796-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:20	KHOURIBGA	KHOURIBGA	08:30	TAMOUD---->3	190	5.00	8.00	40.00
5ceef763-2654-415f-bf4a-3a0ad6b86147	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LACHTOUKI	S38	79796-A-13	MINIBUS	HYUNDAI	KHOURIBGA	STEP	RETOUR	12:00	STEP	KHOURIBGA	12:30	\N	30	5.00	1.00	5.00
479e20af-5b07-4a70-a51e-762325c2df97	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LACHTOUKI	S38	79796-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:40	KHOURIBGA	KHOURIBGA	17:00	TAMOUD---->5	200	5.00	6.00	30.00
1ac021fe-4746-4c16-af9d-27d209ecb943	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LACHTOUKI	S38	79796-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:40	KHOURIBGA	KHOURIBGA	00:30	TAMOUD---->3	170	5.00	5.00	25.00
069dd5ab-a7b2-4a2a-b739-0b5843b57706	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ESSABRI	S39	79805-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:40	KHOURIBGA	KHOURIBGA	08:30	JAR EL KHAIR--->3	170	4.00	7.00	28.00
04410689-9118-4382-8879-476d70663b74	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ESSABRI	S39	79805-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:40	KHOURIBGA	KHOURIBGA	17:00	JAR EL KHAIR--->5	200	5.00	6.00	30.00
3e9c6feb-1c2c-4bde-97d5-3aa463c4a042	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ESSABRI	S39	79805-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	21:40	KHOURIBGA	KHOURIBGA	00:30	JAR EL KHAIR--->3	170	4.00	5.00	20.00
4a145363-a2d8-4674-b9c3-851e8832c036	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERAIS	S40	79402-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	05:00	KHOURIBGA	KHOURIBGA	08:30	10---->HAY BADR	210	2.00	10.00	20.00
077af87b-d96f-47b6-b500-182618529f1d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERAIS	S40	79402-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	13:00	KHOURIBGA	KHOURIBGA	14:30	10---->HAY BADR	90	2.00	2.00	4.00
10e18a5f-0c25-4af8-9777-0b434b68d732	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERAIS	S40	79402-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	15:00	KHOURIBGA	KHOURIBGA	15:15	10---->VILLAGE	15	2.00	1.00	2.00
b63c5d27-fe1a-42a5-a2c6-907a55c2bef7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERAIS	S40	79402-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	15:15	KHOURIBGA	KHOURIBGA	15:30	5------>HAY RIAD	15	6.00	1.00	6.00
d6d0dc8d-fbc4-4213-8e2b-a652171fb8bf	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERAIS	S40	79402-A-13	MINIBUS	HYUNDAI	KHOURIBGA	NAVETTE	ALLER	16:15	KHOURIBGA	KHOURIBGA	16:30	CFO--->N	15	3.00	1.00	3.00
e3b39093-c82b-45fa-8635-135790d2b75e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	ALLER	06:00	BOULANOIR	UB	06:30	\N	30	40.00	0.50	20.00
565145d1-9931-45dc-a986-5dd55e62130d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	RETOUR	06:40	UB	BOULANOIR	07:00	\N	20	40.00	0.50	20.00
7846adad-c419-4a1f-9ac3-80379846c168	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	KHOURIBGA	RECETT6	ALLER	07:00	KHOURIBGA	RECETTE 6	07:30	N-A	30	48.00	1.00	48.00
e4da8104-8a76-4312-a35d-1544216ce767	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	ALLER	14:00	BOULANOIR	UB	14:30	\N	30	40.00	0.50	20.00
44ced736-1f75-4b28-aee1-246ea07d09f5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	RETOUR	14:40	UB	BOULANOIR	15:00	\N	20	40.00	0.50	20.00
9e1b4fd4-e83d-454b-8630-01291a4c4412	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	15:00	KHOURIBGA	KHOURIBGA	17:00	AVOLA----->TAMOUD	120	3.00	1.00	3.00
91ca3143-7f43-44de-8b86-4435a8fd4b40	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	ALLER	22:00	BOULANOIR	UB	22:30	\N	30	40.00	0.50	20.00
b261d1a9-344c-419c-b5e1-83998e41a1b2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	BOULANOIR	UB	RETOUR	22:40	UB	BOULANOIR	23:00	\N	20	40.00	0.50	20.00
08262f78-d06c-481b-a3f3-3514b909ab87	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	23:00	KHOURIBGA	KHOURIBGA	23:30	10---->VILLAGE	30	2.00	1.00	2.00
0156ba12-fd7d-4a11-acd2-ac3b93029a7c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MOSBAH	S41	63690-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	00:00	KHOURIBGA	KHOURIBGA	00:30	10---->Q	30	6.00	1.00	6.00
b5278f31-0ebb-41d7-a957-f398efeb71e8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	ALLER	06:00	BOULANOIR	MLIKATE	06:40	\N	40	70.00	0.50	35.00
4568ccf4-07be-4fa3-a92a-b9262b42c394	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	RETOUR	06:45	MLIKATE	BOULANOIR	07:30	\N	45	70.00	0.50	35.00
89080baa-b5e5-4ace-8848-6e67da681fe3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	KHOURIBGA	ZONE CENTRALE	RETOUR	07:45	ZONE CENTRALE	KHOURIBGA	08:30	A-N	45	50.00	1.00	50.00
456be829-d4d3-4b75-8e06-19f653877a4f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	ALLER	14:00	BOULANOIR	MLIKATE	14:30	\N	30	70.00	0.50	35.00
6d3d9723-825c-42ed-a7e5-6d1f42693db6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	RETOUR	14:40	MLIKATE	BOULANOIR	15:30	\N	50	70.00	0.50	35.00
e73467a0-03f3-41db-af61-c71edaf1e12c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	KHOURIBGA	UB	RETOUR	15:45	UB	KHOURIBGA	16:30	\N	45	50.00	1.00	50.00
dee71a09-c041-44a9-9832-742855a9ad29	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	ALLER	22:00	BOULANOIR	MLIKATE	22:30	\N	30	70.00	0.50	35.00
96a09d9e-4803-4ff5-ab4b-dab1147426ea	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRI	S42	77757-A-13	MINICAR	ISUZU	BOULANOIR	MLIKATE	RETOUR	22:45	MLIKATE	BOULANOIR	23:30	\N	45	70.00	0.50	35.00
1353c248-a84b-4047-ba7c-5885940939ec	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	ALLER	06:00	HATTANE	MLIKATE	06:40	\N	40	56.00	0.50	28.00
b48ff71b-16b4-464c-b0d5-45e7f905c6c8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	06:45	MLIKATE	HATTANE	07:30	\N	45	56.00	0.50	28.00
346310e9-cd1f-4a11-8896-9c8230847bef	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	07:45	MLIKATE-7900	HATTANE	08:30	\N	45	60.00	1.00	60.00
a6db80c5-2681-4ed4-be29-c9a7f499d87c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	ALLER	14:00	HATTANE	MLIKATE	14:30	\N	30	56.00	0.50	28.00
ba1b8616-96fd-432a-bcbf-f9ef4aca8ba1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	14:40	MLIKATE	HATTANE	15:30	\N	50	56.00	0.50	28.00
869fac39-9a6e-4e4b-b9db-6c4bd5e3e0e1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	KHOURIBGA	LABORATOIRE	RETOUR	15:45	LABORATOIRE	KHOURIBGA	16:30	\N	45	30.00	1.00	30.00
d158dc4f-ecd4-420c-8c6e-8925cfa56399	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	ALLER	22:00	HATTANE	MLIKATE	22:30	\N	30	56.00	0.50	28.00
3f910413-3482-4f8c-a6a8-ac1b98b2a9fc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	22:45	MLIKATE	HATTANE	23:30	\N	45	56.00	0.50	28.00
e4921532-8b4d-4bcc-af50-a14d7cd60c6a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AKESSBI	S43	64026-A-14	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	23:45	MLIKATE-7900	HATTANE	00:30	\N	45	60.00	1.00	60.00
f2f7ea0c-976a-402c-b51d-57a8ecdd858e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:00	\N	10	3.00	1.00	3.00
16fc7d20-f554-4549-b7f3-c1a15a21f09c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	06:45	KHOURIBGA	KHOURIBGA	07:00	5--->HAY RIAD	15	6.00	1.00	6.00
d01082f0-f4b4-4a2c-aefc-671680e4b4e3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	KHOURIBGA	MLIKATE	ALLER	07:00	KHOURIBGA	PARC 7900-MLIKATE	07:40	Q+5+9+10	40	74.00	1.00	74.00
5ccf5bd0-ab41-4688-b59f-8c018d497e2e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	BOULANOIR	MLIKATE	RETOUR	15:45	MLIKATE-7900	BOULANOIR	16:30	\N	45	70.00	1.00	70.00
1eeda94d-7bd0-4297-9c31-7720ab397946	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	BOULANOIR	PARC 7900	ALLER	22:00	BOULANOIR	LAVERIE MERA-7900	22:30	\N	30	50.00	0.50	25.00
0a22f43d-0272-496b-878c-1b8e13337e78	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	S.TOURISME	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HADDAOUI	S44	63689-A-14	MINICAR	ISUZU	BOULANOIR	MLIKATE	RETOUR	23:45	MLIKATE-7900	BOULANOIR	00:30	\N	45	50.00	0.50	25.00
c04d54f5-e807-4c14-b45a-0d8b162d8c3f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	PARC 7900	ALLER	06:00	HATTANE	PARC 7900	06:30	\N	30	56.00	0.50	28.00
edfe26ec-5085-4dab-b671-756b9ec004af	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	MLIKATE	RETOUR	06:45	MLIKATE	HATTANE	07:30	\N	45	56.00	0.50	28.00
e76a73a6-6786-4534-900c-11344bc22d92	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	08:15	KHOURIBGA	KHOURIBGA	08:30	5--->HAY RIAD	15	6.00	1.00	6.00
efbff34d-e042-4e42-80a3-4c4773f50975	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	KHOURIBGA	LAVERIE MERA	ALLER	08:20	KHOURIBGA	PIPE LINE-LAVERIE MERA	09:00	\N	40	50.00	1.00	50.00
77024b07-7409-4d34-8d3b-66f41df1ef0a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	PARC 7900	ALLER	14:00	HATTANE	PARC 7900	14:30	\N	30	46.00	0.50	23.00
ac5cd79d-8ad3-4f9b-99c3-0ef6b41e67c6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	PARC 7900	RETOUR	14:45	PARC 7900	HATTANE	15:30	\N	45	46.00	0.50	23.00
c37026b4-2fec-4a51-9590-e71ae18167e9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	KHOURIBGA	RECETT6	RETOUR	16:00	RECETTE 6	KHOURIBGA	16:30	T+10+Z+OM QORA+Q	30	48.00	1.00	48.00
77a60bf3-1ede-459a-9ec5-a0478402519c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	PARC 7900	ALLER	22:00	HATTANE	PARC 7900	22:30	\N	30	46.00	0.50	23.00
52de560b-2596-4090-950c-ba4e8f44fe5e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BAHOUT	S45	77753-A-13	MINICAR	ISUZU	HATTANE	PARC 7900	RETOUR	22:45	PARC 7900	HATTANE	23:30	\N	45	46.00	0.50	23.00
0c855cb0-eb40-4a57-b652-36062d5ef5c1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	ALLER	06:20	MERA	ZONE CENTRALE-7900-MLIKATE	06:45	\N	25	78.00	0.50	39.00
3a40d57d-bcd5-426b-a6d9-5707071e9a62	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	RETOUR	07:00	MLIKATE-7900-ZONE CENTRALE	MERA	07:30	\N	30	78.00	0.50	39.00
87340b63-37a2-4ffe-a90e-42a9a74a98e2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	KHOURIBGA	STEP	ALLER	08:20	KHOURIBGA	STEP	08:45	\N	25	10.00	1.00	10.00
e5249b0b-77d8-4ef4-aa9b-6ea4fe1360f0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	ALLER	13:20	MERA	ZONE CENTRALE-7900-MLIKATE	13:45	\N	25	78.00	0.50	39.00
9f8daa45-329d-4170-862c-c11db95defd8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	RETOUR	14:00	MLIKATE-7900-ZONE CENTRALE	MERA	14:30	\N	30	78.00	0.50	39.00
621c6271-3e7b-4bdd-8556-0ce3927dbb1e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	RETOUR	15:30	MLIKATE-7900-ZONE CENTRALE	MERA	16:00	\N	30	78.00	1.00	78.00
07f0864d-240b-4bb5-a86b-ee590873f52e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	ALLER	21:20	MERA	ZONE CENTRALE-7900-MLIKATE	21:45	\N	25	78.00	0.50	39.00
e560233a-9be9-40ec-aff1-49dfda615437	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	RETOUR	22:00	MLIKATE-7900-ZONE CENTRALE	MERA	22:30	\N	30	78.00	0.50	39.00
e16f4bbb-8d10-4937-b9b0-ecedf5365ec4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MAGDOUD	S46	77756-A-13	MINICAR	ISUZU	HATTANE	MERA	RETOUR	23:30	MLIKATE-7900-ZONE CENTRALE	MERA	00:00	\N	30	78.00	1.00	78.00
f9887b99-a0b1-4791-803d-9b4889655cfe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:00	\N	10	2.00	1.00	2.00
f0597843-5ccf-409f-8657-d135e44a436f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	ALLER	06:00	KHOURIBGA	BENI AMIR MINE	06:40	N-A	40	96.00	0.50	48.00
f4e58ac0-b713-4341-bc89-303316baf533	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	RETOUR	07:45	BENI AMIR MINE	KHOURIBGA	08:30	\N	45	96.00	0.50	48.00
0a838d82-9940-4939-912d-42d939c003be	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	ALLER	14:00	KHOURIBGA	BENI AMIR MINE	14:40	N-A	40	96.00	0.50	48.00
3edf98eb-1995-4cc5-8fca-cc97ccd0a213	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	RETOUR	15:45	BENI AMIR MINE	KHOURIBGA	16:30	N-A	45	96.00	0.50	48.00
ae3908f6-4390-460d-8643-5bc0469fc473	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	21:50	KHOURIBGA	KHOURIBGA	22:00	Q---->5	10	96.00	1.00	96.00
ef3ea072-7c31-44f4-b60b-80697c597b1a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	ALLER	22:00	KHOURIBGA	BENI AMIR MINE	22:40	N-A	40	96.00	0.50	48.00
a98eba62-f1de-48ab-bed7-ccddd9dce76a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ALOUL	S47	64025-A-14	MINICAR	ISUZU	KHOURIBGA	BENI AMIR MINE	RETOUR	23:45	BENI AMIR MINE	KHOURIBGA	00:30	N-A	45	96.00	0.50	48.00
210d5f51-a341-48b7-b1be-35a6001a1bbc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LIAMANI	S48	65382-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	05:30	KHOURIBGA	KHOURIBGA	08:30	EL AIDI---->3	180	7.00	9.00	63.00
3f701109-9e12-447a-8690-c36441d03fd4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LIAMANI	S48	65382-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	13:30	KHOURIBGA	KHOURIBGA	16:30	EL AIDI---->3	180	7.00	8.00	56.00
074a9758-d096-489f-b634-47e03cb8ef6f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	STCR	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	LIAMANI	S48	65382-A-14	MINICAR	ISUZU	KHOURIBGA	NAVETTE	ALLER	21:30	KHOURIBGA	KHOURIBGA	00:30	EL AIDI---->3	180	7.00	8.00	56.00
ce2981bd-f0d7-4165-8c74-ae69e89b1207	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	DARNAKH/EL KOUDI	S49	65409-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	04:50	KHOURIBGA	KHOURIBGA	08:30	5<------>HAY RIAD	220	6.00	10.00	60.00
9399366c-f32f-49d2-9e33-ef2bd9140bcb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	DARNAKH/EL KOUDI	S49	65409-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	12:50	KHOURIBGA	KHOURIBGA	17:00	5<------>HAY RIAD	250	6.00	11.00	66.00
23148428-a384-4136-b971-b5a59e906564	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	DARNAKH/EL KOUDI	S49	65409-A-12	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	20:50	KHOURIBGA	KHOURIBGA	00:30	5<------>HAY RIAD	220	6.00	10.00	60.00
463825f9-4254-4878-87a6-4311ef48c27e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MOUKANE	S50	65408-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	05:40	KHOURIBGA	KHOURIBGA	08:30	H4<------>HAY ESSAFAA	170	10.00	8.00	80.00
9782e3a7-8158-4b93-84de-378270aa0790	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MOUKANE	S50	65408-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	13:40	KHOURIBGA	KHOURIBGA	16:30	H4<------>HAY ESSAFAA	170	10.00	7.00	70.00
6626b796-f221-4a75-9e9d-9475f3a615e8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL MOUKANE	S50	65408-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	21:40	KHOURIBGA	KHOURIBGA	00:30	H4<------>HAY ESSAFAA	170	10.00	8.00	80.00
95abbb92-0d60-4042-8f57-d1c92ccfba77	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	ALLER	05:00	KHOURIBGA	UTAC	06:00	\N	60	80.00	1.00	80.00
4f6582f6-c200-4789-adc7-d1809b0aa2ca	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	ALLER	08:00	KHOURIBGA	UTAC	09:00	\N	60	80.00	1.00	80.00
04d00945-bf40-4ce4-a6e6-74ede37a7344	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	MERA	RETOUR	12:00	MERA	KHOURIBGA	12:30	N-A	30	60.00	1.00	60.00
6d3e310e-0b96-4e8d-acca-08ec9a07cf32	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	ALLER	13:00	KHOURIBGA	UTAC	14:00	\N	60	80.00	0.50	40.00
f6ebe273-37d0-466a-a1c7-007c62dbccd0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	RETOUR	14:00	UTAC	KHOURIBGA	15:00	\N	60	80.00	0.50	40.00
a75be9b4-7b9d-4a91-a7df-fa8788984b47	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	RETOUR	18:00	UTAC	KHOURIBGA	19:00	\N	60	80.00	1.00	80.00
6e6c9443-f126-4172-95a9-bad834412f57	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	BOUKRIM	S51	65410-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	RETOUR	22:00	UTAC	KHOURIBGA	23:00	\N	60	80.00	1.00	80.00
50e18755-8c36-4a0a-8ade-f5530252a585	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HAMASSI	S52	65659-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	05:20	KHOURIBGA	KHOURIBGA	05:30	HAY ESSAFAA----->H4	10	10.00	1.00	10.00
0c32ce97-24b3-4583-bb7f-311f4473ab2c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HAMASSI	S52	65659-A-11	MINIBUS	FORD	KHOURIBGA	NAVETTE	ALLER	05:30	KHOURIBGA	KHOURIBGA	05:45	EL AIDI---->3	15	7.00	1.00	7.00
9ac8f0bc-c8f2-4baa-8f77-ac031f550d50	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HAMASSI	S52	65659-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	ALLER	08:00	KHOURIBGA	UTAC	09:00	\N	60	80.00	1.00	80.00
cb9e4a9a-e223-4783-a4f8-ef26413426cc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	EL HAMASSI	S52	65659-A-11	MINIBUS	FORD	KHOURIBGA	UTAC	ALLER	18:00	UTAC	KHOURIBGA	19:00	\N	60	80.00	1.00	80.00
690401a6-b503-4bd1-978f-abe8de46ba2b	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERRAZIQI	S53	65405-A-11	MINIBUS	FORD	OUEDZEM	NAVETTE	ALLER	05:30	OUED ZEM	OUED ZEM	08:30	\N	180	4.00	5.00	20.00
ce1f4391-0eef-4c78-8a30-6b2d638a213e	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERRAZIQI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	SIDI CHENNANE	ALLER	07:00	OUED ZEM	SIDI CHENNANE	07:30	\N	30	76.00	1.00	76.00
de0cd04b-5d50-4f1c-a554-e7bfc034becf	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERRAZIQI	S53	65405-A-11	MINIBUS	FORD	OUEDZEM	NAVETTE	ALLER	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	4.00	3.00	12.00
f70d67c2-a565-48fb-a3a9-b34fe189b42c	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ERRAZIQI	S53	65405-A-11	MINIBUS	FORD	OUEDZEM	NAVETTE	ALLER	22:00	OUED ZEM	OUED ZEM	00:30	\N	150	4.00	5.00	20.00
6137a15d-7829-46f0-9750-65f194c04054	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MERRASSI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	UTAC	ALLER	08:00	OUED ZEM	UTAC	08:30	\N	30	30.00	1.00	30.00
949af850-5f7b-44ef-ba08-f03b12b38a1c	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MERRASSI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	SIDI CHENNANE	RETOUR	12:30	SIDI CHENNANE	OUED ZEM	13:00	\N	30	76.00	1.00	76.00
970f9953-ee80-4fdf-a73e-926b56954df9	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MERRASSI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	NAVETTE	ALLER	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	4.00	4.00	16.00
e9975583-eb96-428f-a320-9c09050176e2	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MERRASSI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	UTAC	RETOUR	18:00	UTAC	OUED ZEM	18:30	\N	30	30.00	1.00	30.00
591b3360-7f70-432d-9c7a-a73f66349efa	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	MANAVETTE	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	MERRASSI	S54	65411-A-11	MINIBUS	FORD	OUEDZEM	NAVETTE	ALLER	20:45	OUED ZEM	OUED ZEM	00:30	\N	225	4.00	4.00	16.00
08e5f1f2-5852-439f-9b1b-cca7af0c01fc	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	ALLER	05:50	OUED ZEM	T2	06:30	\N	40	74.00	0.50	37.00
599cb91f-14a1-4fc9-b169-b0241468ca87	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	RETOUR	06:45	T2	OUED ZEM	07:15	\N	30	74.00	0.50	37.00
c306d7b2-52b6-49b0-935d-b9ad47729884	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	ALLER	13:50	OUED ZEM	T2	14:30	\N	40	74.00	0.50	37.00
068de65b-ebdb-41f8-92ad-1c0e4da69b48	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	RETOUR	14:45	T2	OUED ZEM	15:15	\N	30	74.00	0.50	37.00
5e823b7c-0f5e-4956-88b5-b176a001d5d2	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	15:45	T1	OUED ZEM	16:30	\N	45	74.00	1.00	74.00
b2e49241-e406-4503-84bd-18990dc3cee9	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	ALLER	21:50	OUED ZEM	T2	22:30	\N	40	74.00	0.50	37.00
5d20a8cd-846c-42ba-98e4-aee6d028bcb0	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	RETOUR	22:45	T2	OUED ZEM	23:15	\N	30	74.00	0.50	37.00
65523bb1-180c-45bf-8e08-b4fbfcdd7520	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	KARIMI	S55	70944-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	23:45	T1	OUED ZEM	00:15	\N	30	74.00	1.00	74.00
58768fd7-d1cf-47ca-9e5f-a1c4e717332d	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	ALLER	05:00	OUED ZEM	LAVERIE DAOUI	05:30	\N	30	40.00	0.50	20.00
33fbe3ab-6e7c-4564-ab1d-9dbd690695eb	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	RETOUR	05:45	LAVERIE DAOUI	OUED ZEM	06:15	\N	30	40.00	0.50	20.00
2230179e-5e54-4e76-ae1b-ebe64a915a50	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	ALLER	07:00	OUED ZEM	DAOUI	07:30	\N	30	40.00	1.00	40.00
9507ca6a-ba37-4b40-a2e9-95db8f03e2d2	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	ALLER	13:00	OUED ZEM	LAVERIE DAOUI	13:30	\N	30	40.00	0.50	20.00
e1316518-c928-4848-a075-8fb4de38edcd	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	RETOUR	13:45	LAVERIE DAOUI	OUED ZEM	14:15	\N	30	40.00	0.50	20.00
472aeb1a-69d4-46e5-93c8-50c2f6a60507	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	RETOUR	15:45	DAOUI	OUED ZEM	16:15	\N	30	40.00	1.00	40.00
07803e6f-fef9-4308-9068-c8f5c6d77585	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	ALLER	21:00	OUED ZEM	LAVERIE DAOUI	21:30	\N	30	40.00	0.50	20.00
b8dd7e32-f960-4f08-bc74-5c39a214b8fb	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	AMRAOUI	S56	70939-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	RETOUR	21:45	LAVERIE DAOUI	OUED ZEM	22:15	\N	30	40.00	0.50	20.00
b02b3416-4a73-4085-a963-2fc4e4b1a66a	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	ALLER	05:50	OUED ZEM	SIDI CHENNANE	06:30	\N	40	76.00	0.50	38.00
3ebdc623-f8ea-4cf1-bde9-1ff51701715a	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	06:45	SIDI CHENNANE	OUED ZEM	07:30	\N	45	76.00	0.50	38.00
2c58f738-b329-4ed3-84b2-35084fc7397e	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	CCI	ALLER	07:30	OUED ZEM	CCI	08:30	\N	60	92.00	1.00	92.00
d8791365-883c-468f-80a1-ab5c45ee926e	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	OUED ZEM	15:15	\N	30	76.00	0.50	38.00
1287adf5-473b-47e6-934f-6ba88f57f356	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE	OUED ZEM	16:15	\N	30	76.00	0.50	38.00
0b98a3d5-cb49-4461-8667-d4734ba99c90	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	ZAKARIA	S57	70947-A-13	AUTOCAR	VOLVO	OUEDZEM	T2	RETOUR	23:45	T2	OUED ZEM	00:15	\N	30	74.00	1.00	74.00
9b31b922-cbed-42a7-bded-2ae321792ad3	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	07:45	SIDI CHENNANE	OUED ZEM	08:30	\N	45	76.00	1.00	76.00
1b31a1e5-f2c8-404b-a11a-8396b784d943	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	ALLER	13:50	OUED ZEM	SIDI CHENNANE	14:30	\N	40	76.00	0.50	38.00
41a5960a-96ed-4515-a3ec-ec6efd04df5c	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	OUED ZEM	15:15	\N	30	76.00	0.50	38.00
9b7871bb-67cd-4e9b-ac0b-80c50c685aa0	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	CCI	RETOUR	16:15	CCI	OUED ZEM	17:00	\N	45	92.00	1.00	92.00
8c5394e7-1d38-4530-a576-cf9cae08071f	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	DAOUI	RETOUR	18:00	LAVERIE DAOUI	OUED ZEM	18:30	\N	30	73.00	1.00	73.00
89ec7e1f-f533-49b5-8063-9a519a8caea7	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	ALLER	21:50	OUED ZEM	SIDI CHENNANE	22:30	\N	40	76.00	0.50	38.00
457151bc-0052-4a93-bddc-6abf7c75ee35	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	CTM	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	HRAGA	S58	70949-A-13	AUTOCAR	VOLVO	OUEDZEM	SIDI CHENNANE	RETOUR	22:45	SIDI CHENNANE	OUED ZEM	23:30	\N	45	76.00	0.50	38.00
387ede89-5fbe-4bf9-a7fc-d966e6e7c1f6	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78373	Z1	320	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	21:30	OUED ZEM	OUED ZEM	00:30	\N	180	4.00	3.00	12.00
45fa2aea-2083-44cf-99bf-9186602db289	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77626	Z2	337	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	4.00	3.00	12.00
911b7d5c-c95c-4ff4-9911-9019077c7735	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77626	Z2	337	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	21:30	OUED ZEM	OUED ZEM	00:30	\N	180	4.00	3.00	12.00
7e1e7c70-5dba-4ab3-a77f-177376fea767	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77403	Z3	333	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	4.00	5.00	20.00
c6b07cae-2fa9-47e3-8470-6e5452904c47	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77403	Z3	333	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	21:30	OUED ZEM	OUED ZEM	00:30	\N	180	4.00	4.00	16.00
820d519b-bf39-4c5c-94d4-c8205ea6508b	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	57267	Z4	337	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	05:30	OUED ZEM	OUED ZEM	09:30	\N	240	4.00	3.00	12.00
4eee1728-3584-4d9e-8ccf-40bc988f8cd5	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	57267	Z4	337	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	4.00	5.00	20.00
13ff69cb-a652-4cbf-8585-876bc1cae454	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77532	Z4	320	MINIBUS	HYUNDAI	OUEDZEM	NAVETTE	ALLER	05:30	OUED ZEM	OUED ZEM	09:30	\N	240	4.00	5.00	20.00
5737fb75-425c-4722-a321-506b477cb8c6	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77532	Z4	320	MINIBUS	HYUNDAI	OUEDZEM	\N	\N	13:30	OUED ZEM	OUED ZEM	16:30	\N	180	\N	0.00	0.00
db7e067e-9425-44ae-a4d2-e403d99449ff	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77805	P1	410	AUTOCAR	MAN	BOUJNIBA	\N	\N	13:30	BOUJNIBA	BOUJNIBA	16:30	\N	180	\N	0.00	0.00
fd0d55f4-9e66-4acc-a518-1215f56265da	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77805	P1	410	AUTOCAR	MAN	HATTANE	UB	ALLER	21:30	HATTANE	UB	22:00	\N	30	30.00	0.50	15.00
531dacb3-1b24-4aa4-abbb-4ed29f44dd83	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77805	P1	410	AUTOCAR	MAN	HATTANE	UB	RETOUR	22:30	UB	HATTANE	23:00	\N	30	30.00	0.50	15.00
88e2bf20-a996-4988-8a3f-4ff4198de6f7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77805	P1	410	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	23:45	MLIKATE-7900	BOUJNIBA	00:30	\N	45	70.00	1.00	70.00
d836f729-7769-4c52-adf9-1fde64d46564	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42761	P2	467	AUTOCAR	MAN	HATTANE	UB	ALLER	13:30	HATTANE	UB	14:00	\N	30	30.00	0.50	15.00
25a6f297-b291-4daa-9a1e-6ada2b5ef2a5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42761	P2	467	AUTOCAR	MAN	HATTANE	UB	RETOUR	14:30	UB	HATTANE	15:00	\N	30	30.00	0.50	15.00
72450263-de85-4319-ae5e-21df89c1e351	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42761	P2	467	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	15:45	MLIKATE-7900	BOUJNIBA	16:30	\N	45	70.00	1.00	70.00
37d34e97-794e-4a8c-9984-13e058c52e51	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42761	P2	467	AUTOCAR	MAN	BOUJNIBA	UB	ALLER	21:30	BOUJNIBA	UB-UM3	22:00	\N	30	30.00	0.50	15.00
d2e19736-001e-45f3-9519-a1a148d016d4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41649	P3	438	AUTOCAR	MAN	BOUJNIBA	DAOUI	ALLER	06:00	BOUJNIBA	LAVERIE DAOUI	06:30	\N	30	40.00	0.50	20.00
e8107a3a-896f-4d68-ada9-22c3decf8dec	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41649	P3	438	AUTOCAR	MAN	BOUJNIBA	DAOUI	RETOUR	06:45	LAVERIE DAOUI	BOUJNIBA	07:30	\N	45	40.00	0.50	20.00
071dc797-b19e-4f0e-a698-c39ecc77c172	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41649	P3	438	AUTOCAR	MAN	BOUJNIBA	CCI	ALLER	07:30	BOUJNIBA-HATTNE	CCI	08:30	\N	60	90.00	1.00	90.00
faabe209-ebcc-431c-8c3b-37e954f57907	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41649	P3	438	AUTOCAR	MAN	BOUJNIBA	\N	\N	09:00	BOUJNIBA	BOUJNIBA	13:00	\N	240	\N	0.00	0.00
969c3d49-a77c-4ccb-a37f-a40d25eb26d9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77808	P4	\N	AUTOCAR	MAN	BOUJNIBA	\N	\N	21:00	BOUJNIBA	BOUJNIBA	00:30	\N	210	\N	0.00	0.00
84483b8b-7fbc-40da-9f10-7a978ccfa035	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43168	P5	438	AUTOCAR	MAN	BOUJNIBA	\N	\N	13:30	BOUJNIBA	BOUJNIBA	15:30	\N	120	\N	0.00	0.00
e6c52475-a06a-4c1c-a8ea-ebf5dd6633eb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43168	P5	438	AUTOCAR	MAN	BOUJNIBA	CCI	RETOUR	16:15	CCI	HATTANE-BOUJNIBA-LAGFAF	17:00	\N	45	90.00	1.00	90.00
42ec4b8a-9e6c-40ed-b9b5-545ba034d30c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43168	P5	438	AUTOCAR	MAN	BOUJNIBA	DAOUI	ALLER	22:00	BOUJNIBA	LAVERIE DAOUI	22:30	\N	30	40.00	0.50	20.00
5338312e-2aef-4f19-8db8-d04d939955ca	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43168	P5	438	AUTOCAR	MAN	BOUJNIBA	DAOUI	RETOUR	22:45	LAVERIE DAOUI	BOUJNIBA	23:30	\N	45	40.00	0.50	20.00
ce028401-ef96-4f31-8257-c659f87b6a1a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42739	P6	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	ALLER	06:00	BOUJNIBA	MLIKATE	06:30	\N	30	80.00	0.50	40.00
467ba9b5-5f9f-49af-8163-0dd92e6b667c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42739	P6	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	RETOUR	06:45	MLIKATE	BOUJNIBA	07:30	\N	45	80.00	0.50	40.00
cbf1b157-d74f-44e8-b4c0-3983b783f8f7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42739	P6	433	AUTOCAR	MAN	HATTANE	LAVERIE MERA	ALLER	14:00	HATTANE	LAVERIE MERA-ZONE CENTRALE	14:30	\N	30	40.00	0.50	20.00
9450c134-8eaa-4926-b45c-61f0081bc53f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42739	P6	433	AUTOCAR	MAN	HATTANE	LAVERIE MERA	RETOUR	14:45	ZONE CENTRALE-LAVERIE MERA	HATTANE	15:30	\N	45	40.00	0.50	20.00
c15fd48b-24a4-4abd-b9e2-68a47cf32447	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42739	P6	433	AUTOCAR	MAN	HATTANE	PARC 7900	RETOUR	15:45	PARC 7900	HATTANE	16:30	\N	45	46.00	1.00	46.00
f1c5108a-c139-4b80-adf9-b79567a7dfa7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	BOUJNIBA	PARC 7900	ALLER	14:00	BOUJNIBA	PARC 7900	14:30	\N	30	50.00	0.50	25.00
34f7492c-8bbc-4187-8023-c4bc5c3dbc9f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	14:45	PARC 7900	BOUJNIBA	15:30	\N	45	50.00	0.50	25.00
de08ef84-d9db-4c9c-a30d-9a168ead2e9e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	21:00	HATTANE	LAVERIE DAOUI	21:30	\N	30	30.00	0.50	15.00
e6476c93-602c-4c00-8f24-797a3d732093	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	21:45	LAVERIE DAOUI	HATTANE	22:00	\N	15	30.00	0.50	15.00
5fc1ba6f-3180-4624-83ef-7e421e6a9610	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	22:00	HATTANE	DAOUI	22:30	\N	30	30.00	0.50	15.00
e2a53132-f86b-4edd-99ae-a1db81d1aece	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41625	P7	421	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	22:45	DAOUI	HATTANE	23:30	\N	45	30.00	0.50	15.00
a9823024-3211-468f-9578-0b04861fb551	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43184	P8	410	AUTOCAR	MAN	HATTANE	UB	ALLER	05:30	HATTANE	UB	06:00	\N	30	16.00	0.50	8.00
3407abcc-291b-49d4-ac5d-7e7c3954525b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43184	P8	410	AUTOCAR	MAN	HATTANE	UB	RETOUR	06:30	UB	HATTANE	07:00	\N	30	16.00	0.50	8.00
7fad767c-4f47-4f48-a1ed-38b6fd492f18	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43184	P8	410	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	07:45	MLIKATE-7900	BOUJNIBA	08:30	\N	45	70.00	1.00	70.00
1892f398-d1b2-4620-8f6e-61bf6e3d9ca6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43184	P8	410	AUTOCAR	MAN	BOUJNIBA	\N	\N	08:30	BOUJNIBA	BOUJNIBA	13:00	\N	270	\N	0.00	0.00
8a2f45eb-f5d2-4757-9f04-6f72aa43011d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40577	P9	433	AUTOCAR	MAN	BOUJNIBA	\N	ALLER	13:30	BOUJNIBA	BOUJNIBA	16:30	\N	180	\N	0.00	0.00
e16118b3-cb10-462b-958f-e84072d5ff70	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40577	P9	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	ALLER	22:00	BOUJNIBA	MLIKATE	22:30	\N	30	80.00	0.50	40.00
99ffe838-93f5-43d4-935e-5dc401c319f8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40577	P9	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	RETOUR	22:45	MLIKATE	BOUJNIBA	23:30	\N	45	80.00	0.50	40.00
6e6df385-e07b-4f18-af3e-8f5f8715306c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42278	P10	439	AUTOCAR	MAN	BOUJNIBA	\N	\N	05:30	BOUJNIBA	BOUJNIBA	09:30	\N	240	\N	0.00	0.00
15b6792b-fd7f-4831-9a96-55531b484370	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42278	P10	439	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	13:00	HATTANE	LAVERIE DAOUI	13:30	\N	30	30.00	0.50	15.00
3a9503a5-1025-409a-af8e-bcee50873f7d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42278	P10	439	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	13:30	LAVERIE DAOUI	HATTANE	14:00	\N	30	30.00	0.50	15.00
4c29571f-77d4-439e-a2b9-e3aa268ba462	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42278	P10	439	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	14:00	HATTANE	DAOUI	14:30	\N	30	30.00	0.50	15.00
6b0d11bf-63ba-4f6a-9bb4-e75129a2be5e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42278	P10	439	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	14:45	DAOUI	HATTANE	15:30	\N	45	30.00	0.50	15.00
4acd6482-d162-4889-bcc0-0ede3b712ffe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40596	P11	467	AUTOCAR	MAN	BOUJNIBA	UB	ALLER	05:30	BOUJNIBA	UB-UM3	06:00	\N	30	30.00	0.50	15.00
9e3f0988-23fa-4f78-91e2-078a73794e4a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40596	P11	467	AUTOCAR	MAN	BOUJNIBA	UB	RETOUR	06:30	UB-UM3	BOUJNIBA	07:00	\N	30	16.00	0.50	8.00
1f0a2df0-efd9-45d2-92c8-23594a4030ce	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40596	P11	467	AUTOCAR	MAN	BOUJNIBA	UB	ALLER	07:00	BOUJNIBA	UB-R6	07:30	\N	30	30.00	1.00	30.00
887f7260-b61c-4d3f-8bf0-8052584a6700	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40596	P11	467	AUTOCAR	MAN	BOUJNIBA	DAOUI	ALLER	14:00	BOUJNIBA	LAVERIE DAOUI	14:30	\N	30	40.00	0.50	20.00
5c62ef25-e701-40d7-8a96-a78c9d63e3da	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40596	P11	467	AUTOCAR	MAN	BOUJNIBA	DAOUI	RETOUR	14:45	LAVERIE DAOUI	BOUJNIBA	15:30	\N	45	40.00	0.50	20.00
f76751a2-3cff-479b-9800-2e7d51f131c2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41554	P12	439	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	05:00	HATTANE	LAVERIE DAOUI	05:30	\N	30	30.00	0.50	15.00
aa2ed1fb-c057-4651-b611-eb0b76141c9c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41554	P12	439	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	05:30	LAVERIE DAOUI	HATTANE	06:00	\N	30	30.00	0.50	15.00
83fd778e-9af6-41c2-a450-3ffc23291b6f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41554	P12	439	AUTOCAR	MAN	HATTANE	DAOUI	ALLER	06:00	HATTANE	DAOUI	06:30	\N	30	30.00	0.50	15.00
96a4cd7c-488c-4469-b788-9c57b7414a43	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41554	P12	439	AUTOCAR	MAN	HATTANE	DAOUI	RETOUR	07:00	DAOUI	HATTANE	07:30	\N	30	30.00	0.50	15.00
8f2e173b-2cd5-449c-a5a1-98285a33205f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	41554	P12	439	AUTOCAR	MAN	BOUJNIBA	\N	\N	07:30	BOUJNIBA	BOUJNIBA	13:00	\N	330	\N	1.00	0.00
e4409f22-f2a5-457c-89aa-cf6c1729505f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40880	P13	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	ALLER	14:00	BOUJNIBA	MLIKATE	14:30	\N	30	80.00	0.50	40.00
388de382-ab41-4721-b95a-24d04b94db51	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40880	P13	433	AUTOCAR	MAN	BOUJNIBA	MLIKATE	RETOUR	14:45	MLIKATE	BOUJNIBA	15:30	\N	45	80.00	0.50	40.00
95dd9810-36d4-404a-9448-62eeea987eff	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40880	P13	433	AUTOCAR	MAN	BOUJNIBA	UB	RETOUR	15:45	UB-R6	BOUJNIBA	16:30	\N	45	16.00	1.00	16.00
01137849-e8ca-4ed0-9d7d-ba02b562e879	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40880	P13	433	AUTOCAR	MAN	BOUJNIBA	\N	\N	21:30	BOUJNIBA	BOUJNIBA	00:30	\N	180	\N	0.00	0.00
8a39c54c-8980-4521-a904-65410911e289	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40863	P14	421	AUTOCAR	MAN	BOUJNIBA	PARC 7900	ALLER	06:00	BOUJNIBA	PARC 7900	06:30	\N	30	50.00	0.50	25.00
4c77d7f3-67dd-4ab7-937f-e57f2b023846	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40863	P14	421	AUTOCAR	MAN	BOUJNIBA	PARC 7900	RETOUR	06:45	PARC 7900	BOUJNIBA	07:30	\N	45	50.00	0.50	25.00
b52c6b30-4202-4ef5-a052-cf64d75e8e3f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40863	P14	421	AUTOCAR	MAN	BOUJNIBA	\N	\N	13:30	BOUJNIBA	BOUJNIBA	16:30	\N	180	\N	0.00	0.00
5b2cc64c-c113-4e2b-abda-f61ed1dd2671	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58997	A1	431	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:00	HAY RIAD------>5	10	6.00	1.00	6.00
e050f203-de79-4786-915c-f409f456d793	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58997	A1	431	AUTOCAR	MAN	KHOURIBGA	MLIKATE	ALLER	07:00	KHOURIBGA	PARC 7900-MLIKATE	07:45	H-T-1-2-3-4-5-OK	45	74.00	1.00	74.00
f6e736db-b0ab-4372-9c71-471a2b736c8e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58997	A1	431	AUTOCAR	MAN	KHOURIBGA	MERA	RETOUR	14:45	MERA	KHOURIBGA	15:30	1-2-H-T	45	60.00	1.00	60.00
85c30341-a118-488c-a6ae-190b3603e9e8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42214	A2	425	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	13:50	KHOURIBGA	DAOUI	14:30	Q-5-6-7-8-9-10-11	40	86.00	0.50	43.00
f61ff3b4-4b03-4ef1-845c-bd4c66d94f47	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42214	A2	425	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	14:45	DAOUI	KHOURIBGA	15:30	1-2-H-T	45	86.00	0.50	43.00
a723f1e3-b53c-466c-acfb-b6dba29c26a8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42214	A2	425	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	23:00	\N	90	\N	0.00	0.00
0667caef-9b53-4f1c-beef-a064d74b2370	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42214	A2	425	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	23:15	KHOURIBGA	KHOURIBGA	23:30	CFO--->N	15	5.00	1.00	5.00
6bf1e614-54eb-4756-8592-58a13208dc7a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42214	A2	425	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	00:15	KHOURIBGA	KHOURIBGA	00:30	10------>V-Q	15	10.00	1.00	10.00
261344b5-dc6e-412d-a1a9-316659706169	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59097	A3	429	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	05:50	KHOURIBGA	PARC 7900	06:30	2-3-4-5-OK-F	40	60.00	1.00	60.00
360032a9-25c1-4b9b-ad2c-8fdcc84a9f35	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59097	A3	429	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	07:00	KHOURIBGA	DAOUI	07:45	Q-5-6-7-8-9-10-11	45	86.00	1.00	86.00
2d777d63-bbb8-442d-a975-35d8fa758a2a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59097	A3	429	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	08:20	KHOURIBGA	UB	09:00	Q-5-6-7-8-9-10-12	40	50.00	1.00	50.00
e0682dcf-fa12-4a7d-bff5-1ef9d0513f41	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42741	A4	429	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	15:45	MLIKATE	KHOURIBGA	16:30	F-Z-10-1-2-H-T	45	74.00	1.00	74.00
d85ac3f4-ab43-4231-9b8a-1a3bf8cbaaee	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42741	A4	429	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	ALLER	21:50	KHOURIBGA	PIPE LINE	22:30	H-T-1-2-3-4-5-OK	40	52.00	0.50	26.00
1591d85a-8b83-405c-a6fd-df29ca3c8809	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42741	A4	429	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	RETOUR	22:45	PIPE LINE	KHOURIBGA	23:30	F-Z-10-1-2-H-T	45	52.00	0.50	26.00
b4f49eb4-0d8a-4ba0-88fc-0d8b751971e0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40265	A5	443	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	05:50	KHOURIBGA	ZONE CENTRALE	06:30	Q-5-6-7-8-9-10-Z-F	40	60.00	0.50	30.00
4690ba5c-676a-4df2-9004-2b46ee534047	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40265	A5	443	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	06:45	ZONE CENTRALE-LAVERIE MERA	KHOURIBGA	07:30	F-Z-10-1-2-H-T	45	60.00	0.50	30.00
50437be8-559d-4358-829b-62863aa7d551	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40265	A5	443	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	13:50	KHOURIBGA	ZONE CENTRALE	14:30	H-T-1-2-3-4-5-OK	40	60.00	0.50	30.00
2e55b331-538b-47fe-a2de-6eb04bf68285	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40265	A5	443	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	14:45	ZONE CENTRALE	KHOURIBGA	15:30	F-Z-10-1-2-H-T	45	60.00	0.50	30.00
8aa4155d-9497-42d6-8c02-f4cca2cab315	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40265	A5	443	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:10	KHOURIBGA	KHOURIBGA	16:30	10------>N	20	5.00	1.00	5.00
9c69c305-50ad-4397-8727-40347822957b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40346	A6	474	AUTOCAR	MAN	KHOURIBGA	\N	\N	05:30	KHOURIBGA	KHOURIBGA	08:30	\N	180	\N	0.00	0.00
46960cf0-47ed-4c1e-95f0-4896baae4b3c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40346	A6	474	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	\N	0.00	0.00
5060d5ff-ab13-46d5-aab9-a88558b54fc5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77414	B1	471	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:50	KHOURIBGA	DAOUI	06:30	H-T-1-2-3-4-5-9-10-11	40	86.00	1.00	86.00
897989b7-67b2-4dad-a21f-c4d28f2f47d4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77414	B1	471	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	07:10	KHOURIBGA	KHOURIBGA	07:30	5----->Q	20	8.00	1.00	8.00
04e09000-30bb-4b2d-af2b-b92c22ba7dd8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77414	B1	471	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	08:20	KHOURIBGA	DAOUI	09:00	Q-5-6-7-8-9-10-11	40	86.00	1.00	86.00
d15b6c07-84b9-49aa-8294-94c572877d17	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	57275	B2	471	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	15:45	MLIKATE	KHOURIBGA	16:30	F-V-5-4-3-Q	45	74.00	1.00	74.00
499fccbf-163b-4299-8585-2f2beda702a3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	57275	B2	471	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	21:30	KHOURIBGA	UB-UM3	22:00	Q-5-6-7-8-9-10-11	30	50.00	0.50	25.00
c9cae395-4e4e-48c1-b795-2475c1be63a9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	57275	B2	471	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	22:30	UB-UM3	KHOURIBGA	23:00	F-Z-10-1-2-H-T	30	50.00	0.50	25.00
aa36581f-c72f-4032-a064-2249f2bca1f5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78192	B3	455	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:50	KHOURIBGA	DAOUI	06:30	Q-5-6-7-8-9-10-11	40	86.00	1.00	86.00
7e6243fe-5a06-4a0d-a138-c9b5c3a6ca94	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78192	B3	455	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	08:00	KHOURIBGA	KHOURIBGA	08:30	10---->V-Q	30	10.00	1.00	10.00
026a1c44-e0f0-4647-8c3b-70950fc2482a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78192	B3	455	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	ALLER	13:50	KHOURIBGA	PIPE LINE	14:30	H-T-1-2-3-4-5-OK	40	52.00	0.50	26.00
d1b06d6d-c08c-4ea4-96aa-9e83d7d4719a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78192	B3	455	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	RETOUR	14:45	PIPE LINE	KHOURIBGA	15:30	F-Z-10-1-2-H-T	45	52.00	0.50	26.00
036f9d38-63c6-427d-b518-b942957765e4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58996	B4	420	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	14:45	LAVERIE DAOUI	KHOURIBGA	15:30	11-A-4-3-H-T	45	86.00	1.00	86.00
e2dd8ac2-9e65-4eb0-926d-65d52d9a203e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58996	B4	420	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	21:50	KHOURIBGA	KHOURIBGA	22:00	BADR------>10	10	2.00	1.00	2.00
8b194930-31ad-4066-99ef-a89f1c0ada09	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58996	B4	420	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	23:15	KHOURIBGA	KHOURIBGA	23:30	10----->N	15	5.00	1.00	5.00
9e9e6401-325d-4a8e-8239-40c53ab26451	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58996	B4	420	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	00:15	KHOURIBGA	KHOURIBGA	00:30	10----->N	15	5.00	1.00	5.00
c0f3bc49-3ddd-4fe3-8bfa-f11c37e970f5	0cea9745-6aa2-4105-9bdc-341d95999048	1edc2404-0388-4ceb-9970-3743a87ce5ac	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59039	B5	427	AUTOCAR	MAN	FQUIH BEN SALEH	BENI AMIR LAVERIE	ALLER	05:50	FQUIH BEN SALEH	BENI AMIR LAVERIE &MINE	06:40	\N	50	110.00	1.00	110.00
76413614-2b24-48b3-963e-2614a6810a7e	0cea9745-6aa2-4105-9bdc-341d95999048	1edc2404-0388-4ceb-9970-3743a87ce5ac	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59039	B5	427	AUTOCAR	MAN	FQUIH BEN SALEH	BENI AMIR LAVERIE	RETOUR	14:45	BENI AMIR LAVERIE &MINE	FQUIH BEN SALEH	15:30	\N	45	110.00	1.00	110.00
ff1c7553-cdde-44fe-a28c-fa5c38fa8573	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CP	A6	474	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	\N	0.00	0.00
0d26bfbe-0534-4c9e-abf3-6f2939a1c5e3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CP	A6	474	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
c68f1042-8023-486d-8ce9-0170808286bb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59031	C1	424	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	05:30	KHOURIBGA	UB	06:30	Q-5-6-7-8-9-10-11	60	50.00	0.50	25.00
32f99564-0072-4db6-b93b-b56fd03ec24c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59031	C1	424	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	06:30	UB	KHOURIBGA	07:00	11-1-2-H-T	30	50.00	0.50	25.00
15caabcd-e0e0-415b-8f63-e53203b15a5e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59031	C1	424	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	07:00	KHOURIBGA	DAOUI	07:45	H-T-1-2-3-4-5-9-10-11	45	86.00	1.00	86.00
ea17eb4f-55c0-4833-a294-2ea2b9768938	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59031	C1	424	AUTOCAR	MAN	KHOURIBGA	GROUNI	ALLER	08:45	KHOURIBGA	GROUNI	09:00	SJ-11	15	30.00	1.00	30.00
788a8a3e-10a1-4892-9731-183ebcaca7a2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59071	C2	424	AUTOCAR	MAN	KHOURIBGA	T2	RETOUR	14:45	T2	KHOURIBGA	15:30	F-V-5-4-3-Q	45	110.00	1.00	110.00
fc5da4c2-f522-4cd0-9a89-acbcbcd1ca5d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59071	C2	424	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	21:00	KHOURIBGA	LAVERIE DAOUI	21:45	Q-5-6-7-8-9-10-11	45	80.00	0.50	40.00
d3538991-43dc-4a06-bf0f-b0ad57a20de1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59071	C2	424	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	22:30	LAVERIE DAOUI	KHOURIBGA	23:00	11-1-2-H-T	30	80.00	0.50	40.00
8bb0ba65-6959-4bfd-84fe-1e18bd564b05	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77757	C3	446	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:50	KHOURIBGA	DAOUI	06:30	Q-5-6-7-8-9-10-11	40	86.00	0.50	43.00
3f1d1b23-008d-4cd5-a532-80159528fe53	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77757	C3	446	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	06:45	DAOUI	KHOURIBGA	07:30	11-1-2-H-T	45	86.00	0.50	43.00
12ef3ffc-7f4b-47d3-9062-6199e1865363	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77757	C3	446	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	14:45	LAVERIE DAOUI	KHOURIBGA	15:30	1-2-3-Q	45	80.00	1.00	80.00
7741fa96-9cfa-4b9d-8684-b8f94f5f7685	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77757	C3	446	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:10	KHOURIBGA	KHOURIBGA	16:30	CFO--->N	20	5.00	1.00	5.00
0024a484-982d-4801-89ee-413a4876d8a4	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42219	C4	446	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	17:30	\N	240	\N	0.00	0.00
7253d403-e21d-40a2-baed-643ac3708348	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42219	C4	446	AUTOCAR	MAN	KHOURIBGA	BENI AMIR MINE	RETOUR	22:45	BENI AMIR MINE	KHOURIBGA	23:30	F-Z-10-1-2-H-T	45	96.00	1.00	96.00
be6e0eb5-8b41-4473-be5a-a09ba40d7d52	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42219	C4	446	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	00:15	KHOURIBGA	KHOURIBGA	00:30	10----->V-Q	15	10.00	1.00	10.00
eb1c041a-ff40-45a1-8721-3cbca53402da	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43197	C5	446	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	05:50	KHOURIBGA	LAVERIE MERA	06:30	H-T-1-2-3-4-5-9-10-Z-F	40	46.00	1.00	46.00
7f4d0a49-3712-47b3-b0ce-5463def6eee0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43197	C5	446	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	ALLER	07:00	KHOURIBGA	PIPE LINE	07:30	H-T-1-2-3-4-5-OK-8-9-10-Z-F	30	52.00	1.00	52.00
a2df9f76-7deb-4bbe-819b-84ee939fd6cd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43197	C5	446	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	13:50	KHOURIBGA	KHOURIBGA	14:00	HAY BADR--->10	10	2.00	1.00	2.00
33cb38b3-5b32-445c-a7c5-3cd6bcc4b96d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43197	C5	446	AUTOCAR	MAN	KHOURIBGA	MERA	RETOUR	14:45	MERA	KHOURIBGA	15:30	11-10-9-8-OK-4-3-Q	45	60.00	1.00	60.00
9e6e270a-50e7-4708-8243-45dbd3a071a3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59086	C6	473	AUTOCAR	MAN	KHOURIBGA	\N	\N	05:30	KHOURIBGA	KHOURIBGA	08:30	\N	180	\N	0.00	0.00
766e9425-847b-496a-9af8-d9fac933d3fe	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59086	C6	473	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	\N	0.00	0.00
4cc62183-b19e-4025-8a2a-6aae21826613	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78147	D1	462	AUTOCAR	MAN	BOULANOIR	MERA	ALLER	06:00	BOULANOIR-HATTANE	MERA	06:40	\N	40	60.00	1.00	60.00
361641dd-41d2-41a8-8502-224e1e69b50e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78147	D1	462	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	07:15	KHOURIBGA	KHOURIBGA	07:30	5------>Q	15	8.00	1.00	8.00
902aa79f-6933-4f9d-8692-42ccff668edb	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78147	D1	462	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	08:20	KHOURIBGA	DAOUI	09:00	H-T-1-2-3-4-5-9-10-11	40	86.00	1.00	86.00
e940aae0-41ca-4201-9694-8ce15c9c7331	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77427	D2	462	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	15:45	BENI AMIR LAVERIE	KHOURIBGA	16:30	F-Z-10-1-2-H-T	45	94.00	1.00	94.00
113de885-2083-4864-adb9-fc94d7eb674b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77427	D2	462	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
8be5e1cf-473d-4e99-8f22-2bf81cc0a787	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43191	D3	426	AUTOCAR	MAN	BOULANOIR	PARC 7900	ALLER	06:00	BOULANOIR	LAVERIE MERA-7900	06:30	\N	30	50.00	0.50	25.00
538d03c6-b39c-4de7-bbdb-84f2404a121d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43191	D3	426	AUTOCAR	MAN	BOULANOIR	PARC 7900	RETOUR	06:45	LAVERIE MERA-7900	BOULANOIR	07:30	\N	45	50.00	0.50	25.00
de74f6fb-c495-46ec-8452-ed0fa28067d1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43191	D3	426	AUTOCAR	MAN	BOULANOIR	PARC 7900	ALLER	14:00	BOULANOIR	LAVERIE MERA-7900	14:30	\N	30	50.00	0.50	25.00
b839f6a4-2946-49f2-9fb8-5ec2f318135b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43191	D3	426	AUTOCAR	MAN	BOULANOIR	PARC 7900	RETOUR	14:45	LAVERIE MERA-7900	BOULANOIR	15:30	\N	45	50.00	0.50	25.00
a560e1ba-f9c9-4832-b9c4-d28e80e70583	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43191	D3	426	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:10	KHOURIBGA	KHOURIBGA	16:30	10----->Q	20	10.00	1.00	10.00
6c521685-3839-4ed8-9102-b46154b06090	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77470	D4	447	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	ALLER	13:50	KHOURIBGA	SIDI CHENNANE	14:40	2-3-4-5-9-10-Z-F	50	104.00	0.50	52.00
39fb0472-ea1f-4a97-af80-8e9d49dbc4a9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77470	D4	447	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE	KHOURIBGA	15:30	4-3-Q	45	104.00	0.50	52.00
efa33dc1-3dd5-40f4-b73a-7e3eda88f36c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77470	D4	447	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
6a452e3a-9d1f-43bd-9b2a-d2df7cb6965d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59084	D5	483	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:00	HAY RIAD------>5	10	6.00	1.00	6.00
d4a884b7-91aa-4109-b858-a76e1bbd1334	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59084	D5	483	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	06:00	KHOURIBGA	PARC 7900	06:30	5-6-7-8-9-10-Z-F	30	60.00	0.50	30.00
c5652b95-f7e1-45f3-a167-9162777c3625	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59084	D5	483	AUTOCAR	MAN	KHOURIBGA	PARC 7900	RETOUR	06:45	PARC 7900	KHOURIBGA	07:30	N-A	45	60.00	0.50	30.00
ca24e8a7-4c30-40c9-bbd3-7fb878985f73	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59084	D5	483	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	13:50	KHOURIBGA	ZONE CENTRALE	14:30	Q-5-6-7-8-9-10-Z-F	40	50.00	0.50	25.00
1b01d0ab-c92d-4485-a0ee-1653bcd38120	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59084	D5	483	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	14:45	ZONE CENTRALE	KHOURIBGA	15:30	F-Z-10-V-5-4-3-Q	45	50.00	0.50	25.00
25009402-3103-44da-83d3-bc988ae7126f	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77801	D6	435	AUTOCAR	MAN	KHOURIBGA	\N	\N	05:30	KHOURIBGA	KHOURIBGA	08:30	\N	180	\N	0.00	0.00
1bc5812f-acbe-49b5-8964-ba27c5e1ea4a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77801	D6	435	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	\N	0.00	0.00
f233bb01-a4d0-480f-b61c-01b78cbd2708	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40830	E1	481	AUTOCAR	MAN	KHOURIBGA	MERA	ALLER	05:50	KHOURIBGA	MERA	06:30	H-T-1-2-3-4-5-9-10-11	40	60.00	1.00	60.00
f86703c3-ebb0-4144-9ac9-48e986271e9d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40830	E1	481	AUTOCAR	MAN	KHOURIBGA	MERA	ALLER	07:00	KHOURIBGA	MERA	07:40	H-T-1-2-3-4-5-9-10-11	40	60.00	1.00	60.00
3d953a10-14a8-4d10-8e47-9f1ee22113c1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40830	E1	481	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	13:30	KHOURIBGA	UB	14:00	Q-5-6-7-8-9-10-11	30	50.00	0.50	25.00
15f4285a-c64d-4a24-8b9c-b85e558077e1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40830	E1	481	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	14:30	UB	KHOURIBGA	15:00	F-Z-10-1-2-H-T	30	50.00	0.50	25.00
3d0355a0-fd09-4e56-a8f6-4aeef00d0093	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77475	E2	423	AUTOCAR	MAN	KHOURIBGA	GROUNI	RETOUR	15:45	GROUNI	KHOURIBGA	16:15	\N	30	30.00	1.00	30.00
e590b2aa-ac03-4308-b4c2-cb294fef727b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77475	E2	423	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	21:30	KHOURIBGA	UB	22:00	H-T-1-2-3-4-5-9-10-11	30	50.00	0.50	25.00
6a39e586-2934-4334-a48c-6f7124947e5e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77475	E2	423	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	22:30	UB	KHOURIBGA	23:00	11-10-1-2-H-T	30	50.00	0.50	25.00
0d7ffe86-09ca-436d-a86f-951e09e142f0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77475	E2	423	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	23:15	ZONE CENTRALE-LAVERIE MERA	KHOURIBGA	00:30	A-N	75	50.00	1.00	50.00
4201634a-e7b0-4c9c-b59a-8f967ea30106	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40316	E3	481	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	05:30	KHOURIBGA	UB-UM3	06:00	H-T-1-2-3-4-5-9-10-11	30	54.00	0.50	27.00
dad8a7c3-51d7-45f4-83cd-5797a4147cda	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40316	E3	481	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	06:30	UB-UM3	KHOURIBGA	07:00	11-10-9-8-7-6-5-4-3-Q	30	54.00	0.50	27.00
a8a9928c-2fe5-47d2-b3f9-e7b9b46e054e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40316	E3	481	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	07:00	KHOURIBGA	LAVERIE MERA	07:30	Q-5-6-7-8-9-10-Z-F	30	46.00	1.00	46.00
a9baed14-696f-4e0b-ba43-20a68d798e12	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40316	E3	481	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	08:20	KHOURIBGA	UB-UM1	09:00	H-T-1-2-3-4-5-9-10-11	40	50.00	1.00	50.00
e6dbeed0-c019-4265-97ca-48541ab6ed7a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	15:15	KHOURIBGA	KHOURIBGA	15:30	10----->HAY BADR	15	2.00	1.00	2.00
aafb4c7d-dbbc-4ec1-b451-ad2148cac007	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	15:30	KHOURIBGA	KHOURIBGA	15:45	10----->HAY BADR	15	2.00	1.00	2.00
d1af1a4e-3819-4edf-b7dc-f01c01200a13	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:15	KHOURIBGA	KHOURIBGA	16:30	10----->HAY BADR	15	2.00	1.00	2.00
16f2987d-a3ce-46ea-8df2-6c7ca716a44d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:30	KHOURIBGA	KHOURIBGA	16:45	10----->HAY BADR	15	2.00	1.00	2.00
0c68e4c1-b96d-4130-9f23-dca6c954ca3e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	21:00	KHOURIBGA	LAVERIE DAOUI	21:30	H-T-1-2-3-4-5-9-10-11	30	84.00	0.50	42.00
403e7d9f-ce2d-478b-b1c4-d3d35cb53905	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77404	E4	481	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	21:30	LAVERIE DAOUI	KHOURIBGA	22:00	11-10-9-8-7-6-5-4-3-Q	30	84.00	0.50	42.00
e01173ab-2365-4a72-83d4-5d2bec701ce8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78345	E5	481	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	ALLER	05:50	KHOURIBGA	PIPE LINE	06:30	H-T-1-2-3-4-5-OK-8-9-10-Z-F	40	50.00	0.50	25.00
95052423-099b-41ee-8c17-a1240ec8efa5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78345	E5	481	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	RETOUR	06:45	PIPE LINE	KHOURIBGA	07:30	F-Z-10-V-5-4-3-Q	45	50.00	0.50	25.00
d8b8136d-e95d-4798-a878-29e6353950ea	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78345	E5	481	AUTOCAR	MAN	KHOURIBGA	BENI AMIR LAVERIE	RETOUR	15:45	BENI AMIR LAVERIE	KHOURIBGA	16:30	F-Z-10-V-5-4-3-Q	45	92.00	1.00	92.00
2edde558-b134-48fd-8c03-b60fc5dfe52d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40882	E6	465	AUTOCAR	MAN	KHOURIBGA	\N	\N	05:30	KHOURIBGA	KHOURIBGA	08:30	\N	180	\N	0.00	0.00
8f9aa306-03ae-46aa-a0cb-56005d6cd1e2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	40882	E6	465	AUTOCAR	MAN	KHOURIBGA	\N	\N	13:30	KHOURIBGA	KHOURIBGA	16:30	\N	180	\N	0.00	0.00
31ec5547-43d0-4d6c-af57-8d2750245be1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42888	F1	479	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:00	KHOURIBGA	LAVERIE DAOUI	05:30	H-T-1-2-3-4-5-9-10-11	30	84.00	0.50	42.00
2677e9d8-8897-4c5a-b25f-1a1eeeac4dce	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42888	F1	479	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	06:30	LAVERIE DAOUI	KHOURIBGA	07:00	11-10-9-8-7-6-5-4-3-Q	30	84.00	0.50	42.00
178c2f30-9c7f-42d2-960b-f5b8bbf09cc9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42888	F1	479	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	07:00	KHOURIBGA	UB-UM3	07:30	Q-5-6-7-8-9-10-11	30	54.00	1.00	54.00
935bc3c4-7406-4563-a4ce-466212ecfcd5	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	42888	F1	479	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	08:20	KHOURIBGA	LAVERIE MERA	09:00	H-T-1-2-3-4-5-OK-8-9-10-Z-F	40	46.00	1.00	46.00
00b62b83-3ce2-4a45-90f2-bd639ae9e298	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43449	F2	479	AUTOCAR	MAN	KHOURIBGA	MERA	RETOUR	15:45	MERA	KHOURIBGA	16:30	11-10-9-8-7-6-5-4-3-Q	45	60.00	1.00	60.00
78c69959-4ce1-4c93-b1b0-9f858d74cc3d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43449	F2	479	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
a2a95bd0-ec79-43f4-a87b-e22d55174fe6	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59005	F3	448	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	05:50	KHOURIBGA	KHOURIBGA	06:00	HAY BADR--->10	10	2.00	1.00	2.00
3cc460d6-c7de-4c72-bf14-3d586958e91b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59005	F3	448	AUTOCAR	MAN	KHOURIBGA	PARC 7900	ALLER	07:15	KHOURIBGA	KHOURIBGA	07:30	10----->Q	15	10.00	1.00	10.00
1bfaf9a9-e61a-4a76-9e7e-4520cd3852a9	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59005	F3	448	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	08:15	KHOURIBGA	KHOURIBGA	08:30	10----->N	15	5.00	1.00	5.00
d1b0aa96-bfe3-431d-9d75-9f115886ca09	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59005	F3	448	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	13:30	KHOURIBGA	UB-UM3	14:00	H-T-1-2-3-4-5-9-10-11	30	54.00	0.50	27.00
e0984eb5-db2b-4a6e-ad7c-eea9f8c058d1	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59005	F3	448	AUTOCAR	MAN	KHOURIBGA	UB	RETOUR	14:30	UB-UM3	KHOURIBGA	15:00	11-10-9-8-7-6-5-4-3-Q	30	54.00	0.50	27.00
50c0c537-19d9-415e-b154-39e1290b64a0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43441	F4	448	AUTOCAR	MAN	KHOURIBGA	PIPE LINE	RETOUR	15:45	PIPE LINE	KHOURIBGA	16:30	N-A	45	50.00	1.00	50.00
5214cf23-64c7-4498-923e-fe5099dbb63b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43441	F4	448	AUTOCAR	MAN	KHOURIBGA	MLIKATE	RETOUR	22:45	MLIKATE	KHOURIBGA	23:30	F-Z-10-9-8-7-6-5-4-3-Q	45	74.00	1.00	74.00
4fda035e-a94e-456f-a30a-753b4d785153	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43441	F4	448	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	00:15	KHOURIBGA	KHOURIBGA	00:30	10----->BL	15	10.00	1.00	10.00
4810b984-daa5-45de-806d-a3da174349dc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59028	F5	434	AUTOCAR	MAN	KHOURIBGA	MERA	ALLER	05:50	KHOURIBGA	MERA	06:30	Q-5-6-7-8-9-10-11	40	60.00	1.00	60.00
d63899f2-7ed8-4523-98bb-2a42a0813a94	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59028	F5	434	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	07:00	KHOURIBGA	LAVERIE MERA	07:30	H-T-1-2-3-4-5-OK-8-9-10-Z-F	30	46.00	0.50	23.00
8d5159b5-9dc7-4bf5-a5b4-cf1ea676023c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59028	F5	434	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	07:45	LAVERIE MERA	KHOURIBGA	08:30	N-A	45	46.00	0.50	23.00
b7c41a0a-b2ab-4c88-a9d8-19d0001c9d16	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59028	F5	434	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	13:50	KHOURIBGA	LAVERIE MERA	14:30	Q-5-6-7-8-9-10-Z-F	40	46.00	0.50	23.00
76ea2527-9468-46f7-b630-55fbfa7e853b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59028	F5	434	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	RETOUR	14:45	LAVERIE MERA	KHOURIBGA	15:30	F-Z-10-1-2-H-T	45	46.00	0.50	23.00
9e8d0a85-6c02-40e0-859e-dc2564c0f1d2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	50592	F2	430	AUTOCAR	MAN	KHOURIBGA	MERA	RETOUR	15:45	MERA	KHOURIBGA	16:30	11-10-9-8-7-6-5-4-3-Q	45	60.00	1.00	60.00
6fd8a546-7235-461e-9aa6-f01538c1deab	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	50592	F2	430	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
1596af68-fba6-42fa-b402-eaa5f1435833	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59056	G1	422	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:00	KHOURIBGA	LAVERIE DAOUI	05:30	Q-5-6-7-8-9-10-11	30	84.00	0.50	42.00
cff694c6-4f33-4be9-a578-0b6e38ed4206	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59056	G1	422	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	06:30	LAVERIE DAOUI	KHOURIBGA	07:00	11-10-1-2-H-T	30	84.00	0.50	42.00
6774abbd-2ebb-49f9-a996-b8126cc6779c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59056	G1	422	AUTOCAR	MAN	KHOURIBGA	UB	ALLER	07:00	KHOURIBGA	UB-UM1	07:30	H-T-1-2-3-4-5-9-10-11	30	50.00	1.00	50.00
2220e633-de16-441b-b882-0840f49fb96a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	S	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	59056	G1	422	AUTOCAR	MAN	KHOURIBGA	LAVERIE MERA	ALLER	08:20	KHOURIBGA	LAVERIE MERA	09:00	Q-5-6-7-8-9-10-Z-F	40	46.00	1.00	46.00
b8769fe3-f2f9-4449-8960-35b4bb72f8f3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58979	G2	422	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	13:50	KHOURIBGA	LAVERIE DAOUI	14:30	H-T-1-2-3-4-5-9-10-11	40	84.00	0.50	42.00
b47f235f-646f-4cfd-8049-fb7d56cdd4a0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58979	G2	422	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	14:45	LAVERIE DAOUI	KHOURIBGA	15:30	11-10-9-8-7-6-5-4-3-Q	45	84.00	0.50	42.00
9ad91735-57ce-4c3c-87d3-d6b645c40cfd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58979	G2	422	AUTOCAR	MAN	BOULANOIR	PARC 7900	RETOUR	22:45	7900-LAVERIE MERA	BOULANOIR	23:30	\N	45	50.00	1.00	50.00
9b8db966-9707-4170-a553-6f177d5af9af	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58979	G2	422	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	00:15	KHOURIBGA	KHOURIBGA	00:30	10------>V-Q	15	10.00	1.00	10.00
1408a1d8-1cf0-448b-bcfa-e0e0e4ff0377	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58959	G3	441	AUTOCAR	MAN	KHOURIBGA	DAOUI	ALLER	05:50	KHOURIBGA	DAOUI	06:30	H-T-1-2-3-4-5-9-10-11	40	86.00	0.50	43.00
4e7d109f-7329-45f2-ba7c-0c779255abef	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58959	G3	441	AUTOCAR	MAN	KHOURIBGA	DAOUI	RETOUR	06:45	DAOUI	KHOURIBGA	07:30	11-10-9-8-7-6-5-4-3-Q	45	86.00	0.50	43.00
4fbfe245-4511-4dfe-9915-7865ec46c642	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58959	G3	441	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	08:10	KHOURIBGA	KHOURIBGA	08:30	10----->V-Q	20	10.00	1.00	10.00
2a6008a1-8340-4a23-8df0-606acccecba0	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	58959	G3	441	AUTOCAR	MAN	BOULANOIR	MERA	RETOUR	14:45	MERA	HATTANE-BOULANOIR	15:30	\N	45	60.00	1.00	60.00
2b0ee3bb-2e9a-4889-9b9f-e7443dbb53ca	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43754	G4	401	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE (T)	KHOURIBGA	16:30	F-Z-10-1-2-H-T	45	104.00	1.00	104.00
7967d749-8fe8-4e86-b56f-8a086c124390	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	43754	G4	401	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
180e2129-0bbc-4389-ad4d-26bbeca13fe4	0cea9745-6aa2-4105-9bdc-341d95999048	1edc2404-0388-4ceb-9970-3743a87ce5ac	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78344	G5	478	AUTOCAR	MAN	FQUIH BEN SALEH	SIDI CHENNANE	ALLER	05:50	FQUIH BEN SALEH	SIDI CHENNANE (D)	06:30	\N	40	125.00	1.00	125.00
75df3599-f1a6-45d1-870e-409114c054ff	0cea9745-6aa2-4105-9bdc-341d95999048	1edc2404-0388-4ceb-9970-3743a87ce5ac	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	78344	G5	478	AUTOCAR	MAN	FQUIH BEN SALEH	SIDI CHENNANE	RETOUR	14:45	SIDI CHENNANE (D)	FQUIH BEN SALEH	15:30	\N	45	125.00	1.00	125.00
d02f354c-2ccc-4222-a57b-ccb8a5991d90	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	N	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77813	G6	430	AUTOCAR	MAN	KHOURIBGA	MERA	RETOUR	15:45	MERA	KHOURIBGA	16:30	11-10-9-8-7-6-5-4-3-Q	45	60.00	1.00	60.00
feff2cc9-be9c-4aed-8856-1f3fc13c765b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P3	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77813	G6	430	AUTOCAR	MAN	KHOURIBGA	\N	\N	21:30	KHOURIBGA	KHOURIBGA	00:30	\N	180	\N	0.00	0.00
f7af26c0-f90f-49ad-b9f5-e198cc6f231e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77654	H1	405	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	ALLER	05:50	KHOURIBGA	ZONE CENTRALE	06:30	H-T-1-2-3-4-5-OK-8-9-10-Z-F	40	50.00	0.50	25.00
52ea9780-23eb-4763-8a98-7b57eaf349c8	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P1	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77654	H1	405	AUTOCAR	MAN	KHOURIBGA	ZONE CENTRALE	RETOUR	06:45	ZONE CENTRALE-LAVERIE MERA	KHOURIBGA	07:30	F-Z-10-V-5-4-3-Q	45	50.00	0.50	25.00
d2fde544-dc68-4053-84cc-70b459842807	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	77654	H1	405	AUTOCAR	MAN	KHOURIBGA	SIDI CHENNANE	RETOUR	15:45	SIDI CHENNANE (D)	KHOURIBGA	16:30	F-Z-10-V-5	45	104.00	1.00	104.00
69f44b3a-2eee-4128-80cc-9be0c725215a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CP	H2	466	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	15:30	KHOURIBGA	KHOURIBGA	16:00	5----->HAY RIAD	30	6.00	1.00	6.00
6d58c725-cf83-4b18-a8cc-6f0459ffb5a7	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	SOTREG	P2	t	2026-04-03 01:52:54.718687+00	2026-04-03 01:52:54.718687+00	818abb76-2384-4ff8-b786-c2758ab4d19d	CP	H2	466	AUTOCAR	MAN	KHOURIBGA	NAVETTE	ALLER	16:30	KHOURIBGA	KHOURIBGA	17:30	5------>HAY RIAD	60	6.00	1.00	6.00
\.


--
-- Data for Name: constraint_param; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.constraint_param (tenant_id, key, value, category, description, is_active, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee (tenant_id, matricule, first_name, last_name, site_id, shift_time, address, quartier, city, lat, lng, geom, preferred_pickup_address, preferred_pickup_lat, preferred_pickup_lng, is_pmr, function_role, phone, department, transport_required, current_transport_mode, opt_in_company_transport, has_private_car, volunteer_driver, carpool_seats, active, sirh_external_id, hire_date, end_date, id, created_at, updated_at, point_arret_id) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00001	Adil	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	50 Rue de la Paix	Quartier Al Amal	Khouribga	32.853223	-6.5675335	\N	\N	\N	\N	f	Qualité	+212611799355	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	9c4ba5a2-6d7e-4815-a677-888f5bb06b99	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00002	Hicham	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	78 Rue Al Massira	Quartier Al Wifaq	Oued Zem	32.8726607	-6.9204997	\N	\N	\N	\N	f	Opérateur	+212626861103	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	1c247824-1ab5-4721-a2b4-4c0b7cce8e50	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00003	Soufiane	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	N	114 Rue de la Paix	Quartier Anassi	Khouribga	32.8694951	-6.5772546	\N	\N	\N	\N	f	Opérateur	+212693168073	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	86a57603-a5bb-42b3-bfeb-d68e3063e04d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00004	Hassan	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	150 Rue Ifrane	Quartier Hassania	Khouribga	32.8985371	-6.9357609	\N	\N	\N	\N	f	Sécurité	+212691252207	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	2b8c6cd9-dc91-47da-b6b3-832aad6a855d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00005	Mehdi	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	3 Rue Ifrane	Quartier Hay Mohammadi	Bir Mezoui	32.8524206	-6.5771831	\N	\N	\N	\N	f	Administratif	+212644434962	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	a13b3aed-8b2e-413a-bb25-a0665c627bf2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00006	Laila	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P2	156 Rue des Orangers	Quartier Al Wifaq	Hattane	32.859482	-6.5730379	\N	\N	\N	\N	f	Comptable	+212699955964	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	fd3270f8-fa50-4bc6-a4ac-84f692099208	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00007	Jamila	Sahraoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	150 Rue Atlas	Quartier Medersa	Oued Zem	32.8923799	-6.8962853	\N	\N	\N	\N	f	Analyste	+212658108820	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	5012488d-9e28-4435-a3e1-806a7a4b8d44	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00008	Youssef	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	65 Rue Hassan II	Quartier Al Amal	Hattane	32.885395	-6.9047682	\N	\N	\N	\N	f	Qualité	+212638175387	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	f0d60a8f-dd7a-4940-9162-4a60fc467f78	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00009	Driss	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	S	52 Rue Al Massira	Quartier Al Wifaq	Hattane	32.8891593	-6.8905328	\N	\N	\N	\N	f	Conducteur	+212665307759	Informatique	f	personal_car	Non	t	f	0	t	\N	\N	\N	1353c217-661f-4ff1-9fb2-63d97e8ec006	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00010	Anass	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	96 Rue Hassan II	Quartier Tamaris	Bir Mezoui	32.8392503	-6.805437	\N	\N	\N	\N	f	Sécurité	+212616879739	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	23e9ea87-5e07-4cd9-b46f-d93f9a81eeb3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00011	Bouchra	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	89 Rue de la Paix	Quartier Al Amal	Hattane	32.9195941	-6.7216127	\N	\N	\N	\N	f	Comptable	+212671947527	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	36a19f89-f0e0-4c4b-b670-230e730b2a64	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00012	Fatima	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	42 Rue Ifrane	Quartier Medersa	Boulanoir	32.8989459	-6.6785156	\N	\N	\N	\N	f	Logisticien	+212650665069	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	b7c484b4-5195-4163-b2b2-3f69a58fef3e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00013	Hicham	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	50 Rue Ifrane	Quartier Al Wifaq	Oued Zem	32.8996317	-6.9025095	\N	\N	\N	\N	f	Opérateur	+212675912953	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	6af47774-1863-452c-8397-ce38b9717dbd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00014	Latifa	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	184 Rue Mohammed V	Quartier Al Amal	Gueffaf	32.8786264	-6.9210602	\N	\N	\N	\N	f	Opérateur	+212628211409	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	83762953-004c-4f97-9328-5b64312d9866	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00015	Adil	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	112 Rue de la Paix	Quartier Medersa	Gueffaf	32.889001	-6.9369255	\N	\N	\N	\N	f	Logisticien	+212640361629	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	93bf10c9-c9e9-47ef-b252-4f96a1503ff1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00016	Latifa	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	63 Rue Hassan II	Quartier Al Wifaq	Gueffaf	32.887683	-6.9295309	\N	\N	\N	\N	f	Superviseur	+212665964967	Maintenance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	960713e0-3dad-403d-a3fc-bc4e6ff20433	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00017	Rachid	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	107 Rue des Orangers	Quartier Al Wifaq	Oued Zem	32.8577333	-6.8768682	\N	\N	\N	\N	f	RH	+212692704835	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	6a21a73e-5c0b-44cd-a663-07108dd6a478	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00018	Ghita	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	N	115 Rue Al Massira	Quartier Hay Salam	Hattane	32.8566994	-6.571911	\N	\N	\N	\N	f	Logisticien	+212626955021	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	3286cf67-384c-4c9a-8919-b3071eba3754	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00019	Kawtar	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	164 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.8902395	-6.8932953	\N	\N	\N	\N	f	Superviseur	+212636774386	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	e859261a-214a-46d0-a531-956f887a72ca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00020	Wafae	Lamrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	36 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8837054	-6.9187829	\N	\N	\N	\N	f	Superviseur	+212630303737	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	deea51e5-f4c9-428b-a4ee-4d5a0fc3b2ed	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00021	Bouchra	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	38 Rue de la Paix	Quartier Hassania	Oued Zem	32.8992973	-6.7776204	\N	\N	\N	\N	f	Agent de maîtrise	+212626767452	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	b47a30f0-6299-47bb-8323-a13db1d8aa91	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00022	Hicham	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	68 Rue de la Paix	Quartier Anassi	Oued Zem	32.8559087	-6.5767298	\N	\N	\N	\N	f	Opérateur	+212615015435	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	58d2283a-aeb0-4b5d-bd22-be9f996591f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00023	Othmane	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	179 Rue de la Paix	Quartier Medersa	Khouribga	32.8787106	-6.9128522	\N	\N	\N	\N	f	Analyste	+212635566613	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	38209ec4-5486-4f85-a225-78e53345d088	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00024	Soumia	Laroui	d39d79ec-a716-4839-a93d-1845d00c182c	S	83 Rue des Orangers	Quartier Al Wifaq	Khouribga	32.8766586	-6.9165938	\N	\N	\N	\N	f	Ingénieur	+212655362576	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	61a06693-c8e5-4b6d-ad63-28e75bda6cd6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00025	Nadia	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	113 Rue des Orangers	Quartier Hassania	Boulanoir	32.861576	-6.5789872	\N	\N	\N	\N	f	Analyste	+212642248514	Qualité	f	taxi	Non	t	f	0	t	\N	\N	\N	0673dca9-ef55-4482-b1c4-be2e12818218	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00026	Mustapha	Ouazzani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	103 Rue Ifrane	Quartier Medersa	Hattane	32.9252584	-6.7189465	\N	\N	\N	\N	t	Analyste	+212620521632	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	77134a79-cbb8-4cc3-bc77-f0183c46fd47	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00027	Hassan	Laaroussi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	118 Rue Ifrane	Quartier Medersa	Bir Mezoui	32.8511657	-6.879942	\N	\N	\N	\N	f	Opérateur	+212686369387	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	d5f37122-8a21-498a-b930-a18459540c45	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00028	Ahmed	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	158 Rue Ifrane	Quartier Al Amal	Bir Mezoui	32.8977893	-6.939701	\N	\N	\N	\N	f	Comptable	+212659683977	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	f5ff2213-6210-41e7-b2c5-c41ea6cc30e5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00029	Aicha	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	107 Rue Atlas	Quartier Anassi	Gueffaf	32.9029386	-6.7844513	\N	\N	\N	\N	f	Opérateur	+212631817205	Production	f	walk	Non	t	f	0	t	\N	\N	\N	451f010e-f537-469e-94ea-15108f204ba3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00030	Othmane	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	139 Rue Al Massira	Quartier Al Amal	Boujniba	32.8618716	-6.5665747	\N	\N	\N	\N	f	Technicien	+212650017255	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	dbe6ff99-d30c-4048-b392-0a2dab95a450	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00031	Hicham	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	189 Rue des Orangers	Quartier Al Amal	Bir Mezoui	32.9043016	-6.7848746	\N	\N	\N	\N	f	Administratif	+212696732408	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	83dd6a98-3bea-4455-8849-3b47f0ac2aee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00032	Ibrahim	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	124 Rue des Orangers	Quartier Hay Salam	Hattane	32.8945088	-6.942695	\N	\N	\N	\N	f	RH	+212653194933	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	ace53bfa-d218-44de-a808-a554f29b86f9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00033	Hicham	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	N	178 Rue Ifrane	Quartier Anassi	Bir Mezoui	32.8349168	-6.8074449	\N	\N	\N	\N	f	Ingénieur	+212668230419	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	30c618af-d517-46f8-9cb9-fce46bbd2d79	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00034	Mustapha	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	149 Rue Hassan II	Quartier Centre	Oued Zem	32.8867422	-6.9198131	\N	\N	\N	\N	f	Conducteur	+212690497824	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	84d79f49-ef53-4d48-b523-c5f5ece1db1c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00035	Youssef	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	32 Rue Hassan II	Quartier Al Wifaq	Oued Zem	32.8677003	-6.9048156	\N	\N	\N	\N	f	Sécurité	+212632516991	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	c79d51f7-9fd4-4072-aedc-122557a3c15b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00036	Wafae	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	49 Rue Mohammed V	Quartier Al Wifaq	Boujniba	32.89922	-6.7794962	\N	\N	\N	\N	f	Analyste	+212687555277	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	63e1aea3-5b57-4fa1-a85d-12f6df249f02	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00037	Ilham	Hassouni	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	145 Rue Mohammed V	Quartier Hay Salam	Hattane	32.8957052	-6.7746095	\N	\N	\N	\N	f	Électricien	+212649592450	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	17866a37-b77a-4ead-b120-7f87f5c48a11	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00038	Soufiane	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	23 Rue Al Massira	Quartier Al Amal	Khouribga	32.8971625	-6.7803501	\N	\N	\N	\N	f	Opérateur	+212677093373	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	0dac94b1-f92f-41d6-849a-8dd68d77237e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00039	Bilal	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	S	82 Rue des Orangers	Quartier Hassania	Boujniba	32.8654	-6.5809947	\N	\N	\N	\N	f	Comptable	+212680191619	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	88b1eb80-6553-476b-834c-51a3d063cec5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00040	Hanane	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	168 Rue Mohammed V	Quartier Anassi	Hattane	32.8504785	-6.8763886	\N	\N	\N	\N	f	Administratif	+212678706492	RH	f	walk	Non	t	f	0	t	\N	\N	\N	3be33463-9ade-452f-be03-9a2a6e376e43	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00041	Ali	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	26 Rue Mohammed V	Quartier Centre	Hattane	32.867931	-6.5752121	\N	\N	\N	\N	f	Administratif	+212680039405	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	d37d62b1-fbf9-4bb0-acb8-c5c23b2efc4e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00042	Jamila	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P3	59 Rue Hassan II	Quartier Tamaris	Khouribga	32.9191795	-6.7211381	\N	\N	\N	\N	f	Analyste	+212615973555	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	67a72c77-a229-42d0-906f-442bf459f446	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00043	Tariq	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	101 Rue Al Massira	Quartier Tamaris	Khouribga	32.8747323	-6.9208721	\N	\N	\N	\N	f	Ingénieur	+212624404621	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	80930f69-a035-4828-9dec-c13ec38ff836	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00044	Bilal	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	105 Rue Ifrane	Quartier Hay Salam	Boulanoir	32.8790148	-6.9090852	\N	\N	\N	\N	f	Agent de maîtrise	+212660170083	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	cf270cea-1265-456b-a789-d5c498c6268c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00045	Hanane	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	114 Rue Al Massira	Quartier Centre	Gueffaf	32.8657133	-6.9108415	\N	\N	\N	\N	f	Administratif	+212636299777	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	98c92524-676b-4ea7-a593-aae19ab24a58	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00046	Bouchra	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	4 Rue Mohammed V	Quartier Al Amal	Khouribga	32.9028282	-6.68505	\N	\N	\N	\N	f	Superviseur	+212653581981	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	7787244d-2be2-48c0-b787-92f32076513d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00047	Noureddine	Bennani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	179 Rue des Orangers	Quartier Hassania	Oued Zem	32.8943875	-6.9359379	\N	\N	\N	\N	f	Administratif	+212629994375	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	e52baec1-c1f9-4cbb-985b-0af6b0850425	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00048	Soumia	Laroui	d39d79ec-a716-4839-a93d-1845d00c182c	N	167 Rue de la Paix	Quartier Tamaris	Bir Mezoui	32.8885403	-6.9030932	\N	\N	\N	\N	f	Sécurité	+212639203892	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	bcfe4fc4-c376-4b0a-8359-a2fc1715ae4c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00049	Soufiane	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	8 Rue des Orangers	Quartier Hassania	Khouribga	32.899064	-6.9371193	\N	\N	\N	\N	f	Superviseur	+212665809063	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	a3e71b38-11de-49dd-95a8-d69057f4d26e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00050	Naima	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	98 Rue Hassan II	Quartier Medersa	Boujniba	32.8400767	-6.8004872	\N	\N	\N	\N	f	Mécanicien	+212671084313	Informatique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	0d61213e-7a14-4523-8b22-5cf4492ef34a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00051	Hicham	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	121 Rue de la Paix	Quartier Medersa	Boujniba	32.8921658	-6.7726339	\N	\N	\N	\N	f	RH	+212614506222	Informatique	f	personal_car	Non	t	f	0	t	\N	\N	\N	c07046c8-49ae-491e-888f-00fdde036b37	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00052	Hanane	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	114 Rue de la Paix	Quartier Centre	Boulanoir	32.8700214	-6.9193924	\N	\N	\N	\N	f	Logisticien	+212678924358	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	621a4b5f-b8d2-49f1-ba1c-5b9d6db10bb2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00053	Hassan	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	143 Rue des Orangers	Quartier Al Wifaq	Bir Mezoui	32.8846013	-6.9220146	\N	\N	\N	\N	f	Comptable	+212642656899	Production	f	walk	Non	t	f	0	t	\N	\N	\N	f2bb085a-772c-4dc6-845d-b0ad46169a5a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00054	Jawad	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	S	97 Rue Atlas	Quartier Hassania	Oued Zem	32.8504161	-6.575801	\N	\N	\N	\N	f	Sécurité	+212662853338	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	afa7dfe5-28bf-492e-a579-0e6db93e7e62	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00055	Khadija	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	151 Rue des Orangers	Quartier Medersa	Khouribga	32.8365317	-6.7998008	\N	\N	\N	\N	f	Opérateur	+212691466955	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	38775634-5262-4f68-9a40-833804862c33	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00056	Jamila	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	162 Rue Hassan II	Quartier Hay Salam	Khouribga	32.8614341	-6.5830226	\N	\N	\N	\N	f	Analyste	+212664776072	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	ac3da9bd-a792-4c57-87df-99cce1e8903b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00057	Omar	Zemmouri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	35 Rue Ifrane	Quartier Tamaris	Bir Mezoui	32.8861101	-6.923078	\N	\N	\N	\N	f	Mécanicien	+212694695083	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	de3a5631-52d3-4fcf-b6c3-981f602aed85	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00058	Hafida	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	119 Rue Ifrane	Quartier Hay Salam	Boulanoir	32.8932125	-6.9024814	\N	\N	\N	\N	f	Mécanicien	+212686109841	RH	f	walk	Non	t	f	0	t	\N	\N	\N	66557331-8b12-4b8a-bbcd-ec8f74a4ff09	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00059	Naima	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	23 Rue des Orangers	Quartier Hay Salam	Bir Mezoui	32.9019966	-6.769399	\N	\N	\N	\N	f	Superviseur	+212699096285	Qualité	f	taxi	Non	t	f	0	t	\N	\N	\N	01a9e7c5-c699-434d-a59c-0bb553e5fc36	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00060	Rachid	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P1	125 Rue Ifrane	Quartier Hay Salam	Boujniba	32.9235651	-6.721571	\N	\N	\N	\N	f	Sécurité	+212692182146	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	f5c9886c-a68a-4156-b6be-219f959fbe68	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00061	Naima	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	167 Rue Atlas	Quartier Tamaris	Hattane	32.8832825	-6.9176888	\N	\N	\N	\N	f	Administratif	+212618711680	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	1bb88cfa-dc81-492b-bfda-28890ea0b8cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00062	Zakaria	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	90 Rue Hassan II	Quartier Medersa	Boulanoir	32.8469099	-6.7984646	\N	\N	\N	\N	f	Superviseur	+212616144283	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	f881dc74-155a-4735-a878-a55e7774ff53	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00063	Kawtar	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	N	108 Rue des Orangers	Quartier Hay Salam	Oued Zem	32.9057029	-6.7822959	\N	\N	\N	\N	f	Agent de maîtrise	+212628076757	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	68029e1e-062a-4922-80e8-6128e2e5e699	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00064	Issam	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	81 Rue Atlas	Quartier Hay Salam	Khouribga	32.9012886	-6.9419947	\N	\N	\N	\N	f	Sécurité	+212620100989	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	9f43bdd9-7e69-44c1-b439-7adbb9c2d97a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00065	Laila	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	33 Rue Mohammed V	Quartier Centre	Boulanoir	32.8741467	-6.90996	\N	\N	\N	\N	f	Logisticien	+212645581512	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	b9c541f1-24c1-44e2-a14e-da366b3ab1cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00066	Soufiane	Talbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	184 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8660259	-6.9157368	\N	\N	\N	\N	t	Technicien	+212644080862	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	4cd96177-a764-4fb5-bca1-e9ff4f15a287	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00067	Ghita	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	128 Rue Atlas	Quartier Al Wifaq	Boujniba	32.8987737	-6.9092009	\N	\N	\N	\N	f	Technicien	+212672122285	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	a81bc22f-1826-42c6-8e7f-212fc9c0106d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00068	Ibrahim	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	166 Rue des Orangers	Quartier Tamaris	Gueffaf	32.87241	-6.9054824	\N	\N	\N	\N	f	Administratif	+212682073380	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	8c5d6d77-b1d6-48db-b8cf-a94a24c0ba78	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00069	Soufiane	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	S	186 Rue des Orangers	Quartier Hay Salam	Hattane	32.9034049	-6.7705937	\N	\N	\N	\N	f	Technicien	+212642546274	Transport	f	walk	Non	t	f	0	t	\N	\N	\N	e406533d-84e1-4a72-b82b-f4c95682bc11	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00070	Malika	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	173 Rue Hassan II	Quartier Al Amal	Boujniba	32.8656734	-6.5813468	\N	\N	\N	\N	f	Administratif	+212681458208	Finance	f	taxi	Non	t	f	0	t	\N	\N	\N	d92ee771-ed4c-4474-a0ac-a9c02ce647af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00071	Omar	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	120 Rue des Orangers	Quartier Tamaris	Hattane	32.8380431	-6.8035802	\N	\N	\N	\N	f	Électricien	+212670663886	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	279c57f1-f9c2-422e-b30d-9d263e6cf92d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00072	Ahmed	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	67 Rue de la Paix	Quartier Anassi	Oued Zem	32.8518373	-6.5741978	\N	\N	\N	\N	f	Agent de maîtrise	+212692417033	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	adead7ae-e791-4333-98e8-cf5fe4467b48	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00073	Ghita	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	9 Rue Mohammed V	Quartier Centre	Boujniba	32.8855838	-6.9084681	\N	\N	\N	\N	f	Électricien	+212685350929	Production	f	walk	Non	t	f	0	t	\N	\N	\N	128f8c09-d59d-45fc-91c0-2aa3c81e8e7e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00074	Loubna	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	138 Rue de la Paix	Quartier Centre	Bir Mezoui	32.8952917	-6.9369174	\N	\N	\N	\N	f	Administratif	+212644009005	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	39296edb-c721-45d9-bf08-ea76848abf2d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00075	Youssef	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P1	173 Rue Ifrane	Quartier Centre	Khouribga	32.8979244	-6.7847544	\N	\N	\N	\N	t	Administratif	+212676696206	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	db84e4fd-5560-4134-a009-dafdde3d56fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00076	Zakaria	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	36 Rue des Orangers	Quartier Hassania	Bir Mezoui	32.8904991	-6.9378674	\N	\N	\N	\N	f	Superviseur	+212695897255	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	756579fe-83ec-4187-b5c8-f08c4aa99ee9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00077	Malika	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	52 Rue des Orangers	Quartier Centre	Gueffaf	32.8633194	-6.5528933	\N	\N	\N	\N	f	Ingénieur	+212640207417	Production	f	taxi	Non	t	f	0	t	\N	\N	\N	b22e8aa7-e06a-47bc-9701-1bb0075bd3d1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00078	Khadija	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	N	154 Rue Mohammed V	Quartier Anassi	Hattane	32.899998	-6.7783957	\N	\N	\N	\N	f	Électricien	+212637620925	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	0e2cef32-f000-41be-a3f7-eec75ce2b188	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00079	Ilham	Mouttaki	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	31 Rue Al Massira	Quartier Medersa	Boujniba	32.8989439	-6.9066958	\N	\N	\N	\N	f	Superviseur	+212642957846	Informatique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	36f7dcb9-bfe6-4c30-878b-aaf0be54b80c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00080	Malika	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	23 Rue Al Massira	Quartier Al Wifaq	Hattane	32.8947969	-6.7747926	\N	\N	\N	\N	f	Logisticien	+212670924994	Informatique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	61b039c4-8ddf-4f98-b773-748a54300365	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00081	Rajaa	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P2	199 Rue Al Massira	Quartier Centre	Hattane	32.8691094	-6.9135979	\N	\N	\N	\N	f	Sécurité	+212638795079	Production	f	taxi	Non	t	f	0	t	\N	\N	\N	bdf33185-91ad-420d-b0fc-db7a6ebfb7ad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00082	Anass	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	161 Rue Atlas	Quartier Hassania	Khouribga	32.8531895	-6.5767558	\N	\N	\N	\N	f	Logisticien	+212674762563	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	a2d56046-261c-4926-9fdc-8aa487548c78	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00083	Bouchra	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	35 Rue Hassan II	Quartier Anassi	Khouribga	32.8953634	-6.7816244	\N	\N	\N	\N	f	Analyste	+212661452341	Production	f	walk	Non	t	f	0	t	\N	\N	\N	cf2dfd60-96c6-4397-8846-0e9c2007ed90	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00084	Khalid	Slaoui	d39d79ec-a716-4839-a93d-1845d00c182c	S	66 Rue Atlas	Quartier Hassania	Khouribga	32.8954053	-6.9380425	\N	\N	\N	\N	f	Administratif	+212622863986	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	610a8580-efa4-4b34-81fe-ddab42a08729	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00085	Amina	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	87 Rue Ifrane	Quartier Hassania	Bir Mezoui	32.9214442	-6.7186828	\N	\N	\N	\N	f	Comptable	+212663636892	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	976566cd-564a-48f7-816f-2bb05b08cf89	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00086	Kawtar	El Fassi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	22 Rue de la Paix	Quartier Al Wifaq	Oued Zem	32.898678	-6.9338192	\N	\N	\N	\N	f	Opérateur	+212630837970	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	df93cd88-bd74-4c11-88b1-e3fe2b208a00	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00087	Aicha	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	P3	164 Rue de la Paix	Quartier Al Amal	Gueffaf	32.8737164	-6.9253426	\N	\N	\N	\N	f	Qualité	+212655450355	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	33336d7d-5e85-454f-90a4-6074a02be791	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00088	Driss	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	120 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.8603697	-6.5547021	\N	\N	\N	\N	f	Électricien	+212698647404	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	5de85957-35d2-4eac-88af-709a9f109c10	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00089	Zakaria	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	87 Rue des Orangers	Quartier Hassania	Boujniba	32.9098422	-6.7818287	\N	\N	\N	\N	f	Ingénieur	+212655322413	Transport	f	personal_car	Non	t	f	0	t	\N	\N	\N	dcaff2d1-15f4-4979-9bf8-55d71fe26c9e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00090	Sanaa	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P1	166 Rue Mohammed V	Quartier Al Amal	Boulanoir	32.9025676	-6.7705764	\N	\N	\N	\N	f	Analyste	+212638834477	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	42e6a49c-d35d-48dd-afe9-cf5337b31d8b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00091	Kawtar	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	49 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.8508079	-6.5761918	\N	\N	\N	\N	t	Sécurité	+212637033020	Informatique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	5c6d7187-6efd-40f6-b068-8f0596c4988e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00092	Meryem	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	2 Rue Al Massira	Quartier Hassania	Gueffaf	32.8563968	-6.5756357	\N	\N	\N	\N	f	Superviseur	+212625560497	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	e02f72a5-2a69-4fa1-95f4-b09181d9f78d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00093	Naima	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	150 Rue Mohammed V	Quartier Anassi	Gueffaf	32.8612846	-6.5504746	\N	\N	\N	\N	f	Ingénieur	+212656648951	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	7c7aa543-59ce-46b7-a5e8-d5adc69f0a68	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00094	Ghita	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	139 Rue Ifrane	Quartier Al Amal	Oued Zem	32.8993718	-6.7816295	\N	\N	\N	\N	f	Sécurité	+212692804149	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	098e74b7-4894-47c6-ba5e-4a564bd73363	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00095	Amine	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	11 Rue Al Massira	Quartier Medersa	Bir Mezoui	32.8852588	-6.9018722	\N	\N	\N	\N	f	Sécurité	+212684104825	Qualité	f	personal_car	Non	t	f	0	t	\N	\N	\N	74414e91-7141-4314-936e-faf134354df9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00096	Meryem	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	134 Rue Atlas	Quartier Hay Mohammadi	Bir Mezoui	32.8923299	-6.9384549	\N	\N	\N	\N	f	Logisticien	+212641071047	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	3444ac93-b70c-4ac7-a348-6204683ce885	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00097	Ghita	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	121 Rue Atlas	Quartier Medersa	Oued Zem	32.896966	-6.7743058	\N	\N	\N	\N	f	Opérateur	+212638699832	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	b3c0530f-f3d2-428e-9412-07cb25145c60	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00098	Amine	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	47 Rue Atlas	Quartier Centre	Bir Mezoui	32.8974339	-6.9291892	\N	\N	\N	\N	t	Technicien	+212648810761	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	589413cf-57a3-4948-a24c-d46bf22240b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00099	Bouchra	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	S	9 Rue de la Paix	Quartier Medersa	Boulanoir	32.9262866	-6.7141334	\N	\N	\N	\N	f	Qualité	+212639564329	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	3cedac6a-3724-4a51-b78e-09a0485e9d55	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00100	Youssef	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	192 Rue de la Paix	Quartier Medersa	Oued Zem	32.8949566	-6.9433532	\N	\N	\N	\N	f	RH	+212692394127	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	15276fa7-6774-4875-bf97-babe5a241192	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00101	Issam	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	166 Rue Mohammed V	Quartier Anassi	Khouribga	32.9000001	-6.7815462	\N	\N	\N	\N	f	Opérateur	+212647702399	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	cf848656-091f-4d76-9000-82d10f818a3e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00102	Bilal	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	170 Rue Al Massira	Quartier Medersa	Gueffaf	32.89859	-6.91147	\N	\N	\N	\N	f	Superviseur	+212651861937	Qualité	f	taxi	Non	t	f	0	t	\N	\N	\N	0aab3a5a-c0e2-4dc1-b2ed-559ffff2823a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00103	Ibrahim	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	188 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.9222517	-6.718871	\N	\N	\N	\N	f	Superviseur	+212653269911	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	20ed9f72-7e4a-4bd6-8bee-1b9bde40ca03	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00104	Rajaa	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	97 Rue de la Paix	Quartier Medersa	Oued Zem	32.8981404	-6.7724694	\N	\N	\N	\N	f	Qualité	+212621602302	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	3a755e00-e4ba-4f6c-ba1b-ec127d3c8d20	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00105	Zineb	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	102 Rue des Orangers	Quartier Al Wifaq	Gueffaf	32.9042333	-6.7757941	\N	\N	\N	\N	f	Mécanicien	+212650223650	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	59cc4259-bfc9-4a02-a12f-15c277be8a49	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00106	Lahcen	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	139 Rue Al Massira	Quartier Medersa	Boulanoir	32.8717179	-6.9054245	\N	\N	\N	\N	f	Conducteur	+212645311124	Transport	f	personal_car	Non	t	f	0	t	\N	\N	\N	742e4762-7502-4f29-a91a-e4940fef6cf7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00107	Omar	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	195 Rue Mohammed V	Quartier Centre	Khouribga	32.8859283	-6.9317296	\N	\N	\N	\N	f	Ingénieur	+212656597352	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	20054384-d2e5-4a18-b8ad-421b33cb65e5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00108	Hassan	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	N	19 Rue Hassan II	Quartier Medersa	Bir Mezoui	32.86194	-6.5808144	\N	\N	\N	\N	f	RH	+212682575794	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	02b67164-8b8b-4e65-843b-60ac1bdb50e0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00109	Hassan	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	12 Rue Hassan II	Quartier Al Amal	Boujniba	32.8562589	-6.575299	\N	\N	\N	\N	f	Sécurité	+212617173515	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	396782f5-18d8-47ed-b6c5-bdb5ae5e395c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00110	Ilham	Lahlou	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	74 Rue Ifrane	Quartier Medersa	Hattane	32.8989507	-6.7787352	\N	\N	\N	\N	f	Agent de maîtrise	+212667739329	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	c1b3e420-4b39-4462-b732-b3e9e045f504	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00111	Naima	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	P2	115 Rue Hassan II	Quartier Al Amal	Hattane	32.8642954	-6.5776866	\N	\N	\N	\N	f	Ingénieur	+212625409321	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	dc30ab48-4d88-4d01-8f26-3fa1a4d35a46	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00112	Karim	Mouttaki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	80 Rue de la Paix	Quartier Anassi	Hattane	32.9195361	-6.7165417	\N	\N	\N	\N	f	Analyste	+212667558284	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	c1898595-7a2c-4684-9157-d02a6eeae856	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00113	Bouchra	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	12 Rue des Orangers	Quartier Al Amal	Gueffaf	32.859039	-6.9058821	\N	\N	\N	\N	f	Opérateur	+212655736865	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	7d5f0f76-c9a4-47c9-9c3e-0303e07a3600	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00114	Khadija	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	S	73 Rue Mohammed V	Quartier Tamaris	Khouribga	32.8841114	-6.9076023	\N	\N	\N	\N	f	Analyste	+212653152096	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	94216a26-bca3-445b-a201-65d7ad309394	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00115	Zineb	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	176 Rue des Orangers	Quartier Hassania	Hattane	32.8714033	-6.9256893	\N	\N	\N	\N	f	RH	+212686669893	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	5fe2e9c4-4427-43fa-b7c2-eb613e78b125	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00116	Lahcen	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	164 Rue des Orangers	Quartier Tamaris	Boujniba	32.8972038	-6.9314805	\N	\N	\N	\N	f	Opérateur	+212650728470	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	f0b5eff0-5a65-47e3-9c29-c462767e1514	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00117	Hafida	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	145 Rue Hassan II	Quartier Medersa	Hattane	32.8999408	-6.7737954	\N	\N	\N	\N	f	RH	+212659274646	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	741191cf-d7be-4c6e-b303-6e22e3102cee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00118	Lahcen	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	20 Rue Al Massira	Quartier Hay Mohammadi	Boujniba	32.8763812	-6.9219349	\N	\N	\N	\N	f	Électricien	+212626538598	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	acd39489-95b9-4eb8-afb9-56a09d470205	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00119	Omar	Ouazzani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	27 Rue Atlas	Quartier Tamaris	Hattane	32.8752645	-6.9082481	\N	\N	\N	\N	f	Administratif	+212635893192	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	45245cfa-c20b-4ea2-b33c-1231a21834b1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00120	Mustapha	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	P1	69 Rue Mohammed V	Quartier Al Wifaq	Hattane	32.8970521	-6.9336152	\N	\N	\N	\N	f	Analyste	+212617261702	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	a70a4af4-ca42-41d7-b3d3-35af0a9d29c5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00121	Najat	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	110 Rue Ifrane	Quartier Hassania	Khouribga	32.8950676	-6.89584	\N	\N	\N	\N	f	Ingénieur	+212687733727	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	39a816f5-f5be-4767-be66-c82af80f20e8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00122	Amine	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	122 Rue de la Paix	Quartier Hassania	Boujniba	32.8976162	-6.7854748	\N	\N	\N	\N	f	Opérateur	+212630082576	Transport	f	walk	Non	t	f	0	t	\N	\N	\N	b235ce4e-c3b0-4046-a8c3-55bc7e57bad7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00123	Hafida	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	N	99 Rue des Orangers	Quartier Hay Salam	Gueffaf	32.8910267	-6.9375813	\N	\N	\N	\N	f	Technicien	+212624208259	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	6eebb022-cac0-485b-a5dd-9d22cb73ab65	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00124	Soumia	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	143 Rue des Orangers	Quartier Hay Salam	Oued Zem	32.8621732	-6.9062191	\N	\N	\N	\N	f	Conducteur	+212623247127	Production	f	taxi	Non	t	f	0	t	\N	\N	\N	dae9a511-22c3-4b8e-bab7-21983477bf7a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00125	Naima	El Fassi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	51 Rue Atlas	Quartier Hassania	Oued Zem	32.8685357	-6.578822	\N	\N	\N	\N	f	Agent de maîtrise	+212670583751	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	cf0ec9a9-1e77-4de7-a291-77425ac8f4b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00126	Noureddine	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P2	147 Rue de la Paix	Quartier Al Wifaq	Gueffaf	32.8899938	-6.8956165	\N	\N	\N	\N	f	RH	+212677114577	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	9321ba15-95c1-4ec3-9c08-1eb5745e5010	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00127	Ghita	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	25 Rue Ifrane	Quartier Centre	Boujniba	32.8778616	-6.9231715	\N	\N	\N	\N	f	Administratif	+212686113458	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	11ae411c-b572-4ada-b29c-40c8c6b1bc9a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00128	Rajaa	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	7 Rue Ifrane	Quartier Hassania	Hattane	32.9016273	-6.7790806	\N	\N	\N	\N	f	Ingénieur	+212671702669	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	7f4b1c4f-7c79-4ab7-b47e-25bb90ad3910	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00129	Karim	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	S	167 Rue de la Paix	Quartier Centre	Boujniba	32.8350656	-6.8034423	\N	\N	\N	\N	f	Logisticien	+212697769083	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	b04c50f1-7d92-4514-a6bf-b8ed5ad4bb30	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00130	Zakaria	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	18 Rue Hassan II	Quartier Hassania	Hattane	32.8697495	-6.9094607	\N	\N	\N	\N	f	Opérateur	+212680434154	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	53eb0d04-079a-4bbe-aaa0-0e77e27f8c81	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00131	Omar	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	154 Rue de la Paix	Quartier Al Wifaq	Khouribga	32.8981616	-6.7836178	\N	\N	\N	\N	f	Opérateur	+212660489276	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	3fb3b131-04a2-44da-abd4-7080a353efa4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00132	Laila	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	84 Rue Ifrane	Quartier Medersa	Oued Zem	32.895238	-6.7764001	\N	\N	\N	\N	f	Administratif	+212636852620	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	62b7f830-6686-49af-9348-0292cb786168	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00133	Karim	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	51 Rue de la Paix	Quartier Hay Mohammadi	Gueffaf	32.8937003	-6.9310705	\N	\N	\N	\N	f	Agent de maîtrise	+212683388679	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	6ce5fdbc-3ac1-4255-9c6b-1ebe6f1bb0b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00134	Malika	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	78 Rue Atlas	Quartier Tamaris	Bir Mezoui	32.8787133	-6.9168278	\N	\N	\N	\N	f	Opérateur	+212697762036	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	65676ec7-b631-4253-a6ad-15428d6992e0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00135	Amina	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	2 Rue Hassan II	Quartier Al Wifaq	Khouribga	32.8907635	-6.9382837	\N	\N	\N	\N	f	Administratif	+212639269116	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	3e2f8bbb-cb46-4896-9f95-ec8dd45e8ac5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00136	Tariq	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	133 Rue Atlas	Quartier Hay Mohammadi	Boulanoir	32.8946264	-6.9050364	\N	\N	\N	\N	f	Mécanicien	+212643421744	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	a521ad47-9f57-4942-afd4-aea0a085bcb5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00137	Jawad	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	29 Rue Ifrane	Quartier Al Amal	Boujniba	32.8937544	-6.9404743	\N	\N	\N	\N	f	Mécanicien	+212652906857	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	95f491da-a787-43a4-bf18-15c10c922e09	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00138	Amina	El Kabbaj	d39d79ec-a716-4839-a93d-1845d00c182c	N	133 Rue de la Paix	Quartier Medersa	Boujniba	32.8521276	-6.5696766	\N	\N	\N	\N	f	Superviseur	+212624846575	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	ec69d990-9a38-4d91-bdca-a30c25ab1e94	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00139	Hasnaa	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	7 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.8539298	-6.8797053	\N	\N	\N	\N	f	Logisticien	+212679444940	Transport	f	walk	Non	t	f	0	t	\N	\N	\N	a1b05e50-0aa7-431c-9ea3-efb799a24094	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00140	Imane	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	55 Rue des Orangers	Quartier Hay Salam	Boujniba	32.8848432	-6.903841	\N	\N	\N	\N	f	Analyste	+212678678143	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	1c53874e-722b-4d58-b05c-1dce2ae07b55	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00141	Hamza	Talbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	71 Rue Ifrane	Quartier Hay Mohammadi	Khouribga	32.8896682	-6.9303927	\N	\N	\N	\N	f	Opérateur	+212662983779	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	0756994f-8f9c-454a-b219-4d8d9da98af4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00142	Zakaria	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	103 Rue Ifrane	Quartier Hay Salam	Hattane	32.8548449	-6.8724189	\N	\N	\N	\N	f	Qualité	+212625737262	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	5b62d303-9aa7-4c66-91f5-c2a30edf809d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00143	Ali	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	85 Rue Atlas	Quartier Hassania	Oued Zem	32.9068338	-6.7832166	\N	\N	\N	\N	f	Logisticien	+212643348601	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	cd06c062-dfb9-4ff1-bf91-f24be2504a0d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00144	Siham	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	S	9 Rue Hassan II	Quartier Anassi	Khouribga	32.8981667	-6.904229	\N	\N	\N	\N	f	Mécanicien	+212620366828	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	76046856-66cd-4461-bdf2-80153ef0ec86	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00145	Mustapha	Yakine	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	19 Rue Atlas	Quartier Al Wifaq	Boujniba	32.8923749	-6.9332499	\N	\N	\N	\N	f	Agent de maîtrise	+212617508773	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	2a7d35e0-26c4-4c02-9337-9cc4a58b1020	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00146	Ali	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	144 Rue Al Massira	Quartier Anassi	Boulanoir	32.8406207	-6.8021981	\N	\N	\N	\N	f	Électricien	+212619998115	Transport	f	personal_car	Non	t	f	0	t	\N	\N	\N	85cfc935-1de5-43be-9801-84c4aa16d980	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00147	Naima	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	P3	149 Rue Hassan II	Quartier Centre	Oued Zem	32.8603868	-6.565574	\N	\N	\N	\N	f	Superviseur	+212632955310	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	5428f0b7-8867-4f52-95ea-16a0e450c27f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00148	Fouad	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	15 Rue Hassan II	Quartier Anassi	Hattane	32.869414	-6.9155982	\N	\N	\N	\N	f	Conducteur	+212661517694	Production	f	taxi	Non	t	f	0	t	\N	\N	\N	50ccc32f-a653-4d45-9f98-2755bc48ac5b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00149	Tariq	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	102 Rue Atlas	Quartier Tamaris	Hattane	32.9023006	-6.6768527	\N	\N	\N	\N	f	Mécanicien	+212669105515	Sécurité	f	taxi	Non	t	f	0	t	\N	\N	\N	ef118fb3-138a-4a1b-92dc-32daea63c03a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00150	Malika	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P1	1 Rue des Orangers	Quartier Hay Salam	Boujniba	32.9052168	-6.6797041	\N	\N	\N	\N	f	Logisticien	+212659926988	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	c1e28bdb-8c95-4e25-bea9-fccb2c73e70e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00151	Ibrahim	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	90 Rue Hassan II	Quartier Al Wifaq	Boujniba	32.8938481	-6.9256304	\N	\N	\N	\N	f	Administratif	+212610369206	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	5dadc178-70dc-4bfb-8efa-6c91c13ae366	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00152	Najat	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	29 Rue des Orangers	Quartier Anassi	Boujniba	32.8968796	-6.7761105	\N	\N	\N	\N	f	Analyste	+212615254752	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	d56c544c-7e00-4cf1-8937-6829a01e479d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00153	Meryem	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	N	189 Rue Ifrane	Quartier Al Amal	Gueffaf	32.9215823	-6.7223776	\N	\N	\N	\N	f	Opérateur	+212663519095	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	f14238f5-ffc3-4aab-a114-6f19c9200300	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00154	Anass	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	82 Rue Al Massira	Quartier Tamaris	Boujniba	32.8770772	-6.9128337	\N	\N	\N	\N	f	Agent de maîtrise	+212699018229	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	251c6301-416e-44df-b2ad-d9eccbe0a143	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00155	Fatima	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	145 Rue des Orangers	Quartier Hassania	Boulanoir	32.9234933	-6.7171987	\N	\N	\N	\N	f	Mécanicien	+212665831794	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	ff203c09-bb3a-42cd-9e26-62a9f8f0142d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00156	Mustapha	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	53 Rue Hassan II	Quartier Tamaris	Boulanoir	32.8574891	-6.5537542	\N	\N	\N	\N	f	Sécurité	+212629226310	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	6b0c22fa-65e5-45fb-8222-8036755cc237	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00157	Kawtar	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	178 Rue Mohammed V	Quartier Hassania	Oued Zem	32.8586174	-6.909486	\N	\N	\N	\N	f	Opérateur	+212694169339	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	52b24c38-f759-4cdd-9aae-aa7a518b8d46	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00158	Hafida	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	108 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8607271	-6.5534428	\N	\N	\N	\N	f	Logisticien	+212692721395	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	ea1a34e4-a176-4edc-9e33-359a1174f8a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00159	Khalid	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	S	17 Rue Mohammed V	Quartier Centre	Hattane	32.8995591	-6.9355651	\N	\N	\N	\N	f	Technicien	+212638680047	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	e49df7e6-0fae-410c-90db-6271fbdda6da	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00160	Houda	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	184 Rue Ifrane	Quartier Centre	Oued Zem	32.852244	-6.5685041	\N	\N	\N	\N	f	Comptable	+212638230126	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	de4711d0-947f-4f57-8149-fc7c0a9110c3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00161	Sanaa	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	174 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8722526	-6.9074909	\N	\N	\N	\N	f	Analyste	+212637928415	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	38f87330-3294-4e5e-b6e2-76dc2e5e551e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00162	Kawtar	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	7 Rue de la Paix	Quartier Anassi	Khouribga	32.8585925	-6.5567722	\N	\N	\N	\N	f	Mécanicien	+212646603163	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	695d5d2d-d04b-44e5-81c6-febecfce4314	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00163	Zineb	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	21 Rue Mohammed V	Quartier Al Wifaq	Oued Zem	32.8536604	-6.5662814	\N	\N	\N	\N	f	Qualité	+212637534475	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	caaea6e0-1623-4aee-9da4-a8ec6ec11bce	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00164	Hamza	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	63 Rue Mohammed V	Quartier Medersa	Bir Mezoui	32.89278	-6.9309852	\N	\N	\N	\N	f	Mécanicien	+212659972215	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	866cbf53-feb4-4f15-8dd8-6bf0dcdd44ad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00165	Ilham	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	21 Rue Mohammed V	Quartier Medersa	Oued Zem	32.8716804	-6.9224636	\N	\N	\N	\N	f	Agent de maîtrise	+212681137211	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	fa33febd-2ab8-4478-9e26-871e6557fbac	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00166	Issam	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	25 Rue Ifrane	Quartier Al Amal	Boujniba	32.86746	-6.5841917	\N	\N	\N	\N	f	Conducteur	+212617763580	Transport	f	walk	Non	t	f	0	t	\N	\N	\N	6c0ddb85-72d2-4f90-a708-abdef9a750a3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00167	Youssef	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	164 Rue Atlas	Quartier Centre	Hattane	32.8579697	-6.573798	\N	\N	\N	\N	f	Analyste	+212644882698	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	d11f8e96-ae8c-4286-9fd3-7008194befab	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00168	Omar	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	79 Rue de la Paix	Quartier Hay Salam	Khouribga	32.8935819	-6.7720679	\N	\N	\N	\N	f	RH	+212656436595	Transport	f	taxi	Non	t	f	0	t	\N	\N	\N	0a8e9726-bfdf-4187-86ac-f4f67a099477	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00169	Soumia	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	87 Rue Ifrane	Quartier Hay Mohammadi	Gueffaf	32.8658633	-6.5824701	\N	\N	\N	\N	f	Technicien	+212680934182	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	f1d0dce9-6150-4136-aa4c-b239d9488b6a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00170	Khalid	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	82 Rue Al Massira	Quartier Al Amal	Boulanoir	32.8723515	-6.9095024	\N	\N	\N	\N	f	Technicien	+212667689750	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	7c98ce7e-9e13-49c0-9a30-976bfc3610dd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00171	Bouchra	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	106 Rue Mohammed V	Quartier Centre	Khouribga	32.9014713	-6.9039707	\N	\N	\N	\N	f	Sécurité	+212670790984	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	d0ebfbd2-159b-4c71-86fa-83b3b3ee4cec	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00172	Houda	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	157 Rue Hassan II	Quartier Anassi	Oued Zem	32.8407892	-6.8049693	\N	\N	\N	\N	f	Comptable	+212677503191	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	5bae135b-d3e3-4c76-afd6-5b0672cca30b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00173	Issam	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	118 Rue de la Paix	Quartier Medersa	Bir Mezoui	32.8934418	-6.9025119	\N	\N	\N	\N	f	Logisticien	+212616479346	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	94c400fd-a623-4f27-810a-8f583c426143	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00174	Anass	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	S	34 Rue Ifrane	Quartier Medersa	Oued Zem	32.8889749	-6.9316579	\N	\N	\N	\N	f	Technicien	+212683091422	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	efd46c48-0e70-4f58-a14f-68226326c42e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00175	Hasnaa	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	97 Rue Ifrane	Quartier Al Amal	Khouribga	32.8839129	-6.9016272	\N	\N	\N	\N	f	Conducteur	+212689470639	Production	f	walk	Non	t	f	0	t	\N	\N	\N	d39c085b-3289-415a-adfd-cb050e9564aa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00176	Hasnaa	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	33 Rue Hassan II	Quartier Hay Salam	Boujniba	32.848494	-6.8735318	\N	\N	\N	\N	f	Administratif	+212666422061	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	4c5aad99-ac5f-46da-b083-87926766056e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00177	Laila	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	115 Rue Ifrane	Quartier Centre	Gueffaf	32.8603793	-6.5675173	\N	\N	\N	\N	f	Administratif	+212617810948	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	0d978fa3-52c6-4012-a70d-8f210271f5a9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00178	Houda	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	148 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.8535549	-6.8793731	\N	\N	\N	\N	f	Technicien	+212682578234	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	ef8941fc-ca49-4e27-9f00-c73e0773e282	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00179	Ali	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	112 Rue Atlas	Quartier Centre	Bir Mezoui	32.90453	-6.7841865	\N	\N	\N	\N	f	Mécanicien	+212694382263	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	b6e7e777-e93f-49f0-86be-6adb79cd808d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00180	Siham	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	188 Rue des Orangers	Quartier Anassi	Boulanoir	32.8571031	-6.8795184	\N	\N	\N	\N	f	Sécurité	+212686797153	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	2cdc09b9-48fd-4b98-89f9-ddb4425bb64a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00181	Karim	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	173 Rue Atlas	Quartier Hassania	Gueffaf	32.9031528	-6.7790861	\N	\N	\N	\N	f	Sécurité	+212637144746	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	19e3d019-38b7-4f09-9786-908a6f5fca0d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00182	Jawad	Mouttaki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	195 Rue Mohammed V	Quartier Al Wifaq	Khouribga	32.9003813	-6.6840136	\N	\N	\N	\N	f	Agent de maîtrise	+212638383195	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	38d091bd-5442-47cf-b8e3-9a84356ec78e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00183	Meryem	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	N	109 Rue Mohammed V	Quartier Hay Mohammadi	Hattane	32.8778035	-6.9037359	\N	\N	\N	\N	f	Opérateur	+212673489602	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	f4ee6fa9-73b7-4564-b80e-5c1b55d31552	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00184	Hicham	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	132 Rue des Orangers	Quartier Tamaris	Oued Zem	32.8645663	-6.5645618	\N	\N	\N	\N	f	RH	+212683789250	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	09379dd6-1776-4ee6-9cd1-b57be78881ff	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00185	Bouchra	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	21 Rue des Orangers	Quartier Al Amal	Bir Mezoui	32.8813612	-6.8992773	\N	\N	\N	\N	f	Opérateur	+212647123999	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	8c03d983-7f81-474b-8aea-c171a2ed9472	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00186	Bilal	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	P2	90 Rue des Orangers	Quartier Al Wifaq	Bir Mezoui	32.8625646	-6.5488673	\N	\N	\N	\N	f	Électricien	+212653054247	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	5cb8ecd2-15a3-451c-a960-2fe44aa8370c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00187	Rachid	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	108 Rue de la Paix	Quartier Al Amal	Boujniba	32.9008429	-6.7841116	\N	\N	\N	\N	f	Technicien	+212676028450	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	008a9cfd-b523-4ddb-a9e0-e0c3984f39b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00188	Hasnaa	Zemmouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	138 Rue Atlas	Quartier Hay Mohammadi	Hattane	32.8577676	-6.5767242	\N	\N	\N	\N	f	Logisticien	+212657726082	RH	f	walk	Non	t	f	0	t	\N	\N	\N	b6a20e8e-5ce9-4d46-9bf8-fba44c508104	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00189	Naima	Laroui	d39d79ec-a716-4839-a93d-1845d00c182c	S	69 Rue Hassan II	Quartier Hassania	Hattane	32.8593194	-6.9075802	\N	\N	\N	\N	f	Mécanicien	+212643704516	Production	f	walk	Non	t	f	0	t	\N	\N	\N	93264ca5-7533-4151-b286-749ece408b96	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00190	Hassan	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	30 Rue de la Paix	Quartier Medersa	Gueffaf	32.8922719	-6.7720887	\N	\N	\N	\N	f	Administratif	+212616461695	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	6ef4c068-4ea3-4c73-80fd-e0c51caedab3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00191	Soumia	Chaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	23 Rue Atlas	Quartier Tamaris	Khouribga	32.8539556	-6.5777989	\N	\N	\N	\N	f	Analyste	+212694429340	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	87af31f2-cea4-4bed-a718-9ceb07289aa9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00192	Siham	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	33 Rue des Orangers	Quartier Hay Mohammadi	Khouribga	32.8784688	-6.9085845	\N	\N	\N	\N	f	Analyste	+212646402757	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	62708711-2fa3-4551-90be-5129bcf0a94d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00193	Soufiane	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	18 Rue des Orangers	Quartier Anassi	Bir Mezoui	32.9012945	-6.6757024	\N	\N	\N	\N	t	Opérateur	+212614215129	Transport	f	personal_car	Non	t	f	0	t	\N	\N	\N	63299800-c031-4aba-bb06-03bd7d7ad453	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00194	Samira	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	71 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.8755307	-6.9146565	\N	\N	\N	\N	f	Sécurité	+212690109322	Transport	f	motorcycle	Non	t	f	0	t	\N	\N	\N	19f5e833-d774-44a5-9d28-a6407e96c992	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00195	Siham	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P1	146 Rue Mohammed V	Quartier Centre	Boujniba	32.853177	-6.5795255	\N	\N	\N	\N	f	Qualité	+212687386825	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	4ca09792-a618-404f-86c9-924f3f8ca92f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00196	Amina	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	38 Rue des Orangers	Quartier Hay Mohammadi	Gueffaf	32.8879938	-6.9304646	\N	\N	\N	\N	f	Électricien	+212619084122	Qualité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	a768f886-dcb1-4736-8eb6-39537734bb48	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00197	Hanane	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	190 Rue Ifrane	Quartier Tamaris	Boulanoir	32.8647049	-6.9088693	\N	\N	\N	\N	f	Qualité	+212676719061	Qualité	f	taxi	Non	t	f	0	t	\N	\N	\N	809f0b11-31d4-4e0b-8422-7ae7e6e94331	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00198	Nadia	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	N	34 Rue Mohammed V	Quartier Hay Mohammadi	Bir Mezoui	32.9032644	-6.7697689	\N	\N	\N	\N	f	Électricien	+212678284707	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	1a0098d6-5ede-425e-a3c4-f6057e965eb3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00199	Karim	Yakine	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	79 Rue Mohammed V	Quartier Hay Salam	Bir Mezoui	32.8680303	-6.5843633	\N	\N	\N	\N	f	Logisticien	+212623129180	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	0c025cab-1496-4cb5-b6f9-10b0c9a0c8a1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00200	Mehdi	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	57 Rue des Orangers	Quartier Hassania	Boulanoir	32.8658569	-6.9047753	\N	\N	\N	\N	t	Conducteur	+212663403597	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	8fcb49ee-4161-453c-b2d2-17ec7f9ea988	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00201	Mohammed	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	188 Rue des Orangers	Quartier Hay Mohammadi	Hattane	32.903245	-6.7730265	\N	\N	\N	\N	f	RH	+212614384514	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	b5acf770-f51b-4998-a0c5-96de3cf4868e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00202	Najat	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	184 Rue de la Paix	Quartier Tamaris	Boujniba	32.9078142	-6.7811948	\N	\N	\N	\N	f	Superviseur	+212612828849	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	259365ee-33dd-40d5-a4b6-4cb56b257965	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00203	Khadija	Benomar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	7 Rue Ifrane	Quartier Al Amal	Boulanoir	32.8788658	-6.9015103	\N	\N	\N	\N	f	Analyste	+212658697560	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	359cbe6c-3a0e-490e-841e-5983b8bbae08	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00204	Hanane	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	S	127 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8910686	-6.9285015	\N	\N	\N	\N	f	Sécurité	+212635438485	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	815f67e9-0992-49b1-8543-2992561a14c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00205	Noureddine	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	80 Rue de la Paix	Quartier Hay Mohammadi	Boujniba	32.9033715	-6.7782917	\N	\N	\N	\N	f	Superviseur	+212684678276	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	e77efd43-d89c-4619-b3d1-9e212d9de3a1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00206	Bouchra	Qasmi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	71 Rue Ifrane	Quartier Hassania	Gueffaf	32.859327	-6.5493535	\N	\N	\N	\N	f	Ingénieur	+212681238941	Production	f	walk	Non	t	f	0	t	\N	\N	\N	d40820fa-6fb2-4383-ad02-9a7d3ec617db	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00207	Ibrahim	El Kabbaj	d39d79ec-a716-4839-a93d-1845d00c182c	P3	60 Rue de la Paix	Quartier Hay Mohammadi	Oued Zem	32.9034562	-6.7705717	\N	\N	\N	\N	f	Administratif	+212611272239	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	75fb9229-d1df-4ef1-a9ea-24f90f7d59cb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00208	Ali	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	61 Rue des Orangers	Quartier Tamaris	Boujniba	32.8617231	-6.5694227	\N	\N	\N	\N	f	Logisticien	+212698477476	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	59c57032-e653-4aaf-9889-c4ecf045ac27	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00209	Tariq	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	148 Rue Hassan II	Quartier Al Wifaq	Khouribga	32.8843018	-6.9324056	\N	\N	\N	\N	f	Mécanicien	+212650222191	Production	f	walk	Non	t	f	0	t	\N	\N	\N	9246ece4-caf5-496e-972a-c207c5c185a6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00210	Amine	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	180 Rue de la Paix	Quartier Hassania	Khouribga	32.924283	-6.7147109	\N	\N	\N	\N	f	Sécurité	+212642231070	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	5fca6958-4f98-4af5-9c0f-cd5bfff71bb6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00211	Zineb	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	180 Rue Hassan II	Quartier Centre	Boulanoir	32.8720782	-6.9048908	\N	\N	\N	\N	f	Technicien	+212624819306	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	e128edb1-327e-4be4-b40d-240e98cd70f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00212	Amina	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	138 Rue Mohammed V	Quartier Al Wifaq	Boujniba	32.8757405	-6.9098655	\N	\N	\N	\N	f	Agent de maîtrise	+212640062973	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	d0a94fd9-83a5-4280-a198-286d6d68296b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00213	Nadia	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	N	162 Rue des Orangers	Quartier Hay Salam	Boujniba	32.8730939	-6.9092301	\N	\N	\N	\N	f	Ingénieur	+212698706647	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	cee1fb74-1058-4c4c-84d4-7743b5cc57f6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00214	Bouchra	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	139 Rue Al Massira	Quartier Medersa	Bir Mezoui	32.8526423	-6.8814417	\N	\N	\N	\N	f	Logisticien	+212695578212	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	8d1c23e7-a244-4766-a8f4-2779a0e1783c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00215	Najat	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	171 Rue Ifrane	Quartier Tamaris	Gueffaf	32.8618129	-6.5795038	\N	\N	\N	\N	f	Qualité	+212664678201	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	c9c69125-2ffc-402b-854e-b666de313608	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00216	Loubna	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P2	3 Rue Al Massira	Quartier Anassi	Bir Mezoui	32.8940266	-6.7847327	\N	\N	\N	\N	f	Ingénieur	+212635746579	RH	f	walk	Non	t	f	0	t	\N	\N	\N	16a449c3-8645-4d93-9a7f-3cca74e02e4f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00217	Rajaa	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	29 Rue des Orangers	Quartier Hay Salam	Gueffaf	32.8408591	-6.8003439	\N	\N	\N	\N	f	Ingénieur	+212617851143	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	e109f306-55ab-490e-b59b-c5c33cd6922c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00218	Ibrahim	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	93 Rue Ifrane	Quartier Al Amal	Khouribga	32.8891473	-6.9303981	\N	\N	\N	\N	f	Technicien	+212697403446	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	3c1347e6-5f86-44cc-b06d-c7d368a512dc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00219	Hamza	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	S	163 Rue des Orangers	Quartier Medersa	Boulanoir	32.9003725	-6.9355436	\N	\N	\N	\N	f	Analyste	+212627104549	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	882f38f1-944e-474a-be36-d9478f8913c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00220	Mohammed	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	44 Rue Ifrane	Quartier Al Wifaq	Khouribga	32.8739126	-6.9104551	\N	\N	\N	\N	f	Administratif	+212621869178	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	b71e3009-6cde-4c2b-a497-62e737c0472a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00221	Adil	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	90 Rue Atlas	Quartier Al Amal	Khouribga	32.8391558	-6.8045913	\N	\N	\N	\N	f	Mécanicien	+212653431468	Maintenance	f	walk	Non	t	f	0	t	\N	\N	\N	3391933d-8bd5-43c3-b451-7e17680db99e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00222	Ahmed	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	109 Rue Ifrane	Quartier Centre	Khouribga	32.8690541	-6.9124649	\N	\N	\N	\N	t	Administratif	+212618035937	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	d6aaa11e-4b41-4262-9dae-e5d4ed31b65e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00223	Hanane	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	142 Rue Mohammed V	Quartier Tamaris	Gueffaf	32.8626072	-6.5836293	\N	\N	\N	\N	f	Comptable	+212635147610	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	5f519f16-067c-4dda-bea1-6d27f19cdd85	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00224	Laila	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	192 Rue Mohammed V	Quartier Al Amal	Bir Mezoui	32.9005835	-6.9046886	\N	\N	\N	\N	f	Opérateur	+212627568202	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	649e84f5-5688-448a-82f5-2386a0ebb978	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00225	Najat	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	84 Rue Atlas	Quartier Centre	Bir Mezoui	32.8808977	-6.9200954	\N	\N	\N	\N	f	Logisticien	+212632397621	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	074f4322-6e1a-4345-be11-5b3f8342adeb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00226	Kawtar	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	81 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.8930711	-6.779311	\N	\N	\N	\N	f	Conducteur	+212615323577	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	746e6040-1329-4740-b544-1446d23be776	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00227	Soumia	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	147 Rue Ifrane	Quartier Centre	Oued Zem	32.8728576	-6.9073788	\N	\N	\N	\N	f	Sécurité	+212697265381	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	f04c78d0-eddd-4a62-b1b7-586dd568d388	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00228	Wafae	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	N	161 Rue de la Paix	Quartier Medersa	Gueffaf	32.8736423	-6.9254521	\N	\N	\N	\N	f	Mécanicien	+212612060212	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	bacdae55-8442-4024-8920-73bcbce3d29c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00229	Adil	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	46 Rue des Orangers	Quartier Anassi	Boujniba	32.9041538	-6.6768879	\N	\N	\N	\N	f	Agent de maîtrise	+212651562432	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	c55a56ab-93bd-4d52-8f53-53b249ed49a4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00230	Ahmed	Benomar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	146 Rue Hassan II	Quartier Al Amal	Khouribga	32.8634981	-6.581089	\N	\N	\N	\N	f	Opérateur	+212697003078	Production	f	walk	Non	t	f	0	t	\N	\N	\N	58bb5bc8-a236-46cb-af7a-27e3ac230649	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00231	Latifa	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P2	37 Rue Mohammed V	Quartier Hassania	Boujniba	32.8952217	-6.9408654	\N	\N	\N	\N	f	Technicien	+212688690419	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	20645a38-ca95-436d-9e8d-54d78067984e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00232	Ahmed	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	44 Rue des Orangers	Quartier Al Amal	Gueffaf	32.896287	-6.780302	\N	\N	\N	\N	f	Technicien	+212670755178	RH	f	walk	Non	t	f	0	t	\N	\N	\N	ae1ccf45-06ac-424c-ad9e-4785770eaaa6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00233	Naima	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	122 Rue de la Paix	Quartier Hassania	Bir Mezoui	32.8989659	-6.7764301	\N	\N	\N	\N	f	Électricien	+212672288625	Finance	f	taxi	Non	t	f	0	t	\N	\N	\N	2426b670-8e99-4923-93ec-fa6000772e1f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00234	Wafae	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	S	102 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.9071921	-6.7861574	\N	\N	\N	\N	f	Agent de maîtrise	+212691859317	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	890129af-0dfd-4874-90a9-c230422717fe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00235	Mehdi	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	189 Rue de la Paix	Quartier Tamaris	Hattane	32.8793568	-6.8987228	\N	\N	\N	\N	f	Opérateur	+212668557118	Production	f	walk	Non	t	f	0	t	\N	\N	\N	690cbaa6-34ff-4703-9c1b-fe7ad486964b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00236	Wafae	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	98 Rue Mohammed V	Quartier Tamaris	Khouribga	32.8609288	-6.5692007	\N	\N	\N	\N	f	Sécurité	+212644536798	RH	f	walk	Non	t	f	0	t	\N	\N	\N	b8052315-aee6-4319-8e7b-31f7ab89a66e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00237	Anass	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	P3	116 Rue de la Paix	Quartier Centre	Boujniba	32.8619534	-6.5838604	\N	\N	\N	\N	f	Électricien	+212669018801	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	f57f7af6-bdb5-481d-a491-90ba8b0416ff	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00238	Zineb	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	173 Rue Atlas	Quartier Hay Mohammadi	Hattane	32.9029221	-6.771076	\N	\N	\N	\N	f	Conducteur	+212652736660	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	4b434723-beb6-4161-9f5c-80df87b0b17d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00239	Jawad	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	149 Rue Atlas	Quartier Medersa	Boujniba	32.8655009	-6.9195067	\N	\N	\N	\N	f	RH	+212613598858	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	a26dd641-884b-4bfb-b885-735270191be3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00240	Adil	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P1	190 Rue de la Paix	Quartier Hassania	Boulanoir	32.8685382	-6.9072146	\N	\N	\N	\N	f	Électricien	+212676929679	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	fb30a0c5-9619-4ddb-9e79-8b92d1ff0da5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00241	Meryem	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	114 Rue Ifrane	Quartier Al Wifaq	Oued Zem	32.8736431	-6.9262296	\N	\N	\N	\N	f	Logisticien	+212672173128	Sécurité	f	personal_car	Non	t	f	0	t	\N	\N	\N	88a3a0be-a5ee-43d5-a9e3-c8087051f638	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00242	Samira	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	89 Rue Ifrane	Quartier Medersa	Khouribga	32.8860659	-6.9076764	\N	\N	\N	\N	f	Électricien	+212670861866	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	a8870590-c830-48ce-b220-70e6e0db8f82	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00243	Nadia	Laaroussi	d39d79ec-a716-4839-a93d-1845d00c182c	N	46 Rue Hassan II	Quartier Hay Salam	Boujniba	32.877428	-6.91508	\N	\N	\N	\N	f	Superviseur	+212687934654	Administration	f	personal_car	Non	t	f	0	t	\N	\N	\N	a07a10f0-f82b-43bb-8df1-bb84866b7a21	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00244	Amina	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	79 Rue Mohammed V	Quartier Anassi	Bir Mezoui	32.8823961	-6.9177781	\N	\N	\N	\N	f	Comptable	+212686645228	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	7ae1e58e-1708-4cc1-9c58-f84105015514	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00245	Amine	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	77 Rue Atlas	Quartier Tamaris	Khouribga	32.8567047	-6.5589149	\N	\N	\N	\N	f	Logisticien	+212662984865	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	ab400f63-6a3b-4915-877d-f8cdcae103f8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00246	Lahcen	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P2	36 Rue Ifrane	Quartier Medersa	Oued Zem	32.9022312	-6.6799889	\N	\N	\N	\N	f	Opérateur	+212640833527	Administration	f	motorcycle	Non	t	f	0	t	\N	\N	\N	29b9c94d-6b6e-4e8d-83ff-9085636bf5af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00247	Samira	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	107 Rue de la Paix	Quartier Medersa	Khouribga	32.9011427	-6.9324342	\N	\N	\N	\N	f	Superviseur	+212662172619	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	8d86c28d-77dc-433a-9051-107afcafd2be	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00248	Fouad	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	192 Rue Mohammed V	Quartier Al Wifaq	Hattane	32.9012492	-6.679645	\N	\N	\N	\N	t	Agent de maîtrise	+212634894223	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	cdf8ecdd-761d-45f4-886c-0642a3e028b0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00249	Fatima	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	S	177 Rue Al Massira	Quartier Anassi	Boulanoir	32.8933007	-6.936846	\N	\N	\N	\N	f	Superviseur	+212610771506	Finance	f	taxi	Non	t	f	0	t	\N	\N	\N	8f1b05c4-5d6b-47fa-9656-b38d0ce328b2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00250	Tariq	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	91 Rue Mohammed V	Quartier Al Amal	Khouribga	32.8828674	-6.9178171	\N	\N	\N	\N	f	Comptable	+212663698456	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	72ce3859-2e3a-447e-a76d-30200f2c756f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00251	Nadia	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	16 Rue Mohammed V	Quartier Centre	Khouribga	32.8938852	-6.7726273	\N	\N	\N	\N	f	Logisticien	+212677596872	Finance	f	taxi	Non	t	f	0	t	\N	\N	\N	d0dee275-452b-4b98-bef1-17d3588d5822	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00252	Meryem	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	9 Rue Atlas	Quartier Centre	Boujniba	32.8995592	-6.9335114	\N	\N	\N	\N	f	Qualité	+212633387412	Qualité	f	personal_car	Non	t	f	0	t	\N	\N	\N	b516e846-3d11-428f-8870-0ad806f6378d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00253	Driss	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	196 Rue des Orangers	Quartier Anassi	Bir Mezoui	32.8444283	-6.7961766	\N	\N	\N	\N	f	Électricien	+212633556784	Informatique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	fd013887-42b3-4c93-8bfc-e0e3fddc4f49	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00254	Fatima	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	82 Rue de la Paix	Quartier Anassi	Boujniba	32.8758361	-6.9140519	\N	\N	\N	\N	f	Conducteur	+212631936856	Qualité	f	taxi	Non	t	f	0	t	\N	\N	\N	57d1d315-2da2-4769-a7a2-a3549f4beb92	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00255	Mehdi	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	102 Rue Ifrane	Quartier Al Wifaq	Bir Mezoui	32.9042341	-6.7714852	\N	\N	\N	\N	f	Conducteur	+212677032242	Qualité	f	personal_car	Non	t	f	0	t	\N	\N	\N	7065af31-3723-44d2-842e-28355022c6af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00256	Loubna	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	163 Rue des Orangers	Quartier Hay Salam	Gueffaf	32.9052525	-6.7815806	\N	\N	\N	\N	f	Logisticien	+212634684305	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	870ffdd0-c237-4430-91d2-979e24827d92	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00257	Bouchra	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	77 Rue Ifrane	Quartier Hay Mohammadi	Hattane	32.8891404	-6.9304689	\N	\N	\N	\N	t	Ingénieur	+212645057327	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	86e06c7b-2a63-45a2-a7d9-b84eebc9a73f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00258	Noureddine	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	N	94 Rue Atlas	Quartier Medersa	Hattane	32.8412026	-6.7970408	\N	\N	\N	\N	f	Agent de maîtrise	+212671277372	Maintenance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	80cf042e-825b-424a-b313-9a4371401598	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00259	Khalid	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	185 Rue Mohammed V	Quartier Anassi	Oued Zem	32.8648457	-6.9123736	\N	\N	\N	\N	f	Sécurité	+212633444828	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	fd0896d0-e2b1-4835-8321-1701d9928ac4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00260	Souad	Chaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	156 Rue Al Massira	Quartier Anassi	Oued Zem	32.8867944	-6.9275065	\N	\N	\N	\N	f	Mécanicien	+212688131703	Production	f	walk	Non	t	f	0	t	\N	\N	\N	a275f40f-6238-492e-b3c8-825135bdfa2c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00261	Hassan	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	77 Rue de la Paix	Quartier Anassi	Boujniba	32.8559895	-6.5747133	\N	\N	\N	\N	f	RH	+212621955014	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	3fbe6377-5ea6-4005-9a6a-b6e423d3b5d7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00262	Mohammed	Hassouni	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	145 Rue Atlas	Quartier Anassi	Hattane	32.9033451	-6.7856507	\N	\N	\N	\N	f	Superviseur	+212698017263	Transport	f	personal_car	Non	t	f	0	t	\N	\N	\N	c4ae5758-f16c-4cac-833d-96b18d7b2f5d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00263	Ghita	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	35 Rue Hassan II	Quartier Hay Mohammadi	Bir Mezoui	32.8401373	-6.8032697	\N	\N	\N	\N	f	Logisticien	+212640190702	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	ee11624d-18ee-43c1-b5d6-8d2205648742	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00264	Hamza	Slaoui	d39d79ec-a716-4839-a93d-1845d00c182c	S	191 Rue Atlas	Quartier Al Wifaq	Hattane	32.8657772	-6.5687937	\N	\N	\N	\N	f	Mécanicien	+212647815045	Production	f	taxi	Non	t	f	0	t	\N	\N	\N	b2f68155-7040-4f7b-bc54-f8341f78eb3d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00265	Ibrahim	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	153 Rue Al Massira	Quartier Medersa	Khouribga	32.90732	-6.7830242	\N	\N	\N	\N	f	Mécanicien	+212669608088	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	56f75d99-121b-4272-93f7-6fe292587702	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00266	Rajaa	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	122 Rue des Orangers	Quartier Centre	Gueffaf	32.9225338	-6.720955	\N	\N	\N	\N	f	Comptable	+212696394771	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	a91e622f-fa5c-46fd-97db-5f59805bfaa5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00267	Jawad	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	115 Rue de la Paix	Quartier Al Amal	Hattane	32.8747647	-6.9226654	\N	\N	\N	\N	f	Analyste	+212698969675	Production	f	walk	Non	t	f	0	t	\N	\N	\N	f2393ac2-2990-4075-986c-8014373fe2bc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00268	Hanane	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	56 Rue Hassan II	Quartier Anassi	Hattane	32.8916398	-6.9148837	\N	\N	\N	\N	f	Logisticien	+212660939290	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	b0b0fe95-64a2-458b-91dd-eaa67ea080f2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00269	Soufiane	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	24 Rue de la Paix	Quartier Medersa	Gueffaf	32.8625047	-6.905414	\N	\N	\N	\N	f	Superviseur	+212684260738	Finance	f	walk	Non	t	f	0	t	\N	\N	\N	61c21840-ff5e-40f0-a34b-1666b06f4443	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00270	Khalid	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	105 Rue Atlas	Quartier Hay Salam	Boulanoir	32.9017514	-6.7737372	\N	\N	\N	\N	f	RH	+212614603988	Administration	f	taxi	Non	t	f	0	t	\N	\N	\N	3275a71e-1d2c-464a-bef0-9f7d0e84c4b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00271	Rajaa	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	34 Rue Al Massira	Quartier Anassi	Hattane	32.8758352	-6.9240239	\N	\N	\N	\N	f	Technicien	+212624012361	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	d8f87c8c-c376-46dc-9114-0a9932e97eec	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00272	Soumia	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	61 Rue Atlas	Quartier Al Amal	Boulanoir	32.8927626	-6.9002747	\N	\N	\N	\N	f	Qualité	+212636514851	Finance	f	personal_car	Non	t	f	0	t	\N	\N	\N	2b319a38-bcd5-4467-a0c1-5b48103c538c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00273	Ali	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	N	24 Rue Ifrane	Quartier Hay Mohammadi	Oued Zem	32.8766327	-6.9187659	\N	\N	\N	\N	f	Mécanicien	+212628627419	Production	f	personal_car	Non	t	f	0	t	\N	\N	\N	38b4704e-68e4-4a60-818a-3748b387989a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00274	Hafida	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	122 Rue des Orangers	Quartier Hassania	Gueffaf	32.9005171	-6.9354019	\N	\N	\N	\N	t	Comptable	+212685495649	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	cdc45b37-2ce2-492b-a83a-9ca7d211d6df	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00275	Khalid	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	190 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8885905	-6.8916954	\N	\N	\N	\N	f	Superviseur	+212677861926	Production	f	motorcycle	Non	t	f	0	t	\N	\N	\N	dbc200b8-49dd-48e5-9c1a-6fb16ca30646	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00276	Abdelilah	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	20 Rue de la Paix	Quartier Anassi	Hattane	32.8982103	-6.9299461	\N	\N	\N	\N	f	Sécurité	+212666062777	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	f8917791-00c3-456d-bc82-18abaec9cea6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00277	Anass	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	44 Rue de la Paix	Quartier Hassania	Bir Mezoui	32.8838504	-6.9313601	\N	\N	\N	\N	f	Logisticien	+212686176926	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	bfda7d8c-97de-499a-9d3b-7067db511dcd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00278	Samira	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	141 Rue Ifrane	Quartier Centre	Hattane	32.8584663	-6.8706071	\N	\N	\N	\N	f	Qualité	+212615825691	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	58ca638c-7b3e-480a-88df-f10e727fb17f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00279	Ghita	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	S	143 Rue des Orangers	Quartier Centre	Khouribga	32.9215995	-6.7179776	\N	\N	\N	\N	f	Mécanicien	+212615233849	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	68f1edff-acab-4aa5-80f6-859cda9d59a6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00280	Noureddine	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	92 Rue Ifrane	Quartier Tamaris	Khouribga	32.836857	-6.8018466	\N	\N	\N	\N	f	Administratif	+212610707675	Administration	f	walk	Non	t	f	0	t	\N	\N	\N	7d519f95-ef48-459a-8b80-3f93e2a757e6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00281	Khadija	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	7 Rue Mohammed V	Quartier Tamaris	Hattane	32.8862024	-6.9021491	\N	\N	\N	\N	f	Technicien	+212670625503	Logistique	f	motorcycle	Non	t	f	0	t	\N	\N	\N	2fceab3a-4d9a-4234-9ce9-708ee433f7af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00282	Soufiane	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P3	186 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.8627784	-6.5779747	\N	\N	\N	\N	f	Électricien	+212699480260	Finance	f	taxi	Non	t	f	0	t	\N	\N	\N	c33f0095-a6b6-4e1e-9400-dc4d00591ee1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00283	Ibrahim	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	166 Rue Ifrane	Quartier Al Wifaq	Hattane	32.8976091	-6.7760684	\N	\N	\N	\N	f	Agent de maîtrise	+212632910922	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	3666a7b0-7765-4725-82c2-50743417caa3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00284	Adil	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	126 Rue Atlas	Quartier Hay Salam	Oued Zem	32.8517866	-6.5752619	\N	\N	\N	\N	f	Sécurité	+212671658837	Finance	f	motorcycle	Non	t	f	0	t	\N	\N	\N	0d4e0966-3960-4a90-8e5f-5d20c3e5e4fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00285	Lahcen	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	173 Rue des Orangers	Quartier Centre	Boujniba	32.8339757	-6.8031162	\N	\N	\N	\N	f	Comptable	+212616906124	Qualité	f	walk	Non	t	f	0	t	\N	\N	\N	b98347d8-a76b-492a-84a2-00e95a7411b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00286	Hicham	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	63 Rue Al Massira	Quartier Medersa	Bir Mezoui	32.8936286	-6.8955248	\N	\N	\N	\N	f	Superviseur	+212678155997	RH	f	motorcycle	Non	t	f	0	t	\N	\N	\N	a9ebbd4f-ce12-4d8d-8b00-5732093e091a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00287	Abdelilah	Ouazzani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	123 Rue des Orangers	Quartier Hassania	Khouribga	32.865807	-6.5815716	\N	\N	\N	\N	f	Conducteur	+212627526542	Logistique	f	walk	Non	t	f	0	t	\N	\N	\N	d5979616-e39d-48c0-86ed-fc7237730d12	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00288	Anass	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	N	88 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.885519	-6.917818	\N	\N	\N	\N	f	Mécanicien	+212630413255	Maintenance	f	personal_car	Non	t	f	0	t	\N	\N	\N	5302e42f-263b-41c3-adbf-5ac851d1279d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00289	Ilham	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	61 Rue Al Massira	Quartier Al Wifaq	Oued Zem	32.8663853	-6.5842723	\N	\N	\N	\N	f	Analyste	+212697261838	RH	f	personal_car	Non	t	f	0	t	\N	\N	\N	2597445a-d594-4867-ac60-7d36ba6d78fd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00290	Meryem	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	105 Rue Al Massira	Quartier Hay Mohammadi	Hattane	32.8558728	-6.5776193	\N	\N	\N	\N	f	Conducteur	+212670342515	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	34a35556-d2a0-43e6-a7f0-4f07a0c45610	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00291	Rajaa	Laroui	d39d79ec-a716-4839-a93d-1845d00c182c	P2	91 Rue de la Paix	Quartier Tamaris	Boulanoir	32.8644728	-6.9043533	\N	\N	\N	\N	f	Agent de maîtrise	+212644925953	Logistique	f	personal_car	Non	t	f	0	t	\N	\N	\N	e6a6c5dd-8e1f-49e3-a262-ebba07916f6e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00292	Fatima	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	50 Rue Al Massira	Quartier Tamaris	Boujniba	32.8571517	-6.8790959	\N	\N	\N	\N	f	Conducteur	+212638534904	Maintenance	f	taxi	Non	t	f	0	t	\N	\N	\N	5cd8c10b-d726-4afa-98ff-23fb22f7e931	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00293	Fouad	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	31 Rue des Orangers	Quartier Hay Mohammadi	Gueffaf	32.8807819	-6.9086982	\N	\N	\N	\N	f	RH	+212625244189	Logistique	f	taxi	Non	t	f	0	t	\N	\N	\N	a00c3a3e-d442-4237-a1f3-725a5ba1eacd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00294	Adil	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	S	53 Rue Ifrane	Quartier Al Amal	Hattane	32.8681465	-6.9083088	\N	\N	\N	\N	f	Agent de maîtrise	+212667096305	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	910c1362-7244-43ad-a14d-12df841baf03	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00295	Bouchra	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	1 Rue Al Massira	Quartier Hay Mohammadi	Khouribga	32.8643007	-6.5804166	\N	\N	\N	\N	f	Ingénieur	+212653118707	RH	f	taxi	Non	t	f	0	t	\N	\N	\N	df54ce1b-59d9-4b0e-bb7b-c0a36682176d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00296	Khadija	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	8 Rue de la Paix	Quartier Al Amal	Khouribga	32.8932384	-6.783175	\N	\N	\N	\N	f	Analyste	+212664498739	Informatique	f	walk	Non	t	f	0	t	\N	\N	\N	83443238-81fc-4383-811e-c7f85bcf899c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00297	Malika	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P3	6 Rue Ifrane	Quartier Hay Mohammadi	Khouribga	32.892743	-6.9308257	\N	\N	\N	\N	f	Comptable	+212696751390	Sécurité	f	motorcycle	Non	t	f	0	t	\N	\N	\N	936f1239-c781-4d9f-b329-9063287d9246	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00298	Jamila	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	168 Rue des Orangers	Quartier Centre	Boujniba	32.8987483	-6.7837835	\N	\N	\N	\N	f	Ingénieur	+212635107707	Transport	f	walk	Non	t	f	0	t	\N	\N	\N	ea649b0b-9a2e-4c54-b7bb-d5fa761760b7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00299	Jamila	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	180 Rue Al Massira	Quartier Hay Mohammadi	Oued Zem	32.8675283	-6.576967	\N	\N	\N	\N	f	Logisticien	+212631311978	Sécurité	f	walk	Non	t	f	0	t	\N	\N	\N	1b1f7c01-1cf4-4bc0-8e00-78970c898540	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00300	Bouchra	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P1	29 Rue de la Paix	Quartier Centre	Boujniba	32.8792681	-6.920715	\N	\N	\N	\N	f	Technicien	+212622240047	Informatique	f	taxi	Non	t	f	0	t	\N	\N	\N	f7573935-16cd-4704-b81d-6f2574e7a0a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	\N
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00301	Ahmed	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	150 Rue Ifrane	Quartier Hay Mohammadi	Hattane	32.8379607	-6.8053479	\N	\N	\N	\N	f	Superviseur	+212650401168	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fa352b22-ff30-4843-b8d8-129376418014	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00302	Soumia	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	48 Rue de la Paix	Quartier Hay Salam	Bir Mezoui	32.8999837	-6.7792461	\N	\N	\N	\N	f	Électricien	+212635354731	Finance	t	company_bus	Non	f	f	0	t	\N	\N	\N	5a7c2a82-fc07-41f6-b38b-32f4909e4270	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00303	Samira	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	N	78 Rue Atlas	Quartier Tamaris	Bir Mezoui	32.8766015	-6.9078258	\N	\N	\N	\N	f	Comptable	+212667028842	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ee4d01f8-fbb8-4f70-a2cb-aac10afadc52	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00304	Karim	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	79 Rue de la Paix	Quartier Hay Mohammadi	Khouribga	32.8983159	-6.7792152	\N	\N	\N	\N	f	Ingénieur	+212660898563	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a30371de-e850-4ce2-8a02-d4ec7b13ba5c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00305	Jamila	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	17 Rue Atlas	Quartier Al Amal	Khouribga	32.8905956	-6.9363466	\N	\N	\N	\N	f	Conducteur	+212683163934	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	987a1d2a-c410-4faa-981e-b6dc63d6eaf6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00306	Kawtar	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	149 Rue des Orangers	Quartier Tamaris	Bir Mezoui	32.8981964	-6.7749204	\N	\N	\N	\N	f	Opérateur	+212620866048	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4a1e4d95-acc5-4850-bc68-9fdab010f12e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00307	Najat	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	111 Rue Mohammed V	Quartier Tamaris	Gueffaf	32.871989	-6.9065314	\N	\N	\N	\N	f	Administratif	+212645545295	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	be3e548b-224c-4dbb-bdc7-87af6c12b00a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00308	Hamza	Sahraoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	13 Rue Mohammed V	Quartier Medersa	Boulanoir	32.8975023	-6.9055771	\N	\N	\N	\N	f	Électricien	+212655807958	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57aa9f00-7e93-4c06-9168-4816f4804428	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00309	Amina	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	S	43 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8941468	-6.9313675	\N	\N	\N	\N	f	Opérateur	+212680500624	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b07f1f5d-ef27-4e3a-8ee8-9ac143d62562	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00310	Noureddine	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	145 Rue Ifrane	Quartier Medersa	Hattane	32.8972069	-6.932347	\N	\N	\N	\N	f	Comptable	+212666800295	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	677e69d3-2693-490d-ab2e-fc8c2bcb9482	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00311	Soufiane	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	149 Rue Ifrane	Quartier Tamaris	Khouribga	32.8760519	-6.9035069	\N	\N	\N	\N	f	Qualité	+212626855642	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	546b494f-10cd-4e5d-9b8c-b2ece2a3a225	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00312	Ibrahim	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	178 Rue de la Paix	Quartier Al Wifaq	Boulanoir	32.8676136	-6.5808285	\N	\N	\N	\N	f	Comptable	+212670705714	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6047d4d8-966c-4aea-af4a-1e3629f8a481	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00313	Hamza	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	44 Rue des Orangers	Quartier Hassania	Bir Mezoui	32.9004062	-6.9046525	\N	\N	\N	\N	f	Logisticien	+212659057857	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	34925b4e-7f67-48cc-b442-2c3f250bf695	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00314	Lahcen	Sahraoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	168 Rue Al Massira	Quartier Tamaris	Oued Zem	32.8822318	-6.9332594	\N	\N	\N	\N	f	Administratif	+212613838901	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1555a994-97c9-427f-96f3-bb5f41a104e4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00315	Othmane	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	138 Rue Al Massira	Quartier Al Amal	Gueffaf	32.8919376	-6.8979114	\N	\N	\N	\N	t	Technicien	+212678971385	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e53e40ad-db39-4762-936b-2e4ee1f65aca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00316	Imane	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	50 Rue des Orangers	Quartier Hay Salam	Oued Zem	32.8588183	-6.5685223	\N	\N	\N	\N	f	RH	+212654244188	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	713d6f4e-5ae8-472c-8c34-e1b8bd12472e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00317	Souad	El Fassi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	90 Rue Mohammed V	Quartier Anassi	Oued Zem	32.8672544	-6.9127163	\N	\N	\N	\N	f	Sécurité	+212672659726	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a0657129-7045-4ac4-b192-f589aebf4c7a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00318	Anass	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	N	129 Rue Atlas	Quartier Hay Salam	Boulanoir	32.8658657	-6.5734586	\N	\N	\N	\N	f	Ingénieur	+212610387031	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7ae2060d-d450-4e5c-bf48-b7b7db1478a4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00319	Amine	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	122 Rue de la Paix	Quartier Anassi	Khouribga	32.8707906	-6.9245439	\N	\N	\N	\N	f	Qualité	+212665887363	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dfb9a17b-6e70-4a7d-a59c-c5b45d22a780	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00320	Bouchra	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	82 Rue de la Paix	Quartier Centre	Boujniba	32.9009363	-6.7701361	\N	\N	\N	\N	f	RH	+212617548765	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43bc4659-e6d3-4550-8181-a2a0d0888cfe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00321	Ali	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	45 Rue Hassan II	Quartier Anassi	Boujniba	32.8965446	-6.9332378	\N	\N	\N	\N	f	Électricien	+212686847249	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dbe9aba5-619b-4fda-afbc-7144404872eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00322	Hamza	Ouazzani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	163 Rue Ifrane	Quartier Al Amal	Boujniba	32.8380135	-6.8038497	\N	\N	\N	\N	f	Sécurité	+212648862381	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d0bbcc7b-4835-4d28-b3cd-fcdf2e049645	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00323	Karim	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	113 Rue Ifrane	Quartier Anassi	Boujniba	32.8578333	-6.5511758	\N	\N	\N	\N	f	Opérateur	+212610936378	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5575174f-8df7-4b4e-a291-ade3c6c831e9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00324	Anass	Talbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	117 Rue Mohammed V	Quartier Anassi	Boulanoir	32.8837551	-6.9035062	\N	\N	\N	\N	f	Analyste	+212672819841	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a662103-1919-4dba-805a-1604bdf268ca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00325	Jawad	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	102 Rue de la Paix	Quartier Hay Mohammadi	Khouribga	32.8464291	-6.800931	\N	\N	\N	\N	f	Comptable	+212677463753	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f43d440c-e81e-4ec3-9ff2-2596442f7785	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00326	Loubna	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	119 Rue Al Massira	Quartier Centre	Bir Mezoui	32.8796168	-6.9041817	\N	\N	\N	\N	f	Comptable	+212675572284	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2476ac3c-0df2-4b17-b1c3-4a33b30a4a3c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00327	Amina	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P3	60 Rue Atlas	Quartier Al Wifaq	Khouribga	32.8754329	-6.9202621	\N	\N	\N	\N	f	Technicien	+212638443895	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cd8c373e-b9f5-4b4e-828f-66f39b8e9d88	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00328	Abdelilah	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	111 Rue des Orangers	Quartier Medersa	Boujniba	32.8967413	-6.9315272	\N	\N	\N	\N	f	Superviseur	+212678383801	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1fdfc1bc-536f-496d-9aff-5ef592d00ae8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00329	Hanane	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	72 Rue Mohammed V	Quartier Al Wifaq	Khouribga	32.8937647	-6.9050102	\N	\N	\N	\N	f	Électricien	+212699917512	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ea752ec9-8e77-4497-bc53-6abe8ac4aaed	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00330	Ilham	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P1	89 Rue de la Paix	Quartier Anassi	Hattane	32.8505801	-6.5757988	\N	\N	\N	\N	f	Qualité	+212662329940	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d1994143-2e76-4050-bc8f-9e0e7e9cec48	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00331	Noureddine	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	24 Rue Al Massira	Quartier Medersa	Hattane	32.8597831	-6.5710849	\N	\N	\N	\N	f	Superviseur	+212693323288	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8d38cde1-5049-4fbf-a12e-8b7387c93bad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00332	Ali	Errahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	175 Rue Atlas	Quartier Anassi	Oued Zem	32.8765835	-6.9071518	\N	\N	\N	\N	f	Sécurité	+212694903416	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a302a8fe-c5f1-4acf-a3da-3286990e78ee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00333	Meryem	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	N	86 Rue Al Massira	Quartier Hay Salam	Bir Mezoui	32.9044306	-6.7814615	\N	\N	\N	\N	f	Mécanicien	+212634441884	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1a3c52e0-4d0f-47ed-b26d-5623b65fd3fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00334	Lahcen	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	76 Rue de la Paix	Quartier Hassania	Boulanoir	32.8765763	-6.9145611	\N	\N	\N	\N	f	Technicien	+212677375780	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	47583344-5da1-4e70-a32e-6701f859e084	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00335	Hicham	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	68 Rue Hassan II	Quartier Tamaris	Boujniba	32.8922008	-6.9274972	\N	\N	\N	\N	f	Ingénieur	+212666599455	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0e417a6b-5acc-4e3c-90f9-c27eaea0a027	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00336	Ilham	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	P2	196 Rue Ifrane	Quartier Centre	Oued Zem	32.8995242	-6.9299286	\N	\N	\N	\N	f	Qualité	+212683590996	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4ee0f237-2e1e-40ce-841a-309a8f9bb58b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00337	Samira	Hassouni	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	102 Rue Ifrane	Quartier Hay Mohammadi	Bir Mezoui	32.8967091	-6.781788	\N	\N	\N	\N	t	Analyste	+212651403368	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	db21fc60-0dcd-40f2-a079-b5e83e2c256a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00338	Hanane	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	88 Rue Atlas	Quartier Anassi	Bir Mezoui	32.9047444	-6.6781188	\N	\N	\N	\N	f	Administratif	+212686681133	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	685db034-0dae-469b-ab9f-be85ff00551e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00339	Hafida	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	117 Rue des Orangers	Quartier Anassi	Oued Zem	32.9008591	-6.9368907	\N	\N	\N	\N	f	Administratif	+212631451195	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6569a758-025f-4678-bc1a-e70a2b52ad0b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00340	Houda	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	100 Rue Al Massira	Quartier Al Wifaq	Gueffaf	32.8733533	-6.9193216	\N	\N	\N	\N	f	Électricien	+212614263334	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	49fc53e4-7dd2-4db7-a39a-016f0e6fa0d8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00341	Hicham	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	128 Rue Al Massira	Quartier Hassania	Gueffaf	32.8951658	-6.9021672	\N	\N	\N	\N	f	Logisticien	+212690637488	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	039a6e32-0208-43cb-a8d5-48b42c719d62	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00342	Bouchra	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	52 Rue Al Massira	Quartier Al Wifaq	Oued Zem	32.8754102	-6.9033352	\N	\N	\N	\N	f	Électricien	+212667367127	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	38d8903a-2151-42f0-82b4-d09f7237d1a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00343	Noureddine	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	133 Rue Al Massira	Quartier Hassania	Boujniba	32.8979813	-6.7733043	\N	\N	\N	\N	f	Opérateur	+212688428268	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	098972b6-ec6c-44ab-8f1e-e082de7cbda9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00344	Imane	Bennani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	50 Rue Al Massira	Quartier Al Wifaq	Bir Mezoui	32.8592222	-6.5543745	\N	\N	\N	\N	f	Ingénieur	+212677132551	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	01043f24-39ab-4ea0-9e25-6a417eeaeb77	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00345	Amine	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P1	163 Rue Ifrane	Quartier Anassi	Bir Mezoui	32.8618217	-6.8743261	\N	\N	\N	\N	f	Qualité	+212699648804	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8e1970ce-0ee8-4b7f-967d-9f8502141216	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00346	Driss	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	20 Rue Hassan II	Quartier Anassi	Hattane	32.8632929	-6.9109703	\N	\N	\N	\N	f	Ingénieur	+212610624087	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9a72d3f1-fe4e-4a0d-9e64-c564dd182c21	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00347	Lahcen	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	134 Rue Mohammed V	Quartier Anassi	Khouribga	32.8959262	-6.8981068	\N	\N	\N	\N	f	Agent de maîtrise	+212640183169	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9860d0ef-ddee-4617-9623-d9f31e6f47f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00348	Hamza	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	N	155 Rue des Orangers	Quartier Hay Salam	Gueffaf	32.8987107	-6.7774674	\N	\N	\N	\N	f	Ingénieur	+212657808835	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0a409737-631d-494f-8a0e-df6dd22dcd15	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00349	Wafae	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	7 Rue de la Paix	Quartier Hay Mohammadi	Hattane	32.8966621	-6.7806858	\N	\N	\N	\N	f	Superviseur	+212619072951	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1ed65376-5c26-4afb-ae54-6a936b4c9576	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00350	Youssef	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	163 Rue Hassan II	Quartier Hay Mohammadi	Boujniba	32.875134	-6.9031281	\N	\N	\N	\N	f	Électricien	+212630019045	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	90450ddf-aa35-439d-80e7-a6e449366075	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00351	Najat	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P2	2 Rue de la Paix	Quartier Hay Mohammadi	Boujniba	32.8909885	-6.9339375	\N	\N	\N	\N	f	Électricien	+212629005937	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	990b7e1c-67f9-4284-b320-321353249c37	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00352	Anass	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	17 Rue Hassan II	Quartier Hay Salam	Boulanoir	32.8769237	-6.9228599	\N	\N	\N	\N	f	Opérateur	+212647128071	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5c972b77-e9da-434d-a1f1-c9e1733d16a8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00353	Latifa	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	180 Rue Mohammed V	Quartier Hay Salam	Bir Mezoui	32.8785471	-6.9064848	\N	\N	\N	\N	f	Qualité	+212668732560	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4a6c3958-90af-44f7-b45b-5bae4128f355	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00354	Hamza	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	S	23 Rue Ifrane	Quartier Hassania	Oued Zem	32.8668856	-6.9050041	\N	\N	\N	\N	f	Opérateur	+212664644396	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	37e2abb2-3076-41c3-b0eb-5e4259e9db07	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00355	Houda	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	192 Rue Mohammed V	Quartier Centre	Oued Zem	32.877564	-6.9217609	\N	\N	\N	\N	f	Sécurité	+212619311398	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	52ff6307-cfcd-451e-a9a5-ef6674238f6d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00356	Sanaa	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	108 Rue de la Paix	Quartier Tamaris	Oued Zem	32.8629223	-6.91115	\N	\N	\N	\N	f	Conducteur	+212611575061	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2228b69a-6eed-49fa-bbea-3938110774c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00357	Najat	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	148 Rue Al Massira	Quartier Anassi	Hattane	32.9005328	-6.7791119	\N	\N	\N	\N	f	Administratif	+212647189526	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	45bb854f-5abd-4147-ae2b-086f5c9049b7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00358	Zineb	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	119 Rue des Orangers	Quartier Medersa	Boulanoir	32.8811254	-6.9001793	\N	\N	\N	\N	f	Qualité	+212657424625	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	38a385d8-abe5-45b0-8868-2058afe398b5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00359	Loubna	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	119 Rue Hassan II	Quartier Hay Mohammadi	Oued Zem	32.8747149	-6.9170326	\N	\N	\N	\N	f	Technicien	+212613726468	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1f959a29-482a-442a-9d77-ef5c76f847c2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00360	Hasnaa	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	132 Rue de la Paix	Quartier Anassi	Bir Mezoui	32.8924219	-6.8919051	\N	\N	\N	\N	f	Logisticien	+212648876119	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	199b2265-03c1-491e-8861-326ac07126fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00361	Issam	Chaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	46 Rue Mohammed V	Quartier Medersa	Boujniba	32.9008417	-6.7759451	\N	\N	\N	\N	f	Analyste	+212617004201	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d64a3390-9e2e-4fc6-9a80-31d187665c0d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00362	Imane	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	141 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8908339	-6.9213707	\N	\N	\N	\N	f	Qualité	+212698527225	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3d79e03a-e90e-4a55-a273-c282cf60bf09	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00363	Anass	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	N	124 Rue Al Massira	Quartier Al Amal	Boujniba	32.8590742	-6.8783563	\N	\N	\N	\N	f	Logisticien	+212649351163	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e22b6600-c6a6-4f5e-b70d-39e9238eac1d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00364	Aicha	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	77 Rue Hassan II	Quartier Anassi	Gueffaf	32.8955654	-6.9340624	\N	\N	\N	\N	f	Agent de maîtrise	+212671685019	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3df6e967-d4ad-41f7-ba9b-59affceb5ad0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00365	Abdelilah	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	84 Rue Al Massira	Quartier Centre	Gueffaf	32.8920716	-6.8920026	\N	\N	\N	\N	f	Technicien	+212673532599	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	904bf922-2492-4163-897d-4d134483b89b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00366	Omar	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	58 Rue Ifrane	Quartier Anassi	Gueffaf	32.8787785	-6.9155278	\N	\N	\N	\N	f	Technicien	+212672709454	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5722c67d-991e-40b9-b5a2-e143870eefaa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00367	Loubna	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	128 Rue Ifrane	Quartier Tamaris	Hattane	32.8928136	-6.928845	\N	\N	\N	\N	t	Qualité	+212683780678	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cac343ef-301d-4328-9fa8-e19f13281969	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00368	Hassan	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	149 Rue Hassan II	Quartier Anassi	Oued Zem	32.8891333	-6.8980011	\N	\N	\N	\N	f	Superviseur	+212614886272	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0b219dea-45f6-45a9-872a-cfd0ed3451b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00369	Meryem	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	S	27 Rue Hassan II	Quartier Al Amal	Hattane	32.9034094	-6.6761721	\N	\N	\N	\N	f	Administratif	+212650259043	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6fcb8e52-9bb3-4aad-9f2b-c30b55cefa22	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00370	Ilham	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	39 Rue Ifrane	Quartier Al Wifaq	Boujniba	32.8567251	-6.5754426	\N	\N	\N	\N	f	Comptable	+212689277207	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8821a912-3888-4fd7-ae28-5557463baa5a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00371	Siham	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	84 Rue de la Paix	Quartier Anassi	Hattane	32.8885329	-6.9284596	\N	\N	\N	\N	f	RH	+212638490320	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f254299b-d213-4c7b-a586-f1b00afcbf93	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00372	Fatima	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	P3	29 Rue Hassan II	Quartier Tamaris	Khouribga	32.8999059	-6.9300473	\N	\N	\N	\N	f	Comptable	+212618589289	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c63ba3cb-449e-4cef-a209-c2295753ec5b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00373	Lahcen	Slaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	153 Rue Atlas	Quartier Al Amal	Boulanoir	32.8928478	-6.7820001	\N	\N	\N	\N	f	Opérateur	+212639011567	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6ea31ce7-3e21-4a3e-ab91-4423f3ebedf6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00374	Aicha	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	37 Rue Ifrane	Quartier Hay Mohammadi	Boulanoir	32.9010714	-6.8996184	\N	\N	\N	\N	t	Logisticien	+212622293437	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5883b260-86aa-458a-8ce3-95c76248a578	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00375	Mustapha	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	87 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8636148	-6.881645	\N	\N	\N	\N	f	Logisticien	+212675458611	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a5caad0e-b83c-4f73-99ff-ba31431c2a5e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00376	Ali	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	55 Rue Hassan II	Quartier Hassania	Bir Mezoui	32.8690203	-6.9084204	\N	\N	\N	\N	f	Électricien	+212612007215	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ea1b1711-a737-4457-a443-444827e5a727	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00377	Mehdi	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	31 Rue Ifrane	Quartier Hay Salam	Gueffaf	32.8988922	-6.6835864	\N	\N	\N	\N	f	Agent de maîtrise	+212635324197	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	35dddd7b-e6f8-4c84-86c0-0158d1bf1f50	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00378	Loubna	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	N	145 Rue Al Massira	Quartier Centre	Boujniba	32.9008056	-6.9058802	\N	\N	\N	\N	f	Analyste	+212671524505	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	65d2cd26-3a4b-4f04-bd16-cac5fa693998	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00379	Ali	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	37 Rue Mohammed V	Quartier Al Amal	Oued Zem	32.8962272	-6.8908491	\N	\N	\N	\N	f	Électricien	+212616376951	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	64f45595-a370-4050-a36a-e19b4aff9c20	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00380	Hafida	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	172 Rue Al Massira	Quartier Al Wifaq	Bir Mezoui	32.8998222	-6.779118	\N	\N	\N	\N	f	Analyste	+212643896600	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e36985de-8eba-4a39-994a-a3985b419ce0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00381	Amina	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	126 Rue de la Paix	Quartier Al Amal	Boujniba	32.8769174	-6.9227976	\N	\N	\N	\N	f	Électricien	+212644845180	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c3e1877c-f403-468b-8e58-9cd3dc603165	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00382	Hamza	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	5 Rue de la Paix	Quartier Hassania	Boujniba	32.921919	-6.7223817	\N	\N	\N	\N	f	Agent de maîtrise	+212658521363	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2a65ac88-8b0f-49e6-bf69-83a01165f93f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00383	Siham	Ouazzani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	177 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8776391	-6.9063939	\N	\N	\N	\N	f	Qualité	+212673407235	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43d93e6c-1859-496f-b38a-5d91e256f0eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00384	Hamza	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	158 Rue Mohammed V	Quartier Centre	Bir Mezoui	32.857149	-6.5530802	\N	\N	\N	\N	f	Électricien	+212631736850	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aa7353da-ef21-4559-9b20-927ef45033d9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00385	Nadia	Slaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	121 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.8951771	-6.7746244	\N	\N	\N	\N	f	RH	+212614294470	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	baf6d89c-ef0c-4663-9293-bfe94181da0f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00386	Ghita	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	39 Rue Al Massira	Quartier Al Amal	Hattane	32.8966731	-6.904662	\N	\N	\N	\N	f	Qualité	+212693357112	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eb379dc4-3507-40b5-9746-81d6d8c6ba57	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00387	Driss	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	P3	42 Rue Al Massira	Quartier Medersa	Boujniba	32.8974068	-6.9400255	\N	\N	\N	\N	f	Opérateur	+212619605088	Informatique	t	company_bus	Non	f	f	0	t	\N	\N	\N	316eb1a4-8540-44dc-ade4-c4a362294819	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00388	Tariq	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	140 Rue de la Paix	Quartier Medersa	Boujniba	32.8536218	-6.8754817	\N	\N	\N	\N	f	Sécurité	+212679684574	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5dac89be-5ac0-4716-9bca-e48d9c494eee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00389	Nadia	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	43 Rue Mohammed V	Quartier Hay Salam	Boujniba	32.843825	-6.8002699	\N	\N	\N	\N	f	Conducteur	+212657942030	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9e368332-cccf-4191-8376-7c9824b1cae8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00390	Othmane	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	119 Rue Atlas	Quartier Al Wifaq	Gueffaf	32.9034391	-6.6800838	\N	\N	\N	\N	f	Sécurité	+212632465497	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0a11f816-19ca-4bc1-b515-57181cedb6a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00391	Anass	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	108 Rue des Orangers	Quartier Medersa	Bir Mezoui	32.8589741	-6.5553882	\N	\N	\N	\N	f	Mécanicien	+212638053803	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6e567c12-943a-4865-9f08-94f5b6c4d901	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00392	Karim	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	6 Rue de la Paix	Quartier Al Amal	Oued Zem	32.8657845	-6.9055325	\N	\N	\N	\N	f	Technicien	+212695948863	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e4492aea-0dbe-468c-99f6-733cbd2adc63	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00393	Saad	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	N	87 Rue Hassan II	Quartier Centre	Boulanoir	32.8954552	-6.9022231	\N	\N	\N	\N	f	Logisticien	+212697839695	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4b915c59-2f0b-430e-a65a-3ac079bb083b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00394	Soumia	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	80 Rue des Orangers	Quartier Medersa	Hattane	32.8987839	-6.7741068	\N	\N	\N	\N	f	Opérateur	+212627794280	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e694d3f1-f58b-4010-9298-5ee5483f0707	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00395	Othmane	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	6 Rue Ifrane	Quartier Al Wifaq	Boulanoir	32.8611836	-6.8754091	\N	\N	\N	\N	f	Mécanicien	+212641374117	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f91d0885-0d37-4ac8-a3c5-f2736dcb968d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00396	Fatima	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	49 Rue de la Paix	Quartier Al Wifaq	Gueffaf	32.8354303	-6.809336	\N	\N	\N	\N	f	Conducteur	+212671687104	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	49362f89-c6c7-4c47-8351-b326141ed82f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00397	Souad	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	172 Rue Atlas	Quartier Medersa	Khouribga	32.8730896	-6.9140875	\N	\N	\N	\N	f	Électricien	+212698495124	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a91bda0b-f67a-4d57-a147-3706ec3230b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00398	Amina	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	64 Rue de la Paix	Quartier Al Wifaq	Gueffaf	32.8600492	-6.5493796	\N	\N	\N	\N	f	Administratif	+212677024896	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	39471c2d-7db0-4071-b92f-84e8d976cb3d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00399	Amina	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	S	15 Rue Atlas	Quartier Centre	Boulanoir	32.8626155	-6.5502212	\N	\N	\N	\N	f	Ingénieur	+212696676122	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2de0db40-f29a-4c94-a6fc-8b6f115fef5f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00400	Sanaa	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	122 Rue des Orangers	Quartier Al Wifaq	Gueffaf	32.8834965	-6.9224515	\N	\N	\N	\N	f	Comptable	+212656436993	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f1a1d332-6889-4ffc-bda7-c21dcd5ea149	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00401	Jamila	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	96 Rue Ifrane	Quartier Hassania	Gueffaf	32.8935995	-6.9417067	\N	\N	\N	\N	f	Électricien	+212654973961	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	08f3cfe6-3663-4d7a-aaf8-dd1f0b331f55	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00402	Tariq	Zemmouri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	169 Rue de la Paix	Quartier Centre	Oued Zem	32.8962492	-6.9059994	\N	\N	\N	\N	f	Ingénieur	+212660257716	Informatique	t	company_bus	Non	f	f	0	t	\N	\N	\N	247ef1e7-04a8-4ef5-8981-3624613388c4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00403	Zakaria	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	26 Rue Hassan II	Quartier Hay Mohammadi	Gueffaf	32.8888008	-6.9091044	\N	\N	\N	\N	f	Sécurité	+212657001109	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	7de8b6c5-97d4-415f-b9b2-19ba34ca90bb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00404	Youssef	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	171 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8426389	-6.7982804	\N	\N	\N	\N	f	Ingénieur	+212686575493	RH	t	company_bus	Non	f	f	0	t	\N	\N	\N	504c0337-af9b-44ef-9042-8336ca9feda9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00405	Bouchra	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	P1	107 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.8586517	-6.571325	\N	\N	\N	\N	f	Mécanicien	+212615821543	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	381bc0f4-afdd-4b60-945d-84c817afa244	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00406	Samira	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	96 Rue Atlas	Quartier Medersa	Hattane	32.8529567	-6.8815383	\N	\N	\N	\N	f	Comptable	+212645504150	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	99dec490-28dc-4bf1-9008-8e2480a9fd36	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00407	Ghita	Lamrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	27 Rue de la Paix	Quartier Al Amal	Gueffaf	32.8649851	-6.5795574	\N	\N	\N	\N	f	Mécanicien	+212687514456	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5708a916-cfae-4eee-a416-2eff0c0b5f74	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00408	Youssef	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	N	163 Rue Hassan II	Quartier Tamaris	Boujniba	32.8894674	-6.9014639	\N	\N	\N	\N	f	Mécanicien	+212652808117	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	98c122b4-80e8-4d0b-976d-98d9dac53b42	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00409	Rajaa	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	83 Rue Al Massira	Quartier Hassania	Gueffaf	32.9182964	-6.7206577	\N	\N	\N	\N	f	Superviseur	+212693454810	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	e3ac0569-1272-4b8b-be3e-4730ddb99a73	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00410	Rachid	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	190 Rue Mohammed V	Quartier Medersa	Hattane	32.8620084	-6.5518283	\N	\N	\N	\N	f	Sécurité	+212642367910	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7e06909f-fbe4-41e8-bcf1-04bd949d9d3b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00411	Houda	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P2	37 Rue de la Paix	Quartier Anassi	Oued Zem	32.892518	-6.9360578	\N	\N	\N	\N	f	Administratif	+212632349420	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	564c56b0-be4e-4deb-89ce-ce2e4fc3c90d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00412	Jawad	Ouazzani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	72 Rue Al Massira	Quartier Centre	Oued Zem	32.9071915	-6.7816213	\N	\N	\N	\N	f	Conducteur	+212658352674	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5a39a292-a071-4c4c-b35a-ae312f51b9b7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00413	Rajaa	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	194 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.8632132	-6.5635934	\N	\N	\N	\N	f	Opérateur	+212653453010	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e4a58086-00fd-418c-9a12-1601c9c52f2f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00414	Hamza	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	S	97 Rue Atlas	Quartier Medersa	Gueffaf	32.9039925	-6.6806121	\N	\N	\N	\N	f	Technicien	+212642553669	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f2927827-026e-4d38-84c9-e3adf89d08e3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00415	Naima	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	128 Rue Atlas	Quartier Centre	Boujniba	32.8461368	-6.8025335	\N	\N	\N	\N	t	Mécanicien	+212690960614	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b4196b16-2158-42e6-9aca-fdc7619792ae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00416	Loubna	Benomar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	169 Rue Ifrane	Quartier Tamaris	Gueffaf	32.8961222	-6.7804471	\N	\N	\N	\N	f	Mécanicien	+212648932006	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4856b8bf-31a2-47a3-9847-e07c19b4fc1b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00417	Hafida	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P3	64 Rue Al Massira	Quartier Anassi	Oued Zem	32.86365	-6.5698446	\N	\N	\N	\N	f	Mécanicien	+212657203619	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3e1ff55-7d79-4317-bbb8-d83bfa0f9efc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00418	Karim	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	176 Rue Atlas	Quartier Anassi	Boulanoir	32.897211	-6.7697562	\N	\N	\N	\N	f	Analyste	+212658976885	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8d9b3d72-5a57-407f-8334-acbc148976eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00419	Omar	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	136 Rue Ifrane	Quartier Al Amal	Hattane	32.8662454	-6.9096748	\N	\N	\N	\N	f	Sécurité	+212671262140	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d482ff5f-a800-41bb-8914-03f9e4ed00a4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00420	Samira	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	144 Rue Atlas	Quartier Centre	Gueffaf	32.9058676	-6.6796461	\N	\N	\N	\N	f	Conducteur	+212612138496	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1f7d0f3f-8047-4853-9727-2bb5ff69d303	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00421	Soufiane	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	17 Rue Hassan II	Quartier Anassi	Gueffaf	32.8481155	-6.8729506	\N	\N	\N	\N	f	Analyste	+212624445766	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43724349-fa1a-4f36-8f00-ccb32f71c35b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00422	Ilham	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	7 Rue Mohammed V	Quartier Anassi	Boujniba	32.922403	-6.7199605	\N	\N	\N	\N	f	Comptable	+212648819183	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	044db2cb-96e0-4fa3-a383-3b6cb00bcfb2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00423	Soufiane	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	N	80 Rue Al Massira	Quartier Anassi	Hattane	32.886629	-6.9219597	\N	\N	\N	\N	f	Superviseur	+212647065991	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3f081de3-35ae-480d-9edf-92b7416f9965	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00424	Wafae	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	87 Rue des Orangers	Quartier Hay Mohammadi	Khouribga	32.8633398	-6.5720028	\N	\N	\N	\N	f	Comptable	+212695889536	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b51fd16d-4443-49e1-9d6d-c31098f515b1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00425	Omar	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	32 Rue de la Paix	Quartier Centre	Hattane	32.854579	-6.5784694	\N	\N	\N	\N	f	Électricien	+212636180546	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3ddc6610-6c3d-4190-93d8-3fb620c3e984	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00426	Naima	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	P2	62 Rue des Orangers	Quartier Tamaris	Khouribga	32.8775565	-6.9088723	\N	\N	\N	\N	f	RH	+212617812966	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	83c5da92-ee7b-4b79-ba07-b96d0ca2d833	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00427	Meryem	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	102 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8660582	-6.5685384	\N	\N	\N	\N	f	Sécurité	+212666216117	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	249c9edd-18aa-4c37-95c5-aa87dd12124d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00428	Imane	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	143 Rue Mohammed V	Quartier Hay Mohammadi	Gueffaf	32.8769751	-6.9211853	\N	\N	\N	\N	f	Qualité	+212611389031	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ca1d776f-6654-4731-a43e-4246d4256e50	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00429	Tariq	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	S	57 Rue de la Paix	Quartier Centre	Oued Zem	32.893476	-6.9375234	\N	\N	\N	\N	f	RH	+212628770700	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4bceaf3d-2e52-4610-8ec6-ba322b89bc91	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00430	Saad	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	88 Rue de la Paix	Quartier Hay Salam	Boujniba	32.8631302	-6.5794185	\N	\N	\N	\N	f	Qualité	+212670993724	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d9521cd4-e598-44d1-a99a-e2f5b2be157e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00431	Loubna	Sahraoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	123 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.852884	-6.877496	\N	\N	\N	\N	f	Comptable	+212688065514	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	113020ab-a42c-4171-9468-1f57ac2ee1d6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00432	Anass	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	156 Rue Al Massira	Quartier Hay Mohammadi	Khouribga	32.8655409	-6.9191956	\N	\N	\N	\N	f	Comptable	+212691771771	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cc82321c-15ff-4480-851c-c687ef5f4fe6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00433	Mehdi	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	91 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8972387	-6.7767424	\N	\N	\N	\N	f	Électricien	+212641492172	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	97cadcd5-c7a7-4c43-b84e-1762bca2a46e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00434	Samira	Lahlou	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	159 Rue Ifrane	Quartier Centre	Bir Mezoui	32.8629095	-6.5799491	\N	\N	\N	\N	f	Électricien	+212619204141	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3b251c71-6213-4e7e-bad8-b0ad98ac3e2a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00435	Bilal	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	13 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.8822391	-6.9197217	\N	\N	\N	\N	f	Opérateur	+212667407266	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	16f3d609-c107-4a98-885d-e4d19fbe153d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00436	Ibrahim	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	52 Rue Atlas	Quartier Al Amal	Gueffaf	32.8967267	-6.9389813	\N	\N	\N	\N	f	RH	+212642546471	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	62b235fe-8b2c-43a1-84eb-f65cb17f4158	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00437	Zakaria	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	46 Rue Atlas	Quartier Al Amal	Gueffaf	32.8966425	-6.9351241	\N	\N	\N	\N	f	Superviseur	+212629126815	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f7896a42-4b12-4649-91b0-aef85a798b23	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00438	Wafae	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	N	73 Rue Hassan II	Quartier Hay Salam	Boujniba	32.8584005	-6.8743563	\N	\N	\N	\N	f	Opérateur	+212649279755	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a41b94b0-e654-4098-b32a-60abf23e8900	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00439	Khadija	Slaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	36 Rue Hassan II	Quartier Medersa	Oued Zem	32.8512044	-6.8729158	\N	\N	\N	\N	t	Qualité	+212688064877	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c8ae1276-678b-4fc1-ac1e-56c8adec7b47	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00440	Khadija	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	85 Rue des Orangers	Quartier Hay Mohammadi	Oued Zem	32.9012143	-6.9312747	\N	\N	\N	\N	f	Logisticien	+212674466537	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	176a53c3-179b-45fb-92e0-7a74c22562b3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00441	Ilham	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P2	16 Rue Hassan II	Quartier Hay Mohammadi	Boulanoir	32.8343969	-6.8010504	\N	\N	\N	\N	f	Ingénieur	+212671753791	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a4f7bf62-068f-48fd-908d-970baeef7a5e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00442	Karim	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	49 Rue Hassan II	Quartier Centre	Boulanoir	32.8531666	-6.567989	\N	\N	\N	\N	f	Superviseur	+212693877581	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	6d8c32ae-3973-4ccc-8a4e-aa5eb5932568	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00443	Jawad	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	115 Rue Ifrane	Quartier Hay Salam	Khouribga	32.8615471	-6.8744735	\N	\N	\N	\N	f	Mécanicien	+212619817921	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aa509658-02dc-4065-8aaa-36b4174e6074	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00444	Driss	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	S	37 Rue des Orangers	Quartier Medersa	Gueffaf	32.9013474	-6.7799607	\N	\N	\N	\N	f	Technicien	+212630130568	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	adbca8b1-a0c3-4624-ac17-f0e753ce15dd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00445	Soufiane	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	183 Rue Atlas	Quartier Hay Mohammadi	Khouribga	32.8865363	-6.9220539	\N	\N	\N	\N	f	Sécurité	+212637569378	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	44f38fda-4366-4a29-86a7-3485d22cc0eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00446	Lahcen	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	27 Rue Al Massira	Quartier Hay Mohammadi	Gueffaf	32.8696841	-6.9033889	\N	\N	\N	\N	f	Ingénieur	+212638791692	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	40c72a23-a741-4e22-b492-92833e0f6370	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00447	Hafida	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P3	116 Rue des Orangers	Quartier Medersa	Oued Zem	32.9264071	-6.7166283	\N	\N	\N	\N	f	Mécanicien	+212616556360	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3138baaf-949e-4e30-91a6-f76d284d705e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00448	Ahmed	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	58 Rue Mohammed V	Quartier Medersa	Oued Zem	32.8942626	-6.7753455	\N	\N	\N	\N	f	Conducteur	+212664510811	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43ea2d59-fc31-47a7-82e8-465ee8d357e4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00449	Amine	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	144 Rue Ifrane	Quartier Hay Mohammadi	Bir Mezoui	32.9000285	-6.9026534	\N	\N	\N	\N	f	Opérateur	+212693006163	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f8aad23c-7a17-4e55-8b1f-157d84b51a72	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00450	Rajaa	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	P1	169 Rue Mohammed V	Quartier Al Wifaq	Oued Zem	32.8951607	-6.9368401	\N	\N	\N	\N	f	Opérateur	+212647773513	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e05f44fa-95f2-4ceb-b2e9-c7c33c7901eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00451	Soumia	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	131 Rue des Orangers	Quartier Medersa	Bir Mezoui	32.8645367	-6.5726099	\N	\N	\N	\N	t	Mécanicien	+212696465248	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aac8b513-fb4b-4549-9aae-dbfea7866066	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00452	Hicham	Qasmi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	162 Rue de la Paix	Quartier Hay Salam	Khouribga	32.9192725	-6.7165066	\N	\N	\N	\N	f	Administratif	+212657676138	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	48a643c3-4b99-4af3-af9b-b62651f727b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00453	Souad	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	195 Rue Ifrane	Quartier Anassi	Boujniba	32.8571681	-6.578793	\N	\N	\N	\N	f	Logisticien	+212668694855	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4493cc2c-1030-455c-994d-a6a3b64a3493	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00454	Aicha	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	64 Rue Atlas	Quartier Anassi	Boujniba	32.8557028	-6.5552637	\N	\N	\N	\N	f	Analyste	+212671876836	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	14d9b52d-0c24-4703-84a0-546e9799b92a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00455	Houda	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	93 Rue des Orangers	Quartier Hassania	Oued Zem	32.8580655	-6.9074602	\N	\N	\N	\N	f	Agent de maîtrise	+212676129449	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a4c9dddf-36e8-4c40-a2da-e9c20901fd62	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00456	Jawad	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	29 Rue Atlas	Quartier Anassi	Boujniba	32.8544379	-6.879545	\N	\N	\N	\N	f	Sécurité	+212683601764	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dabc1f29-3a24-4723-a50d-672cc44ff364	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00457	Issam	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	17 Rue des Orangers	Quartier Al Wifaq	Khouribga	32.9022475	-6.6784247	\N	\N	\N	\N	f	Analyste	+212651799860	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	338a0886-5308-4503-a458-9978d3b6fe0b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00458	Hamza	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	167 Rue des Orangers	Quartier Hassania	Khouribga	32.8575937	-6.5804118	\N	\N	\N	\N	f	Superviseur	+212663648220	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5ca79a9a-9aea-4fa1-9c72-5cecfbb744a0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00459	Zineb	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	S	161 Rue Atlas	Quartier Medersa	Bir Mezoui	32.8775991	-6.9038937	\N	\N	\N	\N	f	Sécurité	+212648818341	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f092f10-d45d-4ce6-87ed-d4fb9c2532fe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00460	Latifa	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	124 Rue Hassan II	Quartier Medersa	Boulanoir	32.8433379	-6.8010586	\N	\N	\N	\N	f	Mécanicien	+212643218299	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	86b162af-6083-4aef-b036-70b90afc09b9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00461	Ahmed	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	130 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8931967	-6.9258286	\N	\N	\N	\N	f	Opérateur	+212628516929	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3c5fd666-7405-464b-9109-b1bb5d5a5cc6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00462	Anass	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P3	14 Rue Hassan II	Quartier Al Wifaq	Bir Mezoui	32.8992649	-6.8992203	\N	\N	\N	\N	f	Superviseur	+212612466198	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	89063ce6-5c7f-4c33-a475-2f60b458246c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00463	Siham	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	81 Rue de la Paix	Quartier Medersa	Boujniba	32.8563664	-6.5774911	\N	\N	\N	\N	f	Conducteur	+212624562975	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	55076649-d08c-4a94-adb0-fa8c3eac4096	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00464	Zineb	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	106 Rue Mohammed V	Quartier Hassania	Khouribga	32.8383045	-6.8067492	\N	\N	\N	\N	f	Analyste	+212647833721	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1b701444-ffb5-439a-a22d-3b85b117e14c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00465	Hicham	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	P1	23 Rue de la Paix	Quartier Al Amal	Boujniba	32.8803425	-6.909635	\N	\N	\N	\N	f	Ingénieur	+212660985380	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3f6b04c1-7e87-49b1-b123-bc7773137caf	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00466	Saad	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	13 Rue Hassan II	Quartier Hay Salam	Hattane	32.8798144	-6.8976554	\N	\N	\N	\N	f	Analyste	+212642968581	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3e3eb524-39ed-434a-89dd-d83fd30a30a3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00467	Laila	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	70 Rue de la Paix	Quartier Hay Salam	Boulanoir	32.8623856	-6.5797609	\N	\N	\N	\N	f	RH	+212637225441	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ce0b155c-f120-404e-b3a4-ff2e0bbe8395	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00468	Karim	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	115 Rue Hassan II	Quartier Centre	Boujniba	32.8831863	-6.9213293	\N	\N	\N	\N	f	Opérateur	+212634648972	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	541a7275-ea62-4d93-870a-c9144efcaf7b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00469	Rachid	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	45 Rue Atlas	Quartier Al Wifaq	Bir Mezoui	32.8845199	-6.9313902	\N	\N	\N	\N	f	Qualité	+212676523408	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	92598a4b-ecd3-434b-a63a-590c40cc4ff3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00470	Adil	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	17 Rue Hassan II	Quartier Hay Mohammadi	Gueffaf	32.8566891	-6.8728752	\N	\N	\N	\N	f	Analyste	+212695097177	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fc776e2a-f99a-4849-91ce-b61dc77b9e1d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00471	Mustapha	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	55 Rue des Orangers	Quartier Anassi	Boujniba	32.8973508	-6.9062078	\N	\N	\N	\N	f	Administratif	+212623266344	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	de02678a-49cc-42ab-ac34-16d0f664069a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00472	Tariq	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	59 Rue Ifrane	Quartier Hay Mohammadi	Hattane	32.8990367	-6.7807478	\N	\N	\N	\N	f	Superviseur	+212649624255	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2b601110-9187-4a16-8fcd-88e41a4f5367	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00473	Khadija	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	42 Rue de la Paix	Quartier Al Wifaq	Boujniba	32.886606	-6.9256235	\N	\N	\N	\N	f	Technicien	+212627685418	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f4fe6d6d-48e9-4bbf-9cd4-f302f0aa1081	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00474	Hamza	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	S	155 Rue des Orangers	Quartier Hassania	Khouribga	32.8942687	-6.7718589	\N	\N	\N	\N	f	Technicien	+212669891492	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a3f733ef-6698-437c-9730-afaee5d779da	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00475	Mohammed	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	80 Rue Mohammed V	Quartier Hassania	Oued Zem	32.8685939	-6.5785713	\N	\N	\N	\N	f	Qualité	+212654978217	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bda0158a-81be-4708-ad66-37898346b7da	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00476	Malika	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	143 Rue Ifrane	Quartier Medersa	Gueffaf	32.8616682	-6.5800469	\N	\N	\N	\N	f	RH	+212653554596	Qualité	t	company_bus	Non	f	f	0	t	\N	\N	\N	c8f9b6f6-b7e9-4f58-b82f-727a5ff2cc0e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00477	Fatima	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	85 Rue Hassan II	Quartier Medersa	Khouribga	32.8846101	-6.9056261	\N	\N	\N	\N	f	Administratif	+212620692389	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6709cc0c-bce8-43e0-bc78-b3f4c19b60fd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00478	Noureddine	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	37 Rue des Orangers	Quartier Hay Salam	Khouribga	32.9007465	-6.9096932	\N	\N	\N	\N	f	Administratif	+212669239988	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1de19b6e-6696-411f-87cd-8c4ae2a377d9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00479	Youssef	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	128 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.9026274	-6.6800489	\N	\N	\N	\N	f	Logisticien	+212631740779	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1885315a-4f58-42e7-83a1-7c0958e09495	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00480	Zakaria	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P1	102 Rue de la Paix	Quartier Anassi	Bir Mezoui	32.8926256	-6.7782442	\N	\N	\N	\N	f	Sécurité	+212697888955	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ad3cd08f-b639-4189-bb87-07d829967bcb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00481	Souad	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	153 Rue Mohammed V	Quartier Hay Mohammadi	Hattane	32.8760027	-6.9187909	\N	\N	\N	\N	f	Sécurité	+212695274024	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d365eebe-d65a-49fa-a7ca-e4407b8a6ee0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00482	Bilal	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	14 Rue des Orangers	Quartier Tamaris	Boulanoir	32.8974479	-6.7741375	\N	\N	\N	\N	f	Administratif	+212627115298	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9db58f3f-2e71-48d1-b114-3d60cd26e250	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00483	Hanane	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	N	12 Rue des Orangers	Quartier Al Amal	Khouribga	32.8981525	-6.7855382	\N	\N	\N	\N	f	Qualité	+212673565642	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b342f92f-677c-4be6-9589-275a1421bdc7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00484	Karim	Ouazzani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	40 Rue Atlas	Quartier Al Wifaq	Khouribga	32.8641643	-6.9104585	\N	\N	\N	\N	f	Analyste	+212660241947	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	27fbf426-0223-4ea9-b910-9b79055e013f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00485	Siham	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	182 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8763251	-6.9075041	\N	\N	\N	\N	f	Logisticien	+212667069417	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	392f3757-e2eb-4f21-9bb9-437e1597ef92	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00486	Abdelilah	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	150 Rue Ifrane	Quartier Hay Salam	Boujniba	32.9200384	-6.7207777	\N	\N	\N	\N	f	Superviseur	+212637836327	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cf1e2993-52e3-4003-960f-01007a82812e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00487	Mehdi	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	80 Rue Ifrane	Quartier Centre	Boujniba	32.8345317	-6.8063044	\N	\N	\N	\N	f	Opérateur	+212687624624	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a8e29cae-0248-4b32-986a-b858b873f520	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00488	Mehdi	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	86 Rue de la Paix	Quartier Anassi	Khouribga	32.8351848	-6.8079655	\N	\N	\N	\N	f	Électricien	+212672972348	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d19f2ad5-217c-43f6-a8b6-199b38a99de8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00489	Issam	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	90 Rue des Orangers	Quartier Hassania	Bir Mezoui	32.87081	-6.9255365	\N	\N	\N	\N	f	Mécanicien	+212616243173	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8da10c62-a3a7-4184-bb4e-3827540adf7c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00490	Hamza	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	168 Rue Al Massira	Quartier Al Amal	Oued Zem	32.9026776	-6.9323348	\N	\N	\N	\N	f	Électricien	+212634400235	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c0d7e801-dcd2-477e-80a4-c0f6d15db6ab	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00491	Wafae	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	179 Rue Hassan II	Quartier Medersa	Bir Mezoui	32.8902587	-6.9315497	\N	\N	\N	\N	f	Conducteur	+212651458524	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b1ae3803-ef06-4c32-9d09-b8afa8b4ac8a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00492	Soumia	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	112 Rue Al Massira	Quartier Hassania	Boujniba	32.8708437	-6.9127073	\N	\N	\N	\N	f	Ingénieur	+212681697218	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b54612d1-ef3f-4f78-8d74-7f827f59877d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00493	Saad	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	183 Rue Al Massira	Quartier Tamaris	Boulanoir	32.8565868	-6.876645	\N	\N	\N	\N	f	Mécanicien	+212631474652	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	35241a1e-873e-4c21-8e48-ff9b295ce9f1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00494	Khalid	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	165 Rue Hassan II	Quartier Centre	Bir Mezoui	32.8518046	-6.8795201	\N	\N	\N	\N	f	Qualité	+212631333652	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0e008402-6632-49fe-9e0e-c284312a695d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00495	Imane	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	106 Rue des Orangers	Quartier Al Amal	Bir Mezoui	32.8616661	-6.8781693	\N	\N	\N	\N	t	Conducteur	+212633920105	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1ea9e7cf-ac4d-403f-bedd-9ecee141396b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00496	Hasnaa	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	177 Rue Atlas	Quartier Hay Salam	Boujniba	32.9047354	-6.6817261	\N	\N	\N	\N	f	Logisticien	+212695069815	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1add9df9-ea1d-4e79-9af0-9956fdbfa214	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00497	Othmane	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	33 Rue de la Paix	Quartier Medersa	Boujniba	32.8993421	-6.6802683	\N	\N	\N	\N	f	Analyste	+212617373374	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	aba5ebf5-9576-41d2-b193-7f23df3b10c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00498	Ali	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	92 Rue des Orangers	Quartier Hay Salam	Bir Mezoui	32.8633005	-6.5763628	\N	\N	\N	\N	f	Superviseur	+212662539028	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	644f15d9-36ac-4161-b44e-23da179dc65e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00499	Loubna	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	86 Rue Ifrane	Quartier Medersa	Boulanoir	32.8995768	-6.9370438	\N	\N	\N	\N	f	Ingénieur	+212673939840	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6aa1b53e-4a0c-4232-8841-640ef5acb7cb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00500	Zakaria	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	176 Rue Hassan II	Quartier Medersa	Oued Zem	32.871581	-6.9144744	\N	\N	\N	\N	f	Superviseur	+212676350647	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	53c59906-f7a4-4430-b2b5-f88ff8a3a93c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00501	Driss	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P2	120 Rue Atlas	Quartier Centre	Bir Mezoui	32.8755251	-6.9147517	\N	\N	\N	\N	f	Administratif	+212622423684	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	557fab10-5dcf-4f78-b594-373ecde98d5f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00502	Bilal	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	45 Rue Al Massira	Quartier Medersa	Boulanoir	32.8669633	-6.5791518	\N	\N	\N	\N	f	Sécurité	+212691549466	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	12127609-207c-43dd-8d49-001904e5015c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00503	Wafae	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	200 Rue Hassan II	Quartier Anassi	Bir Mezoui	32.8406759	-6.8062637	\N	\N	\N	\N	f	Analyste	+212640738533	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	695eda00-bbca-46c4-bd42-99058661ac4c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00504	Loubna	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	S	11 Rue Ifrane	Quartier Anassi	Hattane	32.8676073	-6.9066937	\N	\N	\N	\N	f	Administratif	+212671776240	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f2291d35-776e-4472-9c58-81a14af8e82a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00505	Zineb	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	152 Rue Atlas	Quartier Hay Salam	Gueffaf	32.9014846	-6.7787342	\N	\N	\N	\N	f	Logisticien	+212631853645	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6c1d7bf0-c375-4eee-8bd6-2bec23f00885	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00506	Meryem	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	95 Rue Atlas	Quartier Al Amal	Boulanoir	32.874157	-6.9120721	\N	\N	\N	\N	f	RH	+212694291138	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fa124e6f-c3f5-4b51-a316-ea1aaaef0617	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00507	Fouad	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	118 Rue Ifrane	Quartier Anassi	Khouribga	32.8944553	-6.7780854	\N	\N	\N	\N	f	Mécanicien	+212653156350	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	40f2f78b-235e-4123-846b-147f900e93a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00508	Laila	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	113 Rue Atlas	Quartier Al Amal	Hattane	32.8874421	-6.9257858	\N	\N	\N	\N	f	Électricien	+212643108128	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2bc6c514-e6d1-441a-8c10-91ea2c0d0341	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00509	Kawtar	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	90 Rue des Orangers	Quartier Medersa	Oued Zem	32.88934	-6.9393661	\N	\N	\N	\N	f	Technicien	+212683985074	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	847e7d61-7c93-4348-9a7f-513422007885	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00510	Soumia	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	P1	115 Rue Atlas	Quartier Hay Mohammadi	Khouribga	32.8993611	-6.7840098	\N	\N	\N	\N	f	Qualité	+212696811813	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d7348307-7390-4605-a68b-a4e77f4bc342	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00511	Ilham	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	87 Rue Atlas	Quartier Anassi	Boulanoir	32.8923759	-6.9328711	\N	\N	\N	\N	f	Mécanicien	+212647383974	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	af2ab7a8-7c2f-478d-840b-3e81090f9deb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00512	Noureddine	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	57 Rue Al Massira	Quartier Anassi	Bir Mezoui	32.8866778	-6.9230793	\N	\N	\N	\N	f	Sécurité	+212639121007	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8a668176-a4f0-4f1b-af17-f041ecd140bc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00513	Hasnaa	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	N	27 Rue Ifrane	Quartier Centre	Boujniba	32.8642183	-6.8796757	\N	\N	\N	\N	f	Opérateur	+212654988721	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	90923559-33be-4888-8f0b-a87511eecb46	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00514	Youssef	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	161 Rue de la Paix	Quartier Tamaris	Gueffaf	32.8751074	-6.9198796	\N	\N	\N	\N	f	Technicien	+212646759528	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a1bc0f58-2849-4d5b-8418-edb136a6b682	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00515	Hicham	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	21 Rue Atlas	Quartier Centre	Oued Zem	32.8876098	-6.9053056	\N	\N	\N	\N	f	RH	+212681933267	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7e29c38b-0c67-4ae1-b182-608808c2f80f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00516	Saad	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	65 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8950788	-6.934701	\N	\N	\N	\N	f	Sécurité	+212622986737	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e5461c06-7b83-48d6-80ea-34bcf7ba0c5f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00517	Soufiane	Benomar	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	162 Rue Hassan II	Quartier Hassania	Bir Mezoui	32.8937626	-6.9307681	\N	\N	\N	\N	f	Logisticien	+212637556370	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	122ba367-4a66-470d-aae1-6a25ec9ba11b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00518	Nadia	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	34 Rue des Orangers	Quartier Hay Mohammadi	Bir Mezoui	32.8988473	-6.6779276	\N	\N	\N	\N	f	Administratif	+212651226709	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0c16ac66-fec6-4836-aad0-4ab83bb52658	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00519	Khalid	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	S	94 Rue Hassan II	Quartier Hay Mohammadi	Boujniba	32.8760126	-6.9120261	\N	\N	\N	\N	f	Comptable	+212674817271	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac7b8d64-78a5-4a49-86d8-d7cf42941053	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00520	Soufiane	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	163 Rue Ifrane	Quartier Al Amal	Gueffaf	32.8928551	-6.9319798	\N	\N	\N	\N	f	Ingénieur	+212699435706	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	94fe13dd-aba4-420b-b724-56f70454ceb5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00521	Ahmed	Benomar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	45 Rue des Orangers	Quartier Centre	Boujniba	32.9000434	-6.7803599	\N	\N	\N	\N	f	Technicien	+212621875743	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bff1cca2-5dc1-4c24-8829-33deb1c7cf2b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00522	Ibrahim	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	85 Rue des Orangers	Quartier Hassania	Khouribga	32.8575751	-6.5684732	\N	\N	\N	\N	f	Mécanicien	+212621246542	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	773ded40-b9d2-4fde-84aa-e05ed70a68e9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00612	Hassan	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P3	155 Rue Hassan II	Quartier Hassania	Boujniba	32.8980215	-6.780143	\N	\N	\N	\N	f	RH	+212644964009	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a04611e-ea89-4e84-a96e-2979bf42a493	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00523	Abdelilah	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	85 Rue Al Massira	Quartier Medersa	Boulanoir	32.8600702	-6.5507719	\N	\N	\N	\N	f	Technicien	+212653785050	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eae0928e-7760-474d-87c8-c46af023d8a3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00524	Issam	Lahlou	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	141 Rue Atlas	Quartier Hay Mohammadi	Gueffaf	32.8582504	-6.5540167	\N	\N	\N	\N	f	Électricien	+212641961609	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5dc9e387-98c1-4d64-9af0-cae151839a60	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00525	Laila	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	181 Rue de la Paix	Quartier Hassania	Oued Zem	32.8959504	-6.9055288	\N	\N	\N	\N	f	Mécanicien	+212610564758	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cb7b6368-3076-43eb-bea0-62c4725dd0df	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00526	Latifa	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	189 Rue Hassan II	Quartier Centre	Hattane	32.8767652	-6.9118504	\N	\N	\N	\N	t	Administratif	+212684567108	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c8d0efc9-717a-4c3f-afbe-8427ec8b6c8c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00527	Issam	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	139 Rue Mohammed V	Quartier Anassi	Boujniba	32.8781555	-6.9205364	\N	\N	\N	\N	f	Conducteur	+212675812150	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	96c253eb-646f-451f-8177-76d3069f3fbe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00528	Hassan	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	N	187 Rue des Orangers	Quartier Hay Mohammadi	Khouribga	32.9238107	-6.7212641	\N	\N	\N	\N	f	Électricien	+212612759368	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5b8cd97e-b8cf-49b2-ba61-7a47414b974e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00529	Siham	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	186 Rue Hassan II	Quartier Al Amal	Boujniba	32.8599899	-6.5496111	\N	\N	\N	\N	f	Opérateur	+212673718137	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c1541e78-6423-4fce-a244-11ab7ce63412	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00530	Hasnaa	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	173 Rue Hassan II	Quartier Al Wifaq	Bir Mezoui	32.8787604	-6.912808	\N	\N	\N	\N	f	Technicien	+212663242695	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9eaaedfe-68af-4a7c-af44-201905235a31	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00531	Fatima	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P2	174 Rue de la Paix	Quartier Hay Salam	Boulanoir	32.8894642	-6.938362	\N	\N	\N	\N	f	Comptable	+212638492511	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0cb03479-e99e-49f2-8290-9fbb9803d9ef	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00532	Hasnaa	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	194 Rue Atlas	Quartier Hay Salam	Boujniba	32.8669754	-6.9145833	\N	\N	\N	\N	f	Comptable	+212612301512	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	009cbd29-8adb-49ba-9428-5498658c74b0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00533	Amine	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	117 Rue Mohammed V	Quartier Al Wifaq	Oued Zem	32.8648754	-6.5846406	\N	\N	\N	\N	f	Comptable	+212685313363	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d5ec96b3-be16-4391-bd46-11b20d4c1b50	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00534	Anass	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	S	149 Rue des Orangers	Quartier Anassi	Boulanoir	32.8904287	-6.8931123	\N	\N	\N	\N	f	Comptable	+212624099677	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2323c862-2fa1-4bcf-b691-31e460092943	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00535	Malika	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	118 Rue de la Paix	Quartier Hay Mohammadi	Khouribga	32.8520306	-6.5745029	\N	\N	\N	\N	f	Analyste	+212656879385	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	213fffbb-7f3b-4698-acb6-c0e0059fa96d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00536	Lahcen	Bennani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	138 Rue des Orangers	Quartier Anassi	Bir Mezoui	32.8459819	-6.7983564	\N	\N	\N	\N	f	Conducteur	+212615623101	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	30398eb9-5c1e-4115-94e9-edbfc38c04b4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00537	Hafida	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	69 Rue Hassan II	Quartier Al Wifaq	Hattane	32.8935369	-6.8988547	\N	\N	\N	\N	f	RH	+212691932701	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	af4a9ea8-5d76-41b5-b4ce-03bb0a363aea	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00538	Bilal	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	136 Rue Al Massira	Quartier Medersa	Boulanoir	32.8943553	-6.9352342	\N	\N	\N	\N	f	Conducteur	+212610473955	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	98dff371-9211-4bb6-aa3d-3251a35aa34c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00539	Naima	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	118 Rue Atlas	Quartier Hassania	Hattane	32.8752668	-6.9147172	\N	\N	\N	\N	f	Sécurité	+212654033000	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9d49b300-a0b3-4ab5-8ead-7343e73d3258	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00540	Mohammed	Hassouni	d39d79ec-a716-4839-a93d-1845d00c182c	P1	175 Rue de la Paix	Quartier Centre	Oued Zem	32.8372165	-6.8086254	\N	\N	\N	\N	f	Analyste	+212627459180	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a5a64e9b-488f-4ccc-8a6f-3fa07d3e2b9e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00541	Aicha	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	197 Rue de la Paix	Quartier Al Amal	Khouribga	32.8903216	-6.9331514	\N	\N	\N	\N	f	Ingénieur	+212616484474	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ae667594-5fd4-4526-bf9b-a52d8f4c8d21	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00542	Hasnaa	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	170 Rue Atlas	Quartier Medersa	Bir Mezoui	32.8959876	-6.9114394	\N	\N	\N	\N	f	Superviseur	+212621484990	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3518d12b-fb46-4d96-9ac0-c12f839ae19f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00543	Souad	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	18 Rue de la Paix	Quartier Tamaris	Boulanoir	32.8911103	-6.9156596	\N	\N	\N	\N	f	Opérateur	+212689681512	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	95ad12a3-bedb-43d2-9b8e-df38ea3a139c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00544	Najat	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	95 Rue Hassan II	Quartier Hassania	Khouribga	32.8612992	-6.5553906	\N	\N	\N	\N	f	Analyste	+212621809664	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	f8a52ec5-c98c-498b-ba9f-40ce1d1229cb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00545	Mehdi	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	173 Rue Atlas	Quartier Hay Salam	Khouribga	32.8476955	-6.8011702	\N	\N	\N	\N	f	Opérateur	+212677474998	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	47098220-2ed6-4c42-80ca-92f9323c0946	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00546	Fatima	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	P2	71 Rue Hassan II	Quartier Al Amal	Boulanoir	32.8997838	-6.904895	\N	\N	\N	\N	f	Sécurité	+212641873125	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a5cbe59c-e2de-4023-91b4-9e69da766608	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00547	Mustapha	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	179 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8888543	-6.8968865	\N	\N	\N	\N	f	Superviseur	+212664310500	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7a110bc1-44d4-46c0-a371-3ab1e2fb4d7c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00548	Rajaa	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	200 Rue Hassan II	Quartier Hay Salam	Boujniba	32.8416593	-6.800456	\N	\N	\N	\N	f	Superviseur	+212617472388	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	31cd6438-0b1d-48f1-a8cf-f748a874cafb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00549	Issam	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	S	169 Rue des Orangers	Quartier Al Amal	Boujniba	32.8873811	-6.9014932	\N	\N	\N	\N	f	Logisticien	+212661367245	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b0cdd00c-b792-48f5-87ad-bf7fc70f22fe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00550	Ibrahim	Slaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	104 Rue Atlas	Quartier Anassi	Gueffaf	32.8663653	-6.5709663	\N	\N	\N	\N	f	Technicien	+212640352565	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5459cf1c-b4a8-4c62-a324-3ffe4a079efc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00551	Fatima	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	112 Rue Hassan II	Quartier Tamaris	Hattane	32.8791112	-6.9087993	\N	\N	\N	\N	f	Administratif	+212613204935	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	24faa82b-f038-4566-92a3-e0a4f33b3db6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00552	Ahmed	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P3	131 Rue Atlas	Quartier Al Amal	Khouribga	32.8935704	-6.9014837	\N	\N	\N	\N	f	RH	+212681686293	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9e888a89-dec4-480e-b5d5-ef36054f8edc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00553	Jawad	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	149 Rue Ifrane	Quartier Tamaris	Boujniba	32.8933021	-6.928549	\N	\N	\N	\N	f	Comptable	+212645821928	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	932d7302-5bb6-4b1c-a32b-aca2e870f804	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00554	Mehdi	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	80 Rue de la Paix	Quartier Hassania	Khouribga	32.8969959	-6.9027112	\N	\N	\N	\N	f	Agent de maîtrise	+212624799125	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ae8f6b93-d6a0-4c3c-aac8-60c341ef2372	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00555	Najat	El Kabbaj	d39d79ec-a716-4839-a93d-1845d00c182c	P1	17 Rue Atlas	Quartier Hay Mohammadi	Hattane	32.8972924	-6.9362299	\N	\N	\N	\N	f	Agent de maîtrise	+212671615622	Qualité	t	company_bus	Non	f	f	0	t	\N	\N	\N	9a2dd551-e5e5-462f-baea-3ed3daa231f3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00556	Samira	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	110 Rue Hassan II	Quartier Medersa	Boujniba	32.8509742	-6.8752049	\N	\N	\N	\N	f	Superviseur	+212656675360	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e6ae45b5-d9bb-4cc2-97fb-9ba5856ac911	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00557	Driss	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	88 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8803948	-6.913574	\N	\N	\N	\N	f	Conducteur	+212665442063	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d5b228ca-9d46-44d7-b1d9-85ea7d6b8562	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00558	Rachid	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	N	21 Rue Ifrane	Quartier Tamaris	Boulanoir	32.8570818	-6.5574432	\N	\N	\N	\N	f	Opérateur	+212646827848	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	717fe377-f6ac-4871-a95c-87abecf83fc4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00559	Bouchra	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	20 Rue Ifrane	Quartier Anassi	Hattane	32.9008715	-6.6788312	\N	\N	\N	\N	f	Électricien	+212673598218	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	22d1f67a-d076-4174-85ca-b264b768467e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00560	Ali	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	30 Rue Ifrane	Quartier Anassi	Hattane	32.8767176	-6.9020808	\N	\N	\N	\N	f	RH	+212653362067	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	321c64d9-0625-4edd-8a92-40c21206781f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00561	Jawad	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	13 Rue Ifrane	Quartier Medersa	Khouribga	32.8395197	-6.8074183	\N	\N	\N	\N	f	Agent de maîtrise	+212619994430	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2bd24bfb-25cc-4a0c-9e40-4a87e0b7f894	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00562	Saad	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	143 Rue Ifrane	Quartier Anassi	Hattane	32.8611255	-6.5580791	\N	\N	\N	\N	f	Ingénieur	+212683886730	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0c7ce70d-6874-45ef-a1c3-b5bcc22fc3c0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00563	Tariq	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	110 Rue Ifrane	Quartier Hassania	Hattane	32.9013099	-6.784601	\N	\N	\N	\N	f	Agent de maîtrise	+212631701627	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9ea5649d-3ae8-48f8-accb-333edbefad23	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00564	Amina	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	S	162 Rue des Orangers	Quartier Al Amal	Khouribga	32.8978595	-6.680235	\N	\N	\N	\N	f	Analyste	+212666202383	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	258f9f28-b197-4ba8-b690-4c94e632ab76	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00565	Malika	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	68 Rue des Orangers	Quartier Tamaris	Bir Mezoui	32.8934307	-6.9050499	\N	\N	\N	\N	t	Comptable	+212648520623	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c90fbb1b-3221-447f-a7d2-44300b1241fb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00566	Issam	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	9 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.8952357	-6.9297904	\N	\N	\N	\N	f	Administratif	+212639674967	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cc8b0eaa-9c22-413b-9ff4-87809e452751	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00567	Issam	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	200 Rue Al Massira	Quartier Centre	Hattane	32.8991676	-6.7692566	\N	\N	\N	\N	f	Logisticien	+212689399433	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	02d76475-cb2d-4879-b6ce-b1f8a70faf08	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00568	Zakaria	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	114 Rue des Orangers	Quartier Centre	Bir Mezoui	32.84937	-6.8758456	\N	\N	\N	\N	f	Électricien	+212662943068	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1e2cd0e9-7eb1-4e10-bd23-382427787450	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00569	Houda	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	187 Rue Mohammed V	Quartier Anassi	Bir Mezoui	32.8921307	-6.774186	\N	\N	\N	\N	f	Comptable	+212637004381	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eaa4ed0f-1d31-4e3d-8fee-a1114694499c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00570	Amine	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P1	73 Rue Mohammed V	Quartier Medersa	Boulanoir	32.8414088	-6.804341	\N	\N	\N	\N	f	Technicien	+212688323729	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a940826f-08bc-434e-a665-ce412463b87f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00571	Tariq	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	184 Rue Hassan II	Quartier Hassania	Oued Zem	32.8873439	-6.9291548	\N	\N	\N	\N	f	Technicien	+212625757064	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	99b5353f-8312-4b6a-8b47-49b5b590c1df	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00572	Amine	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	35 Rue des Orangers	Quartier Medersa	Khouribga	32.8663655	-6.9170581	\N	\N	\N	\N	f	Comptable	+212654079878	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d260e0fb-03fc-45d1-9666-1c08882e8d60	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00573	Mustapha	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	N	61 Rue Al Massira	Quartier Hay Salam	Hattane	32.8809889	-6.9172254	\N	\N	\N	\N	f	Superviseur	+212665368850	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d35e483b-559d-416e-a7a5-1bcf96780636	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00574	Sanaa	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	2 Rue Atlas	Quartier Medersa	Bir Mezoui	32.8557071	-6.5755623	\N	\N	\N	\N	f	Opérateur	+212647904867	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ed302dac-c5ee-4fc9-8b5c-03683119f89e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00575	Sanaa	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	56 Rue Atlas	Quartier Hay Salam	Boulanoir	32.8658707	-6.9131508	\N	\N	\N	\N	f	Sécurité	+212626362525	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	da223539-7489-40db-97d0-0915390de56c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00576	Kawtar	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	75 Rue de la Paix	Quartier Al Amal	Boulanoir	32.8931468	-6.8976114	\N	\N	\N	\N	f	Logisticien	+212649147052	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	62714d29-774f-421a-af17-ecc1109902af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00577	Issam	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	125 Rue Ifrane	Quartier Medersa	Hattane	32.8756872	-6.9108524	\N	\N	\N	\N	f	Analyste	+212631425810	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	47a89bbf-34ee-4086-8e1c-c4b3bdb07621	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00578	Tariq	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	132 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8937414	-6.9341252	\N	\N	\N	\N	f	Superviseur	+212674724642	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d749cdbe-0591-4cc8-87e3-93427db6d478	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00579	Ghita	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	S	61 Rue des Orangers	Quartier Hassania	Oued Zem	32.8633781	-6.5817138	\N	\N	\N	\N	f	Logisticien	+212689373879	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e74a43fb-42eb-4723-b09b-c04ad7357cae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00580	Malika	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	58 Rue Ifrane	Quartier Centre	Bir Mezoui	32.8662702	-6.9085002	\N	\N	\N	\N	f	Analyste	+212653339444	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	336b3ef1-ef73-4ee3-b511-2c9e2f59c318	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00581	Imane	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	97 Rue de la Paix	Quartier Centre	Khouribga	32.8558242	-6.549592	\N	\N	\N	\N	f	Logisticien	+212643842292	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	de1693c9-939b-491c-89a6-34494f34bc66	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00582	Othmane	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	108 Rue des Orangers	Quartier Centre	Khouribga	32.8560957	-6.8730023	\N	\N	\N	\N	f	Analyste	+212624970978	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bea28856-0a2e-492f-9646-2b030a03667a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00583	Bilal	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	103 Rue Al Massira	Quartier Anassi	Oued Zem	32.8894099	-6.9335256	\N	\N	\N	\N	f	Opérateur	+212673251558	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9bf7cb98-3d27-455b-8edf-1a8c44132381	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00584	Najat	Bennani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	169 Rue de la Paix	Quartier Hay Salam	Hattane	32.878069	-6.9034509	\N	\N	\N	\N	f	Technicien	+212696773222	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f0614a2f-4ce3-47e9-9f24-87dd18038608	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00585	Noureddine	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P1	25 Rue Mohammed V	Quartier Centre	Bir Mezoui	32.8948266	-6.90728	\N	\N	\N	\N	f	Électricien	+212653404854	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cffb06fe-4c51-4caa-ae7f-c24fd00333b2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00586	Mustapha	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	58 Rue Al Massira	Quartier Tamaris	Khouribga	32.8555239	-6.581117	\N	\N	\N	\N	f	Superviseur	+212638715232	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	351703c0-2c1a-426a-824d-3ffa8b0fccd4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00587	Siham	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	82 Rue des Orangers	Quartier Anassi	Boujniba	32.8601814	-6.8804718	\N	\N	\N	\N	f	Opérateur	+212610797559	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1b63540b-0e5d-4efe-8989-3c08bf359ca3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00588	Siham	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	N	20 Rue de la Paix	Quartier Medersa	Bir Mezoui	32.8557868	-6.564994	\N	\N	\N	\N	f	Sécurité	+212654871166	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e87bb1a5-6d52-4aa1-9836-c417aae2680f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00589	Hicham	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	182 Rue Hassan II	Quartier Al Amal	Boulanoir	32.8520484	-6.5724732	\N	\N	\N	\N	f	Électricien	+212679429252	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	043771ef-5a21-49dd-95f4-f4e026407c1a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00590	Saad	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	92 Rue Ifrane	Quartier Hay Salam	Boujniba	32.8677573	-6.5818682	\N	\N	\N	\N	f	Logisticien	+212620475822	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	94a80652-2692-4471-b210-96972d117a76	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00591	Ilham	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	P2	181 Rue des Orangers	Quartier Anassi	Hattane	32.8796203	-6.9016911	\N	\N	\N	\N	f	Qualité	+212654292008	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0ad1e2cd-bef0-47d6-a413-b6f5b0af5291	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00592	Siham	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	160 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.89656	-6.905592	\N	\N	\N	\N	f	Conducteur	+212620407075	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9b7e1fb7-e080-4bf8-a811-2db056f9b0b0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00593	Loubna	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	43 Rue Hassan II	Quartier Anassi	Boujniba	32.8598096	-6.5588353	\N	\N	\N	\N	f	Superviseur	+212679471676	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d9285e00-eaab-4dba-9999-2bcc1cd57e76	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00594	Sanaa	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	S	1 Rue Atlas	Quartier Al Wifaq	Boulanoir	32.90228	-6.6807799	\N	\N	\N	\N	f	Logisticien	+212633335811	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0b0f9ee4-715e-4ade-9991-a4ec2c35cbed	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00595	Ibrahim	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	129 Rue Ifrane	Quartier Hassania	Bir Mezoui	32.9194188	-6.7190131	\N	\N	\N	\N	f	Analyste	+212671339932	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	896f47b4-586d-499b-b108-33841d62e55d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00596	Ghita	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	16 Rue Ifrane	Quartier Centre	Bir Mezoui	32.8741102	-6.9257269	\N	\N	\N	\N	f	Logisticien	+212660844471	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	55e5439f-e4b4-44a7-be05-5bb65b4eab09	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00597	Ali	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P3	196 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8883018	-6.9003874	\N	\N	\N	\N	f	Technicien	+212655162134	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b090c8d5-571c-4f76-aafb-ed2d56c8a84c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00598	Jawad	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	163 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.8642147	-6.58513	\N	\N	\N	\N	f	Superviseur	+212616208374	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a56f01ac-0e78-4e17-8c36-0b7d9209c921	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00599	Soumia	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	79 Rue Ifrane	Quartier Centre	Oued Zem	32.8594911	-6.5637186	\N	\N	\N	\N	f	Administratif	+212695658339	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bd125c5f-41f3-4757-b143-64e165c4d960	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00600	Hassan	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	105 Rue de la Paix	Quartier Hassania	Khouribga	32.8758074	-6.9215706	\N	\N	\N	\N	f	Technicien	+212644970566	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6840669b-2774-4c38-b78b-4e4b39b83aab	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00601	Abdelilah	Chaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	186 Rue Hassan II	Quartier Centre	Gueffaf	32.8479446	-6.8777682	\N	\N	\N	\N	f	Comptable	+212679898685	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f459d907-3a9a-49c3-bd2a-f2f14c033b34	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00602	Youssef	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	79 Rue de la Paix	Quartier Hassania	Gueffaf	32.8913919	-6.9405063	\N	\N	\N	\N	f	Opérateur	+212611004510	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bfdd080f-06dd-4b56-ae07-ffe5d176c6e1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00603	Rajaa	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	N	157 Rue de la Paix	Quartier Al Wifaq	Boujniba	32.8409442	-6.7974699	\N	\N	\N	\N	f	Qualité	+212696037459	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	79348746-ad04-4418-b204-b2ae61223321	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00604	Houda	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	19 Rue de la Paix	Quartier Hay Mohammadi	Boujniba	32.8713544	-6.925428	\N	\N	\N	\N	f	Superviseur	+212633362254	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5fcf586e-7e87-4bd3-973f-f9a9f820bab2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00605	Fatima	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	60 Rue des Orangers	Quartier Al Amal	Bir Mezoui	32.8710992	-6.9282369	\N	\N	\N	\N	f	Technicien	+212678530888	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	839a81b7-662f-48e1-ac84-60257b27041d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00606	Laila	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	P2	121 Rue Atlas	Quartier Hay Mohammadi	Bir Mezoui	32.8949086	-6.9017198	\N	\N	\N	\N	f	Comptable	+212662863390	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	19563a5f-919e-4d54-862f-2ab16d198d0e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00607	Noureddine	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	167 Rue des Orangers	Quartier Hay Mohammadi	Khouribga	32.8569991	-6.8813604	\N	\N	\N	\N	f	Analyste	+212632482306	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	85755287-fc58-46c0-a8a6-fce3eacdbe2c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00608	Hafida	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	155 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.8927288	-6.7784673	\N	\N	\N	\N	f	Administratif	+212662861773	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	989faf75-6bc7-417b-996c-c92cf5462f93	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00609	Anass	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	S	195 Rue des Orangers	Quartier Medersa	Boujniba	32.8996932	-6.7692562	\N	\N	\N	\N	f	Mécanicien	+212636567825	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1b6f93ad-3beb-4140-99f4-c9ff7d7be88b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00610	Souad	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	110 Rue Mohammed V	Quartier Hay Mohammadi	Hattane	32.8784764	-6.9121118	\N	\N	\N	\N	f	Qualité	+212690053545	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	944920b3-f6be-4cea-aa99-f68afeaad883	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00611	Latifa	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	76 Rue Mohammed V	Quartier Medersa	Hattane	32.8980813	-6.8993991	\N	\N	\N	\N	f	Agent de maîtrise	+212625217137	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3dc2e0f-d2fa-4a43-8865-5e6d0b9bf743	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00613	Sanaa	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	185 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.835293	-6.8039756	\N	\N	\N	\N	f	Ingénieur	+212635120684	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	73730fee-a11e-4497-b758-faebc534cbca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00614	Zineb	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	180 Rue Ifrane	Quartier Hay Mohammadi	Khouribga	32.8968027	-6.7747553	\N	\N	\N	\N	f	Technicien	+212647459271	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b18c4100-0664-49a4-bb38-87033875d962	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00615	Jamila	Slaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	88 Rue Atlas	Quartier Hay Salam	Gueffaf	32.8978345	-6.9377607	\N	\N	\N	\N	f	Administratif	+212647161236	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0fd4dec7-5a45-4f37-8808-f248a38d7dad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00616	Fouad	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	120 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.8994297	-6.9054375	\N	\N	\N	\N	f	RH	+212685291630	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7d9f0259-6f76-42a7-ba7e-054b224dc557	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00617	Mohammed	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	142 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.88873	-6.8981113	\N	\N	\N	\N	f	Opérateur	+212625832071	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	11cc4f96-53d9-4441-a543-73bd5b9edc4f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00618	Ghita	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	N	24 Rue Ifrane	Quartier Al Amal	Gueffaf	32.8490969	-6.8793523	\N	\N	\N	\N	f	Sécurité	+212643728682	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	aa7c68f6-42e7-47b9-8056-1df959394d39	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00619	Ahmed	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	157 Rue Atlas	Quartier Anassi	Oued Zem	32.8647303	-6.5682497	\N	\N	\N	\N	f	Qualité	+212675210806	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e3dfd5bc-6d00-4d9a-9105-82c75b0048c6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00620	Mohammed	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	160 Rue Al Massira	Quartier Centre	Hattane	32.9045427	-6.676257	\N	\N	\N	\N	f	Technicien	+212665318844	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	40f8c5a1-a747-4f77-bc07-fd1f004f2b15	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00621	Bilal	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	180 Rue Hassan II	Quartier Hay Salam	Oued Zem	32.8534936	-6.8798004	\N	\N	\N	\N	t	Mécanicien	+212673076405	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f8b8048-16d2-477f-85a7-850a56650721	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00622	Wafae	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	114 Rue Mohammed V	Quartier Hay Mohammadi	Gueffaf	32.8636966	-6.5837735	\N	\N	\N	\N	f	Mécanicien	+212645617684	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6ba6b9ac-b572-40bb-9143-f05a54f2df1f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00623	Jawad	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	180 Rue Ifrane	Quartier Medersa	Boulanoir	32.9033064	-6.7842933	\N	\N	\N	\N	f	Administratif	+212632431080	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1e5db244-0223-419b-9959-52bb0693e4eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00624	Rajaa	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	S	144 Rue de la Paix	Quartier Hassania	Hattane	32.8529965	-6.5790395	\N	\N	\N	\N	f	Comptable	+212638777148	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	395cb367-d839-405b-af52-f52f0b1f2223	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00625	Othmane	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	121 Rue Ifrane	Quartier Anassi	Khouribga	32.8364754	-6.8001758	\N	\N	\N	\N	f	Sécurité	+212631566339	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7e9cfba0-32f7-4d57-be8d-5529b1cdba33	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00626	Bouchra	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	77 Rue Atlas	Quartier Al Wifaq	Boujniba	32.8624073	-6.8772363	\N	\N	\N	\N	f	Agent de maîtrise	+212626402190	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	13ea21f9-e259-47ac-9990-b975fa22cfaa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00627	Kawtar	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	152 Rue Hassan II	Quartier Al Amal	Gueffaf	32.8940266	-6.9039587	\N	\N	\N	\N	t	RH	+212634330102	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0435d4d1-a64c-448d-a321-7cf93e0e3c95	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00628	Youssef	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	115 Rue Hassan II	Quartier Hassania	Hattane	32.850418	-6.5723132	\N	\N	\N	\N	f	Électricien	+212620489068	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2904f3d3-96b5-4404-ad53-7d61e6b5decb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00629	Saad	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	154 Rue Mohammed V	Quartier Centre	Boujniba	32.8741051	-6.9119278	\N	\N	\N	\N	f	Électricien	+212664283076	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	13fc1d74-41a1-434b-932e-020920a4b9f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00630	Zakaria	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	81 Rue Hassan II	Quartier Centre	Bir Mezoui	32.8562595	-6.8701074	\N	\N	\N	\N	f	RH	+212697856255	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aa3d9c56-6bc2-4b40-8d43-7a60ca4799ab	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00631	Amina	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	15 Rue Al Massira	Quartier Anassi	Boujniba	32.8339979	-6.802737	\N	\N	\N	\N	f	Mécanicien	+212649983172	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b25418a9-ad5c-4427-914a-ee5b06d47c38	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00632	Amina	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	39 Rue Al Massira	Quartier Hassania	Gueffaf	32.8829614	-6.9040945	\N	\N	\N	\N	f	Qualité	+212663812191	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ef85263a-748f-41b6-982a-0e727d4cd528	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00633	Hamza	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	N	186 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8641678	-6.5791487	\N	\N	\N	\N	f	Sécurité	+212690276694	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6ca05b10-c39a-4f69-90c5-6c95e37bfe86	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00634	Ibrahim	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	26 Rue Al Massira	Quartier Medersa	Khouribga	32.8567746	-6.8712229	\N	\N	\N	\N	t	Administratif	+212649747602	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	79b0caf6-50e1-48fe-8685-be70eda40a3f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00635	Amina	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	17 Rue de la Paix	Quartier Al Amal	Oued Zem	32.8516826	-6.8763165	\N	\N	\N	\N	f	Technicien	+212613176399	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4857fae7-96fc-4ac7-91b7-03b7632a9ae5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00636	Ghita	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	169 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.9005617	-6.9420277	\N	\N	\N	\N	f	Technicien	+212618625868	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	67fe2e79-8c2f-49a0-9896-b86718e5dfee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00637	Fatima	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	156 Rue de la Paix	Quartier Al Amal	Bir Mezoui	32.8644581	-6.571086	\N	\N	\N	\N	f	Analyste	+212693129264	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	49ba9e51-1bda-469c-90d7-ebeb64b89570	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00638	Zakaria	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	149 Rue de la Paix	Quartier Hassania	Hattane	32.8948231	-6.8919238	\N	\N	\N	\N	f	Conducteur	+212655861227	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e6ea2b98-ad65-40b1-ada4-1b3e3ec60dba	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00639	Ibrahim	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	S	62 Rue de la Paix	Quartier Hay Mohammadi	Oued Zem	32.8911622	-6.8928197	\N	\N	\N	\N	f	Superviseur	+212687111409	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	18e23050-2aae-4921-80eb-4c1d4ad5acde	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00640	Rachid	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	39 Rue des Orangers	Quartier Hay Salam	Oued Zem	32.8683867	-6.5751789	\N	\N	\N	\N	f	Conducteur	+212623213238	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c7a800c8-892d-418e-a641-0fac5798bcce	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00641	Ahmed	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	89 Rue de la Paix	Quartier Hassania	Bir Mezoui	32.8571964	-6.8704909	\N	\N	\N	\N	f	RH	+212618613588	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b9873354-fdbe-45fa-9620-038e55f2a1e8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00642	Khadija	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	127 Rue Mohammed V	Quartier Centre	Hattane	32.8511497	-6.8791998	\N	\N	\N	\N	f	Superviseur	+212638865991	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9d9c9532-80cf-4dd3-b433-34aea4a6d855	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00643	Rachid	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	188 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.8765693	-6.9088755	\N	\N	\N	\N	f	Technicien	+212654134259	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	640c2d4a-a5c3-4028-8603-f6f190d2bff3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00644	Khalid	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	15 Rue des Orangers	Quartier Anassi	Khouribga	32.8933457	-6.8938258	\N	\N	\N	\N	f	Conducteur	+212642773051	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3061d210-bdf3-42ca-b914-2116b11b3d37	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00645	Mustapha	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	180 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8936331	-6.9279789	\N	\N	\N	\N	f	Sécurité	+212644002108	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	203f6a76-3c40-4282-ba0b-3110baa1e0bb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00646	Soufiane	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	48 Rue de la Paix	Quartier Anassi	Boujniba	32.8650235	-6.9044125	\N	\N	\N	\N	f	Électricien	+212610219042	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f6902175-d864-4abd-a3f4-c624efe0274b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00647	Tariq	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	77 Rue Atlas	Quartier Anassi	Oued Zem	32.8665953	-6.5843006	\N	\N	\N	\N	f	Technicien	+212661655582	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7386784f-10e6-4017-b01f-3a5ec062493c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00648	Zakaria	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	N	134 Rue Mohammed V	Quartier Medersa	Hattane	32.9004638	-6.776361	\N	\N	\N	\N	f	Conducteur	+212692698364	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	29dd3992-ba4e-4a40-8b56-155819899cd0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00649	Abdelilah	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	188 Rue Hassan II	Quartier Hay Mohammadi	Boujniba	32.8968947	-6.9418671	\N	\N	\N	\N	f	Électricien	+212625706694	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	190ce8b7-a4b4-4bbb-aac6-4592a936dfec	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00650	Anass	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	75 Rue Al Massira	Quartier Hassania	Oued Zem	32.8863231	-6.9329829	\N	\N	\N	\N	f	RH	+212659417476	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c37463b8-154e-499c-958d-8f612827b250	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00651	Samira	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	39 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.8592915	-6.5544259	\N	\N	\N	\N	f	Sécurité	+212627048916	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	22750115-0730-4128-ab74-323840f0f9f2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00652	Ilham	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	123 Rue Al Massira	Quartier Hay Mohammadi	Boulanoir	32.8421406	-6.8057669	\N	\N	\N	\N	f	RH	+212682331974	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a84a0e77-a970-4d27-b8f4-bea6592114f9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00653	Fatima	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	42 Rue Atlas	Quartier Anassi	Gueffaf	32.9068237	-6.7818382	\N	\N	\N	\N	f	RH	+212639356515	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f468d450-d403-4b29-9e36-84ff576295ca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00654	Ahmed	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	S	15 Rue Al Massira	Quartier Hay Salam	Oued Zem	32.9043171	-6.6819827	\N	\N	\N	\N	f	Mécanicien	+212612636776	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	61dd5f97-114b-45cc-98b2-080427fbcb1b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00655	Laila	Qasmi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	170 Rue Atlas	Quartier Anassi	Bir Mezoui	32.8887966	-6.9049074	\N	\N	\N	\N	f	Opérateur	+212678431537	Finance	t	company_bus	Non	f	f	0	t	\N	\N	\N	64e73fac-05db-4bb0-b8fb-1144f30f8b6a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00656	Kawtar	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	23 Rue Atlas	Quartier Tamaris	Bir Mezoui	32.8967254	-6.9098323	\N	\N	\N	\N	f	Conducteur	+212686565747	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7abead3d-058a-4fd8-9c2f-e3b4f85f78e5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00657	Omar	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	60 Rue des Orangers	Quartier Hay Salam	Hattane	32.8674582	-6.907857	\N	\N	\N	\N	f	Logisticien	+212618492396	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dc4355da-1688-4ee6-905d-9a8cf056abb5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00658	Rachid	Touhami	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	142 Rue de la Paix	Quartier Al Amal	Oued Zem	32.8764731	-6.9068307	\N	\N	\N	\N	f	Analyste	+212659723409	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	44c0295d-b82f-4f59-ab2e-d9bf2fd5076b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00659	Abdelilah	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	131 Rue Mohammed V	Quartier Centre	Khouribga	32.8875169	-6.8963429	\N	\N	\N	\N	f	Agent de maîtrise	+212628692834	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ed20c90f-b621-4429-a050-4f23b8c2385f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00660	Zineb	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P1	10 Rue Al Massira	Quartier Anassi	Gueffaf	32.9046083	-6.6805124	\N	\N	\N	\N	f	RH	+212650479066	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	db7c8868-f19d-4ad1-813b-d163ce235409	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00661	Anass	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	79 Rue des Orangers	Quartier Medersa	Boujniba	32.8556172	-6.8759122	\N	\N	\N	\N	f	Électricien	+212668396900	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	295406df-c795-4231-8fe2-d34d7fdc014c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00662	Houda	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	54 Rue Al Massira	Quartier Medersa	Hattane	32.8476968	-6.8003171	\N	\N	\N	\N	f	Administratif	+212610618556	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	09b69b68-fe80-4db3-a182-a9a6e013aa00	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00663	Lahcen	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	N	42 Rue Atlas	Quartier Centre	Bir Mezoui	32.8574412	-6.8712048	\N	\N	\N	\N	f	Administratif	+212631150575	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	be9d44e7-d4de-4357-a9fc-118e6985bc41	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00664	Najat	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	33 Rue Atlas	Quartier Hay Mohammadi	Khouribga	32.8510337	-6.5810571	\N	\N	\N	\N	f	Analyste	+212669419323	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d7850390-2c38-4f09-9981-7fb49900ef9f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00665	Ilham	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	3 Rue de la Paix	Quartier Anassi	Boujniba	32.9056187	-6.7789454	\N	\N	\N	\N	f	Mécanicien	+212662630450	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6c9044c5-2de9-4182-89af-2d0e6bb43e77	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00666	Hasnaa	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P2	143 Rue des Orangers	Quartier Hay Salam	Hattane	32.8850672	-6.8959686	\N	\N	\N	\N	f	Opérateur	+212631402623	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	33d939f0-4461-4a8e-8fee-9236ca476869	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00667	Othmane	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	151 Rue de la Paix	Quartier Medersa	Gueffaf	32.8571479	-6.8725546	\N	\N	\N	\N	f	RH	+212655225426	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f04271db-e15c-46bc-adee-6baea44a2d56	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00668	Tariq	Errahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	75 Rue Atlas	Quartier Medersa	Boujniba	32.8546568	-6.5705564	\N	\N	\N	\N	f	Conducteur	+212648592468	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	36511bd7-5963-4380-b861-89d990ce817a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00669	Ali	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	S	158 Rue Al Massira	Quartier Hay Mohammadi	Khouribga	32.890297	-6.9373767	\N	\N	\N	\N	f	Conducteur	+212631419977	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e8e7ff7f-cbc2-4371-b6d4-5f51c187243b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00670	Saad	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	59 Rue Al Massira	Quartier Centre	Boulanoir	32.8553048	-6.5802654	\N	\N	\N	\N	f	Comptable	+212677666347	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	73903a03-b30e-467c-a8c6-5bd9446d39f2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00671	Fatima	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	66 Rue Mohammed V	Quartier Al Wifaq	Bir Mezoui	32.8877612	-6.9210243	\N	\N	\N	\N	f	Superviseur	+212673897693	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5eda8fcc-edf7-4cda-acd1-a42b090ce8c6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00672	Amine	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	72 Rue des Orangers	Quartier Anassi	Boujniba	32.8715037	-6.9128122	\N	\N	\N	\N	f	Électricien	+212675201068	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	09c885a3-a398-44cd-89c8-62919f4c489e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00673	Hasnaa	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	135 Rue Ifrane	Quartier Hay Salam	Oued Zem	32.8990658	-6.6787118	\N	\N	\N	\N	f	Conducteur	+212634992526	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	909ff69c-f014-4ca0-9a22-a2bf7b7218dc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00674	Laila	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	100 Rue de la Paix	Quartier Medersa	Boujniba	32.8699115	-6.9088788	\N	\N	\N	\N	f	Superviseur	+212617355466	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4498334a-c69f-4724-be83-eb0607dea5f6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00675	Hafida	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	188 Rue Al Massira	Quartier Al Wifaq	Gueffaf	32.867541	-6.9095186	\N	\N	\N	\N	f	RH	+212649447289	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f432562f-7cca-4ed5-b914-82722f93af21	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00676	Wafae	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	47 Rue de la Paix	Quartier Hay Mohammadi	Bir Mezoui	32.8593606	-6.5817332	\N	\N	\N	\N	f	RH	+212661675037	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	48d83dae-03ca-477c-8416-da6aa2138283	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00677	Laila	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	27 Rue de la Paix	Quartier Medersa	Bir Mezoui	32.8934813	-6.9259643	\N	\N	\N	\N	f	Opérateur	+212631123894	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2e8da230-aa1d-42da-aaab-b5c0f71f08fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00678	Meryem	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	N	14 Rue Al Massira	Quartier Hay Salam	Hattane	32.8826656	-6.9280353	\N	\N	\N	\N	f	Comptable	+212659244576	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0e57d59b-1c21-4560-b7c2-68716b6fb935	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00679	Bouchra	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	22 Rue Mohammed V	Quartier Al Amal	Hattane	32.8364302	-6.7999207	\N	\N	\N	\N	f	Analyste	+212614115935	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	83a1ebe3-002f-4f10-b118-1a7c6509e2fa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00680	Hasnaa	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	104 Rue Mohammed V	Quartier Al Wifaq	Oued Zem	32.8535587	-6.5702322	\N	\N	\N	\N	f	Opérateur	+212688799165	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e2c1870a-c564-407a-81c6-be3dbd700a2f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00681	Laila	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	P2	88 Rue de la Paix	Quartier Anassi	Boulanoir	32.8832763	-6.924096	\N	\N	\N	\N	f	Électricien	+212650032357	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6c3e7ed5-2c9e-46e3-af1c-dc0c247faf3d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00682	Othmane	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	104 Rue Al Massira	Quartier Hassania	Gueffaf	32.8522036	-6.5768129	\N	\N	\N	\N	f	Opérateur	+212624309588	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7d2bc9a0-f22a-4bf4-96e7-cd5f224096e0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00683	Mehdi	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	93 Rue de la Paix	Quartier Hassania	Bir Mezoui	32.8522914	-6.5770282	\N	\N	\N	\N	t	Sécurité	+212644693614	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	135bf4f0-9d9e-42f0-b907-2b242cc36891	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00684	Malika	Hassouni	d39d79ec-a716-4839-a93d-1845d00c182c	S	77 Rue Atlas	Quartier Hay Mohammadi	Boulanoir	32.8726549	-6.9056503	\N	\N	\N	\N	f	Logisticien	+212640484787	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6455d641-4e77-4049-b65e-f2da92f1129a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00685	Fatima	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	190 Rue Atlas	Quartier Anassi	Oued Zem	32.8950814	-6.9068455	\N	\N	\N	\N	f	Administratif	+212610294548	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	45103e2d-64e4-4db4-bc00-dd12d234f7a0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00686	Ahmed	Bouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	120 Rue Mohammed V	Quartier Hay Salam	Bir Mezoui	32.8562017	-6.5713762	\N	\N	\N	\N	f	Mécanicien	+212634352062	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5b2f897b-559f-44f1-b01f-0dfc97d4460f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00687	Tariq	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	109 Rue Hassan II	Quartier Hassania	Gueffaf	32.8704684	-6.9278466	\N	\N	\N	\N	f	Analyste	+212613453482	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3a7004a-db81-4af9-ab52-e4e7296a6daa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00688	Nadia	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	138 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.8687726	-6.9063057	\N	\N	\N	\N	t	Analyste	+212687720403	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8a539838-6611-490e-9fc2-0b933f7d0b67	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00689	Souad	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	163 Rue des Orangers	Quartier Al Wifaq	Boujniba	32.8515995	-6.5706294	\N	\N	\N	\N	f	Qualité	+212618997224	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8c59746c-001e-4faa-a9db-9235d4109fff	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00690	Ali	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P1	143 Rue Hassan II	Quartier Al Amal	Khouribga	32.8839755	-6.9309265	\N	\N	\N	\N	f	Ingénieur	+212644241796	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c747a49a-37eb-4e41-92b9-bb5d4b2a8277	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00691	Nadia	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	153 Rue des Orangers	Quartier Tamaris	Boujniba	32.8786114	-6.907027	\N	\N	\N	\N	f	Électricien	+212678705868	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5f215037-2d92-41c5-8216-a0007bbc8588	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00692	Ahmed	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	68 Rue Atlas	Quartier Hay Mohammadi	Boulanoir	32.8509636	-6.5702656	\N	\N	\N	\N	f	Sécurité	+212635113777	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	abea1c57-d20e-4a24-bdc0-417bb74e1251	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00693	Soumia	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	N	111 Rue des Orangers	Quartier Medersa	Bir Mezoui	32.8958242	-6.9390333	\N	\N	\N	\N	f	Conducteur	+212614863073	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	260be184-4bf5-42b6-be6c-fb754def3e6f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00694	Khalid	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	186 Rue Al Massira	Quartier Tamaris	Oued Zem	32.9008763	-6.7780408	\N	\N	\N	\N	f	Logisticien	+212619814433	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6e8d83e8-9d37-467b-9857-067d6d23877f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00695	Rachid	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	173 Rue Ifrane	Quartier Centre	Hattane	32.8451984	-6.8025601	\N	\N	\N	\N	f	Électricien	+212664578984	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bdf5615c-634f-48a7-82f6-9343123dda64	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00696	Hafida	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	74 Rue des Orangers	Quartier Hassania	Gueffaf	32.8993078	-6.7834006	\N	\N	\N	\N	f	Opérateur	+212632086637	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	d6de75a5-e19f-4120-b047-d5ccd2a9dd7c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00697	Loubna	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	53 Rue Hassan II	Quartier Tamaris	Hattane	32.8559798	-6.5791641	\N	\N	\N	\N	f	Technicien	+212630604003	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e377edee-d610-40b3-81ca-5714285b13ac	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00698	Noureddine	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	181 Rue Al Massira	Quartier Hay Salam	Khouribga	32.8816539	-6.9203004	\N	\N	\N	\N	f	Conducteur	+212687917094	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	62b5f219-dd3d-416b-9211-5979b63db910	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00699	Kawtar	Zemmouri	d39d79ec-a716-4839-a93d-1845d00c182c	S	46 Rue de la Paix	Quartier Al Wifaq	Boujniba	32.8827969	-6.9237293	\N	\N	\N	\N	f	Comptable	+212668920331	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	548236bc-cf47-40d7-94fc-b35555f2b33d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00700	Khalid	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	196 Rue des Orangers	Quartier Tamaris	Oued Zem	32.897286	-6.7723668	\N	\N	\N	\N	f	Électricien	+212631813104	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8e0c8d31-0750-417b-8b1c-a3df828b83a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00701	Rachid	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	46 Rue Hassan II	Quartier Hay Mohammadi	Boujniba	32.8577371	-6.5517545	\N	\N	\N	\N	f	Technicien	+212619215490	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3191ca42-f429-46cd-b06d-3f59316b387d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00702	Hasnaa	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	162 Rue Atlas	Quartier Medersa	Hattane	32.8891854	-6.9182003	\N	\N	\N	\N	f	Technicien	+212667017669	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	98b64123-eabc-4229-966b-33b19f3efd3d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00703	Zineb	Ouazzani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	112 Rue Ifrane	Quartier Hassania	Boujniba	32.8987369	-6.7779039	\N	\N	\N	\N	f	Qualité	+212667856885	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	17f6ff3d-2aba-4d19-ac3b-0505734738c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00704	Bouchra	Mouttaki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	178 Rue Al Massira	Quartier Tamaris	Gueffaf	32.8967314	-6.7817139	\N	\N	\N	\N	f	Électricien	+212666495696	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b9b678a6-844c-4f85-905d-d8728cb74760	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00705	Hasnaa	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	P1	30 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.8720001	-6.9062883	\N	\N	\N	\N	f	Superviseur	+212663698936	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	80745948-c35b-4ec7-8825-21d28fe02725	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00706	Fatima	Hassouni	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	131 Rue Atlas	Quartier Tamaris	Gueffaf	32.8507842	-6.5705777	\N	\N	\N	\N	f	Électricien	+212655014488	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a53332f-25ef-43de-ad04-d5e18058b926	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00707	Tariq	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	130 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.8562482	-6.5560401	\N	\N	\N	\N	f	Électricien	+212657298608	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2a0810e6-8838-42f0-a1e2-3f856babe367	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00708	Ibrahim	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	N	145 Rue Mohammed V	Quartier Centre	Bir Mezoui	32.8990206	-6.9117869	\N	\N	\N	\N	f	Opérateur	+212687847529	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5109d1d7-e4b2-474e-b7fd-dca370981224	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00709	Ghita	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	128 Rue des Orangers	Quartier Anassi	Khouribga	32.8970594	-6.905184	\N	\N	\N	\N	f	Conducteur	+212699529207	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b45de17f-c9dc-4d29-9ce5-86a4aac0b9b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00710	Youssef	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	145 Rue Hassan II	Quartier Al Amal	Gueffaf	32.8416219	-6.8014388	\N	\N	\N	\N	f	Comptable	+212686497533	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	99546dea-6ae0-40fd-99ad-e47fa4675680	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00711	Souad	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P2	198 Rue Hassan II	Quartier Anassi	Khouribga	32.8622416	-6.5487148	\N	\N	\N	\N	f	Logisticien	+212671231957	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7083d1f8-51b2-4324-a998-154832fb6435	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00712	Loubna	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	81 Rue Ifrane	Quartier Centre	Oued Zem	32.899268	-6.6803251	\N	\N	\N	\N	f	Mécanicien	+212634971567	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6ad01a36-b308-4c4f-87a2-3acac39ce448	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00713	Soufiane	Bennani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	22 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.8724107	-6.9209508	\N	\N	\N	\N	f	Administratif	+212619325628	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9dc06027-3a1c-46a6-b67e-a7e0d3eaa540	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00714	Soumia	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	S	92 Rue de la Paix	Quartier Hassania	Oued Zem	32.8633667	-6.5723859	\N	\N	\N	\N	f	Électricien	+212680309479	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	65cf2841-0214-464e-8648-8cc302c88831	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00715	Mohammed	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	184 Rue Mohammed V	Quartier Al Amal	Khouribga	32.9221078	-6.7176528	\N	\N	\N	\N	f	Agent de maîtrise	+212675428565	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	92ccafa3-db6a-443a-b752-145b31ec07d9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00716	Jamila	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	172 Rue Atlas	Quartier Hay Salam	Boulanoir	32.8592446	-6.5573276	\N	\N	\N	\N	f	Conducteur	+212621780714	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	986bfecc-f074-4a88-9fe0-4d5f0f248399	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00717	Youssef	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	183 Rue Ifrane	Quartier Hassania	Boulanoir	32.8544755	-6.8798997	\N	\N	\N	\N	f	Conducteur	+212681894854	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dbe7cf8f-dddd-4cc0-9e09-b6f23323f34b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00718	Soufiane	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	99 Rue Al Massira	Quartier Medersa	Bir Mezoui	32.8570772	-6.5564224	\N	\N	\N	\N	t	Sécurité	+212654049036	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d177ba59-f0de-45a4-85d3-597b5ea7f5dd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00719	Aicha	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	65 Rue Al Massira	Quartier Centre	Bir Mezoui	32.8540167	-6.8758622	\N	\N	\N	\N	f	Logisticien	+212655097815	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	82e40032-f258-42e9-8c11-2cef93d3db55	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00720	Jawad	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P1	8 Rue de la Paix	Quartier Medersa	Oued Zem	32.8759528	-6.9205991	\N	\N	\N	\N	f	Superviseur	+212618878742	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ebc4fed1-7762-4fd3-b018-d09a67ac97a9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00721	Mustapha	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	194 Rue de la Paix	Quartier Hay Mohammadi	Boujniba	32.8560887	-6.574425	\N	\N	\N	\N	f	Ingénieur	+212659945481	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	311bc25a-b81c-4e33-bd60-568a324b8c06	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00722	Amine	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	109 Rue de la Paix	Quartier Hay Mohammadi	Bir Mezoui	32.9198035	-6.7138893	\N	\N	\N	\N	f	Ingénieur	+212630824416	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0e6e2cae-11a2-4408-a1fc-ad21beaac221	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00723	Bouchra	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	N	146 Rue Al Massira	Quartier Hay Salam	Boujniba	32.8834672	-6.9204997	\N	\N	\N	\N	f	Conducteur	+212648582428	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8c695fee-0c9b-4792-a5d4-3198335dcc19	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00724	Soufiane	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	95 Rue des Orangers	Quartier Hassania	Khouribga	32.9202594	-6.7148421	\N	\N	\N	\N	f	Superviseur	+212642036001	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	48ff64b9-f4ea-4b78-8682-e44855ceef45	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00725	Tariq	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	6 Rue de la Paix	Quartier Tamaris	Boujniba	32.8944679	-6.7782971	\N	\N	\N	\N	f	RH	+212617322250	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e4ab1bd6-3acc-4f34-be86-49cbb910636e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00726	Nadia	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	60 Rue Hassan II	Quartier Tamaris	Bir Mezoui	32.8699207	-6.9178677	\N	\N	\N	\N	f	Analyste	+212648189099	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6cb296fa-e3d4-4889-b320-9a799e8558e7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00727	Zineb	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	62 Rue Hassan II	Quartier Centre	Bir Mezoui	32.88647	-6.9026704	\N	\N	\N	\N	f	Électricien	+212616506636	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43534ce1-0c08-4d0c-85fe-4720f91ec0c7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00728	Saad	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	56 Rue Atlas	Quartier Tamaris	Hattane	32.857069	-6.5764318	\N	\N	\N	\N	f	Technicien	+212680059999	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	73987181-fba3-4b97-866b-b2d0d1ed3535	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00729	Samira	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	S	108 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.8560818	-6.5831038	\N	\N	\N	\N	f	Administratif	+212642294565	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6d1567ff-b6ae-4ae0-b2bd-c7a0f208ed0c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00730	Abdelilah	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	175 Rue Mohammed V	Quartier Al Amal	Hattane	32.8725562	-6.9132819	\N	\N	\N	\N	f	Logisticien	+212690610481	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	810f4998-b1bc-4a7d-8dbc-2acdac044d2d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00731	Ghita	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	159 Rue des Orangers	Quartier Hassania	Boujniba	32.882281	-6.908415	\N	\N	\N	\N	f	Électricien	+212641762246	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e49144b7-8234-4472-8b2b-12f9bbd16ece	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00732	Hasnaa	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P3	71 Rue de la Paix	Quartier Hay Salam	Hattane	32.860607	-6.5794989	\N	\N	\N	\N	f	Sécurité	+212623199500	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3f54088a-8b41-4849-92fd-492c1a199baa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00733	Rajaa	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	15 Rue Al Massira	Quartier Medersa	Oued Zem	32.8609934	-6.5785829	\N	\N	\N	\N	f	Agent de maîtrise	+212668872803	Finance	t	company_bus	Non	f	f	0	t	\N	\N	\N	cc781b16-2c95-41d6-92f4-48e3e3540ade	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00734	Laila	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	90 Rue des Orangers	Quartier Hay Salam	Boulanoir	32.8825945	-6.9209852	\N	\N	\N	\N	t	Sécurité	+212697887902	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2daeb944-216b-42c4-9052-ac008fa7f1d0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00735	Othmane	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	P1	111 Rue Mohammed V	Quartier Al Wifaq	Gueffaf	32.895129	-6.7757449	\N	\N	\N	\N	f	Sécurité	+212616146698	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	12c4747c-a902-4241-8d12-645545a1babe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00736	Mehdi	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	18 Rue Ifrane	Quartier Centre	Boujniba	32.8991044	-6.6793182	\N	\N	\N	\N	f	Superviseur	+212669308170	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	652f1c1a-16de-40d1-bd4d-8e0e93747d9d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00737	Noureddine	Qasmi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	120 Rue Al Massira	Quartier Medersa	Hattane	32.8878966	-6.9347908	\N	\N	\N	\N	f	Sécurité	+212697893251	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ee7dd159-701a-49ad-a32c-9c02f9a29d39	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00738	Latifa	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	N	101 Rue Mohammed V	Quartier Anassi	Boujniba	32.8532529	-6.5754496	\N	\N	\N	\N	f	Qualité	+212627331264	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f89fadfa-9310-410a-9e1a-cea8678a606c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00739	Lahcen	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	117 Rue Mohammed V	Quartier Al Amal	Boujniba	32.8827154	-6.9305989	\N	\N	\N	\N	f	Analyste	+212673995265	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1426a5a5-cb02-46d6-81ca-8ea3e76614af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00740	Mehdi	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	134 Rue Al Massira	Quartier Anassi	Bir Mezoui	32.887834	-6.9207743	\N	\N	\N	\N	f	Électricien	+212646154631	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e3541781-7d51-445e-818b-f6774397e54f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00741	Ahmed	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	18 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.8344087	-6.8066378	\N	\N	\N	\N	f	Mécanicien	+212678641218	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a306c881-6471-4652-b3e2-ba5d378abdae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00742	Tariq	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	3 Rue de la Paix	Quartier Al Wifaq	Gueffaf	32.8654866	-6.9045435	\N	\N	\N	\N	f	Électricien	+212659710490	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9552a897-f784-42da-afd7-7c926f568a8a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00743	Meryem	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	119 Rue Hassan II	Quartier Hay Mohammadi	Oued Zem	32.8985969	-6.7749427	\N	\N	\N	\N	f	Sécurité	+212646092965	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	17e1cb74-c9bb-42dd-b742-36fb3a53e0cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00744	Abdelilah	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	S	21 Rue Ifrane	Quartier Hassania	Gueffaf	32.8935621	-6.7725829	\N	\N	\N	\N	f	Sécurité	+212634477399	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6236e9f4-b780-44e1-880f-1f6d70f9904f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00745	Jawad	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	47 Rue de la Paix	Quartier Medersa	Khouribga	32.8990457	-6.7754796	\N	\N	\N	\N	t	Analyste	+212625016962	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e17c6bab-13dc-4384-91dc-3fe6bdc53e73	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00746	Fouad	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	9 Rue Ifrane	Quartier Hay Salam	Hattane	32.8826065	-6.9239799	\N	\N	\N	\N	f	Superviseur	+212689373628	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b23c6b47-dd3e-4296-a61f-7ed7c41aee04	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00747	Ilham	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	105 Rue de la Paix	Quartier Hay Mohammadi	Bir Mezoui	32.8582098	-6.5815222	\N	\N	\N	\N	f	Conducteur	+212611055635	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6a7e691c-97bf-4a58-93c7-1c0b9c53b65d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00748	Souad	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	59 Rue Atlas	Quartier Hay Mohammadi	Hattane	32.8710116	-6.9174978	\N	\N	\N	\N	f	Analyste	+212644896868	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f01e6fad-583b-46ba-b3da-fdb08ea99bde	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00749	Jamila	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	104 Rue de la Paix	Quartier Medersa	Khouribga	32.8623432	-6.5848736	\N	\N	\N	\N	f	Sécurité	+212676595021	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dcbd1f2d-ed08-45ca-a529-7b86d9407596	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00750	Rajaa	Slaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	51 Rue Mohammed V	Quartier Al Wifaq	Khouribga	32.9081509	-6.7808513	\N	\N	\N	\N	f	Technicien	+212617965095	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9fd96428-5850-4ff5-b50a-48a1a0630b7c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00751	Driss	Senhaji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	5 Rue de la Paix	Quartier Hay Salam	Bir Mezoui	32.8846648	-6.9315997	\N	\N	\N	\N	t	RH	+212629113181	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57ce7d9f-539b-41fd-9cd0-a0463125a602	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00752	Kawtar	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	6 Rue de la Paix	Quartier Medersa	Bir Mezoui	32.8886998	-6.9345556	\N	\N	\N	\N	f	Comptable	+212683507862	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eaa8b1bc-7463-4bb8-a9e0-0700aa6cd12b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00753	Karim	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	N	174 Rue Hassan II	Quartier Tamaris	Boujniba	32.888605	-6.9342349	\N	\N	\N	\N	f	Électricien	+212615657663	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6990b67a-bd42-46bc-ba08-dba6e9ebb3c0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00754	Hasnaa	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	145 Rue de la Paix	Quartier Al Amal	Hattane	32.8616468	-6.875147	\N	\N	\N	\N	f	Logisticien	+212682008141	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0321beaa-7a5e-4f19-813a-42847646510e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00755	Rachid	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	12 Rue Al Massira	Quartier Medersa	Gueffaf	32.901843	-6.7844624	\N	\N	\N	\N	f	Logisticien	+212635102616	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ccdc1b4b-3115-42b1-a036-c25b339b6a2a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00756	Hassan	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P2	83 Rue des Orangers	Quartier Al Wifaq	Oued Zem	32.9016656	-6.6800375	\N	\N	\N	\N	f	RH	+212646431716	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	995c64d8-42c1-41bf-9e04-a47b767bd0a4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00757	Khadija	Slaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	44 Rue Atlas	Quartier Hay Salam	Gueffaf	32.8530068	-6.8747776	\N	\N	\N	\N	f	Ingénieur	+212647866783	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	681b5ada-2b29-4aa5-b6cd-6ac8fb5e0023	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00758	Hanane	El Fassi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	68 Rue Al Massira	Quartier Al Wifaq	Boujniba	32.8960025	-6.7759402	\N	\N	\N	\N	f	Sécurité	+212682803418	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4aa30add-0f59-4126-9356-b3ef8b77a904	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00759	Amine	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	S	98 Rue Atlas	Quartier Hassania	Bir Mezoui	32.8751339	-6.9205166	\N	\N	\N	\N	f	Opérateur	+212662008280	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5d942f7a-e8b4-40bc-97ad-1270481f02e5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00760	Meryem	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	188 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8570606	-6.5788584	\N	\N	\N	\N	f	Administratif	+212622613925	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cc31617e-7ad3-446a-ae30-8ee023028e5f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00761	Mehdi	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	155 Rue Al Massira	Quartier Anassi	Hattane	32.8980317	-6.6785192	\N	\N	\N	\N	f	Électricien	+212635456905	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8cbc891d-ce0a-4d12-97b4-490af7e3dfaa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00762	Houda	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	P3	26 Rue des Orangers	Quartier Hassania	Boulanoir	32.8878657	-6.9045042	\N	\N	\N	\N	f	Sécurité	+212696098011	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	554646b3-50f0-4693-8ec2-0afced9acee3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00763	Ahmed	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	36 Rue Atlas	Quartier Hay Salam	Oued Zem	32.8815131	-6.9172163	\N	\N	\N	\N	f	Comptable	+212621523425	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e1c994f4-71bc-4dfe-960f-c88c6e1df6d3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00764	Zineb	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	75 Rue Atlas	Quartier Hassania	Boulanoir	32.8474162	-6.799949	\N	\N	\N	\N	f	Agent de maîtrise	+212649107279	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8ebed137-15aa-4d90-bf78-ff221c88e17f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00765	Mehdi	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	118 Rue Al Massira	Quartier Anassi	Oued Zem	32.8807007	-6.9241812	\N	\N	\N	\N	f	Électricien	+212629918564	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	146b3430-1285-454f-8576-f832a7ab17ae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00766	Tariq	Sahraoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	106 Rue des Orangers	Quartier Tamaris	Hattane	32.8448026	-6.8016397	\N	\N	\N	\N	f	Administratif	+212687545407	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c9573fad-c402-43d7-9055-7421901e86a1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00767	Meryem	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	61 Rue Al Massira	Quartier Hassania	Boujniba	32.8939866	-6.7754054	\N	\N	\N	\N	f	Superviseur	+212628709560	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d78ba08b-df92-48c1-b812-0d2148f07204	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00768	Hafida	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	N	187 Rue des Orangers	Quartier Al Wifaq	Gueffaf	32.8740464	-6.9170117	\N	\N	\N	\N	f	Technicien	+212671213910	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	14e26c4f-3518-447b-9307-424bcb49f24a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00769	Zakaria	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	26 Rue de la Paix	Quartier Hay Salam	Boulanoir	32.8520363	-6.571639	\N	\N	\N	\N	f	Conducteur	+212685862249	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	227701be-5d26-4d75-8cdd-ac6bb2dd728c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00770	Mehdi	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	17 Rue des Orangers	Quartier Al Wifaq	Khouribga	32.8555173	-6.5696688	\N	\N	\N	\N	f	Analyste	+212667790339	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	83bffd3e-5f79-4bdf-82fa-5d7bb7e525c8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00771	Soumia	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P2	110 Rue de la Paix	Quartier Al Amal	Hattane	32.9027443	-6.6747775	\N	\N	\N	\N	f	RH	+212632445539	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	24b8c019-4c03-4348-9e44-167387684a5a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00772	Tariq	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	161 Rue Al Massira	Quartier Al Wifaq	Boulanoir	32.9207924	-6.7140285	\N	\N	\N	\N	f	Qualité	+212654114356	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c882b4df-d384-43a4-917e-ce34f095fa06	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00773	Khadija	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	196 Rue Atlas	Quartier Hay Mohammadi	Hattane	32.8756508	-6.907515	\N	\N	\N	\N	f	Technicien	+212692921223	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3ea5a0e0-026b-4ebb-ab5c-4a1c7d75cbee	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00774	Mehdi	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	S	193 Rue Hassan II	Quartier Anassi	Hattane	32.8665795	-6.5837244	\N	\N	\N	\N	f	RH	+212699732949	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d6f15a1f-cb33-4110-8ea4-b2916f10c889	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00775	Zakaria	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	107 Rue Al Massira	Quartier Tamaris	Boulanoir	32.8533542	-6.8800511	\N	\N	\N	\N	f	RH	+212627888480	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0f4e9eea-c84f-4593-b063-29d171fe74d5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00776	Issam	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	24 Rue des Orangers	Quartier Hay Mohammadi	Bir Mezoui	32.8623942	-6.9074462	\N	\N	\N	\N	f	Comptable	+212664150708	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c3ba873e-4500-4302-923c-eb4557714470	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00777	Hasnaa	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	39 Rue Hassan II	Quartier Al Wifaq	Gueffaf	32.858746	-6.5693256	\N	\N	\N	\N	f	Conducteur	+212624660527	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	502da0e5-7373-4624-9baf-9936c2426ea8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00778	Samira	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	151 Rue Al Massira	Quartier Hassania	Boulanoir	32.8943203	-6.9313384	\N	\N	\N	\N	f	Comptable	+212642500998	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f3ad5a5-78c1-4f46-801f-5bd3e93c875d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00779	Saad	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	100 Rue de la Paix	Quartier Medersa	Boujniba	32.8667599	-6.5757341	\N	\N	\N	\N	f	Agent de maîtrise	+212647151883	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	827ea029-8614-46ed-80f6-26f506a13d28	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00780	Souad	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	176 Rue de la Paix	Quartier Anassi	Boujniba	32.87824	-6.9197566	\N	\N	\N	\N	f	Technicien	+212631606390	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2e556a0d-679b-485d-94fd-0f5f9e58bec2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00781	Fatima	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	141 Rue Atlas	Quartier Anassi	Hattane	32.8756268	-6.9171256	\N	\N	\N	\N	f	Ingénieur	+212689112443	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	876206e5-a9c7-4549-8b2f-e828d8e44792	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00782	Laila	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	72 Rue Atlas	Quartier Medersa	Khouribga	32.8389552	-6.8044093	\N	\N	\N	\N	t	Agent de maîtrise	+212679749917	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6b535f4e-3011-42a0-a2be-70ad0d43fc52	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00783	Soufiane	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	N	135 Rue Atlas	Quartier Anassi	Oued Zem	32.8863658	-6.9154665	\N	\N	\N	\N	f	Comptable	+212632792451	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1de93efb-8943-489f-8d12-27f859c2e034	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00784	Tariq	Hassouni	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	155 Rue Al Massira	Quartier Hay Salam	Boujniba	32.9253885	-6.7216416	\N	\N	\N	\N	f	Mécanicien	+212648793641	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	db271060-e55b-43ad-8955-1430949e21c5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00785	Mohammed	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	96 Rue Hassan II	Quartier Al Wifaq	Hattane	32.8970516	-6.9330093	\N	\N	\N	\N	f	Analyste	+212648726322	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c5ccfb8e-00ac-405b-8502-f6031648b80a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00786	Khalid	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	12 Rue de la Paix	Quartier Hassania	Hattane	32.8645188	-6.9089426	\N	\N	\N	\N	f	Opérateur	+212691908032	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57af88bb-509e-421b-9e33-767eda80f073	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00787	Noureddine	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	20 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8586236	-6.5630557	\N	\N	\N	\N	f	Technicien	+212660892067	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	71fdc431-8c0c-4e0a-b97e-57e575673644	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00788	Anass	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	151 Rue des Orangers	Quartier Hay Salam	Hattane	32.8791289	-6.9002941	\N	\N	\N	\N	f	Électricien	+212637505474	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b0aa48b7-aab4-4da4-a749-d1631c43b79f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00789	Fouad	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	S	139 Rue Al Massira	Quartier Hassania	Oued Zem	32.8578058	-6.8748555	\N	\N	\N	\N	f	Ingénieur	+212654580496	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a2779bfa-ae39-4f20-9c34-6653af3ed641	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00790	Fouad	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	87 Rue de la Paix	Quartier Hay Salam	Bir Mezoui	32.855142	-6.8774581	\N	\N	\N	\N	f	Sécurité	+212618168040	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5296bf96-4b23-45cb-85c8-11b29c090cfe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00791	Issam	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	71 Rue de la Paix	Quartier Hay Salam	Boujniba	32.9192144	-6.7214923	\N	\N	\N	\N	f	Administratif	+212638748166	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2a8eaaed-eb5b-47df-8bb7-fd32cacc8b48	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00792	Ahmed	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	P3	43 Rue des Orangers	Quartier Centre	Hattane	32.8704286	-6.9179037	\N	\N	\N	\N	f	Conducteur	+212644610439	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ce43614b-2e67-4678-a6e3-26f383b0c4cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00793	Khadija	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	25 Rue des Orangers	Quartier Al Amal	Oued Zem	32.8563607	-6.8762551	\N	\N	\N	\N	f	Logisticien	+212639623144	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	50fadef8-852a-4f3f-91f3-79e70619085b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00794	Khadija	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	92 Rue Ifrane	Quartier Hay Salam	Oued Zem	32.8954963	-6.7765145	\N	\N	\N	\N	f	Logisticien	+212622519328	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6a08e06e-4c25-4dd7-9686-1cff7dbed41b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00795	Ibrahim	Hassouni	d39d79ec-a716-4839-a93d-1845d00c182c	P1	142 Rue Al Massira	Quartier Hay Mohammadi	Khouribga	32.8965533	-6.9027343	\N	\N	\N	\N	f	Sécurité	+212639248192	RH	t	company_bus	Non	f	f	0	t	\N	\N	\N	31f60aeb-050b-4d73-9a34-fd6d2e45614f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00796	Souad	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	35 Rue des Orangers	Quartier Hay Salam	Boulanoir	32.8997597	-6.780383	\N	\N	\N	\N	f	Comptable	+212651717594	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5d40057b-91fc-4755-9699-76013ec330e5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00797	Hafida	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	148 Rue de la Paix	Quartier Hay Mohammadi	Boulanoir	32.8612524	-6.5515088	\N	\N	\N	\N	f	Sécurité	+212614471581	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	51ec9d71-e60d-433a-a961-44d021c73fa3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00798	Ahmed	Laaroussi	d39d79ec-a716-4839-a93d-1845d00c182c	N	168 Rue Atlas	Quartier Centre	Hattane	32.8966762	-6.9054506	\N	\N	\N	\N	f	Comptable	+212674930758	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	21d00dd0-8ce1-4531-bde3-aba1093fb08c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00799	Lahcen	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	176 Rue Mohammed V	Quartier Centre	Khouribga	32.8982092	-6.7844197	\N	\N	\N	\N	f	Analyste	+212651624389	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	49e20734-2c34-4a3a-9c2e-ad767cec1958	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00800	Mustapha	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	26 Rue Ifrane	Quartier Al Amal	Boujniba	32.8807713	-6.920695	\N	\N	\N	\N	f	RH	+212626257027	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	803322bb-8878-4f1c-934f-390d38674e1d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00801	Khalid	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P2	137 Rue Ifrane	Quartier Anassi	Hattane	32.891755	-6.777963	\N	\N	\N	\N	f	Électricien	+212627723884	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	1b8d088c-a861-4692-8cfc-752e3d8065a8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00802	Driss	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	82 Rue Mohammed V	Quartier Tamaris	Hattane	32.923938	-6.7156979	\N	\N	\N	\N	f	Agent de maîtrise	+212686415326	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	36f87c1c-35d5-4acb-936f-e8f5a4389523	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00803	Houda	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	80 Rue Atlas	Quartier Anassi	Hattane	32.8826136	-6.9334418	\N	\N	\N	\N	f	Administratif	+212640389372	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d6645c27-19e0-4975-9ab7-6580e2792559	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00804	Rajaa	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	200 Rue de la Paix	Quartier Tamaris	Hattane	32.8579692	-6.5659361	\N	\N	\N	\N	f	Comptable	+212611934575	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57fa1f71-4741-4e48-a366-564894246672	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00805	Karim	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	167 Rue Atlas	Quartier Hay Salam	Hattane	32.8612713	-6.5580654	\N	\N	\N	\N	f	Logisticien	+212697488252	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac307c81-2b4f-4d09-a5d8-d4536aead71d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00806	Bouchra	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	183 Rue Al Massira	Quartier Al Wifaq	Gueffaf	32.8661514	-6.9079399	\N	\N	\N	\N	f	Comptable	+212649798179	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0dbd7d37-11b3-49f4-99dc-8a4acc186080	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00807	Karim	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	52 Rue Atlas	Quartier Hay Salam	Khouribga	32.8982998	-6.9330368	\N	\N	\N	\N	f	Comptable	+212687291450	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	81cc5ed9-6749-4b74-aebd-8f3b16962d7f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00808	Hicham	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	154 Rue Ifrane	Quartier Hassania	Oued Zem	32.8656663	-6.8771869	\N	\N	\N	\N	f	Comptable	+212691078415	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8d678faf-dde7-4836-9211-9fd6455f1a9e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00809	Souad	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	139 Rue des Orangers	Quartier Centre	Hattane	32.8582508	-6.5559989	\N	\N	\N	\N	f	Conducteur	+212646143876	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2a949a22-f6db-4b7a-b80a-4a554b33b69b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00810	Mohammed	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	16 Rue de la Paix	Quartier Medersa	Hattane	32.8619812	-6.9081356	\N	\N	\N	\N	f	Administratif	+212650633384	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2f0d1ac1-891b-4c33-b253-05145cbf3230	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00811	Saad	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	113 Rue des Orangers	Quartier Al Wifaq	Boulanoir	32.8810359	-6.9223097	\N	\N	\N	\N	f	Administratif	+212664457612	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac4482e4-b50c-4515-9f31-ee6ca5980b17	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00812	Meryem	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	113 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8473908	-6.7986619	\N	\N	\N	\N	f	Comptable	+212641603289	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac3f69c0-b483-4cd7-907e-75ebbc6a0d30	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00813	Wafae	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	N	124 Rue Mohammed V	Quartier Hay Salam	Hattane	32.8727124	-6.9126704	\N	\N	\N	\N	f	Administratif	+212610285617	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	683f9370-c5f0-4a3f-869c-d2e4d0757763	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00814	Malika	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	1 Rue Al Massira	Quartier Anassi	Khouribga	32.8619698	-6.5846078	\N	\N	\N	\N	f	Qualité	+212684830414	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f3025442-d441-48e7-a797-b8b32bfdf45b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00815	Kawtar	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	57 Rue Mohammed V	Quartier Al Wifaq	Hattane	32.8936332	-6.9049431	\N	\N	\N	\N	f	Mécanicien	+212675688686	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	25171a11-e5c9-4c65-9b7e-c474407bde9b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00816	Bilal	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	47 Rue Al Massira	Quartier Al Amal	Boulanoir	32.8605193	-6.56946	\N	\N	\N	\N	f	Sécurité	+212662316877	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	64040e8b-fba7-4d70-bcde-70a502916aaa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00817	Amina	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	105 Rue Hassan II	Quartier Tamaris	Gueffaf	32.8964457	-6.7728789	\N	\N	\N	\N	f	Conducteur	+212671074230	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	976c1c2b-5dcd-4f24-a136-f35eae946f09	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00818	Ghita	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	100 Rue Atlas	Quartier Al Amal	Khouribga	32.851842	-6.5813138	\N	\N	\N	\N	f	Conducteur	+212644414787	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0641f63e-be34-4655-b860-fafc9fd6f9dc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00819	Adil	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	S	55 Rue Mohammed V	Quartier Hassania	Boulanoir	32.8595518	-6.5819189	\N	\N	\N	\N	f	Comptable	+212673519948	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d4f94f3e-ffde-4d51-a53b-13ad755cb2cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00820	Mustapha	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	69 Rue de la Paix	Quartier Al Amal	Boulanoir	32.8641334	-6.9029656	\N	\N	\N	\N	f	Sécurité	+212657719703	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f6e08ec0-7f3c-4399-9b45-76f00ad0fb9c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00821	Loubna	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	197 Rue Atlas	Quartier Centre	Boulanoir	32.8991678	-6.7773988	\N	\N	\N	\N	f	Comptable	+212666414664	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f76ae466-70d1-4b86-9a10-73a0b9b16551	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00822	Khadija	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	123 Rue Ifrane	Quartier Hay Mohammadi	Boujniba	32.8629483	-6.5594398	\N	\N	\N	\N	f	Logisticien	+212665046231	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cfa17e3f-515a-470d-9c4e-ec56770e2955	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00823	Lahcen	Mouttaki	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	145 Rue Al Massira	Quartier Hay Mohammadi	Boujniba	32.901939	-6.7825366	\N	\N	\N	\N	f	Mécanicien	+212634788631	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f170e005-50e4-491e-8284-f9c51e07ce34	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00824	Hanane	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	182 Rue de la Paix	Quartier Hay Mohammadi	Khouribga	32.8825966	-6.9199858	\N	\N	\N	\N	f	Analyste	+212631321114	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0c196b15-eaf8-41de-8244-12662ff1a58c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00825	Nadia	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	P1	103 Rue Ifrane	Quartier Medersa	Hattane	32.8981357	-6.7747317	\N	\N	\N	\N	f	Logisticien	+212624032302	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e738405d-cb3e-4f72-85e3-e1bf85216cf1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00826	Ali	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	171 Rue de la Paix	Quartier Hay Mohammadi	Boujniba	32.8855844	-6.9317574	\N	\N	\N	\N	f	Conducteur	+212633399106	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f80e1b3b-e309-4b84-ac6d-73287240e33a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00827	Ali	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	74 Rue de la Paix	Quartier Medersa	Hattane	32.8595862	-6.5486579	\N	\N	\N	\N	f	Sécurité	+212663235885	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c3b70451-f6db-4c87-8577-379781a277f8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00828	Abdelilah	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	4 Rue des Orangers	Quartier Hassania	Boujniba	32.8845589	-6.904214	\N	\N	\N	\N	f	RH	+212614890285	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	81d07fde-9f84-4b28-b8ee-630bb62dd5d9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00829	Meryem	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	119 Rue Mohammed V	Quartier Al Amal	Gueffaf	32.891592	-6.9218978	\N	\N	\N	\N	f	Technicien	+212646944513	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	54fbf2ab-16b0-4b8d-ab4b-339f2fd34bf1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00830	Sanaa	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	178 Rue Atlas	Quartier Hassania	Boujniba	32.8705808	-6.9127556	\N	\N	\N	\N	f	Agent de maîtrise	+212681874341	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3d51933-dfde-47b2-8452-2c007a502809	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00831	Ibrahim	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	127 Rue Mohammed V	Quartier Hay Mohammadi	Oued Zem	32.866019	-6.909472	\N	\N	\N	\N	f	Conducteur	+212693859243	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	30d2100b-f53c-447e-b086-c31abcc055b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00832	Fatima	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	146 Rue Al Massira	Quartier Hassania	Khouribga	32.9037686	-6.7753599	\N	\N	\N	\N	f	Ingénieur	+212634443891	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a087bb7d-f24b-4bb2-aa20-76460f3a9848	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00833	Zineb	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	14 Rue des Orangers	Quartier Al Amal	Boujniba	32.8898273	-6.8933865	\N	\N	\N	\N	f	Administratif	+212638027488	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fb2b6763-c646-408b-8f93-92f68a7da9e6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00834	Lahcen	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	S	43 Rue Al Massira	Quartier Hay Mohammadi	Boujniba	32.8975418	-6.9340219	\N	\N	\N	\N	f	Ingénieur	+212699225400	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f181eb53-a431-487e-8e2f-4d61efbd2f24	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00835	Khalid	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	129 Rue Ifrane	Quartier Al Wifaq	Bir Mezoui	32.8536287	-6.8764352	\N	\N	\N	\N	f	Sécurité	+212612092041	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c36efc2a-4e46-4530-9f4e-b797b3ea7310	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00836	Malika	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	179 Rue Al Massira	Quartier Hay Mohammadi	Hattane	32.8487183	-6.8755287	\N	\N	\N	\N	f	Technicien	+212690096123	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	12c9fba2-5e0b-4587-9ab7-de9e173e15a2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00837	Karim	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P3	52 Rue Atlas	Quartier Hay Salam	Oued Zem	32.8586012	-6.8766971	\N	\N	\N	\N	f	Conducteur	+212653110869	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3c9bd9f6-a251-4ac3-8d2e-6a7f1f76baa7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00838	Abdelilah	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	15 Rue Atlas	Quartier Hay Salam	Hattane	32.894679	-6.9410234	\N	\N	\N	\N	f	Comptable	+212645703626	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	36e59f9d-d4de-4abe-b90f-4baf4861eb2c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00839	Mehdi	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	197 Rue Atlas	Quartier Centre	Gueffaf	32.8496199	-6.5705217	\N	\N	\N	\N	f	Agent de maîtrise	+212677263373	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	87b58e72-8664-4bb7-bd55-c698376bde9b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00840	Ilham	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	P1	135 Rue Al Massira	Quartier Medersa	Bir Mezoui	32.8599274	-6.8754908	\N	\N	\N	\N	f	Opérateur	+212652158257	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	efbaefb4-fb4d-4843-9ba6-41deb03704f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00841	Meryem	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	44 Rue Hassan II	Quartier Hay Salam	Gueffaf	32.8538115	-6.8761811	\N	\N	\N	\N	f	Analyste	+212647006945	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7d4931f7-06c6-4aec-be09-027bbdaf9c3c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00842	Ghita	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	166 Rue des Orangers	Quartier Hay Salam	Boulanoir	32.8953433	-6.9067505	\N	\N	\N	\N	f	Administratif	+212658768843	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f75b849-e76d-4249-8523-9d85acc1e9c3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00843	Samira	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	N	159 Rue Al Massira	Quartier Hay Salam	Boulanoir	32.8802688	-6.8976369	\N	\N	\N	\N	f	Mécanicien	+212613520850	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0aa9cc58-cdb8-40bb-bd1a-5df48928aa10	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00844	Zineb	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	85 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.9232791	-6.7189512	\N	\N	\N	\N	f	Comptable	+212611568278	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5a9e831f-5c1f-469a-a295-11d80d2b5934	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00845	Othmane	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	191 Rue Atlas	Quartier Al Wifaq	Khouribga	32.9082869	-6.7836797	\N	\N	\N	\N	f	Opérateur	+212690411588	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	3a01c5bb-9ef7-4ae4-9379-92d2f7fc5677	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00846	Khadija	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	116 Rue Hassan II	Quartier Centre	Khouribga	32.8952553	-6.9298663	\N	\N	\N	\N	f	Électricien	+212644386022	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f1831778-525b-4e30-97dd-2aef60ecb641	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00847	Fouad	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	31 Rue Ifrane	Quartier Medersa	Oued Zem	32.8967447	-6.7783015	\N	\N	\N	\N	f	Sécurité	+212614270192	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fe4343e1-2ecb-4e8c-adb2-7a580f9e8d77	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00848	Karim	Lahlou	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	154 Rue Al Massira	Quartier Hassania	Oued Zem	32.8554833	-6.5755742	\N	\N	\N	\N	f	Électricien	+212665831043	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1f8dfe87-24c1-4507-9bd0-48ed885e2fe3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00849	Jawad	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	S	139 Rue Atlas	Quartier Centre	Oued Zem	32.8633468	-6.5529775	\N	\N	\N	\N	f	Administratif	+212667634749	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	39d1699e-fca0-4f64-b9b1-27451eb442ea	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00850	Mohammed	Mouttaki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	65 Rue de la Paix	Quartier Hassania	Khouribga	32.8805669	-6.9201333	\N	\N	\N	\N	f	Technicien	+212641233930	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c5b2ace2-8b71-4b0e-a0b0-615aa2a045cf	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00851	Jawad	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	28 Rue Ifrane	Quartier Anassi	Boulanoir	32.8778786	-6.906579	\N	\N	\N	\N	f	Superviseur	+212635219599	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4b0f7ea9-cade-491e-9ae2-47145ec0710f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00852	Omar	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	136 Rue Hassan II	Quartier Anassi	Gueffaf	32.8572553	-6.5757411	\N	\N	\N	\N	f	Sécurité	+212657953381	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	d276b83a-257d-4844-be0b-2129d9afeff8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00853	Fatima	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	179 Rue Ifrane	Quartier Hassania	Gueffaf	32.8696829	-6.9071576	\N	\N	\N	\N	f	Qualité	+212635405752	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	ca0ce8a8-84f2-42da-8485-04eaef4f52c1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00854	Meryem	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	23 Rue Ifrane	Quartier Hay Salam	Boulanoir	32.9003621	-6.76899	\N	\N	\N	\N	f	Analyste	+212661024314	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b8d5a4c6-b440-4bc4-b7d0-bd75ffdb6810	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00855	Bouchra	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	75 Rue Ifrane	Quartier Hay Salam	Boulanoir	32.84961	-6.5765268	\N	\N	\N	\N	f	Superviseur	+212669087132	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eac4b754-5f74-4f72-85ff-ffb2230f0760	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00856	Nadia	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	115 Rue Ifrane	Quartier Medersa	Oued Zem	32.8527662	-6.8747255	\N	\N	\N	\N	f	Qualité	+212646014048	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dff0259a-e581-4c7f-ba14-19105fc1ac61	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00857	Soumia	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	41 Rue Mohammed V	Quartier Al Amal	Bir Mezoui	32.8482675	-6.8786538	\N	\N	\N	\N	f	Ingénieur	+212673931573	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eeef2d97-6f20-4a8c-995d-078d4d9c02c9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00858	Tariq	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	N	90 Rue Mohammed V	Quartier Hay Salam	Boujniba	32.8587842	-6.8777798	\N	\N	\N	\N	f	Analyste	+212669332987	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	52290718-e6e4-4eef-8ac1-5bb3a2d00af1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00859	Lahcen	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	178 Rue Ifrane	Quartier Medersa	Khouribga	32.8618449	-6.9048225	\N	\N	\N	\N	f	Technicien	+212612145526	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4dbeb67a-4264-4b12-8e50-27ea1794f1e7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00860	Houda	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	37 Rue Hassan II	Quartier Al Amal	Bir Mezoui	32.8748295	-6.917214	\N	\N	\N	\N	f	Sécurité	+212659362575	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dca661e7-4f06-4d91-8656-0b82d95f58ca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00861	Zakaria	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	93 Rue des Orangers	Quartier Hassania	Boulanoir	32.9040182	-6.6756434	\N	\N	\N	\N	f	Administratif	+212682091664	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5ce34416-bde9-4f05-9cbf-5a4d66d186c2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00862	Noureddine	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	139 Rue des Orangers	Quartier Anassi	Gueffaf	32.9006102	-6.9047923	\N	\N	\N	\N	f	Sécurité	+212627362421	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fd943733-7edf-4967-a212-1e2b6ddfbd4f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00863	Jamila	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	98 Rue Ifrane	Quartier Al Wifaq	Hattane	32.8872376	-6.9322125	\N	\N	\N	\N	f	Superviseur	+212680354090	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	da7b565b-6f14-4dc4-acfe-67772e136804	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00864	Anass	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	S	183 Rue de la Paix	Quartier Hassania	Gueffaf	32.8756691	-6.9136813	\N	\N	\N	\N	f	Ingénieur	+212637280797	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2c28cab4-f5af-4c66-b62b-ed081d92f321	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00865	Samira	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	43 Rue Atlas	Quartier Al Wifaq	Khouribga	32.8895184	-6.9365989	\N	\N	\N	\N	f	Analyste	+212691076789	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	acca0450-28aa-4dc2-acd7-3d7a7b55c832	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00866	Hassan	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	9 Rue Atlas	Quartier Anassi	Bir Mezoui	32.8536401	-6.5813662	\N	\N	\N	\N	f	Comptable	+212628360476	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	ec80c87e-72a7-409f-967f-e3605e3d8c81	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00867	Lahcen	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	16 Rue de la Paix	Quartier Al Wifaq	Oued Zem	32.905082	-6.7689743	\N	\N	\N	\N	f	Opérateur	+212628804111	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9c4672a7-5ec1-407d-bde0-9e983bb15815	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00868	Khalid	Yakine	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	16 Rue Hassan II	Quartier Al Amal	Boulanoir	32.8592376	-6.5788331	\N	\N	\N	\N	f	Agent de maîtrise	+212640451035	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	90ac59c1-2ddc-4ace-9b44-1fd1d9e45c28	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00869	Adil	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	134 Rue Al Massira	Quartier Hay Salam	Boujniba	32.898155	-6.8984383	\N	\N	\N	\N	f	Qualité	+212669266581	Transport	t	company_bus	Non	f	f	0	t	\N	\N	\N	fba07129-47f3-440e-81b8-90ad9629f954	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00870	Ilham	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	18 Rue Atlas	Quartier Medersa	Khouribga	32.8586797	-6.574272	\N	\N	\N	\N	f	Technicien	+212684127809	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	29d1b65a-a77b-44ca-9ced-6008e498aba3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00871	Ahmed	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	120 Rue des Orangers	Quartier Al Amal	Oued Zem	32.8843571	-6.9274789	\N	\N	\N	\N	f	Agent de maîtrise	+212676888574	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a1900c8f-ffc5-4823-aa1f-b635f2424585	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00872	Karim	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	28 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.8629095	-6.5838667	\N	\N	\N	\N	f	Conducteur	+212615131871	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	39d8c596-3985-41d8-a403-83dcbcf485f5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00873	Amine	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	N	11 Rue Atlas	Quartier Anassi	Bir Mezoui	32.8420376	-6.802444	\N	\N	\N	\N	f	Électricien	+212684236221	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ae8cf162-8c7e-4bae-a0c2-d3baf6ba63fb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00874	Driss	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	33 Rue de la Paix	Quartier Tamaris	Hattane	32.8970255	-6.8987376	\N	\N	\N	\N	f	Administratif	+212630602440	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	476bbc01-f434-480b-8bdc-3d027802a097	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00875	Fouad	Zemmouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	116 Rue des Orangers	Quartier Hay Mohammadi	Hattane	32.865156	-6.5800645	\N	\N	\N	\N	f	Mécanicien	+212645419707	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	42b2b72b-158b-46ca-b756-42fa3d400c20	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00876	Karim	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	152 Rue Ifrane	Quartier Al Amal	Khouribga	32.8915836	-6.937471	\N	\N	\N	\N	t	RH	+212699293619	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac1da874-a685-4cf2-b67f-90bc403288d7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00877	Ghita	Benomar	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	191 Rue Hassan II	Quartier Hassania	Khouribga	32.8940648	-6.9253282	\N	\N	\N	\N	f	Comptable	+212656509386	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	af546b77-a745-4e89-a52b-44b42713e961	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00878	Amine	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	84 Rue Hassan II	Quartier Centre	Gueffaf	32.8964463	-6.7778955	\N	\N	\N	\N	f	Comptable	+212684553646	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2f82d394-9042-49ec-b802-38475762f7da	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00879	Rachid	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	S	171 Rue des Orangers	Quartier Hassania	Boulanoir	32.894779	-6.7780034	\N	\N	\N	\N	f	Sécurité	+212620948311	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3b46109-bdb4-446a-828c-81b62a04c09d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00880	Noureddine	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	145 Rue des Orangers	Quartier Tamaris	Bir Mezoui	32.9185172	-6.7223623	\N	\N	\N	\N	f	Sécurité	+212697682006	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	817c3e3a-4917-4ffc-af04-b7a4c252f47c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00881	Ahmed	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	164 Rue des Orangers	Quartier Medersa	Oued Zem	32.8779063	-6.9197433	\N	\N	\N	\N	f	Sécurité	+212688675689	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43661aa5-4202-4180-a43d-71635289a877	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00882	Hicham	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	196 Rue Mohammed V	Quartier Al Amal	Bir Mezoui	32.8773804	-6.9125382	\N	\N	\N	\N	f	Comptable	+212621692752	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	543b35e7-5ae4-4219-9954-f81d94c149c5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00883	Rachid	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	123 Rue de la Paix	Quartier Hay Salam	Gueffaf	32.8919931	-6.7763889	\N	\N	\N	\N	f	Agent de maîtrise	+212633037572	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b8fff096-271d-42eb-9302-b232ac2c6ee1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00884	Ghita	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	152 Rue Atlas	Quartier Centre	Boujniba	32.8667567	-6.9129025	\N	\N	\N	\N	f	Superviseur	+212621864467	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4ef9bb59-347d-4e52-ba7d-39618754c448	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00885	Malika	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	165 Rue Ifrane	Quartier Medersa	Khouribga	32.8986638	-6.7788654	\N	\N	\N	\N	f	Mécanicien	+212631503126	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	03eb704c-c45e-4d8d-bf2f-9a9c1a98550a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00886	Lahcen	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	7 Rue Hassan II	Quartier Al Wifaq	Khouribga	32.86601	-6.5810648	\N	\N	\N	\N	t	Logisticien	+212611081740	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cd582c3d-4f38-44df-8260-3e8dcfcb0963	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00887	Soufiane	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	81 Rue Mohammed V	Quartier Anassi	Khouribga	32.8966707	-6.7746967	\N	\N	\N	\N	f	Analyste	+212678368254	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7ee72022-6e94-4763-a3ab-e3a9c1bf4e86	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00888	Ilham	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	N	72 Rue des Orangers	Quartier Centre	Hattane	32.8974163	-6.7713242	\N	\N	\N	\N	f	Électricien	+212617668222	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6f5ea527-5d0f-4fef-bd4a-b7c2579c7b98	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00889	Lahcen	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	194 Rue Mohammed V	Quartier Hay Mohammadi	Oued Zem	32.9050636	-6.679726	\N	\N	\N	\N	f	Conducteur	+212660845754	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1d880575-d4e0-4769-84a2-7a30b2066e30	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00890	Mohammed	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	176 Rue Al Massira	Quartier Al Amal	Khouribga	32.8940086	-6.9346101	\N	\N	\N	\N	f	Conducteur	+212682755065	Informatique	t	company_bus	Non	f	f	0	t	\N	\N	\N	d4c9b305-bcf6-4be9-b2e7-17285f9d35f2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00891	Youssef	Bouali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	50 Rue Ifrane	Quartier Anassi	Hattane	32.8660014	-6.5649291	\N	\N	\N	\N	f	Mécanicien	+212690541478	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e17f6cac-068c-468f-8731-3b90ac556487	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00892	Khadija	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	33 Rue des Orangers	Quartier Hay Salam	Gueffaf	32.8834633	-6.9046063	\N	\N	\N	\N	f	Comptable	+212668650528	Finance	t	company_bus	Non	f	f	0	t	\N	\N	\N	318cb526-95e7-46ab-b19c-1b87464f719f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00893	Houda	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	102 Rue de la Paix	Quartier Centre	Khouribga	32.8889471	-6.9370079	\N	\N	\N	\N	f	Technicien	+212687226050	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	504a46d8-86b9-440a-af42-e2b1947c1198	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00894	Zakaria	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	S	163 Rue de la Paix	Quartier Hay Salam	Bir Mezoui	32.8657519	-6.567613	\N	\N	\N	\N	f	Mécanicien	+212672060047	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	012c2579-c093-48d2-a80e-7a8c565df899	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00895	Najat	El Mansouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	22 Rue Mohammed V	Quartier Hay Mohammadi	Boujniba	32.8885805	-6.9039468	\N	\N	\N	\N	f	Logisticien	+212661427843	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7cd56227-b55e-4488-be09-55ce1a101750	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00896	Ghita	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	26 Rue Hassan II	Quartier Al Amal	Hattane	32.8889266	-6.9362205	\N	\N	\N	\N	f	Administratif	+212647880494	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	22c17516-db2f-4a02-8aa1-eaaae4d90efa	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00897	Ghita	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	117 Rue Ifrane	Quartier Hay Salam	Oued Zem	32.8646964	-6.5722432	\N	\N	\N	\N	f	Opérateur	+212684381069	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e22efd62-f9c2-4ba1-a4e3-e5a4bb3c2dd2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00898	Hicham	Benomar	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	159 Rue Ifrane	Quartier Hassania	Bir Mezoui	32.8746631	-6.9086724	\N	\N	\N	\N	f	Électricien	+212613756140	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cee6e091-85b2-43bc-aeab-1bc1045944d1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00899	Khalid	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	144 Rue Al Massira	Quartier Al Wifaq	Oued Zem	32.8639322	-6.5630007	\N	\N	\N	\N	f	Ingénieur	+212614031328	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f10f80d1-0bad-4c1f-a37d-842d5d900f6b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00900	Zineb	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	116 Rue de la Paix	Quartier Hay Salam	Gueffaf	32.8650123	-6.5787745	\N	\N	\N	\N	f	RH	+212610334901	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cee97acb-af8a-4441-b1d2-88d9739590a4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00901	Zineb	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	33 Rue Atlas	Quartier Al Amal	Khouribga	32.8765025	-6.9074575	\N	\N	\N	\N	t	Administratif	+212669287180	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1ebdaf6b-30cd-4b88-8a74-0907e0b9d4f0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00902	Laila	Chraibi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	84 Rue Mohammed V	Quartier Hay Mohammadi	Gueffaf	32.8987317	-6.6829923	\N	\N	\N	\N	f	Agent de maîtrise	+212629393885	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b4bbb422-c055-4640-a7cf-a4690287c691	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00903	Mehdi	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	N	159 Rue des Orangers	Quartier Medersa	Hattane	32.872495	-6.9155998	\N	\N	\N	\N	f	Mécanicien	+212660372814	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	430f6866-9944-4d91-8809-756744d468a1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00904	Najat	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	49 Rue des Orangers	Quartier Al Wifaq	Hattane	32.8883464	-6.9286633	\N	\N	\N	\N	f	RH	+212686853826	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	36520bef-f283-4592-b6e6-c119d029eec7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00905	Soufiane	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	185 Rue des Orangers	Quartier Centre	Oued Zem	32.8994016	-6.7834621	\N	\N	\N	\N	f	Opérateur	+212610060242	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b0b70da0-c418-481a-9cbc-bdea411a6925	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00906	Amine	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	68 Rue de la Paix	Quartier Al Wifaq	Boujniba	32.8988829	-6.7763827	\N	\N	\N	\N	f	Électricien	+212669769441	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8d2bf872-e6ba-45a7-8074-f8721c24d05b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00907	Houda	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	151 Rue des Orangers	Quartier Centre	Hattane	32.8871799	-6.8972849	\N	\N	\N	\N	f	Conducteur	+212652464559	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	30762b5b-b63e-47a3-8330-c98a3ef7fa5c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00908	Fatima	Zemmouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	153 Rue Atlas	Quartier Hassania	Boujniba	32.9016782	-6.9107147	\N	\N	\N	\N	f	Opérateur	+212670445539	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e77e37d4-ec37-4c51-b014-566cb608f919	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00909	Amine	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	S	19 Rue Hassan II	Quartier Anassi	Gueffaf	32.8705357	-6.9079263	\N	\N	\N	\N	f	Mécanicien	+212685097412	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ded4aa7d-0055-4e96-9aad-d0103433403a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00910	Latifa	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	34 Rue Al Massira	Quartier Hay Mohammadi	Hattane	32.8916962	-6.9364934	\N	\N	\N	\N	f	Agent de maîtrise	+212690332670	Administration	t	company_bus	Non	f	f	0	t	\N	\N	\N	62a78833-945b-4b55-8f51-dc2415e0ffb1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00911	Wafae	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	60 Rue de la Paix	Quartier Hassania	Boujniba	32.8649782	-6.5710853	\N	\N	\N	\N	f	Sécurité	+212676345875	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	421dfacd-a529-448d-a171-4d0be7b20aad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00912	Hafida	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	180 Rue des Orangers	Quartier Hay Salam	Bir Mezoui	32.8601141	-6.8745205	\N	\N	\N	\N	f	Agent de maîtrise	+212695685565	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5cdff2a2-21f1-45c5-8de0-0e671d9e9c2d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00913	Ilham	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	57 Rue Al Massira	Quartier Al Amal	Bir Mezoui	32.8609895	-6.5643091	\N	\N	\N	\N	f	Qualité	+212683986100	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	98c221bd-97c7-483a-9f6d-ad7cf77da4e0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00914	Driss	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	196 Rue Mohammed V	Quartier Centre	Bir Mezoui	32.8581444	-6.5502546	\N	\N	\N	\N	f	Ingénieur	+212669007992	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7c0f7759-b0d4-49e3-bcf0-21d4ea8bb5b8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00915	Laila	Laaroussi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	174 Rue Al Massira	Quartier Al Wifaq	Gueffaf	32.903271	-6.781643	\N	\N	\N	\N	f	Superviseur	+212612085955	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c4c52cfb-1527-4422-bdc8-49744304a9d5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00916	Noureddine	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	54 Rue Ifrane	Quartier Al Wifaq	Oued Zem	32.853274	-6.8768327	\N	\N	\N	\N	f	Conducteur	+212629533775	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	06c506cf-55c3-49bb-a307-c4a7f167db33	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00917	Meryem	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	193 Rue de la Paix	Quartier Medersa	Gueffaf	32.9234887	-6.7171877	\N	\N	\N	\N	f	Logisticien	+212626700995	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	63f9a56f-ded0-4567-9cae-04b3930576df	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	12e1f182-78d1-4a9d-b126-7480b5757fb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00918	Fatima	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	N	133 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.8938678	-6.8979282	\N	\N	\N	\N	t	Sécurité	+212637486353	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	428a92bf-462b-4165-8f98-50555d710423	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00919	Naima	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	70 Rue Ifrane	Quartier Al Amal	Boulanoir	32.8553718	-6.5704677	\N	\N	\N	\N	t	Mécanicien	+212630670007	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	42449232-3524-47ee-bb4e-2830a71b0ee4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00920	Samira	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	159 Rue Al Massira	Quartier Hassania	Boulanoir	32.8840229	-6.9295539	\N	\N	\N	\N	f	Analyste	+212689993612	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c735cf22-6b0d-4303-a952-149bf22b2113	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00921	Hicham	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	168 Rue Al Massira	Quartier Al Wifaq	Khouribga	32.8701025	-6.9144439	\N	\N	\N	\N	f	Conducteur	+212678334875	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f08df5c-1602-4813-ab4f-e20462b6f05b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00922	Nadia	Mouttaki	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	93 Rue Al Massira	Quartier Hay Mohammadi	Khouribga	32.8996761	-6.9422719	\N	\N	\N	\N	f	Administratif	+212623567535	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f2c871ab-bb48-40dc-af9d-501bc7b0174c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00923	Hasnaa	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	173 Rue Ifrane	Quartier Hay Salam	Khouribga	32.861521	-6.572972	\N	\N	\N	\N	f	Superviseur	+212683562962	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	09eeb59c-5758-4c8a-a326-3c35f7b0290b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00924	Rachid	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	153 Rue Al Massira	Quartier Centre	Gueffaf	32.9027417	-6.7795414	\N	\N	\N	\N	f	Logisticien	+212630450640	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1ea7dae9-5ee5-4a77-a005-e291b9899ff4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00925	Jawad	Ouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	190 Rue Al Massira	Quartier Tamaris	Boujniba	32.8941713	-6.7793162	\N	\N	\N	\N	f	Administratif	+212615894844	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bf2f60cf-53cd-451d-8277-3a938a552bf3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00926	Fatima	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	74 Rue de la Paix	Quartier Medersa	Gueffaf	32.8971069	-6.9051029	\N	\N	\N	\N	f	Électricien	+212659156371	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ed141256-79d8-4731-9048-c2c806c5d989	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00927	Imane	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	P3	79 Rue Mohammed V	Quartier Anassi	Hattane	32.8814787	-6.9234697	\N	\N	\N	\N	f	Logisticien	+212642109787	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d65e695b-db0d-4c86-b05e-f7cefb8dc0be	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00928	Ibrahim	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	60 Rue Al Massira	Quartier Hay Salam	Boujniba	32.8547746	-6.57329	\N	\N	\N	\N	f	Logisticien	+212661475870	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b6049528-6f4b-4b52-a555-57b181243a29	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00929	Hasnaa	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	127 Rue de la Paix	Quartier Hay Mohammadi	Hattane	32.8937531	-6.938336	\N	\N	\N	\N	f	Comptable	+212676229651	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b1fec2d3-3a5b-4030-9afb-28cb3a11c23b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00930	Adil	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P1	2 Rue de la Paix	Quartier Al Amal	Oued Zem	32.8898503	-6.8973522	\N	\N	\N	\N	f	Analyste	+212656499712	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9395e1c6-d8fe-4609-bb92-5e06f3aedc1a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00931	Lahcen	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	23 Rue de la Paix	Quartier Hay Mohammadi	Gueffaf	32.8812557	-6.9141174	\N	\N	\N	\N	f	Administratif	+212695344913	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c4aa358e-d2bc-40fb-a62f-005ee9f5b7a9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00932	Hassan	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	89 Rue de la Paix	Quartier Al Wifaq	Gueffaf	32.8894837	-6.9142276	\N	\N	\N	\N	f	Superviseur	+212674839788	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bc8cb8ac-96eb-4e87-a87b-17f8f9cde21b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00933	Mohammed	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	N	35 Rue Mohammed V	Quartier Anassi	Boujniba	32.9050462	-6.6780165	\N	\N	\N	\N	f	Superviseur	+212634735079	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aaef5c04-6477-4aac-82bd-ef608fad6833	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00934	Bilal	Zemmouri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	166 Rue Al Massira	Quartier Medersa	Khouribga	32.8626114	-6.5677458	\N	\N	\N	\N	f	Agent de maîtrise	+212692989426	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c0e18f84-a2bd-4793-905d-5e9aa4f3dfbd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00935	Imane	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	40 Rue Mohammed V	Quartier Hay Salam	Hattane	32.879322	-6.9153372	\N	\N	\N	\N	f	RH	+212690884446	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d7c5a8e0-65c8-4e90-918e-1eebf689692e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00936	Hafida	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	P2	54 Rue des Orangers	Quartier Al Wifaq	Hattane	32.8989303	-6.7731751	\N	\N	\N	\N	f	Technicien	+212673440646	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1f5a1292-1384-426d-9d29-190de5f9986a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00937	Hicham	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	181 Rue des Orangers	Quartier Anassi	Oued Zem	32.8881729	-6.8977811	\N	\N	\N	\N	f	Agent de maîtrise	+212621411617	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f9b418b5-b58e-4862-9057-099b7bb4c3ae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00938	Mohammed	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	72 Rue Al Massira	Quartier Anassi	Hattane	32.8981646	-6.7734848	\N	\N	\N	\N	f	Technicien	+212676833996	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	589437f4-2c4c-4032-9aa8-a91ef9c400e0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00939	Jamila	El Mansouri	d39d79ec-a716-4839-a93d-1845d00c182c	S	87 Rue des Orangers	Quartier Medersa	Hattane	32.8872194	-6.93115	\N	\N	\N	\N	f	Opérateur	+212662822685	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dfb371bb-25de-459d-8efc-884c9777f5b6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00940	Soufiane	Lahlou	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	116 Rue Ifrane	Quartier Tamaris	Hattane	32.8952245	-6.9400524	\N	\N	\N	\N	f	Administratif	+212669357722	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4d0a4d65-efc0-4f9f-a02b-141cf4f5c7fd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00941	Driss	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	100 Rue Atlas	Quartier Hassania	Hattane	32.9046783	-6.6750204	\N	\N	\N	\N	f	Ingénieur	+212610613729	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d1b06bbe-d19f-4345-82a3-d09d763738e9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00942	Ali	El Kabbaj	d39d79ec-a716-4839-a93d-1845d00c182c	P3	89 Rue Mohammed V	Quartier Hassania	Bir Mezoui	32.8649392	-6.877425	\N	\N	\N	\N	f	Administratif	+212621783702	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5abb0e39-b4d8-4249-98c6-a8a61f1edf95	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00943	Othmane	Khattabi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	113 Rue Ifrane	Quartier Hassania	Oued Zem	32.9056057	-6.6812502	\N	\N	\N	\N	f	Ingénieur	+212630977917	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	da97569b-c600-48ae-b463-084776eb604f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00944	Soufiane	Mouttaki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	43 Rue Ifrane	Quartier Anassi	Khouribga	32.8921044	-6.778192	\N	\N	\N	\N	f	Mécanicien	+212663017727	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57674498-62f3-4e74-ac19-185fc2e657bc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00945	Ghita	Mekki	d39d79ec-a716-4839-a93d-1845d00c182c	P1	180 Rue Atlas	Quartier Hay Salam	Khouribga	32.8850773	-6.9303424	\N	\N	\N	\N	f	Comptable	+212661836941	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fd592d9b-0e78-49a1-8d0d-236fafb25285	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00946	Meryem	Ouazzani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	174 Rue Atlas	Quartier Hassania	Bir Mezoui	32.8741761	-6.9118493	\N	\N	\N	\N	f	Analyste	+212660747903	Maintenance	t	company_bus	Non	f	f	0	t	\N	\N	\N	0939653f-ee56-4371-a853-6664a8c54cf9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00947	Ahmed	Lamrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	170 Rue Al Massira	Quartier Anassi	Boulanoir	32.8750966	-6.9204843	\N	\N	\N	\N	f	Opérateur	+212663426963	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1f0fbdfb-1a9a-4344-bcc7-9da206a55083	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00948	Hanane	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	N	190 Rue de la Paix	Quartier Tamaris	Bir Mezoui	32.9005594	-6.6850268	\N	\N	\N	\N	f	Mécanicien	+212641768102	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9ed37631-0cc7-456b-a959-c56855dbf313	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00949	Khalid	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	191 Rue Al Massira	Quartier Medersa	Boujniba	32.8635982	-6.5788758	\N	\N	\N	\N	f	Qualité	+212646900318	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cbff1874-1ae1-4df8-843e-0ff1cb32766a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00950	Meryem	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	132 Rue Mohammed V	Quartier Centre	Oued Zem	32.8655679	-6.9200808	\N	\N	\N	\N	f	Mécanicien	+212696203639	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cab90055-e1a1-4b76-a81e-35769bbe835a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00951	Rachid	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P2	135 Rue Mohammed V	Quartier Medersa	Gueffaf	32.8573368	-6.5762995	\N	\N	\N	\N	f	Mécanicien	+212645374188	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	70fa4413-2a6c-46e0-a26f-53d1dd1590d8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00952	Bilal	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	186 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.8642014	-6.5804834	\N	\N	\N	\N	f	Administratif	+212620492952	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	84aed3b6-8426-4058-a3ea-730a180ecede	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00953	Hamza	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	193 Rue Ifrane	Quartier Hay Mohammadi	Boulanoir	32.9183983	-6.7230868	\N	\N	\N	\N	f	Agent de maîtrise	+212668839409	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1a4e1a7b-8b81-4c21-b1ae-57921961bccc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00954	Saad	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	S	29 Rue Al Massira	Quartier Tamaris	Hattane	32.9019193	-6.9332121	\N	\N	\N	\N	t	Conducteur	+212637274152	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	57a80dd8-d268-469a-8236-dd5775c42691	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00955	Zakaria	Chaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	29 Rue Al Massira	Quartier Hay Mohammadi	Bir Mezoui	32.857567	-6.8761193	\N	\N	\N	\N	f	Conducteur	+212666402927	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	846aa9ea-b7a4-4a6c-bd2d-403ed15d2ff2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00956	Hicham	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	148 Rue Ifrane	Quartier Anassi	Khouribga	32.8679126	-6.5780684	\N	\N	\N	\N	f	Qualité	+212694629552	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	028a7420-cf01-4496-bff1-5352289ad7f1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00957	Noureddine	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P3	95 Rue des Orangers	Quartier Centre	Boulanoir	32.8899947	-6.9341815	\N	\N	\N	\N	f	Technicien	+212627984681	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	31c2272b-01b7-42d0-9e85-82107bacdff0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00958	Laila	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	131 Rue Mohammed V	Quartier Hay Mohammadi	Boujniba	32.8515925	-6.5769887	\N	\N	\N	\N	f	RH	+212693124699	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9d33735f-c79e-4650-b104-281f986c0e19	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00959	Ahmed	Sahraoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	25 Rue des Orangers	Quartier Anassi	Gueffaf	32.8626344	-6.564552	\N	\N	\N	\N	f	Agent de maîtrise	+212610974544	Transport	t	company_bus	Non	f	f	0	t	\N	\N	\N	52ce065a-68a5-4ac6-9f88-096b2f4771c2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00960	Fouad	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P1	71 Rue des Orangers	Quartier Hay Salam	Bir Mezoui	32.8809684	-6.9147388	\N	\N	\N	\N	f	Logisticien	+212698651668	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6c03df70-bb96-4adc-bc70-b0afcb2791dd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00961	Tariq	Naciri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	71 Rue Ifrane	Quartier Hay Mohammadi	Gueffaf	32.8774522	-6.9261534	\N	\N	\N	\N	f	Superviseur	+212618708168	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0b84ff75-79a2-47b6-b500-1f22c78a1a7f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00962	Sanaa	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	161 Rue de la Paix	Quartier Centre	Khouribga	32.8953651	-6.777304	\N	\N	\N	\N	f	Conducteur	+212671533737	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1a4096d6-811b-4894-96c5-56301f58e505	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00963	Mustapha	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	N	157 Rue Atlas	Quartier Hay Salam	Bir Mezoui	32.9013937	-6.9399657	\N	\N	\N	\N	f	Superviseur	+212697716595	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3daefe90-e307-4f4d-b0ea-ef7a410bc5e4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00964	Wafae	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	24 Rue Atlas	Quartier Hay Salam	Oued Zem	32.8503945	-6.8735972	\N	\N	\N	\N	f	Administratif	+212621744054	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a1b3b4aa-57eb-4a42-abbe-67c0edb5a430	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00965	Saad	Benomar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	88 Rue Al Massira	Quartier Anassi	Hattane	32.8524755	-6.8729504	\N	\N	\N	\N	f	Technicien	+212638342122	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e6853f2a-1a2e-49e7-bf02-f30cb5144486	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00966	Abdelilah	Benomar	d39d79ec-a716-4839-a93d-1845d00c182c	P2	6 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8681178	-6.5779419	\N	\N	\N	\N	f	Superviseur	+212663537504	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	81a4f4d9-ea58-446a-a211-3310f6f4ec79	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00967	Khadija	Lamrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	75 Rue Ifrane	Quartier Centre	Oued Zem	32.8586797	-6.582784	\N	\N	\N	\N	f	Administratif	+212629844143	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0137963d-f69e-4b60-913f-a51e4a6fef49	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00968	Zakaria	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	20 Rue Mohammed V	Quartier Al Wifaq	Oued Zem	32.856596	-6.5814201	\N	\N	\N	\N	f	Logisticien	+212679127970	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b1743007-550d-404f-a926-0d1a3179b53d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00969	Najat	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	S	187 Rue Hassan II	Quartier Al Wifaq	Oued Zem	32.9099615	-6.779715	\N	\N	\N	\N	f	Comptable	+212612579562	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3033cb18-2b9f-41f1-8b2e-c6ba180ac292	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00970	Mohammed	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	133 Rue Atlas	Quartier Hassania	Khouribga	32.8750033	-6.9122359	\N	\N	\N	\N	f	Administratif	+212624564077	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7d114539-3e27-4030-b962-b4da7e949863	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00971	Hanane	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	58 Rue Hassan II	Quartier Centre	Khouribga	32.8867544	-6.9222551	\N	\N	\N	\N	f	Opérateur	+212664312120	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3777b89f-e5de-4690-a75a-016b7122b592	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00972	Anass	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P3	30 Rue Atlas	Quartier Hay Mohammadi	Oued Zem	32.8654263	-6.5801734	\N	\N	\N	\N	f	Logisticien	+212626565332	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f38281a7-cf1b-4c8e-adff-3d017f561b2f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00973	Ghita	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	119 Rue Mohammed V	Quartier Hay Salam	Gueffaf	32.8537441	-6.8818086	\N	\N	\N	\N	f	Sécurité	+212642702348	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	85a8483a-3307-49a8-819d-50f628564a8f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00974	Zakaria	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	110 Rue Atlas	Quartier Medersa	Bir Mezoui	32.8981304	-6.9328997	\N	\N	\N	\N	f	Agent de maîtrise	+212668116473	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4bb2039a-ffe6-43a0-b117-fbf446ff5d83	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00975	Malika	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	6 Rue Mohammed V	Quartier Centre	Hattane	32.8989197	-6.9361077	\N	\N	\N	\N	f	RH	+212631351653	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	865974e5-2386-4b76-a5a1-3345bffede61	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00976	Adil	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	96 Rue Al Massira	Quartier Hassania	Boujniba	32.8934936	-6.9342075	\N	\N	\N	\N	f	Ingénieur	+212646883450	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b62e78e5-dd51-4c02-9216-165decb78ced	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00977	Soumia	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	11 Rue Al Massira	Quartier Medersa	Khouribga	32.8872588	-6.9071495	\N	\N	\N	\N	f	Superviseur	+212653324694	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a51a3919-b5a9-47c7-9d49-f5c5654b57ad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00978	Meryem	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	N	116 Rue des Orangers	Quartier Medersa	Hattane	32.8982826	-6.7824422	\N	\N	\N	\N	f	Électricien	+212667887635	Transport	t	company_bus	Non	f	f	0	t	\N	\N	\N	42b2d235-20be-4bd2-abf7-41d3fc930e6b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00979	Mustapha	Jaafar	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	43 Rue Ifrane	Quartier Hay Mohammadi	Gueffaf	32.8568091	-6.5754524	\N	\N	\N	\N	f	Sécurité	+212677776405	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c6df47a3-ac55-4d9a-86af-db827803b1c5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00980	Bilal	Zemmouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	94 Rue Hassan II	Quartier Tamaris	Hattane	32.878774	-6.9076061	\N	\N	\N	\N	f	Qualité	+212678352510	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bc1c67eb-afc4-4031-ab04-cd5650a986bd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00981	Fatima	Rahmani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	144 Rue des Orangers	Quartier Tamaris	Boulanoir	32.8911061	-6.9260533	\N	\N	\N	\N	f	Comptable	+212649558695	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d602a01a-a221-41ba-9d3d-26838c2ae466	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00982	Soumia	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	178 Rue des Orangers	Quartier Centre	Boulanoir	32.8957853	-6.896869	\N	\N	\N	\N	f	Logisticien	+212685234946	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b55f1015-3e9d-4674-8bef-d9dadfe2fa33	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00983	Rajaa	El Fassi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	154 Rue Al Massira	Quartier Al Amal	Boulanoir	32.854724	-6.5757748	\N	\N	\N	\N	f	Administratif	+212634160539	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	36a32388-739a-40db-b4fd-8282b0d80548	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00984	Laila	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	S	107 Rue des Orangers	Quartier Hay Mohammadi	Hattane	32.849313	-6.8785744	\N	\N	\N	\N	f	Superviseur	+212676267374	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	29d9fbe3-e430-4a25-b2aa-6ec809d4ddf7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00985	Samira	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	13 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.8991202	-6.6798763	\N	\N	\N	\N	f	Logisticien	+212693465662	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	52e240f7-e160-4bce-824c-260995f53e39	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00986	Rachid	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	132 Rue Al Massira	Quartier Centre	Khouribga	32.8949064	-6.9395356	\N	\N	\N	\N	f	Mécanicien	+212648223778	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	267ace15-1d9f-424c-9217-afb5026e11d2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00987	Souad	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	P3	29 Rue Hassan II	Quartier Anassi	Bir Mezoui	32.8903565	-6.9184298	\N	\N	\N	\N	f	Analyste	+212618285540	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c543346c-d0c5-4e14-9214-2b65c136c7f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00988	Aicha	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	102 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.8869076	-6.9173084	\N	\N	\N	\N	f	Électricien	+212678017646	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	05e1151d-97b6-4ad1-aba9-170f44da1b2e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	520136de-5ab5-4996-8c97-87b8a848416a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00989	Ibrahim	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	78 Rue Mohammed V	Quartier Hay Salam	Gueffaf	32.9002445	-6.7793499	\N	\N	\N	\N	f	Opérateur	+212631315505	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5e1d40ea-0366-4e93-97a5-bb4d7a250315	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00990	Karim	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	131 Rue de la Paix	Quartier Anassi	Bir Mezoui	32.8974205	-6.7816528	\N	\N	\N	\N	f	Ingénieur	+212670795627	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	96a9e0b0-7f6c-45e1-b693-b9cd644d38c2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00991	Meryem	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	141 Rue Atlas	Quartier Hay Salam	Hattane	32.8797901	-6.8977229	\N	\N	\N	\N	f	RH	+212658899259	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e26f6b6c-cf86-4ead-93a6-88777b68fccb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00992	Fouad	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	49 Rue des Orangers	Quartier Hay Mohammadi	Hattane	32.8921606	-6.9357292	\N	\N	\N	\N	f	Qualité	+212648294699	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	78effaae-4e51-4c06-81f5-1c62c1e895e9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00993	Hasnaa	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	N	157 Rue Hassan II	Quartier Centre	Khouribga	32.8569603	-6.5790464	\N	\N	\N	\N	f	Électricien	+212619789973	Sécurité	t	company_bus	Non	f	f	0	t	\N	\N	\N	d44b3d09-2f1c-4cd6-abca-4117078e2ab5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00994	Issam	El Yazghi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	23 Rue Hassan II	Quartier Centre	Boujniba	32.8648726	-6.5819264	\N	\N	\N	\N	f	Mécanicien	+212678094591	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	de7cd1aa-9460-4610-8f4a-68a32a6ab996	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00995	Wafae	Mekki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	73 Rue Hassan II	Quartier Tamaris	Bir Mezoui	32.8917501	-6.9359519	\N	\N	\N	\N	f	Mécanicien	+212645345089	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4514141e-96ba-41a9-af31-07f98b445539	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00996	Amine	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	P2	101 Rue Ifrane	Quartier Anassi	Gueffaf	32.8680647	-6.5824232	\N	\N	\N	\N	f	Ingénieur	+212692703566	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d66a26ef-701c-4b9d-b09a-c814f54fdade	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00997	Jamila	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	44 Rue Atlas	Quartier Hay Mohammadi	Gueffaf	32.8942985	-6.9042907	\N	\N	\N	\N	f	Sécurité	+212621506116	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	86a9fd47-75cb-45be-b936-248df23669cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00998	Aicha	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	199 Rue Mohammed V	Quartier Al Amal	Boujniba	32.8595854	-6.5491067	\N	\N	\N	\N	f	Agent de maîtrise	+212674973951	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8322bcf9-a3f8-44d6-bd19-130fc21a12f9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP00999	Naima	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	S	135 Rue Atlas	Quartier Anassi	Khouribga	32.8926528	-6.893843	\N	\N	\N	\N	f	Ingénieur	+212627722296	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4081b875-3255-426b-a1a1-31f9e9dd18eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01000	Zakaria	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	28 Rue des Orangers	Quartier Tamaris	Gueffaf	32.9049615	-6.7742087	\N	\N	\N	\N	f	Logisticien	+212653344968	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b5d0cada-e25f-4e8c-ac98-a4bf11826c94	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01001	Karim	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	37 Rue Ifrane	Quartier Medersa	Boujniba	32.8905324	-6.9301606	\N	\N	\N	\N	f	RH	+212663505893	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0b78f8fa-d3af-45fe-8794-ccc8bcbd910a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01002	Imane	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P3	174 Rue Mohammed V	Quartier Centre	Gueffaf	32.8536527	-6.5764382	\N	\N	\N	\N	f	Opérateur	+212659972264	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f7de4c4d-97e1-42aa-9b3b-16d787debcff	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01003	Karim	Berrada	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	44 Rue Al Massira	Quartier Al Wifaq	Bir Mezoui	32.8921935	-6.9318681	\N	\N	\N	\N	f	Logisticien	+212687324575	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2ef22cb0-8bb6-4fcd-b8a3-79d8b520a603	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01004	Khadija	Talbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	200 Rue Atlas	Quartier Al Wifaq	Boujniba	32.8503205	-6.8787492	\N	\N	\N	\N	f	Agent de maîtrise	+212619853703	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4f73b5d9-9c31-4139-a0c2-5eef0d997909	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01005	Driss	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P1	46 Rue Atlas	Quartier Al Wifaq	Oued Zem	32.8602952	-6.5790931	\N	\N	\N	\N	t	Logisticien	+212655814741	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9afa9042-1e5c-46fe-979c-eafac8af3141	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01006	Rachid	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	25 Rue Ifrane	Quartier Centre	Khouribga	32.8596693	-6.5852292	\N	\N	\N	\N	f	Technicien	+212620519772	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	62e3c000-76ef-4340-86f4-b9006765cc0d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01007	Amina	Filali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	134 Rue Mohammed V	Quartier Hassania	Boulanoir	32.8399743	-6.8033071	\N	\N	\N	\N	f	Conducteur	+212679681080	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ff6a838c-cf82-4688-a36c-a1a10285f928	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01008	Nadia	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	N	2 Rue Hassan II	Quartier Anassi	Bir Mezoui	32.9005032	-6.6842619	\N	\N	\N	\N	f	Opérateur	+212660104338	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d8e1aaf4-e1ce-4df0-bc13-8a75db24a55f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01009	Rajaa	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	81 Rue des Orangers	Quartier Anassi	Khouribga	32.859893	-6.8796126	\N	\N	\N	\N	f	Ingénieur	+212621034523	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d32ee2c0-332a-44a7-bb3c-9202c9f4547f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01010	Ghita	Ouazzani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	153 Rue Hassan II	Quartier Al Amal	Bir Mezoui	32.9035874	-6.6772513	\N	\N	\N	\N	f	Agent de maîtrise	+212637442355	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	177cf5fe-47f5-42a1-aa05-4136e17f8b11	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01011	Youssef	Laroui	d39d79ec-a716-4839-a93d-1845d00c182c	P2	141 Rue Ifrane	Quartier Hassania	Bir Mezoui	32.9042308	-6.678462	\N	\N	\N	\N	f	Logisticien	+212697350563	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ed184872-7dbe-4659-983d-568aa7785b17	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01012	Malika	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	1 Rue Ifrane	Quartier Hay Salam	Gueffaf	32.8963634	-6.7771915	\N	\N	\N	\N	f	Administratif	+212690452429	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6acfccf3-744f-47cb-b818-744903a3fcb2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01013	Ilham	Sabri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	103 Rue Al Massira	Quartier Al Amal	Boujniba	32.8662497	-6.5701004	\N	\N	\N	\N	f	Administratif	+212683480754	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	02c42de9-f425-4ae9-831c-ab8e7b313917	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01014	Houda	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	S	173 Rue Hassan II	Quartier Hay Salam	Boujniba	32.8408763	-6.8056517	\N	\N	\N	\N	f	Technicien	+212652780153	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a5d27d3d-e3d8-430f-91c3-91ddf3b6c22b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01015	Jamila	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	94 Rue Mohammed V	Quartier Centre	Oued Zem	32.8845432	-6.9218086	\N	\N	\N	\N	f	Conducteur	+212655091973	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	791a8b23-2fe8-43ff-9b29-c06bc8799693	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01016	Wafae	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	42 Rue de la Paix	Quartier Medersa	Gueffaf	32.8409598	-6.8046616	\N	\N	\N	\N	f	Technicien	+212696222106	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	854c01b0-7194-422a-8051-be56570ea91a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01017	Ahmed	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	P3	180 Rue Ifrane	Quartier Al Wifaq	Khouribga	32.8633316	-6.5551414	\N	\N	\N	\N	f	Conducteur	+212662519986	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a9a1896-f030-4531-9b5a-86634dbe6dbe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7c9aa98e-4b29-4561-a79c-49ea118322ab
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01018	Jamila	Chaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	194 Rue de la Paix	Quartier Anassi	Khouribga	32.8878083	-6.9059887	\N	\N	\N	\N	f	Opérateur	+212663377212	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	11400418-a467-4aa3-b40b-db502e66a03e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01019	Meryem	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	14 Rue Ifrane	Quartier Centre	Boulanoir	32.8693568	-6.9151391	\N	\N	\N	\N	f	Opérateur	+212662123610	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	37a9e595-bb75-462e-b1dd-49d41c149e20	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01020	Tariq	Benaissa	d39d79ec-a716-4839-a93d-1845d00c182c	P1	159 Rue Ifrane	Quartier Hay Mohammadi	Bir Mezoui	32.8573425	-6.5825371	\N	\N	\N	\N	f	Analyste	+212644181683	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	32e8b89a-e204-4ade-9443-51f4e5af5eb6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fa1bf35f-d421-454e-9098-2d82d14a810b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01021	Najat	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	191 Rue Atlas	Quartier Hassania	Hattane	32.8940258	-6.9021793	\N	\N	\N	\N	f	Ingénieur	+212678794110	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	23275208-3242-4978-9399-9803f67c667f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01022	Souad	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	86 Rue Atlas	Quartier Hassania	Oued Zem	32.8572012	-6.8744106	\N	\N	\N	\N	f	Ingénieur	+212612336631	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	30399db9-a44d-4377-8ce1-c3113f61c88e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01023	Anass	Errahmani	d39d79ec-a716-4839-a93d-1845d00c182c	N	53 Rue Mohammed V	Quartier Al Wifaq	Hattane	32.8777148	-6.9089678	\N	\N	\N	\N	f	Administratif	+212656017420	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d16087fc-ca92-49ac-bdf2-072e369754e8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01024	Tariq	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	90 Rue de la Paix	Quartier Centre	Bir Mezoui	32.8584223	-6.5697666	\N	\N	\N	\N	f	Logisticien	+212641320299	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6325461d-42bb-4ffd-aa43-2ea9eb9f63ce	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b188ccc7-d494-4c5c-b537-ea48c8c148fa
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01025	Abdelilah	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	16 Rue des Orangers	Quartier Al Wifaq	Hattane	32.8936783	-6.9367659	\N	\N	\N	\N	f	Opérateur	+212672728305	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cbef7f55-7dd4-4d28-a7cf-37ccf9357285	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01026	Youssef	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	P2	157 Rue Al Massira	Quartier Centre	Khouribga	32.8567	-6.8763169	\N	\N	\N	\N	f	Sécurité	+212684001329	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a879261c-8213-4cb0-9d76-c71bbf0d386e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01027	Zineb	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	190 Rue de la Paix	Quartier Centre	Boulanoir	32.8988111	-6.678794	\N	\N	\N	\N	f	Technicien	+212672275269	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d4662381-b862-4285-b21c-6ca681a9506b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01028	Amine	El Mansouri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	107 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.865921	-6.5748951	\N	\N	\N	\N	f	Opérateur	+212646160162	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	354e1f84-f953-4a22-897c-d12da6921394	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01029	Driss	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	S	39 Rue Al Massira	Quartier Centre	Bir Mezoui	32.8499365	-6.8790812	\N	\N	\N	\N	f	Analyste	+212662724727	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	c5707b5d-296c-4205-a3ae-f2912b397c6c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01030	Imane	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	160 Rue Hassan II	Quartier Al Amal	Boujniba	32.8981799	-6.9067793	\N	\N	\N	\N	f	Logisticien	+212687942278	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fdfb80b4-e86b-4941-8927-3b901dbeb56c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01031	Hicham	Jaafar	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	177 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.9010338	-6.9115837	\N	\N	\N	\N	f	Mécanicien	+212657451174	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	948c8023-bbb3-48e4-a62c-aa793f95eea1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01032	Anass	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	P3	125 Rue Mohammed V	Quartier Hay Mohammadi	Hattane	32.8933284	-6.8998599	\N	\N	\N	\N	f	Superviseur	+212659912398	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cecf79eb-5efa-4433-8307-cfa910a500c8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01033	Ali	Sahraoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	67 Rue de la Paix	Quartier Hassania	Bir Mezoui	32.8993035	-6.93689	\N	\N	\N	\N	f	Administratif	+212651522430	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	67ab753c-c803-4274-99c1-e806ffa852e2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01034	Mustapha	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	90 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.8398629	-6.8038054	\N	\N	\N	\N	f	Logisticien	+212647028468	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5e7581dc-2e85-42dd-be9e-cc37cd4bf364	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01035	Najat	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	196 Rue Atlas	Quartier Hay Mohammadi	Oued Zem	32.8456079	-6.7987341	\N	\N	\N	\N	f	Logisticien	+212649293550	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0c1a130c-f24d-41a8-9167-11f96df0ed79	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01036	Hasnaa	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	118 Rue Atlas	Quartier Al Amal	Hattane	32.9053596	-6.7794664	\N	\N	\N	\N	f	Ingénieur	+212635029273	Transport	t	company_bus	Non	f	f	0	t	\N	\N	\N	6c25776a-e7de-4782-a209-272e41fb6731	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01037	Kawtar	Louizi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	51 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.856749	-6.5570635	\N	\N	\N	\N	f	Comptable	+212662045330	Qualité	t	company_bus	Non	f	f	0	t	\N	\N	\N	0a05cdb9-db45-44bd-8298-adaf7ae0a670	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	309b7f89-2f27-4c54-b608-0e484991e82a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01038	Hafida	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	N	173 Rue Al Massira	Quartier Al Wifaq	Bir Mezoui	32.8768612	-6.9130868	\N	\N	\N	\N	f	Électricien	+212618308993	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0a9dd39a-5c8f-4860-9c24-cbbbe883cdc0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01039	Hassan	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	148 Rue Hassan II	Quartier Hassania	Bir Mezoui	32.8813405	-6.9025085	\N	\N	\N	\N	f	Qualité	+212688320596	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	41619738-5a5c-4c24-a968-736f50d86a3b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	5b6b9621-f986-4910-b2a5-cd15829cae7b
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01040	Jamila	El Amrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	5 Rue Atlas	Quartier Medersa	Oued Zem	32.8497037	-6.572143	\N	\N	\N	\N	f	Mécanicien	+212654548408	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8631c265-fdef-4e8b-a47b-06442d437eb2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01041	Aicha	Filali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	117 Rue Al Massira	Quartier Hassania	Khouribga	32.8999119	-6.9021704	\N	\N	\N	\N	f	Qualité	+212611111649	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ef7601fd-adab-4396-8a11-8d11dd7fd1f8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01042	Aicha	Bennani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	106 Rue Atlas	Quartier Tamaris	Bir Mezoui	32.8703951	-6.9031831	\N	\N	\N	\N	f	Technicien	+212680148424	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e6fddb8b-5daf-40fb-a6b4-8ed3ecb51745	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01043	Houda	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	121 Rue Hassan II	Quartier Hay Mohammadi	Bir Mezoui	32.8971667	-6.7780128	\N	\N	\N	\N	f	Ingénieur	+212620924473	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	167312e0-06b9-402b-a88a-a8cad33ed562	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01044	Issam	Naciri	d39d79ec-a716-4839-a93d-1845d00c182c	S	173 Rue de la Paix	Quartier Hay Mohammadi	Oued Zem	32.9024385	-6.7807067	\N	\N	\N	\N	f	Mécanicien	+212681123896	Finance	t	company_bus	Non	f	f	0	t	\N	\N	\N	bc604837-b976-456f-900a-2e36083c1958	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01045	Amine	Wahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	11 Rue Ifrane	Quartier Hay Salam	Boujniba	32.8637174	-6.5841174	\N	\N	\N	\N	f	Administratif	+212631950711	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7672e261-78b4-412d-b7d9-718d1530da47	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01046	Latifa	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	38 Rue Mohammed V	Quartier Anassi	Oued Zem	32.8839712	-6.9200643	\N	\N	\N	\N	f	Superviseur	+212630212795	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1c68bbb8-b8cb-434c-ae6c-f1c0b07cb7ca	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01047	Loubna	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	76 Rue Ifrane	Quartier Hay Salam	Khouribga	32.895091	-6.930754	\N	\N	\N	\N	f	Technicien	+212692245090	RH	t	company_bus	Non	f	f	0	t	\N	\N	\N	55883308-61f5-4cf8-a77d-abea978bce24	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01048	Loubna	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	109 Rue de la Paix	Quartier Hay Mohammadi	Boulanoir	32.833832	-6.8033861	\N	\N	\N	\N	f	Analyste	+212680895126	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	fdcde2f4-66c6-4722-be35-1bd8223297fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01049	Naima	Mouttaki	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	188 Rue Al Massira	Quartier Medersa	Khouribga	32.8528359	-6.57808	\N	\N	\N	\N	f	Ingénieur	+212699305007	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	be959161-fd38-4dbe-986c-10f210eac72c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	68eb90a0-b5c9-4251-8750-4d3ab026832a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01050	Hamza	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	11 Rue de la Paix	Quartier Al Amal	Boulanoir	32.8346956	-6.8001601	\N	\N	\N	\N	f	Technicien	+212613722404	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	85fde64e-c5ff-429a-b99f-f27866c73853	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01051	Jawad	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	32 Rue des Orangers	Quartier Al Wifaq	Oued Zem	32.8932078	-6.9302722	\N	\N	\N	\N	f	Qualité	+212677785868	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2b190bcf-db7b-4574-a3c9-d2b456d8c9e4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01052	Soumia	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	50 Rue Atlas	Quartier Hay Mohammadi	Boujniba	32.8960036	-6.8995067	\N	\N	\N	\N	f	Mécanicien	+212697188851	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e72bfadf-0d12-4981-8d26-400400308fc3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01053	Sanaa	Talbi	d39d79ec-a716-4839-a93d-1845d00c182c	N	24 Rue de la Paix	Quartier Al Wifaq	Hattane	32.8579412	-6.8769077	\N	\N	\N	\N	f	Sécurité	+212673771087	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	86845179-2d9d-483f-8f01-dd16878958bb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01054	Najat	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	5 Rue Hassan II	Quartier Medersa	Boulanoir	32.8884172	-6.9209549	\N	\N	\N	\N	f	Comptable	+212622627584	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	325af7ba-dc77-4335-aa04-d9aaf8bd5df7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01055	Khalid	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	116 Rue Hassan II	Quartier Centre	Khouribga	32.8926839	-6.7798307	\N	\N	\N	\N	f	Technicien	+212623603437	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8c818c60-28f8-499e-95c1-0d740b3a3628	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01056	Ghita	Zouiten	d39d79ec-a716-4839-a93d-1845d00c182c	P2	104 Rue Mohammed V	Quartier Hay Mohammadi	Boulanoir	32.9021743	-6.6764107	\N	\N	\N	\N	f	Technicien	+212654977482	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a04110e6-eb10-4280-a4cc-272a49f094a7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01057	Samira	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	168 Rue des Orangers	Quartier Hay Salam	Hattane	32.8935398	-6.9371223	\N	\N	\N	\N	f	Conducteur	+212638280431	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0fa4383a-3a0e-49a4-b2e0-8aca613b9dd9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01058	Samira	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	94 Rue des Orangers	Quartier Hay Mohammadi	Gueffaf	32.8566595	-6.5718949	\N	\N	\N	\N	f	Superviseur	+212628917558	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d31e6183-f5ea-46f1-94c2-a1cbd2e777a2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01059	Naima	Talbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	114 Rue Mohammed V	Quartier Hassania	Boulanoir	32.8869978	-6.9304611	\N	\N	\N	\N	f	Technicien	+212666387026	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	789c089e-26ff-4b9e-8b70-eb8ee1d1d375	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f384b735-a167-43bf-a36c-0c61da2f0977
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01060	Tariq	Benkiran	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	113 Rue Atlas	Quartier Centre	Hattane	32.9025369	-6.7732863	\N	\N	\N	\N	f	Comptable	+212662236453	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b51c0a1c-6fe1-4f91-b4f2-f835926476b7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01061	Hanane	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	123 Rue Atlas	Quartier Tamaris	Boujniba	32.8686869	-6.5817286	\N	\N	\N	\N	f	Administratif	+212689809029	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bc3456aa-53e8-4a9d-ab8f-301a6dcce21d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01062	Wafae	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	121 Rue Ifrane	Quartier Hay Mohammadi	Hattane	32.8770768	-6.9178349	\N	\N	\N	\N	f	Comptable	+212645908858	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3b79602a-96ad-421b-94ae-6b786125f4ae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01063	Khalid	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	129 Rue Al Massira	Quartier Al Wifaq	Gueffaf	32.8990388	-6.7724079	\N	\N	\N	\N	f	Comptable	+212676130941	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0152642e-3413-40c1-b1c2-b39f3c7fc32f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01064	Omar	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	149 Rue Al Massira	Quartier Hay Salam	Oued Zem	32.8955463	-6.7787301	\N	\N	\N	\N	f	RH	+212625849647	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	11f7a9a3-a419-4d5a-bd01-1c374aeace49	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01065	Tariq	Chraibi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	126 Rue Hassan II	Quartier Hassania	Hattane	32.8934881	-6.7789412	\N	\N	\N	\N	f	Logisticien	+212633847989	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1c52b26d-0a8a-4425-a823-4b1e9d5c8bc4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01066	Zineb	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	32 Rue Mohammed V	Quartier Hay Mohammadi	Khouribga	32.877842	-6.9054131	\N	\N	\N	\N	f	Administratif	+212692812635	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4800d7e9-d164-41e7-8935-3ce103dad323	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01067	Bilal	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	173 Rue Ifrane	Quartier Hassania	Khouribga	32.9199231	-6.7217632	\N	\N	\N	\N	f	Agent de maîtrise	+212626749956	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e2aa7639-e341-4188-bf8b-0109b20c5efe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01068	Ilham	Jaafar	d39d79ec-a716-4839-a93d-1845d00c182c	N	44 Rue Al Massira	Quartier Hassania	Bir Mezoui	32.8379034	-6.8040008	\N	\N	\N	\N	f	Sécurité	+212646932767	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bc4ab644-69da-4360-96fb-3e0ce7d334e8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01069	Issam	Mekki	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	140 Rue Ifrane	Quartier Hay Salam	Hattane	32.855355	-6.5657778	\N	\N	\N	\N	f	Opérateur	+212620342823	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9a2682fb-f584-412e-a6c3-997ebfbe5f82	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01070	Hamza	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	42 Rue Hassan II	Quartier Al Wifaq	Oued Zem	32.9032276	-6.7817864	\N	\N	\N	\N	t	Superviseur	+212671471863	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	83d96e5c-4d21-45ea-9eab-bc670eba565c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01071	Nadia	Slaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P2	169 Rue des Orangers	Quartier Anassi	Khouribga	32.8937395	-6.7778948	\N	\N	\N	\N	f	Opérateur	+212676509703	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ea25013b-b07d-465c-a054-4124a4a4d4f6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01072	Latifa	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	120 Rue des Orangers	Quartier Tamaris	Boulanoir	32.9009652	-6.7839265	\N	\N	\N	\N	f	Agent de maîtrise	+212697597763	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d7b15dbf-8c7e-4f1f-abe5-968fab27bd86	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01073	Latifa	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	26 Rue Atlas	Quartier Hay Salam	Gueffaf	32.9093575	-6.7798378	\N	\N	\N	\N	f	Analyste	+212657315649	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ee3da0d7-4e78-42f0-a47e-ffcb8dea9fd4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01074	Siham	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	27 Rue des Orangers	Quartier Tamaris	Boujniba	32.8565888	-6.8765228	\N	\N	\N	\N	f	Électricien	+212663637449	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	579a7818-bd16-4e53-ad01-1ea50a5cf238	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01075	Amine	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	142 Rue Hassan II	Quartier Medersa	Boujniba	32.8961188	-6.7850542	\N	\N	\N	\N	f	Mécanicien	+212669232530	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	71060752-47f1-4422-b15b-dfc6e72a081a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01076	Bilal	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	74 Rue de la Paix	Quartier Centre	Oued Zem	32.901335	-6.7750616	\N	\N	\N	\N	f	Agent de maîtrise	+212674102589	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b1f4b6cc-1641-4fe9-93ee-fd3e57430b7f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01077	Lahcen	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	17 Rue Ifrane	Quartier Hay Salam	Oued Zem	32.8940757	-6.9310534	\N	\N	\N	\N	f	Comptable	+212688717304	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	51cb46fe-665f-49e3-b9b9-9ac6585849bf	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01078	Hasnaa	Laroui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	72 Rue Hassan II	Quartier Al Amal	Hattane	32.8616016	-6.9051	\N	\N	\N	\N	f	Comptable	+212659629428	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d6b83ffb-05c4-47f7-8e46-6d24201c94e9	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01079	Anass	Chaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	59 Rue de la Paix	Quartier Hassania	Boujniba	32.8901077	-6.940624	\N	\N	\N	\N	f	Électricien	+212640988790	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	eac4abd8-3031-4f47-9590-d205490326ce	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01080	Aicha	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	128 Rue Ifrane	Quartier Hay Mohammadi	Hattane	32.9039588	-6.6803013	\N	\N	\N	\N	t	Mécanicien	+212619604762	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3871a52c-8dcd-4050-a8a1-5fd21a8086cf	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01081	Aicha	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	98 Rue Hassan II	Quartier Al Amal	Boulanoir	32.8609887	-6.9109552	\N	\N	\N	\N	f	Électricien	+212633873889	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0b6c00a9-50a9-43e4-924e-5247987a9e15	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01082	Zineb	Slaoui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	53 Rue Ifrane	Quartier Centre	Khouribga	32.8594015	-6.8755285	\N	\N	\N	\N	f	Qualité	+212612957196	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	031e90f7-37d8-417c-8274-780facd69edd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01083	Omar	El Amrani	d39d79ec-a716-4839-a93d-1845d00c182c	N	8 Rue Atlas	Quartier Anassi	Boulanoir	32.8984463	-6.7740635	\N	\N	\N	\N	f	Opérateur	+212689596580	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5c0b5e38-c1c8-4ac6-adce-4eb446ac5d40	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01084	Ibrahim	Filali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	55 Rue Al Massira	Quartier Al Amal	Oued Zem	32.8926285	-6.9367074	\N	\N	\N	\N	f	Sécurité	+212694726111	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	29d9e805-679b-45a8-813c-409a24de0b95	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01085	Omar	Errahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	128 Rue Ifrane	Quartier Al Amal	Bir Mezoui	32.9026712	-6.7868004	\N	\N	\N	\N	f	Conducteur	+212690638309	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ad9efbbd-d147-41e5-bd1b-0870d16ee1da	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01086	Zakaria	Skali	d39d79ec-a716-4839-a93d-1845d00c182c	P2	183 Rue Al Massira	Quartier Hassania	Hattane	32.8709882	-6.9265813	\N	\N	\N	\N	f	Technicien	+212612687223	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	25c93266-cbc2-4c8f-8f5a-731c709ae05b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01087	Bilal	El Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	149 Rue des Orangers	Quartier Al Amal	Gueffaf	32.8921176	-6.773886	\N	\N	\N	\N	f	Analyste	+212644017565	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9220e9c0-fd06-4ed6-9561-945f9b639d7b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	057ec0d4-3d1a-4f9a-b1dc-6eec769ba329
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01088	Houda	El Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	15 Rue Atlas	Quartier Hay Salam	Khouribga	32.8837501	-6.8957063	\N	\N	\N	\N	f	Administratif	+212622199872	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	85f3afce-a952-4669-99f3-c6268e41eb05	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01089	Zineb	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	S	24 Rue Mohammed V	Quartier Al Amal	Boulanoir	32.8619405	-6.5796065	\N	\N	\N	\N	f	Opérateur	+212689137580	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	dfd5e230-f257-4803-99de-20cf269d61eb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01090	Samira	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	123 Rue Ifrane	Quartier Al Amal	Bir Mezoui	32.8587681	-6.8779888	\N	\N	\N	\N	f	Analyste	+212688330667	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5b710eaf-d617-4943-bd88-923bd03771a6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	564f621c-a30b-4757-8217-db10cc94c897
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01091	Hasnaa	Lamrani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	184 Rue Al Massira	Quartier Al Wifaq	Bir Mezoui	32.861199	-6.8820096	\N	\N	\N	\N	f	Opérateur	+212678992764	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d5ccb761-4de4-4f48-874c-d21f156226cc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01092	Laila	Tazi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	28 Rue Ifrane	Quartier Hassania	Hattane	32.8486816	-6.8776131	\N	\N	\N	\N	f	Opérateur	+212624763098	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cf8f7f49-4fc3-4d07-aacc-d75b9be2e515	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01093	Mehdi	Chaoui	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	21 Rue Hassan II	Quartier Tamaris	Hattane	32.8942848	-6.7751718	\N	\N	\N	\N	t	Technicien	+212696881080	Production	t	company_bus	Non	f	f	0	t	\N	\N	\N	16075d42-fbea-4979-ac55-e770a5a3f32f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01094	Latifa	Laroui	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	99 Rue Atlas	Quartier Tamaris	Hattane	32.8700739	-6.9214567	\N	\N	\N	\N	f	Ingénieur	+212665891967	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1db679ef-177a-474e-835d-6b85211d6816	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01095	Najat	Ouazzani	d39d79ec-a716-4839-a93d-1845d00c182c	P1	121 Rue Al Massira	Quartier Al Amal	Hattane	32.8518106	-6.565377	\N	\N	\N	\N	f	Sécurité	+212649305551	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4d1303a0-071e-48cc-8732-62b5830d4192	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	55779b27-5083-4587-b420-cceda99cca35
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01096	Jamila	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	90 Rue Hassan II	Quartier Al Wifaq	Boulanoir	32.8650095	-6.5809634	\N	\N	\N	\N	f	Comptable	+212617753977	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	685c5246-3715-4277-87c2-d1013af63b35	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8b127225-8987-4118-a1c3-8b18d476db1f
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01097	Abdelilah	Benali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	171 Rue Atlas	Quartier Hay Salam	Boulanoir	32.8802749	-6.9238214	\N	\N	\N	\N	f	Analyste	+212694443748	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bbb2de41-5ec0-49b9-8597-40cf4a679bc1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01098	Malika	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	N	27 Rue Atlas	Quartier Tamaris	Oued Zem	32.8587229	-6.5834076	\N	\N	\N	\N	f	Qualité	+212650640846	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8e945239-2f3d-4ac4-bdb3-db461df0127a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01099	Khadija	El Amrani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	164 Rue de la Paix	Quartier Hay Mohammadi	Boulanoir	32.859315	-6.5672122	\N	\N	\N	\N	f	Superviseur	+212623977128	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8542a793-7829-425d-bd4f-6f17b145958c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01100	Latifa	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	144 Rue des Orangers	Quartier Hassania	Hattane	32.9026978	-6.771324	\N	\N	\N	\N	f	Opérateur	+212654413336	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	34cb14ab-8485-46eb-8105-8f69a00b84a5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01101	Zineb	Senhaji	d39d79ec-a716-4839-a93d-1845d00c182c	P2	101 Rue Ifrane	Quartier Hay Salam	Bir Mezoui	32.8757063	-6.9160462	\N	\N	\N	\N	f	Administratif	+212666332472	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f0fffea2-0368-488b-86af-335121d9646c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	afd2c042-05e2-4439-98e0-04dd22298c55
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01102	Youssef	Benaissa	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	103 Rue Ifrane	Quartier Medersa	Boujniba	32.8617379	-6.5808104	\N	\N	\N	\N	f	Comptable	+212675322914	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7f2a6827-0ba0-47c7-acef-249b408c0dae	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01103	Nadia	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	14 Rue Mohammed V	Quartier Centre	Gueffaf	32.8616684	-6.8709575	\N	\N	\N	\N	f	Technicien	+212627168538	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5fef89a8-c4dc-4d00-988b-0b7614f6884b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01104	Hicham	Yakine	d39d79ec-a716-4839-a93d-1845d00c182c	S	161 Rue Hassan II	Quartier Al Wifaq	Boulanoir	32.8686357	-6.9094456	\N	\N	\N	\N	f	Ingénieur	+212685314813	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	05c52da5-7310-4d49-b762-1b7810a9fd45	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	caa53059-ba46-45cb-b51d-aac8e75b86da
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01105	Adil	Louizi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	3 Rue Mohammed V	Quartier Al Amal	Boulanoir	32.8993183	-6.7820525	\N	\N	\N	\N	f	Logisticien	+212688081475	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8b4cadde-8980-413b-b3d5-fdd28d464532	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01106	Soufiane	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	194 Rue des Orangers	Quartier Anassi	Khouribga	32.8963279	-6.9046136	\N	\N	\N	\N	f	Technicien	+212671502567	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e2e292c2-07f1-4914-a964-8fd69d21916b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	4e65a9fb-1294-44cd-b429-40fca7d48bd2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01107	Najat	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	P3	115 Rue des Orangers	Quartier Hay Mohammadi	Oued Zem	32.8956822	-6.8980224	\N	\N	\N	\N	f	Comptable	+212671448026	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2f2563a6-474f-4846-90bc-cc0935db1747	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01108	Jawad	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	59 Rue Mohammed V	Quartier Anassi	Bir Mezoui	32.861949	-6.8762888	\N	\N	\N	\N	f	Opérateur	+212681582529	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b99b61cf-6028-4143-af82-f6086e27c310	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01109	Fouad	Wahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	107 Rue Atlas	Quartier Hay Salam	Bir Mezoui	32.8927465	-6.9309591	\N	\N	\N	\N	f	Qualité	+212691323251	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7709bb94-b801-4fe7-8fa4-d70d50863aa7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01110	Laila	Hassouni	d39d79ec-a716-4839-a93d-1845d00c182c	P1	62 Rue Atlas	Quartier Hay Salam	Gueffaf	32.8947021	-6.9320011	\N	\N	\N	\N	f	Superviseur	+212643099254	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a0ab0c5-45a3-4345-b9f3-bbfe04930778	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01111	Noureddine	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	80 Rue Hassan II	Quartier Tamaris	Oued Zem	32.8944839	-6.9416684	\N	\N	\N	\N	f	RH	+212612166015	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7470827e-d4ea-4a15-8823-9a7c73b63db4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01112	Hanane	Dahbi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	134 Rue Al Massira	Quartier Hassania	Boujniba	32.8673166	-6.5752126	\N	\N	\N	\N	f	Conducteur	+212668521028	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a911f8d9-3381-496c-a689-d38de9c4c8bb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	8c1a4d52-abda-485a-a2ed-da70ed803bb5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01113	Laila	El Yazghi	d39d79ec-a716-4839-a93d-1845d00c182c	N	117 Rue de la Paix	Quartier Tamaris	Oued Zem	32.8969817	-6.9382507	\N	\N	\N	\N	f	Sécurité	+212658582546	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2f2e6c09-a3a5-4d8f-8e74-520d065c75ed	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01114	Soumia	Bouali	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	172 Rue Ifrane	Quartier Tamaris	Hattane	32.8966397	-6.9348325	\N	\N	\N	\N	f	Opérateur	+212699013554	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9f23d0b4-840a-4837-839f-82f623d535dd	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	eb0a6b1c-35b6-4397-990a-a25bde1af56d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01115	Mehdi	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	190 Rue Hassan II	Quartier Al Wifaq	Gueffaf	32.8967733	-6.9342051	\N	\N	\N	\N	f	Technicien	+212635360360	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e56e2220-3914-4705-ad8a-6e16a9d4b7a7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01116	Adil	Mouttaki	d39d79ec-a716-4839-a93d-1845d00c182c	P2	28 Rue Ifrane	Quartier Hay Mohammadi	Oued Zem	32.9048196	-6.7832669	\N	\N	\N	\N	f	Conducteur	+212629651752	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a83af5e6-75c1-457b-9e91-db58db0c1077	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01117	Naima	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	120 Rue de la Paix	Quartier Al Amal	Hattane	32.8623517	-6.8777887	\N	\N	\N	\N	f	Comptable	+212635885189	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	418fe1a6-22bf-4645-9e3a-10ffdd6766cf	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01118	Hamza	Benaissa	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	160 Rue Al Massira	Quartier Medersa	Gueffaf	32.863278	-6.8701073	\N	\N	\N	\N	f	Administratif	+212635652120	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8da10e63-c2dd-44b8-b5e1-829440f317e2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01119	Loubna	Touhami	d39d79ec-a716-4839-a93d-1845d00c182c	S	68 Rue Hassan II	Quartier Hassania	Bir Mezoui	32.8786923	-6.9133065	\N	\N	\N	\N	f	Superviseur	+212695330313	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6fab15ee-3ac4-4946-80b8-a1fd97a5b8fc	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ba717b0e-fedb-4a58-b7a7-253549662e69
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01120	Lahcen	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	141 Rue de la Paix	Quartier Al Amal	Boujniba	32.86347	-6.8770281	\N	\N	\N	\N	f	Qualité	+212698704915	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f0c272dd-e05f-4e8c-ada5-d30d44da54fe	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01121	Hamza	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	4 Rue Al Massira	Quartier Centre	Boulanoir	32.8942859	-6.7814631	\N	\N	\N	\N	f	RH	+212678481268	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	82f66e6b-2d2f-4573-a3bb-267b9480225c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7963b7d6-e42f-4620-acf3-51938a4f9742
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01122	Malika	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	35 Rue Mohammed V	Quartier Tamaris	Oued Zem	32.9084527	-6.7854934	\N	\N	\N	\N	f	Comptable	+212632766859	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	2404ac05-58b4-477a-b295-e94e2d152385	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01123	Meryem	El Fassi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	146 Rue Hassan II	Quartier Al Wifaq	Khouribga	32.9000431	-6.7707558	\N	\N	\N	\N	f	Conducteur	+212612841010	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3d679df1-91d0-4ff3-a2d5-b1219e551619	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01124	Amine	El Yazghi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	41 Rue de la Paix	Quartier Medersa	Bir Mezoui	32.897642	-6.7775976	\N	\N	\N	\N	f	Mécanicien	+212619156927	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	87bfff95-c342-4984-9c2c-bd9cd23113a2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01125	Ilham	Wahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	46 Rue Atlas	Quartier Tamaris	Boulanoir	32.8968161	-6.9110058	\N	\N	\N	\N	f	RH	+212648587692	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f7fed789-7ea9-4966-8000-0e49292c8310	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01126	Ghita	Laaroussi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	23 Rue Atlas	Quartier Tamaris	Boulanoir	32.8840781	-6.9077	\N	\N	\N	\N	f	Administratif	+212646764611	Logistique	t	company_bus	Non	f	f	0	t	\N	\N	\N	61d0670b-a1db-4b46-8243-da368653e0f6	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01127	Tariq	El Kabbaj	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	163 Rue des Orangers	Quartier Hay Mohammadi	Boujniba	32.8617395	-6.5666392	\N	\N	\N	\N	t	Comptable	+212643486279	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e9e513d1-80fa-42e1-92cf-eabbf2a723af	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a51a72f3-499c-4a94-9697-d3ba1d9fddda
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01128	Meryem	Lamrani	d39d79ec-a716-4839-a93d-1845d00c182c	N	86 Rue Hassan II	Quartier Medersa	Gueffaf	32.8627088	-6.8734217	\N	\N	\N	\N	f	Ingénieur	+212641172921	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ae50b171-2775-49c8-813b-c62e3db68004	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ed3c446d-5d01-4043-8568-b261001ffdec
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01129	Issam	Errahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	67 Rue de la Paix	Quartier Medersa	Khouribga	32.8705008	-6.9269932	\N	\N	\N	\N	f	Qualité	+212665612930	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	cfe4b625-6935-43ea-92e3-14f806738231	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01130	Soufiane	Ouali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	166 Rue Ifrane	Quartier Hay Salam	Oued Zem	32.9024107	-6.6791391	\N	\N	\N	\N	f	Ingénieur	+212688303692	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e657e131-a98d-4187-a112-fd74a141ea79	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01131	Souad	Hajji	d39d79ec-a716-4839-a93d-1845d00c182c	P2	193 Rue des Orangers	Quartier Al Amal	Hattane	32.9240663	-6.7162515	\N	\N	\N	\N	f	Comptable	+212661122872	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	02618627-78fa-499a-b5c8-65061fb1f8ff	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01132	Bilal	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	140 Rue des Orangers	Quartier Hassania	Bir Mezoui	32.8380877	-6.8081199	\N	\N	\N	\N	f	Administratif	+212649414210	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b3891883-4cc5-4963-be34-121edc0f4806	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	773c4704-46df-4e90-af11-4a957fb87ab5
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01133	Saad	Maâchi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	72 Rue Hassan II	Quartier Hay Salam	Bir Mezoui	32.8991175	-6.9401694	\N	\N	\N	\N	f	Qualité	+212690843333	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ff6e8cbe-682b-4ed8-82ae-bba944a51551	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	51168416-2650-41a2-b43a-e3150d5638bc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01134	Meryem	El Fassi	d39d79ec-a716-4839-a93d-1845d00c182c	S	57 Rue Ifrane	Quartier Hay Mohammadi	Oued Zem	32.8839669	-6.9018835	\N	\N	\N	\N	f	Technicien	+212613226719	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9034b766-46fe-4e6c-b969-0f312bd5660c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01135	Othmane	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	89 Rue Mohammed V	Quartier Centre	Khouribga	32.8922178	-6.7781774	\N	\N	\N	\N	f	Agent de maîtrise	+212642849391	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6c908490-e382-4391-bc3f-bfddb6c2f6d1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	97ee6b1d-35c8-46e1-96f4-249229429500
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01136	Ilham	Senhaji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	75 Rue Mohammed V	Quartier Al Amal	Boulanoir	32.9068876	-6.7793938	\N	\N	\N	\N	f	Qualité	+212624339329	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	bdd12ba9-d50a-41f9-99bb-63b161ed6cf1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01137	Abdelilah	Maâchi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	38 Rue Hassan II	Quartier Centre	Boujniba	32.844244	-6.7978074	\N	\N	\N	\N	f	RH	+212622685997	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ebe8015a-f0ec-4bf5-bdd8-5317b496848f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01138	Siham	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	128 Rue de la Paix	Quartier Hassania	Gueffaf	32.8599292	-6.5803879	\N	\N	\N	\N	f	Conducteur	+212691015216	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	487fe76c-a644-4051-a4fd-6bea302620c5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01139	Sanaa	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	33 Rue Mohammed V	Quartier Al Wifaq	Gueffaf	32.8772469	-6.9021627	\N	\N	\N	\N	f	Électricien	+212642315252	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f52234c1-bde8-4d0f-836a-0d4c1c2d80e1	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01140	Lahcen	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	P1	112 Rue Al Massira	Quartier Centre	Gueffaf	32.8994092	-6.684206	\N	\N	\N	\N	f	Technicien	+212621510699	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5bdd4cd5-29ed-4000-b60c-dc7662fe1683	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01141	Ahmed	Yakine	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	91 Rue Atlas	Quartier Tamaris	Boulanoir	32.8709388	-6.925242	\N	\N	\N	\N	f	Mécanicien	+212642917012	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	43f8e82b-8567-47a1-957f-fa0c240b036e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01142	Aicha	Tazi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	83 Rue de la Paix	Quartier Al Amal	Oued Zem	32.891433	-6.9350087	\N	\N	\N	\N	f	Ingénieur	+212633143063	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	1757ebeb-4e6f-4c27-b494-29d2068e4473	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01143	Driss	Sahraoui	d39d79ec-a716-4839-a93d-1845d00c182c	N	117 Rue Ifrane	Quartier Hay Salam	Hattane	32.8617194	-6.8820407	\N	\N	\N	\N	f	Mécanicien	+212628471140	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5cc75735-c834-4b1c-9a38-f07d147c00d8	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01144	Hicham	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	80 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8839235	-6.9335885	\N	\N	\N	\N	t	Logisticien	+212683429628	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	98d4b7e3-235c-492e-abbc-15d0e570ffb3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01145	Mehdi	Berrada	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	103 Rue Mohammed V	Quartier Al Amal	Boujniba	32.8994498	-6.7810971	\N	\N	\N	\N	f	Sécurité	+212683730846	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4be16f18-5cee-495c-b80b-7bad3bcc0a32	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9cad5401-9690-4f20-a2b1-32db93b477a1
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01146	Bouchra	El Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	179 Rue Mohammed V	Quartier Hay Salam	Gueffaf	32.8986581	-6.9032592	\N	\N	\N	\N	f	Analyste	+212684681352	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6235fa6d-be95-43c2-a183-58106dc02d84	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01147	Hamza	Hajji	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	119 Rue des Orangers	Quartier Hay Mohammadi	Bir Mezoui	32.8886318	-6.9341376	\N	\N	\N	\N	f	Technicien	+212641867977	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7ba5382f-8224-4b2d-acf6-7a16ac2fb85c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	04c98969-73d1-467c-a8b2-4f274861a5b2
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01148	Amina	Yakine	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	75 Rue Al Massira	Quartier Hassania	Khouribga	32.8500484	-6.8769387	\N	\N	\N	\N	f	Agent de maîtrise	+212665225086	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8f706427-9c0b-4a4a-8888-c8a12da85121	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01149	Siham	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	S	93 Rue Hassan II	Quartier Centre	Boujniba	32.9016258	-6.7703871	\N	\N	\N	\N	f	RH	+212635125133	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ffe97213-64ce-4f40-a72f-51aeabf1b7a0	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01150	Driss	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	176 Rue Atlas	Quartier Tamaris	Boulanoir	32.8893882	-6.9332924	\N	\N	\N	\N	f	Comptable	+212643819992	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	010294a7-e338-45f6-a1b6-209eabf0f68d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01151	Loubna	Moumen	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	40 Rue Ifrane	Quartier Hay Mohammadi	Khouribga	32.8988868	-6.9370578	\N	\N	\N	\N	f	Opérateur	+212632619010	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6e98f983-c669-42c7-8ea7-2c284a272977	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0a42051c-cafb-428d-a297-608bfe74954a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01152	Mustapha	Bennani	d39d79ec-a716-4839-a93d-1845d00c182c	P3	194 Rue Al Massira	Quartier Hay Salam	Hattane	32.898535	-6.7727843	\N	\N	\N	\N	f	Opérateur	+212690831318	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	39d37f0d-dc45-49a3-808e-9c87e3473717	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01153	Khadija	Skali	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	139 Rue Hassan II	Quartier Centre	Oued Zem	32.8999436	-6.6806293	\N	\N	\N	\N	f	Technicien	+212676013985	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	55b94630-2d20-4ba1-8599-96ab69076464	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01154	Naima	Tijani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	61 Rue Al Massira	Quartier Hay Mohammadi	Bir Mezoui	32.8966482	-6.9058007	\N	\N	\N	\N	f	Qualité	+212660076909	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	76384f54-6976-4fb2-9c01-a8c06819303d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01155	Hasnaa	Dahbi	d39d79ec-a716-4839-a93d-1845d00c182c	P1	11 Rue Ifrane	Quartier Centre	Oued Zem	32.8779817	-6.9016443	\N	\N	\N	\N	f	Superviseur	+212618687047	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	01fc5f7a-28ab-4e4c-9aa4-bbd47a7d01c2	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01156	Zineb	Talbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	133 Rue Ifrane	Quartier Al Wifaq	Boujniba	32.9049975	-6.6818566	\N	\N	\N	\N	f	Sécurité	+212634837255	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	7a0b5295-56bc-40db-ad31-1f128853166c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01157	Othmane	Touhami	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	114 Rue Hassan II	Quartier Anassi	Oued Zem	32.8826257	-6.9190305	\N	\N	\N	\N	f	Mécanicien	+212622190863	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	40327ad8-75f4-47b4-9eed-04fa4fbcbe2a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01158	Hicham	Chaoui	d39d79ec-a716-4839-a93d-1845d00c182c	N	21 Rue de la Paix	Quartier Tamaris	Bir Mezoui	32.8756945	-6.9110627	\N	\N	\N	\N	f	Comptable	+212677801348	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	73b75242-cead-4b1a-86f8-ab99f98a5a23	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ec25ddbf-0661-43f8-86e9-d39ec1b89f70
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01159	Anass	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	179 Rue Al Massira	Quartier Hassania	Gueffaf	32.8968976	-6.9322715	\N	\N	\N	\N	f	Logisticien	+212649899503	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ac4651cf-6e9c-4797-852a-af0196f9b862	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	81fbe024-836e-4b22-9fb1-084e1c1d4b02
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01160	Anass	Laaroussi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	125 Rue Atlas	Quartier Medersa	Bir Mezoui	32.8537634	-6.8771614	\N	\N	\N	\N	f	Ingénieur	+212650843473	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	893c496d-f803-4897-817a-80458907aa38	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01161	Bilal	Louizi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	141 Rue de la Paix	Quartier Hay Mohammadi	Gueffaf	32.8586146	-6.8744339	\N	\N	\N	\N	f	Sécurité	+212639872739	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	86a9f310-694f-441b-ad97-d5d610b5651a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9d79e041-d6fb-4c2c-a77f-1871b8371021
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01162	Rajaa	Chraibi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	117 Rue des Orangers	Quartier Hassania	Boulanoir	32.8964208	-6.7737099	\N	\N	\N	\N	f	Superviseur	+212686570363	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3928cf2f-8766-4937-82b9-200e27d1ec54	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01163	Noureddine	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	5 Rue Mohammed V	Quartier Hay Salam	Oued Zem	32.8414033	-6.8024476	\N	\N	\N	\N	f	Superviseur	+212681246039	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5651902d-100b-4a47-9ccc-853cda347bb5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	7a33b4ff-370a-4ecf-a056-7e94f8dd87a9
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01164	Samira	Lahlou	d39d79ec-a716-4839-a93d-1845d00c182c	S	90 Rue Ifrane	Quartier Al Wifaq	Gueffaf	32.8603787	-6.9049781	\N	\N	\N	\N	f	Analyste	+212681606502	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	962b68f1-469d-41e1-b99a-2bbf9c841d3c	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c3508c3b-7286-4057-9cd4-c9920a7d80cf
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01165	Saad	Zouiten	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	155 Rue Al Massira	Quartier Al Amal	Oued Zem	32.8772069	-6.9262504	\N	\N	\N	\N	f	Électricien	+212653304170	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b34654c3-ba2b-4efa-b325-0e79b269244a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01166	Hicham	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	69 Rue Atlas	Quartier Anassi	Boulanoir	32.8647577	-6.5803532	\N	\N	\N	\N	f	Comptable	+212654621771	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f028f857-e98b-41b6-a54c-5f1612be8203	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01167	Mohammed	Idrissi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	88 Rue Mohammed V	Quartier Tamaris	Khouribga	32.8919104	-6.7763058	\N	\N	\N	\N	f	Logisticien	+212648107207	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	940c09b9-6233-4265-96a6-d8f9ad7cdade	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01168	Anass	Moumen	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	42 Rue Atlas	Quartier Al Amal	Bir Mezoui	32.8507322	-6.8734961	\N	\N	\N	\N	f	Technicien	+212657958902	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f573614f-ade8-496d-9518-be00d7f02005	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	cc84056a-d973-4b87-ac37-68494dfb67ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01169	Soumia	Benkiran	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	163 Rue de la Paix	Quartier Medersa	Boulanoir	32.8738866	-6.9042284	\N	\N	\N	\N	f	Administratif	+212634344912	Qualité	t	company_bus	Non	f	f	0	t	\N	\N	\N	5e48bcd6-96a1-4de8-85a3-9c71143b519b	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01170	Samira	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	P1	46 Rue Mohammed V	Quartier Al Wifaq	Boulanoir	32.8401806	-6.8065504	\N	\N	\N	\N	f	RH	+212614878825	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0650ee4b-95cf-450b-8f83-f267d26a5d4e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01171	Sanaa	Tijani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	152 Rue Al Massira	Quartier Hay Salam	Bir Mezoui	32.885616	-6.9013956	\N	\N	\N	\N	f	Administratif	+212692719670	Logistique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f966b5a3-286b-4689-a792-db06c91deffb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	40888fb9-721f-4164-9e0b-bdd83b245b3a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01172	Othmane	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	165 Rue des Orangers	Quartier Al Wifaq	Oued Zem	32.9006119	-6.7824587	\N	\N	\N	\N	f	Mécanicien	+212660249089	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	f1dd61b2-a188-4d7b-b0c9-47ae89abce9f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	a13c5262-8689-4e24-827c-5d97dbe0dbfc
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01173	Hanane	El Kabbaj	d39d79ec-a716-4839-a93d-1845d00c182c	N	172 Rue Atlas	Quartier Tamaris	Boulanoir	32.8901471	-6.9352301	\N	\N	\N	\N	f	Administratif	+212617048760	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	6904812f-c153-4902-9be1-aea7cbebe3a3	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	b7046491-64cb-4b98-86cd-aa75fa98c450
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01174	Karim	Sabri	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	28 Rue Al Massira	Quartier Anassi	Hattane	32.9022962	-6.6835408	\N	\N	\N	\N	f	RH	+212632712108	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	9ccf4a9d-bbdd-4a59-a95d-f04cddb188ad	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	47c757ae-ce45-4436-b79c-4781198f9507
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01175	Soumia	Zouiten	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	131 Rue Hassan II	Quartier Hay Mohammadi	Oued Zem	32.8938807	-6.9046024	\N	\N	\N	\N	f	Agent de maîtrise	+212643071241	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ba29d720-ae3a-46ea-a8a9-8dc16e3a3701	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	ee482df6-057a-42e5-99f9-3ad96f7e23ed
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01176	Aicha	Tijani	d39d79ec-a716-4839-a93d-1845d00c182c	P2	68 Rue Ifrane	Quartier Al Amal	Gueffaf	32.871956	-6.9112276	\N	\N	\N	\N	f	Superviseur	+212652867731	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d20b744b-49fb-452f-9bd9-1e2f500de672	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01177	Naima	Maâchi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	133 Rue Hassan II	Quartier Tamaris	Oued Zem	32.8962784	-6.7746081	\N	\N	\N	\N	f	Mécanicien	+212675917909	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d5b31bbf-82ed-4998-ad15-0e0661f16a1a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	f8f58974-a171-4b18-9b74-77d6694663c0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01178	Zineb	Hajji	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	132 Rue Ifrane	Quartier Hassania	Gueffaf	32.8981611	-6.7732964	\N	\N	\N	\N	f	Électricien	+212640966348	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	e07ef038-ed25-47b3-80a6-6c6a0a4d7380	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	c0adf89f-fd4e-4548-aea5-667f94d8b96d
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01179	Karim	Berrada	d39d79ec-a716-4839-a93d-1845d00c182c	S	47 Rue Mohammed V	Quartier Centre	Boujniba	32.8775075	-6.9276297	\N	\N	\N	\N	f	Qualité	+212689846024	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3154466c-2783-4ed5-96c9-eba6b3c05398	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01180	Hafida	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	143 Rue de la Paix	Quartier Medersa	Hattane	32.8368092	-6.8024872	\N	\N	\N	\N	f	Électricien	+212630710892	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d2cbfe5a-bc3c-4882-94da-f41884712a82	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	6e7624c7-f81a-4577-87e7-a294b2a2ef8a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01181	Kawtar	Idrissi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	104 Rue Hassan II	Quartier Anassi	Bir Mezoui	32.8648544	-6.5811276	\N	\N	\N	\N	f	Agent de maîtrise	+212629527737	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	5e49c7df-4596-494a-b2df-2d1a8abdd36a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01182	Anass	Sabri	d39d79ec-a716-4839-a93d-1845d00c182c	P3	195 Rue Ifrane	Quartier Al Amal	Hattane	32.8654574	-6.5833296	\N	\N	\N	\N	f	Ingénieur	+212637220737	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8a8a5be3-db4f-4991-9296-3178d5d3f510	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	13d1b81c-96b9-42d8-a1cb-996e864cc66a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01183	Lahcen	Idrissi	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	70 Rue Hassan II	Quartier Hay Mohammadi	Oued Zem	32.900293	-6.676797	\N	\N	\N	\N	f	RH	+212656513043	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	d479e2bf-7880-4e30-9508-b11175cd8cab	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01184	Fatima	Hassouni	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	36 Rue Atlas	Quartier Hay Mohammadi	Boulanoir	32.8706114	-6.9270922	\N	\N	\N	\N	f	Mécanicien	+212639436932	Sécurité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	75aee4c8-e57d-405d-8219-29b7e6ed3d54	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	10de6a3b-f933-40f9-a92c-2f0b74b1b48c
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01185	Laila	Benali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	104 Rue Mohammed V	Quartier Hay Salam	Khouribga	32.8680654	-6.9178123	\N	\N	\N	\N	f	Comptable	+212663538450	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	ff1d4311-aab8-4a89-a7f5-f94fc92e086f	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	90db88b2-09d7-49ea-87da-2b7957386653
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01186	Houda	Dahbi	1edc2404-0388-4ceb-9970-3743a87ce5ac	P2	57 Rue Ifrane	Quartier Tamaris	Gueffaf	32.9070388	-6.7817717	\N	\N	\N	\N	f	Conducteur	+212654690086	Qualité	t	company_bus	Non	f	f	0	t	\N	\N	\N	e66e1f55-a549-4d5b-9efe-ee707b2fed66	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01187	Najat	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P3	23 Rue de la Paix	Quartier Tamaris	Gueffaf	32.8649466	-6.5820935	\N	\N	\N	\N	f	Comptable	+212661971154	Administration	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3a2923e0-68aa-4b32-a4e4-b45f37039bdb	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01188	Zineb	Benkiran	d39d79ec-a716-4839-a93d-1845d00c182c	N	32 Rue Hassan II	Quartier Hay Mohammadi	Oued Zem	32.8790246	-6.9093778	\N	\N	\N	\N	f	RH	+212669019991	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0f53399a-c129-4f8d-87cf-6d256b85cc8e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	9e7839b9-a63b-4b5b-88cf-299c28ff2192
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01189	Khalid	Tazi	1edc2404-0388-4ceb-9970-3743a87ce5ac	S	40 Rue Hassan II	Quartier Hassania	Hattane	32.8844564	-6.9307381	\N	\N	\N	\N	f	Qualité	+212656469454	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3bd5327b-e2ec-451b-970f-91892a04417e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01190	Othmane	Skali	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P1	117 Rue de la Paix	Quartier Hassania	Oued Zem	32.8646706	-6.5836642	\N	\N	\N	\N	f	Logisticien	+212650957606	RH	t	company_bus	Oui	f	f	0	t	\N	\N	\N	aa6248aa-c436-4621-ab0f-5c56ab210f24	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	433f864f-a2dc-4593-bcec-62afa30011ac
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01191	Khalid	Khattabi	d39d79ec-a716-4839-a93d-1845d00c182c	P2	27 Rue Al Massira	Quartier Hay Mohammadi	Boulanoir	32.8735751	-6.9081335	\N	\N	\N	\N	f	Comptable	+212664343763	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0a7f4de9-bb4e-4c19-b671-462550ff12b5	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	da969ae8-b71f-4468-8d5a-d30d36a039b3
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01192	Loubna	Rahmani	1edc2404-0388-4ceb-9970-3743a87ce5ac	P3	154 Rue Atlas	Quartier Hay Salam	Oued Zem	32.8541291	-6.5734201	\N	\N	\N	\N	f	Comptable	+212635254867	Maintenance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	3677f9c8-c4e9-46f2-b7b4-182d49a730e4	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	561752fb-64c6-4268-aba6-6273825254f7
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01193	Ilham	Naciri	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	N	118 Rue Mohammed V	Quartier Hay Mohammadi	Gueffaf	32.8996905	-6.9016522	\N	\N	\N	\N	f	Comptable	+212653484552	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	4a6c27e7-cfca-4e99-8d09-17f47c8e6b6a	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01194	Omar	Moumen	d39d79ec-a716-4839-a93d-1845d00c182c	S	165 Rue Mohammed V	Quartier Al Wifaq	Gueffaf	32.8868473	-6.9077265	\N	\N	\N	\N	f	Agent de maîtrise	+212622943095	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	a5e1ecd0-056c-4dcc-b55f-d6379088cd29	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	23bf1f3d-4d8c-405d-bb18-d89c2e9f6390
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01195	Hamza	Benali	1edc2404-0388-4ceb-9970-3743a87ce5ac	P1	178 Rue Atlas	Quartier Centre	Gueffaf	32.9170721	-6.723243	\N	\N	\N	\N	f	Technicien	+212657143315	Production	t	company_bus	Oui	f	f	0	t	\N	\N	\N	0eee9bcf-392f-4b3c-b057-c3f884803b5e	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01196	Anass	Khattabi	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	P2	111 Rue Mohammed V	Quartier Hay Salam	Bir Mezoui	32.8744148	-6.9143834	\N	\N	\N	\N	f	Électricien	+212689975610	Qualité	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b46a6f75-97a7-495a-aaf3-9a14ad8f7e0d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	1d054f29-25a9-40d0-8848-cb09d9c7919e
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01197	Noureddine	Qasmi	d39d79ec-a716-4839-a93d-1845d00c182c	P3	193 Rue Hassan II	Quartier Centre	Gueffaf	32.8999398	-6.9005097	\N	\N	\N	\N	t	Électricien	+212689531863	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	8579fdcd-9152-4e09-af3e-991d7bf6faec	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	fff5e343-50e8-4297-9345-9e7d91528cae
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01198	Mustapha	El Kabbaj	1edc2404-0388-4ceb-9970-3743a87ce5ac	N	103 Rue Mohammed V	Quartier Hassania	Khouribga	32.8928436	-6.8968406	\N	\N	\N	\N	f	Ingénieur	+212689881110	Transport	t	company_bus	Oui	f	f	0	t	\N	\N	\N	39ffe18b-77eb-46f6-9667-025f0a11ca9d	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	64878d4e-b9f9-4fea-825d-d1b4e996f40a
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01199	Nadia	Rahmani	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	S	88 Rue Ifrane	Quartier Al Amal	Hattane	32.9060154	-6.7864602	\N	\N	\N	\N	f	Électricien	+212611709295	Finance	t	company_bus	Oui	f	f	0	t	\N	\N	\N	74f85a86-10c7-4d2e-bc9e-5815a738b086	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	394f0f69-98b0-49aa-9f87-41412603ebf0
0cea9745-6aa2-4105-9bdc-341d95999048	EMP01200	Khadija	Ouali	d39d79ec-a716-4839-a93d-1845d00c182c	P1	57 Rue Ifrane	Quartier Tamaris	Boujniba	32.8812553	-6.9186621	\N	\N	\N	\N	f	Électricien	+212636460392	Informatique	t	company_bus	Oui	f	f	0	t	\N	\N	\N	b65f0d39-7732-47c2-9c1a-e434306f81f7	2026-04-03 03:52:31.332682+00	2026-04-03 03:52:31.332682+00	d645e2db-3fb3-48c8-aec0-76fc9413697d
\.


--
-- Data for Name: employee_leave; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_leave (employee_id, leave_type, start_date, end_date, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_modal; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_modal (employee_id, primary_mode, alternative_mode, distance_km, travel_time_min, frequency, interest_company_transport, reason_current_mode, departure_time, accepts_common_pickup, max_pickup_distance_meters, has_private_car, volunteer_driver, carpool_seats_available, max_detour_minutes, bonus_opt_in, observations, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: financial_scenario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.financial_scenario (tenant_id, name, investment_model, duration_years, fleet_composition, params, results, created_by, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: generated_report; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.generated_report (tenant_id, report_type, params, file_url, format, generated_at, generated_by, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: horaire_travail; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.horaire_travail (id, tenant_id, site_id, type_horaire, depart_h1, retour_h1, depart_h2, retour_h2, observations, created_at, updated_at) FROM stdin;
4cf717dd-9922-4a2b-b892-f4d72a19a724	0cea9745-6aa2-4105-9bdc-341d95999048	\N	Poste 1	05:50	14:45	\N	15:45	\N	2026-04-02 23:50:41.950918+00	2026-04-02 23:50:41.950918+00
861a7942-a86c-46a9-85e8-b73a6d4cd476	0cea9745-6aa2-4105-9bdc-341d95999048	\N	Poste 2	13:50	22:45	\N	23:45	\N	2026-04-02 23:50:41.950918+00	2026-04-02 23:50:41.950918+00
64562fdd-aff5-41cb-85f5-de8a3e2663bd	0cea9745-6aa2-4105-9bdc-341d95999048	\N	Poste 3	21:50	06:45	\N	07:45	\N	2026-04-02 23:50:41.950918+00	2026-04-02 23:50:41.950918+00
729f0682-4444-41af-9a7a-8941e3f4b09e	0cea9745-6aa2-4105-9bdc-341d95999048	\N	Normal	07:00	16:00	\N	\N	\N	2026-04-02 23:50:41.950918+00	2026-04-02 23:50:41.950918+00
c0ff5e68-c7da-4ee6-8107-f41926f15822	0cea9745-6aa2-4105-9bdc-341d95999048	\N	Sirène	07:00	12:00	14:00	18:00	\N	2026-04-02 23:50:41.950918+00	2026-04-02 23:50:41.950918+00
\.


--
-- Data for Name: km_consommation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.km_consommation (id, tenant_id, site_id, prestataire, vehicle_type, vehicle_count_peak, km_avg, km_min, km_max, seat_count, fuel_consumption_l100km, monthly_cost_per_vehicle_mad, observations, created_at, updated_at) FROM stdin;
fe000fc9-6578-4215-ac19-2e5323bcd185	0cea9745-6aa2-4105-9bdc-341d95999048	\N	STCR	Autocars	13	8948.00	7313.00	8854.00	48	34.00	114721.20	\N	2026-04-03 01:21:08.208173+00	2026-04-03 01:21:08.208173+00
9bdd6b52-f992-4140-a803-6eddd643fdda	0cea9745-6aa2-4105-9bdc-341d95999048	\N	STCR	Minibus 17	9	2811.00	1981.00	4192.00	17	13.00	23760.00	\N	2026-04-03 01:21:08.21218+00	2026-04-03 01:21:08.21218+00
8527c8f1-ee3e-4c2b-989c-6d14c9244d75	0cea9745-6aa2-4105-9bdc-341d95999048	\N	STCR	Minibus 20	5	6360.00	4653.00	8502.00	20	11.00	44550.00	\N	2026-04-03 01:21:08.21512+00	2026-04-03 01:21:08.21512+00
d2766556-2887-47dd-9ac7-c5d72ae26f25	0cea9745-6aa2-4105-9bdc-341d95999048	\N	STCR	Minicar 30	3	7141.00	6531.00	7479.00	30	21.00	59400.00	\N	2026-04-03 01:21:08.226044+00	2026-04-03 01:21:08.226044+00
fdc6fe88-247e-4474-9e97-7dc63653f2a1	0cea9745-6aa2-4105-9bdc-341d95999048	\N	S/TOURISME	Autocars	12	8632.00	7240.00	10146.00	48	34.00	113330.80	\N	2026-04-03 01:21:08.228655+00	2026-04-03 01:21:08.228655+00
1b7c7118-942c-48d7-abe2-6dd6769e36d8	0cea9745-6aa2-4105-9bdc-341d95999048	\N	S/TOURISME	Minicar 30	5	7094.00	5352.00	9570.00	30	21.00	59400.00	\N	2026-04-03 01:21:08.231638+00	2026-04-03 01:21:08.231638+00
151a6254-e00a-493b-9a97-7aac7a07dd67	0cea9745-6aa2-4105-9bdc-341d95999048	\N	MANAVETTE	Minibus 17	8	3722.00	1489.00	5090.00	17	13.00	23760.00	\N	2026-04-03 01:21:08.234412+00	2026-04-03 01:21:08.234412+00
2fd0d190-e346-4c5a-b7fc-05a2d20b4298	0cea9745-6aa2-4105-9bdc-341d95999048	\N	CTM	Autocars	4	10600.00	9500.00	11600.00	48	35.00	121990.00	\N	2026-04-03 01:21:08.236757+00	2026-04-03 01:21:08.236757+00
017a3ef4-d9a9-4bd6-b61b-97076b4e9e56	0cea9745-6aa2-4105-9bdc-341d95999048	\N	SOTREG	Autocars	32	5500.00	\N	7500.00	48	41.00	38250.00	\N	2026-04-03 01:21:08.239753+00	2026-04-03 01:21:08.239753+00
555b3c69-ae68-476f-addf-4a03e3001acf	0cea9745-6aa2-4105-9bdc-341d95999048	\N	SOTREG	Minibus 17	4	1500.00	1000.00	3000.00	17	17.00	22750.00	\N	2026-04-03 01:21:08.241885+00	2026-04-03 01:21:08.241885+00
\.


--
-- Data for Name: kpi_snapshot; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.kpi_snapshot (tenant_id, site_id, snapshot_date, kpi_type, value, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: optimization; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.optimization (tenant_id, site_id, condition_type, status, params, metrics, target_date, completed_at, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: optimization_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.optimization_settings (tenant_id, meeting_radius_meters, max_walking_distance_meters, max_route_duration_seconds, fuel_cost_per_liter, fuel_consumption_l_per_100km, co2_kg_per_liter, rti_threshold_minutes, night_mode_start, night_mode_end, min_night_group_size, id, created_at, updated_at) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	500	800	5400	12	15	2.68	15	22:00	06:00	3	5d3f82aa-9b46-4845-9da7-d4771880483f	2026-04-02 20:41:41.243263+00	2026-04-02 20:41:41.243263+00
\.


--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.permission (resource, action, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: point_arret; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.point_arret (id, tenant_id, site_id, code, nom, adresse, ville, lat, lng, prestataire, is_active, observations, created_at, updated_at, correspondance_tb) FROM stdin;
ee482df6-057a-42e5-99f9-3ad96f7e23ed	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH01	HAMROUKAT1	\N	Khouribga	32.8977513	-6.9078049	SOTREG	t	\N	2026-04-03 01:13:22.092247+00	2026-04-03 01:13:22.092247+00	H
4e65a9fb-1294-44cd-b429-40fca7d48bd2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH02	HAMROUKAT2	\N	Khouribga	32.8970871	-6.903115	SOTREG	t	\N	2026-04-03 01:13:22.125452+00	2026-04-03 01:13:22.125452+00	H
fff5e343-50e8-4297-9345-9e7d91528cae	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH03	HAMROUKAT3	\N	Khouribga	32.8966001	-6.8992711	SOTREG	t	\N	2026-04-03 01:13:22.137038+00	2026-04-03 01:13:22.137038+00	\N
64878d4e-b9f9-4fea-825d-d1b4e996f40a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH04	TITANIC	\N	Khouribga	32.8925012	-6.8943217	SOTREG	t	\N	2026-04-03 01:13:22.139895+00	2026-04-03 01:13:22.139895+00	T
40888fb9-721f-4164-9e0b-bdd83b245b3a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH05	AL MASSIRA	\N	Khouribga	32.8873482	-6.8990454	SOTREG	t	\N	2026-04-03 01:13:22.14192+00	2026-04-03 01:13:22.14192+00	1
23bf1f3d-4d8c-405d-bb18-d89c2e9f6390	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH06	NAHDA	\N	Khouribga	32.8858381	-6.9057054	SOTREG	t	\N	2026-04-03 01:13:22.144718+00	2026-04-03 01:13:22.144718+00	2
520136de-5ab5-4996-8c97-87b8a848416a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH07	LAADOULAT	\N	Khouribga	32.8883051	-6.9181398	SOTREG	t	\N	2026-04-03 01:13:22.147888+00	2026-04-03 01:13:22.147888+00	3
f384b735-a167-43bf-a36c-0c61da2f0977	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH08	ONEP	\N	Khouribga	32.8904708	-6.9276843	SOTREG	t	\N	2026-04-03 01:13:22.150507+00	2026-04-03 01:13:22.150507+00	Q1
04c98969-73d1-467c-a8b2-4f274861a5b2	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH09	CAFE WARDA	\N	Khouribga	32.8919377	-6.9338923	SOTREG	t	\N	2026-04-03 01:13:22.153123+00	2026-04-03 01:13:22.153123+00	Q2
81fbe024-836e-4b22-9fb1-084e1c1d4b02	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH10	AVOLA	\N	Khouribga	32.8975878	-6.9330748	SOTREG	t	\N	2026-04-03 01:13:22.154846+00	2026-04-03 01:13:22.154846+00	Q3
51168416-2650-41a2-b43a-e3150d5638bc	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH11	Pharmacie Attraoui	\N	Khouribga	32.8973972	-6.9395981	SOTREG	t	\N	2026-04-03 01:13:22.157896+00	2026-04-03 01:13:22.157896+00	Q4
0a42051c-cafb-428d-a297-608bfe74954a	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH12	Pharmacie Ouafae (Marjane Market)	\N	Khouribga	32.8987787	-6.9363085	SOTREG	t	\N	2026-04-03 01:13:22.160322+00	2026-04-03 01:13:22.160322+00	Q5
eb0a6b1c-35b6-4397-990a-a25bde1af56d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH13	RABBANI	\N	Khouribga	32.8930183	-6.9379905	SOTREG	t	\N	2026-04-03 01:13:22.163091+00	2026-04-03 01:13:22.163091+00	Q6
b7046491-64cb-4b98-86cd-aa75fa98c450	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH14	ECOLE AMAL	\N	Khouribga	32.891086	-6.9340732	SOTREG	t	\N	2026-04-03 01:13:22.166084+00	2026-04-03 01:13:22.166084+00	Q7
fc0350fe-3fa3-4f40-bdaa-b702a4cecfcd	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH15	MOSQUE QODS	\N	Khouribga	32.8860129	-6.9310167	SOTREG	t	\N	2026-04-03 01:13:22.168523+00	2026-04-03 01:13:22.168523+00	Q8
d645e2db-3fb3-48c8-aec0-76fc9413697d	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH16	ROUDANI	\N	Khouribga	32.8845079	-6.9208855	SOTREG	t	\N	2026-04-03 01:13:22.170714+00	2026-04-03 01:13:22.170714+00	4
10de6a3b-f933-40f9-a92c-2f0b74b1b48c	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH17	IMARA	\N	Khouribga	32.873605	-6.924402	SOTREG	t	\N	2026-04-03 01:13:22.172896+00	2026-04-03 01:13:22.172896+00	IMARA
afd2c042-05e2-4439-98e0-04dd22298c55	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH18	KHOUADRIA	\N	Khouribga	32.8789325	-6.9199215	SOTREG	t	\N	2026-04-03 01:13:22.174973+00	2026-04-03 01:13:22.174973+00	5
ba717b0e-fedb-4a58-b7a7-253549662e69	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH19	BELLE ILE	\N	Khouribga	32.8778011	-6.916716	SOTREG	t	\N	2026-04-03 01:13:22.177449+00	2026-04-03 01:13:22.177449+00	6
1d054f29-25a9-40d0-8848-cb09d9c7919e	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH20	KASSOU	\N	Khouribga	32.8731463	-6.9169585	SOTREG	t	\N	2026-04-03 01:13:22.179855+00	2026-04-03 01:13:22.179855+00	7
da969ae8-b71f-4468-8d5a-d30d36a039b3	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH21	BARIGOU	\N	Khouribga	32.8743092	-6.9118776	SOTREG	t	\N	2026-04-03 01:13:22.181999+00	2026-04-03 01:13:22.181999+00	8
ec25ddbf-0661-43f8-86e9-d39ec1b89f70	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH22	GOUTE DE LAIT	\N	Khouribga	32.877201	-6.9107695	SOTREG	t	\N	2026-04-03 01:13:22.184117+00	2026-04-03 01:13:22.184117+00	9
9e7839b9-a63b-4b5b-88cf-299c28ff2192	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH23	LA PISCINE	\N	Khouribga	32.8756811	-6.9054707	SOTREG	t	\N	2026-04-03 01:13:22.186361+00	2026-04-03 01:13:22.186361+00	10
5b6b9621-f986-4910-b2a5-cd15829cae7b	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH24	CFO	\N	Khouribga	32.8799843	-6.9010458	SOTREG	t	\N	2026-04-03 01:13:22.188745+00	2026-04-03 01:13:22.188745+00	11
caa53059-ba46-45cb-b51d-aac8e75b86da	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH25	LA FACULTE	\N	Khouribga	32.8681224	-6.9068366	SOTREG	t	\N	2026-04-03 01:13:22.191648+00	2026-04-03 01:13:22.191648+00	Z
c3508c3b-7286-4057-9cd4-c9920a7d80cf	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH26	LA FERME	\N	Khouribga	32.861961	-6.9078155	SOTREG	t	\N	2026-04-03 01:13:22.197822+00	2026-04-03 01:13:22.197822+00	F
90db88b2-09d7-49ea-87da-2b7957386653	0cea9745-6aa2-4105-9bdc-341d95999048	d39d79ec-a716-4839-a93d-1845d00c182c	KH27	OUM KORA	\N	Khouribga	32.868222	-6.916244	SOTREG	t	\N	2026-04-03 01:13:22.200192+00	2026-04-03 01:13:22.200192+00	OK
cc84056a-d973-4b87-ac37-68494dfb67ac	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BL01	HAMAM OCP	\N	Bolanouir	32.851847	-6.8763768	SOTREG	t	\N	2026-04-03 01:13:22.202304+00	2026-04-03 01:13:22.202304+00	\N
564f621c-a30b-4757-8217-db10cc94c897	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BL02	CHEF VILLAGE	\N	Bolanouir	32.8554409	-6.8778762	SOTREG	t	\N	2026-04-03 01:13:22.204446+00	2026-04-03 01:13:22.204446+00	\N
9d79e041-d6fb-4c2c-a77f-1871b8371021	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BL03	LA PISCINE	\N	Bolanouir	32.8625471	-6.8782838	SOTREG	t	\N	2026-04-03 01:13:22.210994+00	2026-04-03 01:13:22.210994+00	\N
ed3c446d-5d01-4043-8568-b261001ffdec	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BL04	EL MONTALAQ	\N	Bolanouir	32.8600485	-6.8739306	SOTREG	t	\N	2026-04-03 01:13:22.21386+00	2026-04-03 01:13:22.21386+00	\N
394f0f69-98b0-49aa-9f87-41412603ebf0	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ01	station	\N	Boujniba	32.9060757	-6.7829419	SOTREG	t	\N	2026-04-03 01:13:22.216204+00	2026-04-03 01:13:22.216204+00	\N
a13c5262-8689-4e24-827c-5d97dbe0dbfc	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ02	pharmacie Ihssan	\N	Boujniba	32.9019261	-6.7816601	SOTREG	t	\N	2026-04-03 01:13:22.218526+00	2026-04-03 01:13:22.218526+00	\N
c0adf89f-fd4e-4548-aea5-667f94d8b96d	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ03	châteaux d'eau	\N	Boujniba	32.90118	-6.7727951	SOTREG	t	\N	2026-04-03 01:13:22.220912+00	2026-04-03 01:13:22.220912+00	\N
057ec0d4-3d1a-4f9a-b1dc-6eec769ba329	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ04	hammam Saadâ	\N	Boujniba	32.895293	-6.77559	SOTREG	t	\N	2026-04-03 01:13:22.227031+00	2026-04-03 01:13:22.227031+00	\N
f8f58974-a171-4b18-9b74-77d6694663c0	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ05	gendarme de bj	\N	Boujniba	32.8957806	-6.7755766	SOTREG	t	\N	2026-04-03 01:13:22.230068+00	2026-04-03 01:13:22.230068+00	\N
7963b7d6-e42f-4620-acf3-51938a4f9742	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ06	poste Bank - et l'hopital	\N	Boujniba	32.8978638	-6.7778887	SOTREG	t	\N	2026-04-03 01:13:22.23238+00	2026-04-03 01:13:22.23238+00	\N
9cad5401-9690-4f20-a2b1-32db93b477a1	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ07	wafa Bank	\N	Boujniba	32.899411	-6.7816303	SOTREG	t	\N	2026-04-03 01:13:22.234684+00	2026-04-03 01:13:22.234684+00	\N
97ee6b1d-35c8-46e1-96f4-249229429500	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BJ08	collège Khalid ben Walid	\N	Boujniba	32.8958121	-6.7810724	SOTREG	t	\N	2026-04-03 01:13:22.237394+00	2026-04-03 01:13:22.237394+00	\N
7a33b4ff-370a-4ecf-a056-7e94f8dd87a9	0cea9745-6aa2-4105-9bdc-341d95999048	\N	HT01	Sbata 1 château de l'eau	\N	Hattane	32.8437162	-6.7999096	SOTREG	t	\N	2026-04-03 01:13:22.239664+00	2026-04-03 01:13:22.239664+00	\N
6e7624c7-f81a-4577-87e7-a294b2a2ef8a	0cea9745-6aa2-4105-9bdc-341d95999048	\N	HT02	Sbata 2 mosquée	\N	Hattane	32.8383618	-6.8037452	SOTREG	t	\N	2026-04-03 01:13:22.241449+00	2026-04-03 01:13:22.241449+00	\N
773c4704-46df-4e90-af11-4a957fb87ab5	0cea9745-6aa2-4105-9bdc-341d95999048	\N	HT03	gandarme de hat	\N	Hattane	32.8376294	-6.8066581	SOTREG	t	\N	2026-04-03 01:13:22.243339+00	2026-04-03 01:13:22.243339+00	\N
47c757ae-ce45-4436-b79c-4781198f9507	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BM01	Mosquée	\N	Bir Mezoui	32.9024908	-6.681216	SOTREG	t	\N	2026-04-03 01:13:22.245974+00	2026-04-03 01:13:22.245974+00	\N
0afdd869-9cd4-4ece-ab38-a1ef1f90a0b3	0cea9745-6aa2-4105-9bdc-341d95999048	\N	BM02	A côté du Rond-point	\N	Bir Mezoui	32.9013181	-6.6784297	SOTREG	t	\N	2026-04-03 01:13:22.248414+00	2026-04-03 01:13:22.248414+00	\N
31fee6e6-d68d-423a-8d6b-d7b3bb74d2a0	0cea9745-6aa2-4105-9bdc-341d95999048	\N	GF01	A proximité de CHEMIN DE FER	\N	Gueffaf	32.9202721	-6.7192734	SOTREG	t	\N	2026-04-03 01:13:22.250781+00	2026-04-03 01:13:22.250781+00	\N
12e1f182-78d1-4a9d-b126-7480b5757fb5	0cea9745-6aa2-4105-9bdc-341d95999048	\N	GF02	KIYADA	\N	Gueffaf	32.9229051	-6.7178315	SOTREG	t	\N	2026-04-03 01:13:22.253673+00	2026-04-03 01:13:22.253673+00	\N
433f864f-a2dc-4593-bcec-62afa30011ac	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ01	BANANA	\N	Oued Zem	32.8625064	-6.5812701	SOTREG	t	\N	2026-04-03 01:13:22.257738+00	2026-04-03 01:13:22.257738+00	\N
fa1bf35f-d421-454e-9098-2d82d14a810b	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ02	PHARMACIE NOUR	\N	Oued Zem	32.8558643	-6.5794193	SOTREG	t	\N	2026-04-03 01:13:22.260404+00	2026-04-03 01:13:22.260404+00	\N
68eb90a0-b5c9-4251-8750-4d3ab026832a	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ03	SOUK	\N	Oued Zem	32.8547648	-6.5773701	SOTREG	t	\N	2026-04-03 01:13:22.263744+00	2026-04-03 01:13:22.263744+00	\N
561752fb-64c6-4268-aba6-6273825254f7	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ04	AIN BARTI	\N	Oued Zem	32.8532777	-6.5739262	SOTREG	t	\N	2026-04-03 01:13:22.266059+00	2026-04-03 01:13:22.266059+00	\N
55779b27-5083-4587-b420-cceda99cca35	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ05	ISTA	\N	Oued Zem	32.854945	-6.5687871	SOTREG	t	\N	2026-04-03 01:13:22.269122+00	2026-04-03 01:13:22.269122+00	\N
7c9aa98e-4b29-4561-a79c-49ea118322ab	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ06	AL BOUSTAN	\N	Oued Zem	32.859403	-6.5524798	SOTREG	t	\N	2026-04-03 01:13:22.272849+00	2026-04-03 01:13:22.272849+00	\N
309b7f89-2f27-4c54-b608-0e484991e82a	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ07	AL HASANIA	\N	Oued Zem	32.8600461	-6.5562665	SOTREG	t	\N	2026-04-03 01:13:22.275606+00	2026-04-03 01:13:22.275606+00	\N
b188ccc7-d494-4c5c-b537-ea48c8c148fa	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ08	BRACH	\N	Oued Zem	32.8623081	-6.5660727	SOTREG	t	\N	2026-04-03 01:13:22.27813+00	2026-04-03 01:13:22.27813+00	\N
a51a72f3-499c-4a94-9697-d3ba1d9fddda	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ09	CHAABI	\N	Oued Zem	32.8631643	-6.5699887	SOTREG	t	\N	2026-04-03 01:13:22.281131+00	2026-04-03 01:13:22.281131+00	\N
8c1a4d52-abda-485a-a2ed-da70ed803bb5	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ10	TANJI	\N	Oued Zem	32.8646152	-6.5763724	SOTREG	t	\N	2026-04-03 01:13:22.284699+00	2026-04-03 01:13:22.284699+00	\N
8b127225-8987-4118-a1c3-8b18d476db1f	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ11	VILLAGE	\N	Oued Zem	32.8655208	-6.580283	SOTREG	t	\N	2026-04-03 01:13:22.287644+00	2026-04-03 01:13:22.287644+00	\N
13d1b81c-96b9-42d8-a1cb-996e864cc66a	0cea9745-6aa2-4105-9bdc-341d95999048	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	OZ12	KORAIA	\N	Oued Zem	32.8648292	-6.5814002	SOTREG	t	\N	2026-04-03 01:13:22.290248+00	2026-04-03 01:13:22.290248+00	\N
\.


--
-- Data for Name: roi_calculation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.roi_calculation (financial_scenario_id, baseline_absence_rate, target_absence_rate, headcount, daily_cost, replacement_cost, turnover_rate_before, turnover_rate_after, training_hour_cost, engagement_rate, annual_travel_hours, roi_absenteeism, roi_retention, roi_journey, roi_fleet_optimization, roi_total, payback_months, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.role (tenant_id, name, permissions, is_system_role, id, created_at, updated_at) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	admin	["*"]	t	d4200a77-c304-4f56-a79b-c4d0e20e88dd	2026-04-02 20:34:31.852551+00	2026-04-02 20:34:31.852551+00
0cea9745-6aa2-4105-9bdc-341d95999048	drh	["employees:read", "employees:write", "reports:read", "reports:write"]	t	1da51a69-a640-4965-b67a-cf161aaa22db	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	daf	["financial:read", "financial:write", "reports:read"]	t	ffae153f-3699-4d4c-a34a-5e28e9955d73	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	salarie	["profile:read"]	t	c805e4f8-ecf6-4904-a70a-b11fe8e2cf77	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	operateur	["optimization:read", "optimization:write", "sites:read"]	t	72f3e2c7-85ab-48a1-8683-9c9c46ce2c17	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
\.


--
-- Data for Name: role_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.role_permission (role_id, permission_id, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: route; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.route (optimization_id, vehicle_id, site_id, ordered_stops, total_distance_km, total_time_minutes, polyline, geom, rti_compliance_pct, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scenario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scenario (tenant_id, site_id, baseline_optimization_id, condition_type, demand_multiplier, custom_params, estimated_metrics, name, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: site; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.site (tenant_id, code, name, address, city, lat, lng, geom, num_shifts, shift_1_entry, shift_1_exit, shift_2_entry, shift_2_exit, shift_3_entry, shift_3_exit, working_days, days_per_week, contact_name, contact_phone, access_notes, parking_notes, zfe_zone, security_profile, timezone, observations, id, created_at, updated_at, shift_1_type, shift_1_depart_h2, shift_1_retour_h2, shift_2_type, shift_2_depart_h2, shift_2_retour_h2, shift_3_type, shift_3_depart_h2, shift_3_retour_h2, active_shift_ids) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	S02	Garage SOTREG R6	Zone Industrielle, Route de Marrakech	Boujniba	32.9220096017376	-6.80367711438663	0101000020E610000040562B22F7361BC0CE071F6904764040	1	\N	\N	\N	\N	\N	\N	Lundi-Dimanche	7	\N	\N	\N	\N	f	normal	Africa/Casablanca	\N	1edc2404-0388-4ceb-9970-3743a87ce5ac	2026-04-03 00:12:15.963285+00	2026-04-03 00:12:15.963285+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	[]
0cea9745-6aa2-4105-9bdc-341d95999048	S03	Garage SOTREG Oued Zem	Technopolis, Km 7 Route de Nouaceur	Oued Zem	32.8680088492694	-6.58097720763459	0101000020E6100000410C6AB0EB521AC01620FAE91A6F4040	1	\N	\N	\N	\N	\N	\N	Lundi-Dimanche	7	\N	\N	\N	\N	f	normal	Africa/Casablanca	\N	49df8cca-a2bc-48b4-ad68-be4eaae52e4c	2026-04-03 00:12:16.07686+00	2026-04-03 00:12:16.07686+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	[]
0cea9745-6aa2-4105-9bdc-341d95999048	S01	Garage SOTREG KH	Lot 45, Zone Industrielle Ain Sebaa	Khouribga	32.8811608243207	-6.90455166222628	0101000020E61000009D377BCA429E1BC0A67CBDE0C9704040	1	\N	\N	\N	\N	\N	\N	Lundi-Dimanche	7	\N	\N	\N	\N	f	normal	Africa/Casablanca	\N	d39d79ec-a716-4839-a93d-1845d00c182c	2026-04-03 00:12:15.855246+00	2026-04-03 00:39:38.685287+00	\N	\N	\N	\N	\N	\N	\N	\N	\N	["729f0682-4444-41af-9a7a-8941e3f4b09e", "4cf717dd-9922-4a2b-b892-f4d72a19a724"]
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: tco_entry; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tco_entry (financial_scenario_id, vehicle_type, motorization, quantity, purchase_price, annual_maintenance_cost, energy_cost_per_km, annual_km, residual_value, infrastructure_cost, tco_per_vehicle, tco_total, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: tenant; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tenant (name, code, config, data_region, is_active, id, created_at, updated_at) FROM stdin;
Transpop Demo	transpop-demo	{}	eu-west	t	0cea9745-6aa2-4105-9bdc-341d95999048	2026-04-02 20:34:31.852551+00	2026-04-02 20:34:31.852551+00
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (tenant_id, email, password_hash, first_name, last_name, role_id, employee_id, mfa_enabled, mfa_secret, last_login_at, is_active, id, created_at, updated_at) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	drh@transpop.dev	$2b$12$uGjQjaYN4bgSAOfPIyWekeFCBjOxETqu07FXO2mW1kOQaQAVNXE.e	Aicha	El Mansouri	1da51a69-a640-4965-b67a-cf161aaa22db	\N	f	\N	\N	t	2f127e5d-2037-4cd6-bcdc-349a6e6a3968	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	daf@transpop.dev	$2b$12$bg6WkPk2/CIcqdivxVuEb.oZOAkOv4KnPlZ0QKN9WFElurSXqdHwy	Youssef	Bennani	ffae153f-3699-4d4c-a34a-5e28e9955d73	\N	f	\N	\N	t	9a089e19-f4e7-45e8-af76-bccbf9eeb20b	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	operateur@transpop.dev	$2b$12$DGtZubtMfyQW5w0fQfyeLezfxF33m0MtexMBpy8.zlKHQZFEC5C6e	Rachid	Tazi	72f3e2c7-85ab-48a1-8683-9c9c46ce2c17	\N	f	\N	\N	t	4ee9bda8-9a15-4cde-857d-f6c2c0e89f05	2026-04-02 20:44:00.352869+00	2026-04-02 20:44:00.352869+00
0cea9745-6aa2-4105-9bdc-341d95999048	admin@transpop.dev	$2b$12$lDyAW0LLR2.V/H22Dz6wzOegS6j5GWrtxBGbp78eMEhQ0FaDbU7RS	Admin	Transpop	d4200a77-c304-4f56-a79b-c4d0e20e88dd	\N	f	\N	2026-04-03 05:04:12.665537+00	t	dcc78e38-a55e-48b8-b730-ea16003ccfbb	2026-04-02 20:34:31.852551+00	2026-04-03 05:04:12.382842+00
\.


--
-- Data for Name: vehicle; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehicle (tenant_id, type, brand_model, capacity, year, owner_type, monthly_cost_mad, monthly_km, condition, site_id, is_pmr_accessible, fuel_consumption, cost_per_km, motorization, length_meters, zfe_compliant, observations, id, created_at, updated_at, matricule, circulation_date, prestataire) FROM stdin;
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2011	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	19d2c4d3-9e3b-44dc-9e69-4d0c30148844	2026-04-03 00:56:07.181397+00	2026-04-03 00:56:07.181397+00	22363	2011-05-30	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	640c8797-b5b9-4f2a-9b28-48dd0f142aef	2026-04-03 00:56:07.18556+00	2026-04-03 00:56:07.18556+00	22401	2012-01-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	1d19ea08-5689-4166-a229-72f67601396d	2026-04-03 00:56:07.196267+00	2026-04-03 00:56:07.196267+00	22405	2012-01-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	356066b8-022d-4e2b-83a9-9b9da91bf64d	2026-04-03 00:56:07.198838+00	2026-04-03 00:56:07.198838+00	22410	2012-01-19	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	09d9d8d2-bccb-4c3a-bff4-4174da015a73	2026-04-03 00:56:07.201702+00	2026-04-03 00:56:07.201702+00	22420	2012-02-17	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	14162238-c70e-4199-8aa5-944d1439c182	2026-04-03 00:56:07.203858+00	2026-04-03 00:56:07.203858+00	22421	2012-02-17	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	6d9377d1-744b-4a41-a35f-65dbcec02c8d	2026-04-03 00:56:07.206874+00	2026-04-03 00:56:07.206874+00	22422	2012-02-17	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	337cffef-c02b-4764-813f-99afd032b1f6	2026-04-03 00:56:07.210045+00	2026-04-03 00:56:07.210045+00	22423	2012-02-17	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	be7bb67d-b3f2-4107-9c20-761b86b6539a	2026-04-03 00:56:07.212664+00	2026-04-03 00:56:07.212664+00	22424	2012-02-17	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	a197edf0-d532-4448-9abe-a486f43cadcf	2026-04-03 00:56:07.215748+00	2026-04-03 00:56:07.215748+00	22425	2012-03-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	2eefc98a-45a6-4973-9311-b7a727e649e1	2026-04-03 00:56:07.218574+00	2026-04-03 00:56:07.218574+00	22426	2012-03-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	3916d200-bcf4-48b9-a262-2d93e7135ba8	2026-04-03 00:56:07.222118+00	2026-04-03 00:56:07.222118+00	22427	2012-03-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	004f36d1-dd65-4b75-b043-7bd905e9d925	2026-04-03 00:56:07.224494+00	2026-04-03 00:56:07.224494+00	22429	2012-03-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	40	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	066bca7e-b5d1-4478-bc12-fb4ac0c460a0	2026-04-03 00:56:07.226955+00	2026-04-03 00:56:07.226955+00	22430	2012-03-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	1fcc7cd4-c1ab-4317-b0d9-5bb36691df47	2026-04-03 00:56:07.229173+00	2026-04-03 00:56:07.229173+00	22431	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	433a862a-6283-46df-994f-c13b49ff7246	2026-04-03 00:56:07.232044+00	2026-04-03 00:56:07.232044+00	22433	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	3d1786a9-8cea-4ed6-a51a-388c3b02c53a	2026-04-03 00:56:07.234419+00	2026-04-03 00:56:07.234419+00	22434	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	e445efb7-3313-40e4-8710-eaf072ab47f4	2026-04-03 00:56:07.236234+00	2026-04-03 00:56:07.236234+00	22435	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	7133b048-eb84-4970-9760-9cc940c034fe	2026-04-03 00:56:07.239357+00	2026-04-03 00:56:07.239357+00	22436	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	f8156b95-9a1d-4d02-b715-41b6cf8c6e9b	2026-04-03 00:56:07.241915+00	2026-04-03 00:56:07.241915+00	22437	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	201872b6-d998-442b-adb3-79d8dd824550	2026-04-03 00:56:07.244107+00	2026-04-03 00:56:07.244107+00	22438	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	62931432-4619-4a6c-8d6e-b3bf3174e368	2026-04-03 00:56:07.246224+00	2026-04-03 00:56:07.246224+00	22439	2012-05-15	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	447221b8-bc61-47b0-a6b2-caf53e578c76	2026-04-03 00:56:07.248352+00	2026-04-03 00:56:07.248352+00	22441	2012-05-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	fa9fd52c-23e4-4739-b1b1-d8f8f9b5c662	2026-04-03 00:56:07.25065+00	2026-04-03 00:56:07.25065+00	22443	2012-06-14	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	ee79a318-26ef-4204-8152-aaec47d0cbdf	2026-04-03 00:56:07.252716+00	2026-04-03 00:56:07.252716+00	22446	2012-06-14	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	aeb74437-5a8f-4ec0-889b-8e483bff1ca5	2026-04-03 00:56:07.254833+00	2026-04-03 00:56:07.254833+00	22447	2012-06-14	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	fd732061-85fc-4fd3-9d91-2182a31d78b9	2026-04-03 00:56:07.257022+00	2026-04-03 00:56:07.257022+00	22448	2012-06-14	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	3ef98e16-c2eb-487f-846b-766bb52054f9	2026-04-03 00:56:07.259418+00	2026-04-03 00:56:07.259418+00	22455	2012-06-13	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	ed224b8d-f0cc-4286-aa53-e5a952df51ee	2026-04-03 00:56:07.261551+00	2026-04-03 00:56:07.261551+00	22462	2012-08-01	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	889f0af3-6a29-4a48-b6eb-796b9ce2c378	2026-04-03 00:56:07.263509+00	2026-04-03 00:56:07.263509+00	22465	2012-09-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	2d1e8efe-a49f-4c63-91f6-fae24b29ed34	2026-04-03 00:56:07.265395+00	2026-04-03 00:56:07.265395+00	22466	2012-09-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	5d93e466-be19-4ee8-98c2-f127c4670b76	2026-04-03 00:56:07.268103+00	2026-04-03 00:56:07.268103+00	22467	2012-09-18	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	a088e9c6-7c46-423a-93fa-417e31269f4c	2026-04-03 00:56:07.270015+00	2026-04-03 00:56:07.270015+00	22471	2012-09-19	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	2062a33b-b0ee-4316-9fee-88f2475122fa	2026-04-03 00:56:07.272477+00	2026-04-03 00:56:07.272477+00	22472	2012-09-19	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	071efb40-6a95-4cfb-94c6-a60d6997ccaa	2026-04-03 00:56:07.27467+00	2026-04-03 00:56:07.27467+00	22473	2012-10-05	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	b0d1d9e0-5344-4012-a45a-f4f821ea2efa	2026-04-03 00:56:07.277078+00	2026-04-03 00:56:07.277078+00	22474	2012-10-08	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	1b5625bf-d752-43a8-b0ed-a0d829a8741d	2026-04-03 00:56:07.278984+00	2026-04-03 00:56:07.278984+00	22477	2012-11-05	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	5ac6c288-8926-42e2-97de-61b7502488dc	2026-04-03 00:56:07.281128+00	2026-04-03 00:56:07.281128+00	22478	2012-10-23	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	649a8417-4dff-48d8-89e0-79f408fefca6	2026-04-03 00:56:07.283952+00	2026-04-03 00:56:07.283952+00	22479	2012-11-05	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	f762a5e3-e6cf-4472-ac86-17bf941d3c26	2026-04-03 00:56:07.286784+00	2026-04-03 00:56:07.286784+00	22481	2012-11-05	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	42	2012	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	3b62e42a-c0bb-4abe-9cc1-d7720cad0e7c	2026-04-03 00:56:07.289191+00	2026-04-03 00:56:07.289191+00	22483	2012-11-02	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2006	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	e22c7888-f877-48af-b9d5-f6d224fe727a	2026-04-03 00:56:07.291712+00	2026-04-03 00:56:07.291712+00	22320	2006-09-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2006	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	b7d4c20c-ec82-4aab-b3fc-76585fa09ecc	2026-04-03 00:56:07.293993+00	2026-04-03 00:56:07.293993+00	22324	2006-09-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2006	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	f251df53-5534-418a-8968-cee4e712fd20	2026-04-03 00:56:07.29815+00	2026-04-03 00:56:07.29815+00	22333	2006-09-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2006	SOTREG	\N	\N	Bon	d39d79ec-a716-4839-a93d-1845d00c182c	f	\N	\N	\N	\N	f	\N	5c5ff42f-13b8-48f3-8e72-6c74cf78c192	2026-04-03 00:56:07.300204+00	2026-04-03 00:56:07.300204+00	22339	2006-09-22	\N
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2017	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	0a35ee8b-a371-4f3a-976b-ddb1d400df78	2026-04-03 00:56:07.302327+00	2026-04-03 00:56:07.302327+00	44105-A-14	2017-09-15	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2020	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	01ff1d56-773f-4f07-8a88-d39060ad2a7a	2026-04-03 00:56:07.304744+00	2026-04-03 00:56:07.304744+00	56046-A-14	2020-10-28	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2020	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	aa1e5e62-c6ad-4fed-8779-a30c0beb53bb	2026-04-03 00:56:07.30699+00	2026-04-03 00:56:07.30699+00	56148-A-14	2020-11-28	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2020	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	d22ef7ef-b3ff-434f-b3ed-15074ec62467	2026-04-03 00:56:07.309071+00	2026-04-03 00:56:07.309071+00	56151-A-14	2020-11-25	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	8c163988-c0f0-4b2f-9c61-0e02b93f8732	2026-04-03 00:56:07.311251+00	2026-04-03 00:56:07.311251+00	61845-A-14	2022-10-11	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	c53bf464-04c5-4cdb-8720-499859cd67ae	2026-04-03 00:56:07.314233+00	2026-04-03 00:56:07.314233+00	61846-A-14	2022-05-06	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	9a6fdf05-ea93-40b5-a6b7-839b1dc0fa19	2026-04-03 00:56:07.316378+00	2026-04-03 00:56:07.316378+00	61847-A-15	2022-05-06	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	55	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	45bee938-0824-4503-bc1b-176eeff207eb	2026-04-03 00:56:07.318682+00	2026-04-03 00:56:07.318682+00	61848-A-15	2022-05-06	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	d8c24575-c604-4f4a-90c6-8c1e7ca1d79d	2026-04-03 00:56:07.320745+00	2026-04-03 00:56:07.320745+00	61858-A-14	2022-05-06	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	12804c30-a359-4c22-9fc5-77fcb2c46bb0	2026-04-03 00:56:07.323076+00	2026-04-03 00:56:07.323076+00	63321-A-14	2022-11-10	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	48b104e5-c915-4e9a-a7fe-0667dcab72e5	2026-04-03 00:56:07.324792+00	2026-04-03 00:56:07.324792+00	63323-A-14	2022-11-10	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	4c5e6219-f318-41fe-85de-d18dc1d0e4a2	2026-04-03 00:56:07.327057+00	2026-04-03 00:56:07.327057+00	63325-A-14	2022-10-11	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	54	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	1833dec2-9f81-469b-b231-97feb8c70909	2026-04-03 00:56:07.32935+00	2026-04-03 00:56:07.32935+00	64362-A-14	2023-02-14	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	54	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	38a8087c-b470-4cd3-b049-438f53d2500c	2026-04-03 00:56:07.331701+00	2026-04-03 00:56:07.331701+00	77839-A-13	2022-10-12	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	0d117f97-b9df-4c73-baf1-8bab00c7ae6b	2026-04-03 00:56:07.333909+00	2026-04-03 00:56:07.333909+00	78234-A-13	2022-11-09	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	9f1c3a2d-f519-45c5-8b0f-c76c129afa87	2026-04-03 00:56:07.336182+00	2026-04-03 00:56:07.336182+00	79142-A-13	2023-02-14	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	b93ef770-7d89-43c7-9991-06e57177fe2b	2026-04-03 00:56:07.338635+00	2026-04-03 00:56:07.338635+00	79143-A-13	2023-02-14	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	ab2be353-1bba-41ee-900a-bf7444127ecd	2026-04-03 00:56:07.340895+00	2026-04-03 00:56:07.340895+00	79401-A-13	2023-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	3e0ae395-8ab2-4265-b108-e9189abcdaba	2026-04-03 00:56:07.343495+00	2026-04-03 00:56:07.343495+00	82195-A-13	2023-10-02	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	61a7198f-ec3c-4b45-9a0c-b976a4ce6afe	2026-04-03 00:56:07.345916+00	2026-04-03 00:56:07.345916+00	82197-A-13	2023-10-02	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	53a91138-18bd-493d-9af5-88b15bba96f2	2026-04-03 00:56:07.347552+00	2026-04-03 00:56:07.347552+00	82198-A-13	2023-10-02	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	605f40af-3d27-4f36-a062-0b3fd97d48b3	2026-04-03 00:56:07.350082+00	2026-04-03 00:56:07.350082+00	82199-A-13	2023-10-02	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	a0b8322a-7a4b-4125-ae6f-bfdb8e2320f4	2026-04-03 00:56:07.351795+00	2026-04-03 00:56:07.351795+00	82516-A-16	2023-11-21	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	e24ade41-d818-44fd-8fe7-7f23e31d966e	2026-04-03 00:56:07.353895+00	2026-04-03 00:56:07.353895+00	82517-A-13	2023-11-21	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	da6526a0-01e5-4ea5-80a7-80fce351bdc5	2026-04-03 00:56:07.356019+00	2026-04-03 00:56:07.356019+00	82519-A-13	2023-11-21	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	MAN	48	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	c08622c5-9fe9-48a5-89a5-d5b115f07247	2026-04-03 00:56:07.358458+00	2026-04-03 00:56:07.358458+00	82520-A-13	2023-11-21	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	cdc16e02-e30c-40d4-bac3-8c4cbbd3e49c	2026-04-03 00:56:07.360329+00	2026-04-03 00:56:07.360329+00	65405-A-11	2024-01-08	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	b2125fe8-9b2a-4c8e-95a6-ea5094c653f9	2026-04-03 00:56:07.363093+00	2026-04-03 00:56:07.363093+00	65408-A-11	2024-01-08	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	f3a4262c-7060-4436-8de6-f5f9d34ad0fb	2026-04-03 00:56:07.365596+00	2026-04-03 00:56:07.365596+00	65409-A-11	2024-01-08	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	1e21323a-95ac-4810-bd86-01a649669d42	2026-04-03 00:56:07.368396+00	2026-04-03 00:56:07.368396+00	65410-A-11	2024-01-08	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	8f594c3b-6a34-4249-a060-848011ef8467	2026-04-03 00:56:07.370697+00	2026-04-03 00:56:07.370697+00	65411-A-11	2024-01-08	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Ford	17	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	bd71acaa-759b-448f-9c85-9867770ead55	2026-04-03 00:56:07.372562+00	2026-04-03 00:56:07.372562+00	65659-A-11	2024-08-01	MANAVETTE
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	c36e7aa4-da76-460f-9c99-47429478c7ea	2026-04-03 00:56:07.374383+00	2026-04-03 00:56:07.374383+00	79402-A-13	2023-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	47aa5519-244e-473d-ad4b-923c3610b167	2026-04-03 00:56:07.377136+00	2026-04-03 00:56:07.377136+00	79636-A-13	2023-03-17	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	37297b4d-2cab-4767-9d39-fc17f115b586	2026-04-03 00:56:07.379691+00	2026-04-03 00:56:07.379691+00	79637-A-13	2023-03-17	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	2af9ce39-4ac2-4967-bd92-1ff8a6544048	2026-04-03 00:56:07.382056+00	2026-04-03 00:56:07.382056+00	79644-A-13	2023-03-20	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	0a4203e3-9bef-4b31-8c64-0a8f29786c2e	2026-04-03 00:56:07.384319+00	2026-04-03 00:56:07.384319+00	79795-A-13	2023-03-24	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	2d92ea00-c073-4f0e-8c7e-7a2621857368	2026-04-03 00:56:07.3867+00	2026-04-03 00:56:07.3867+00	79796-A-13	2023-03-24	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	e0d86e98-57b3-486e-aa9a-81d5a26214b3	2026-04-03 00:56:07.388811+00	2026-04-03 00:56:07.388811+00	79805-A-13	2023-03-24	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	97b30f1a-8023-4759-83aa-0ad74d8f03fa	2026-04-03 00:56:07.391529+00	2026-04-03 00:56:07.391529+00	79806-A-13	2023-03-24	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Hyundai	17	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	0eb75d84-fa84-449b-8176-328b50a22ce4	2026-04-03 00:56:07.393708+00	2026-04-03 00:56:07.393708+00	79826-A-13	2023-03-24	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Mercedes	20	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	130ef476-b552-4b59-ad8f-beede1f333cd	2026-04-03 00:56:07.396143+00	2026-04-03 00:56:07.396143+00	84112-A-13	2024-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Mercedes	20	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	816f64b8-5521-4321-bf27-4d1079acac06	2026-04-03 00:56:07.39841+00	2026-04-03 00:56:07.39841+00	84113-A-13	2024-03-14	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Mercedes	20	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	e66e86ab-228b-47a9-8788-d02e854083ff	2026-04-03 00:56:07.400539+00	2026-04-03 00:56:07.400539+00	84114-A-13	2024-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Mercedes	20	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	03464a4e-7909-419c-abbe-5c92df81974f	2026-04-03 00:56:07.402326+00	2026-04-03 00:56:07.402326+00	84116-A-13	2024-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Minibus	Mercedes	20	2024	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	9f5235d9-b31e-4227-b489-c7819189cc8d	2026-04-03 00:56:07.404785+00	2026-04-03 00:56:07.404785+00	84118-A-13	2024-03-13	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	ff0167fb-18d6-45c6-9eb0-0b9657e8267a	2026-04-03 00:56:07.406858+00	2026-04-03 00:56:07.406858+00	63689-A-14	2022-11-07	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	d26b72cf-9680-4a28-81d0-7726b236f575	2026-04-03 00:56:07.408938+00	2026-04-03 00:56:07.408938+00	63690-A-14	2022-11-07	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	12b611dd-91a0-44cb-b8da-b5724c667330	2026-04-03 00:56:07.411109+00	2026-04-03 00:56:07.411109+00	64025-A-14	2022-11-07	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	8a5f0dd1-4fba-4d5c-b2e5-6b85bdc206e7	2026-04-03 00:56:07.413539+00	2026-04-03 00:56:07.413539+00	64026-A-13	2022-11-07	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2023	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	655101e2-5a94-4e38-bca4-19cfe48772fd	2026-04-03 00:56:07.415848+00	2026-04-03 00:56:07.415848+00	65382-A-14	2023-05-26	S/TOURISME
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	af3e63c6-1827-430e-a210-9fa3abd30669	2026-04-03 00:56:07.417799+00	2026-04-03 00:56:07.417799+00	77753-A-13	2022-10-05	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	4ea2cce8-de10-47e5-8b2d-57f885848b22	2026-04-03 00:56:07.420087+00	2026-04-03 00:56:07.420087+00	77754-A-13	2022-10-05	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	221c14db-2d1f-4501-aec5-6461bf1fabb9	2026-04-03 00:56:07.422508+00	2026-04-03 00:56:07.422508+00	77755-A-13	2022-10-05	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	408fd65f-726b-4f44-a5dd-6059faefc5c6	2026-04-03 00:56:07.425303+00	2026-04-03 00:56:07.425303+00	77756-A-13	2022-10-05	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Mini-car	Isuzu	30	2022	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	fd72eae5-c529-4062-b26e-7c76b66f5f2f	2026-04-03 00:56:07.427639+00	2026-04-03 00:56:07.427639+00	77757-A-13	2022-10-05	STCR
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2021	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	04598418-8f08-4eb9-b067-87da6836b32f	2026-04-03 00:56:07.429531+00	2026-04-03 00:56:07.429531+00	70939-A-13	2021-04-12	CTM
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2021	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	8140fb2b-b5c7-40fe-9cbd-79c9837b7455	2026-04-03 00:56:07.431861+00	2026-04-03 00:56:07.431861+00	70944-A-13	2021-04-12	CTM
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2021	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	6e7168f7-477d-40d9-abcb-275b98da133d	2026-04-03 00:56:07.43399+00	2026-04-03 00:56:07.43399+00	70945-A-13	2021-04-12	CTM
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2021	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	4a67cde0-a401-46a0-9c61-7054e331f442	2026-04-03 00:56:07.43642+00	2026-04-03 00:56:07.43642+00	70951-A-13	2021-04-12	CTM
0cea9745-6aa2-4105-9bdc-341d95999048	Autocar	Volvo	48	2021	Prestataire	\N	\N	Bon	\N	f	\N	\N	\N	\N	f	\N	fff5b618-ed0b-4341-8fee-35a2b4fbf4fe	2026-04-03 00:56:07.438737+00	2026-04-03 00:56:07.438737+00	70953-A-13	2021-04-12	CTM
\.


--
-- Data for Name: vehicle_reference; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vehicle_reference (type, capacity_min, capacity_max, motorizations_available, recommended_use, reference_tco_5y, length_meters, zfe_compliant, id, created_at, updated_at) FROM stdin;
minibus	15	20	["diesel", "hybrid", "electric"]	Small clusters or PMR routes	{"diesel": 180000, "hybrid": 220000, "electric": 280000}	6.50	t	a272950d-3e92-4823-a087-2845054e23cd	2026-04-02 20:24:19.951649+00	2026-04-02 20:24:19.951649+00
midibus	25	35	["diesel", "hybrid", "electric", "gnv"]	Medium-density routes	{"gnv": 270000, "diesel": 250000, "hybrid": 300000, "electric": 380000}	8.00	t	d243a4fe-ae57-4f1c-9f56-76e6eaf8431f	2026-04-02 20:24:19.951649+00	2026-04-02 20:24:19.951649+00
bus_standard	40	55	["diesel", "hybrid", "electric", "hydrogen"]	High-density trunk routes	{"diesel": 350000, "hybrid": 420000, "electric": 520000, "hydrogen": 600000}	12.00	t	724bbc83-a69e-411e-b272-313d1a38ca53	2026-04-02 20:24:19.951649+00	2026-04-02 20:24:19.951649+00
grand_bus	60	80	["diesel", "hybrid", "electric"]	Very high demand, peak hours	{"diesel": 500000, "hybrid": 580000, "electric": 700000}	18.00	t	f96a5773-8642-4b5f-ac08-dedc466a6c29	2026-04-02 20:24:19.951649+00	2026-04-02 20:24:19.951649+00
vehicule_leger	5	9	["diesel", "hybrid", "electric"]	Last-mile, PMR, or VIP shuttle	{"diesel": 80000, "hybrid": 100000, "electric": 130000}	5.00	t	c60271ed-fdd6-43a6-af09-5aad1f2eff4c	2026-04-02 20:24:19.951649+00	2026-04-02 20:24:19.951649+00
\.


--
-- Data for Name: weather_forecast; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.weather_forecast (site_id, date, condition_summary, precipitation_mm, temp_min_c, temp_max_c, wind_kph, fetched_at, source, id, created_at, updated_at) FROM stdin;
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cluster cluster_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cluster
    ADD CONSTRAINT cluster_pkey PRIMARY KEY (id);


--
-- Name: configuration_plan configuration_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_plan
    ADD CONSTRAINT configuration_plan_pkey PRIMARY KEY (id);


--
-- Name: configuration_transport configuration_transport_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_transport
    ADD CONSTRAINT configuration_transport_pkey PRIMARY KEY (id);


--
-- Name: constraint_param constraint_param_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constraint_param
    ADD CONSTRAINT constraint_param_pkey PRIMARY KEY (id);


--
-- Name: employee_leave employee_leave_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_leave
    ADD CONSTRAINT employee_leave_pkey PRIMARY KEY (id);


--
-- Name: employee_modal employee_modal_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_modal
    ADD CONSTRAINT employee_modal_pkey PRIMARY KEY (id);


--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: financial_scenario financial_scenario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_scenario
    ADD CONSTRAINT financial_scenario_pkey PRIMARY KEY (id);


--
-- Name: generated_report generated_report_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_report
    ADD CONSTRAINT generated_report_pkey PRIMARY KEY (id);


--
-- Name: horaire_travail horaire_travail_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horaire_travail
    ADD CONSTRAINT horaire_travail_pkey PRIMARY KEY (id);


--
-- Name: km_consommation km_consommation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.km_consommation
    ADD CONSTRAINT km_consommation_pkey PRIMARY KEY (id);


--
-- Name: kpi_snapshot kpi_snapshot_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kpi_snapshot
    ADD CONSTRAINT kpi_snapshot_pkey PRIMARY KEY (id);


--
-- Name: optimization optimization_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization
    ADD CONSTRAINT optimization_pkey PRIMARY KEY (id);


--
-- Name: optimization_settings optimization_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization_settings
    ADD CONSTRAINT optimization_settings_pkey PRIMARY KEY (id);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);


--
-- Name: point_arret point_arret_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.point_arret
    ADD CONSTRAINT point_arret_pkey PRIMARY KEY (id);


--
-- Name: roi_calculation roi_calculation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roi_calculation
    ADD CONSTRAINT roi_calculation_pkey PRIMARY KEY (id);


--
-- Name: role_permission role_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_pkey PRIMARY KEY (id);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: route route_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_pkey PRIMARY KEY (id);


--
-- Name: scenario scenario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenario
    ADD CONSTRAINT scenario_pkey PRIMARY KEY (id);


--
-- Name: site site_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_code_key UNIQUE (code);


--
-- Name: site site_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_pkey PRIMARY KEY (id);


--
-- Name: tco_entry tco_entry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tco_entry
    ADD CONSTRAINT tco_entry_pkey PRIMARY KEY (id);


--
-- Name: tenant tenant_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant
    ADD CONSTRAINT tenant_code_key UNIQUE (code);


--
-- Name: tenant tenant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenant
    ADD CONSTRAINT tenant_pkey PRIMARY KEY (id);


--
-- Name: constraint_param uq_constraint_param_tenant_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constraint_param
    ADD CONSTRAINT uq_constraint_param_tenant_key UNIQUE (tenant_id, key);


--
-- Name: employee_modal uq_employee_modal_employee_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_modal
    ADD CONSTRAINT uq_employee_modal_employee_id UNIQUE (employee_id);


--
-- Name: employee uq_employee_tenant_matricule; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT uq_employee_tenant_matricule UNIQUE (tenant_id, matricule);


--
-- Name: optimization_settings uq_optimization_settings_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization_settings
    ADD CONSTRAINT uq_optimization_settings_tenant UNIQUE (tenant_id);


--
-- Name: permission uq_permission_resource_action; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT uq_permission_resource_action UNIQUE (resource, action);


--
-- Name: role_permission uq_role_permission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id);


--
-- Name: user uq_user_tenant_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT uq_user_tenant_email UNIQUE (tenant_id, email);


--
-- Name: weather_forecast uq_weather_site_date_source; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_forecast
    ADD CONSTRAINT uq_weather_site_date_source UNIQUE (site_id, date, source);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: vehicle_reference vehicle_reference_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_reference
    ADD CONSTRAINT vehicle_reference_pkey PRIMARY KEY (id);


--
-- Name: weather_forecast weather_forecast_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_forecast
    ADD CONSTRAINT weather_forecast_pkey PRIMARY KEY (id);


--
-- Name: idx_cluster_centroid_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cluster_centroid_geom ON public.cluster USING gist (centroid_geom);


--
-- Name: idx_cluster_optimization; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cluster_optimization ON public.cluster USING btree (optimization_id);


--
-- Name: idx_constraint_param_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_constraint_param_tenant ON public.constraint_param USING btree (tenant_id);


--
-- Name: idx_employee_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_employee_geom ON public.employee USING gist (geom);


--
-- Name: idx_financial_scenario_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_financial_scenario_created_by ON public.financial_scenario USING btree (created_by);


--
-- Name: idx_financial_scenario_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_financial_scenario_tenant ON public.financial_scenario USING btree (tenant_id);


--
-- Name: idx_generated_report_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_generated_report_tenant ON public.generated_report USING btree (tenant_id);


--
-- Name: idx_kpi_snapshot_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_kpi_snapshot_site ON public.kpi_snapshot USING btree (site_id);


--
-- Name: idx_kpi_snapshot_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_kpi_snapshot_tenant ON public.kpi_snapshot USING btree (tenant_id);


--
-- Name: idx_kpi_snapshot_type_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_kpi_snapshot_type_date ON public.kpi_snapshot USING btree (kpi_type, snapshot_date);


--
-- Name: idx_leave_dates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leave_dates ON public.employee_leave USING btree (start_date, end_date);


--
-- Name: idx_leave_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_leave_employee ON public.employee_leave USING btree (employee_id);


--
-- Name: idx_modal_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_modal_employee ON public.employee_modal USING btree (employee_id);


--
-- Name: idx_optimization_settings_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_optimization_settings_tenant ON public.optimization_settings USING btree (tenant_id);


--
-- Name: idx_optimization_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_optimization_tenant ON public.optimization USING btree (tenant_id);


--
-- Name: idx_roi_calculation_financial_scenario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_roi_calculation_financial_scenario ON public.roi_calculation USING btree (financial_scenario_id);


--
-- Name: idx_route_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_route_geom ON public.route USING gist (geom);


--
-- Name: idx_route_optimization; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_route_optimization ON public.route USING btree (optimization_id);


--
-- Name: idx_scenario_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_scenario_site ON public.scenario USING btree (site_id);


--
-- Name: idx_scenario_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_scenario_tenant ON public.scenario USING btree (tenant_id);


--
-- Name: idx_site_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_site_geom ON public.site USING gist (geom);


--
-- Name: idx_tco_entry_financial_scenario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tco_entry_financial_scenario ON public.tco_entry USING btree (financial_scenario_id);


--
-- Name: idx_vehicle_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_site ON public.vehicle USING btree (site_id);


--
-- Name: idx_vehicle_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_tenant ON public.vehicle USING btree (tenant_id);


--
-- Name: idx_weather_forecast_site_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_weather_forecast_site_id ON public.weather_forecast USING btree (site_id);


--
-- Name: ix_configuration_plan_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuration_plan_tenant ON public.configuration_plan USING btree (tenant_id);


--
-- Name: ix_configuration_transport_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuration_transport_plan ON public.configuration_transport USING btree (plan_id);


--
-- Name: ix_configuration_transport_poste; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuration_transport_poste ON public.configuration_transport USING btree (poste);


--
-- Name: ix_configuration_transport_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_configuration_transport_tenant ON public.configuration_transport USING btree (tenant_id);


--
-- Name: ix_employee_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_active ON public.employee USING btree (active);


--
-- Name: ix_employee_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_geom ON public.employee USING gist (geom);


--
-- Name: ix_employee_point_arret_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_point_arret_id ON public.employee USING btree (point_arret_id);


--
-- Name: ix_employee_site_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_site_id ON public.employee USING btree (site_id);


--
-- Name: ix_employee_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employee_tenant_id ON public.employee USING btree (tenant_id);


--
-- Name: ix_horaire_travail_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_horaire_travail_site ON public.horaire_travail USING btree (site_id);


--
-- Name: ix_horaire_travail_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_horaire_travail_tenant ON public.horaire_travail USING btree (tenant_id);


--
-- Name: ix_km_consommation_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_km_consommation_tenant ON public.km_consommation USING btree (tenant_id);


--
-- Name: ix_point_arret_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_point_arret_site ON public.point_arret USING btree (site_id);


--
-- Name: ix_point_arret_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_point_arret_tenant ON public.point_arret USING btree (tenant_id);


--
-- Name: ix_site_geom; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_geom ON public.site USING gist (geom);


--
-- Name: ix_site_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_site_tenant_id ON public.site USING btree (tenant_id);


--
-- Name: cluster cluster_optimization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cluster
    ADD CONSTRAINT cluster_optimization_id_fkey FOREIGN KEY (optimization_id) REFERENCES public.optimization(id) ON DELETE CASCADE;


--
-- Name: cluster cluster_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cluster
    ADD CONSTRAINT cluster_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: configuration_plan configuration_plan_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_plan
    ADD CONSTRAINT configuration_plan_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: configuration_transport configuration_transport_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_transport
    ADD CONSTRAINT configuration_transport_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.configuration_plan(id) ON DELETE CASCADE;


--
-- Name: configuration_transport configuration_transport_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_transport
    ADD CONSTRAINT configuration_transport_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: configuration_transport configuration_transport_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configuration_transport
    ADD CONSTRAINT configuration_transport_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: constraint_param constraint_param_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constraint_param
    ADD CONSTRAINT constraint_param_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: employee_leave employee_leave_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_leave
    ADD CONSTRAINT employee_leave_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: employee_modal employee_modal_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_modal
    ADD CONSTRAINT employee_modal_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employee(id) ON DELETE CASCADE;


--
-- Name: employee employee_point_arret_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_point_arret_id_fkey FOREIGN KEY (point_arret_id) REFERENCES public.point_arret(id) ON DELETE SET NULL;


--
-- Name: employee employee_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: employee employee_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: financial_scenario financial_scenario_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_scenario
    ADD CONSTRAINT financial_scenario_created_by_fkey FOREIGN KEY (created_by) REFERENCES public."user"(id);


--
-- Name: financial_scenario financial_scenario_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.financial_scenario
    ADD CONSTRAINT financial_scenario_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: generated_report generated_report_generated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_report
    ADD CONSTRAINT generated_report_generated_by_fkey FOREIGN KEY (generated_by) REFERENCES public."user"(id);


--
-- Name: generated_report generated_report_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.generated_report
    ADD CONSTRAINT generated_report_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: horaire_travail horaire_travail_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horaire_travail
    ADD CONSTRAINT horaire_travail_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: horaire_travail horaire_travail_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.horaire_travail
    ADD CONSTRAINT horaire_travail_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: km_consommation km_consommation_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.km_consommation
    ADD CONSTRAINT km_consommation_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: km_consommation km_consommation_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.km_consommation
    ADD CONSTRAINT km_consommation_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: kpi_snapshot kpi_snapshot_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kpi_snapshot
    ADD CONSTRAINT kpi_snapshot_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: kpi_snapshot kpi_snapshot_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.kpi_snapshot
    ADD CONSTRAINT kpi_snapshot_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: optimization_settings optimization_settings_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization_settings
    ADD CONSTRAINT optimization_settings_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: optimization optimization_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization
    ADD CONSTRAINT optimization_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: optimization optimization_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.optimization
    ADD CONSTRAINT optimization_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: point_arret point_arret_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.point_arret
    ADD CONSTRAINT point_arret_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: point_arret point_arret_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.point_arret
    ADD CONSTRAINT point_arret_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: roi_calculation roi_calculation_financial_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.roi_calculation
    ADD CONSTRAINT roi_calculation_financial_scenario_id_fkey FOREIGN KEY (financial_scenario_id) REFERENCES public.financial_scenario(id) ON DELETE CASCADE;


--
-- Name: role_permission role_permission_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: role_permission role_permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: role role_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: route route_optimization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_optimization_id_fkey FOREIGN KEY (optimization_id) REFERENCES public.optimization(id) ON DELETE CASCADE;


--
-- Name: route route_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: route route_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicle(id);


--
-- Name: scenario scenario_baseline_optimization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenario
    ADD CONSTRAINT scenario_baseline_optimization_id_fkey FOREIGN KEY (baseline_optimization_id) REFERENCES public.optimization(id);


--
-- Name: scenario scenario_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenario
    ADD CONSTRAINT scenario_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: scenario scenario_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scenario
    ADD CONSTRAINT scenario_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: site site_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: tco_entry tco_entry_financial_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tco_entry
    ADD CONSTRAINT tco_entry_financial_scenario_id_fkey FOREIGN KEY (financial_scenario_id) REFERENCES public.financial_scenario(id) ON DELETE CASCADE;


--
-- Name: user user_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(id);


--
-- Name: user user_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: vehicle vehicle_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- Name: vehicle vehicle_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenant(id);


--
-- Name: weather_forecast weather_forecast_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weather_forecast
    ADD CONSTRAINT weather_forecast_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.site(id);


--
-- PostgreSQL database dump complete
--

