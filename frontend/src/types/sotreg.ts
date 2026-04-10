/* ── SOTREG types — Transport Lines, Fleet Context, OD Matrix, ZFE ────────── */

/* ── Ligne (transport line) ──────────────────────────────────────────────── */

export interface Ligne {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  site_id: string | null;

  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;

  distance_km: number;
  rotations_per_day: number;
  operating_days_per_year: number;
  km_annual: number;

  vehicle_type: string | null;
  motorization: string | null;
  passenger_count_avg: number | null;
  shift_type: string | null;
  service_type: string;
  pente_moyenne_pct: number | null;
  is_active: boolean;

  created_at: string;
  updated_at: string;
}

export interface LigneCreate {
  code: string;
  name: string;
  site_id?: string | null;
  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;
  distance_km: number;
  rotations_per_day: number;
  operating_days_per_year: number;
  vehicle_type?: string | null;
  motorization?: string | null;
  passenger_count_avg?: number | null;
  shift_type?: string | null;
  service_type: string;
  pente_moyenne_pct?: number | null;
}

export interface LigneUpdate {
  name?: string;
  site_id?: string | null;
  origin_lat?: number;
  origin_lng?: number;
  dest_lat?: number;
  dest_lng?: number;
  distance_km?: number;
  rotations_per_day?: number;
  operating_days_per_year?: number;
  vehicle_type?: string | null;
  motorization?: string | null;
  passenger_count_avg?: number | null;
  shift_type?: string | null;
  service_type?: string;
  pente_moyenne_pct?: number | null;
  is_active?: boolean;
}

export interface LigneListMeta {
  page: number;
  pages: number;
  total: number;
  page_size: number;
}

export interface LigneListResponse {
  data: Ligne[];
  meta: LigneListMeta;
}

export interface LigneListParams {
  page?: number;
  page_size?: number;
  service_type?: string;
  site_id?: string;
  is_active?: boolean;
}

/* ── Fleet Context ───────────────────────────────────────────────────────── */

export interface FleetContext {
  id: string;
  tenant_id: string;
  total_vehicles: number;
  total_km_annual: number;
  total_tco2_annual: number;
  average_age_years: number | null;
  pct_diesel: number;
  pct_electric: number;
  pct_hybrid: number;
  currency: string;
  snapshot_date: string;
  created_at: string;
  updated_at: string;
}

/* ── OD Matrix ───────────────────────────────────────────────────────────── */

export interface ODMatrixEntry {
  id: string;
  tenant_id: string;
  ligne_id: string | null;
  origin_zone: string;
  destination_zone: string;
  flow_estimate: number;
  distance_km: number;
  gravity_score: number;
  beta_used: number;
  computed_at: string;
  created_at: string;
  updated_at: string;
}

export interface ODMatrixListResponse {
  data: ODMatrixEntry[];
  total: number;
  beta_used: number;
}

export interface ODMatrixComputeRequest {
  beta?: number;
  k?: number;
}

export interface ODMatrixComputeResponse {
  entries_computed: number;
  beta_used: number;
  k_used: number;
  entries: ODMatrixEntry[];
}

/* ── ZFE ─────────────────────────────────────────────────────────────────── */

export interface ZFEEndpointResult {
  lat: number;
  lng: number;
  is_in_zfe: boolean;
  zone_name: string | null;
  restriction_level: string | null;
  allowed_crit_air: number[] | null;
}

export interface ZFELigneResult {
  ligne_id: string;
  ligne_code: string;
  ligne_name: string;
  origin: ZFEEndpointResult;
  dest: ZFEEndpointResult;
  any_endpoint_in_zfe: boolean;
  checked_at: string;
}

export interface ZFEComplianceResponse {
  total_lignes: number;
  lignes_in_zfe: number;
  results: ZFELigneResult[];
}

export interface ZFEPointCheckResponse {
  is_in_zfe: boolean;
  zone_name: string | null;
  restriction_level: string | null;
  allowed_crit_air: number[] | null;
  checked_at: string;
}

/* ── Range Correction (M2) ───────────────────────────────────────────────── */

export interface RangeCorrectionRequest {
  nominal_range_km: number;
  pente_profile?: string;
  saison_profile?: string;
  vitesse_profile?: string;
}

export interface RangeCorrectionResponse {
  nominal_range_km: number;
  k_pente: number;
  k_saison: number;
  k_vitesse: number;
  correction_factor: number;
  corrected_range_km: number;
  range_reduction_pct: number;
  currency: string;
}

/* ── 15-Year TCO (M2) ───────────────────────────────────────────────────── */

export interface TCO15YearRequest {
  purchase_price: number;
  annual_maintenance_cost: number;
  energy_cost_per_km: number;
  annual_km: number;
  residual_value_pct?: number;
  duration_years?: number;
  loan_rate_pct?: number;
  loan_duration_years?: number;
  energy_escalation_pct?: number;
  maintenance_escalation_pct?: number;
  currency?: string;
}

export interface TCO15YearYearlyBreakdown {
  year: number;
  depreciation: number;
  maintenance: number;
  energy: number;
  financing: number;
  year_total: number;
  cumulative_tco: number;
}

export interface TCO15YearResponse {
  total_tco: number;
  yearly_breakdown: TCO15YearYearlyBreakdown[];
  financing_total: number;
  energy_total: number;
  maintenance_total: number;
  depreciation_total: number;
  residual_value: number;
  duration_years: number;
  currency: string;
}

/* ── Breakeven (M2) ─────────────────────────────────────────────────────── */

export interface BreakevenRequest {
  capex_diesel: number;
  capex_electric: number;
  opex_per_km_diesel: number;
  opex_per_km_electric: number;
  currency?: string;
}

export interface BreakevenResponse {
  km_seuil: number | null;
  delta_capex: number;
  delta_opex_per_km: number;
  payback_years_at_reference_km: number | null;
  is_electric_viable: boolean;
  annual_km_reference: number;
  currency: string;
}

/* ── Charging Optimization (M2) ──────────────────────────────────────────── */

export interface ChargingOptimizationRequest {
  battery_capacity_kwh: number;
  current_soc_pct: number;
  target_soc_pct?: number;
  charger_power_kw?: number;
  departure_hour?: number;
  arrival_hour?: number;
  currency?: string;
}

export interface ChargingWindowSchedule {
  window_name: string;
  start_hour: number;
  end_hour: number;
  duration_hours: number;
  energy_kwh: number;
  cost_mad: number;
}

export interface ChargingOptimizationResponse {
  target_soc_pct: number;
  energy_needed_kwh: number;
  charging_duration_hours: number;
  schedule: ChargingWindowSchedule[];
  total_energy_cost_mad: number;
  peak_demand_kw: number;
  monthly_demand_charge_mad: number;
  currency: string;
}

/* ── IRVE Sizing (M2) ───────────────────────────────────────────────────── */

export interface IRVESizingRequest {
  fleet_size: number;
  daily_km_per_vehicle: number;
  battery_capacity_kwh: number;
  energy_consumption_kwh_per_km?: number;
  charging_window_hours?: number;
  charger_utilization_target?: number;
  preferred_charger_type?: string;
  currency?: string;
}

export interface IRVESizingResponse {
  charger_type: string;
  charger_count: number;
  power_per_charger_kw: number;
  total_installed_power_kw: number;
  daily_energy_demand_kwh: number;
  daily_energy_per_vehicle_kwh: number;
  vehicles_per_charger: number;
  hardware_cost_mad: number;
  installation_cost_mad: number;
  transformer_cost_mad: number;
  grid_connection_cost_mad: number;
  annual_electricity_cost_mad: number;
  total_capex_mad: number;
  currency: string;
}

export const PENTE_PROFILES = ['flat', 'moderate', 'hilly', 'mountainous'] as const;
export const PENTE_LABELS: Record<string, string> = {
  flat: 'Plat (0-2%)',
  moderate: 'Modéré (2-5%)',
  hilly: 'Vallonné (5-8%)',
  mountainous: 'Montagneux (>8%)',
};

export const SAISON_PROFILES = ['temperate', 'hot', 'cold', 'extreme'] as const;
export const SAISON_LABELS: Record<string, string> = {
  temperate: 'Tempéré (15-25°C)',
  hot: 'Chaud (>35°C)',
  cold: 'Froid (<5°C)',
  extreme: 'Extrême',
};

export const VITESSE_PROFILES = ['optimal', 'moderate', 'city', 'highway'] as const;
export const VITESSE_LABELS: Record<string, string> = {
  optimal: 'Optimal (30-50 km/h)',
  moderate: 'Modéré (50-70 km/h)',
  city: 'Urbain (<30 km/h)',
  highway: 'Autoroute (>70 km/h)',
};

export const CHARGER_TYPES = ['ac_7kw', 'ac_22kw', 'dc_50kw', 'dc_150kw'] as const;
export const CHARGER_LABELS: Record<string, string> = {
  ac_7kw: 'AC 7 kW',
  ac_22kw: 'AC 22 kW',
  dc_50kw: 'DC 50 kW',
  dc_150kw: 'DC 150 kW',
};

/* ── Service type helpers ────────────────────────────────────────────────── */

export const SERVICE_TYPE_OPTIONS = ['navette', 'liaison', 'vip', 'mixte'] as const;

export const SERVICE_TYPE_LABELS: Record<string, string> = {
  navette: 'Navette',
  liaison: 'Liaison',
  vip: 'VIP',
  mixte: 'Mixte',
};

/* ── Stop Generation (M3) ────────────────────────────────────────────────── */

export interface StopGenerateRequest {
  site_id?: string | null;
  eps_m?: number;
  min_pts?: number;
}

export interface GeneratedStopResult {
  cluster_id: number;
  centroid_lat: number;
  centroid_lng: number;
  employee_count: number;
  employee_ids: string[];
  catchment_radius_m: number;
  source: string;
}

export interface StopGenerateResponse {
  stops_generated: number;
  eps_m: number;
  min_pts: number;
  noise_count: number;
  stops: GeneratedStopResult[];
}

export interface StopCapacityRequest {
  n_berths?: number;
  green_ratio?: number;
  dwell_time_s?: number;
  clearance_time_s?: number;
  cv_dwell?: number;
  z_factor?: number;
  demand_buses_per_hour?: number;
}

export interface StopCapacityResponse {
  capacity_buses_per_hour: number;
  effective_dwell_s: number;
  n_berths: number;
  green_ratio: number;
  z_factor: number;
  cv_dwell: number;
  utilization: number;
  los_grade: string;
  los_description: string;
  avg_wait_seconds: number;
}

/* ── Depot (M3) ──────────────────────────────────────────────────────────── */

export interface DepotCostEstimateRequest {
  charger_count: number;
  charger_type?: string;
  contingency_pct?: number;
  currency?: string;
}

export interface DepotCostEstimateResponse {
  charger_hardware_mad: number;
  installation_mad: number;
  electrical_upgrade_mad: number;
  transformer_mad: number;
  grid_connection_mad: number;
  civil_works_mad: number;
  contingency_mad: number;
  subtotal_mad: number;
  total_cost_mad: number;
  cost_per_charger_mad: number;
  charger_type: string;
  charger_count: number;
  total_power_kw: number;
  contingency_pct: number;
  currency: string;
}

export interface ChargerPosition {
  bay_id: number;
  x: number;
  y: number;
  bay_width: number;
  bay_depth: number;
}

export interface DepotLayoutRequest {
  charger_count: number;
  fleet_size: number;
  charger_type?: string;
  include_maintenance?: boolean;
  currency?: string;
}

export interface DepotLayoutResponse {
  total_area_m2: number;
  charging_area_m2: number;
  parking_area_m2: number;
  maintenance_area_m2: number;
  circulation_area_m2: number;
  charger_positions: ChargerPosition[];
  parking_bays: number;
  charger_count: number;
  charger_type: string;
  dimensions: { width_m: number; depth_m: number };
  currency: string;
}

export const LOS_COLORS: Record<string, string> = {
  A: '#22c55e', B: '#84cc16', C: '#eab308', D: '#f97316', E: '#ef4444', F: '#991b1b',
};

export const LOS_LABELS: Record<string, string> = {
  A: 'Libre', B: 'Stable', C: 'Acceptable', D: 'Instable', E: 'Capacité', F: 'Saturé',
};

export const MOTORIZATION_OPTIONS = ['diesel', 'essence', 'electrique', 'hybride', 'gnv'] as const;

export const MOTORIZATION_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  essence: 'Essence',
  electrique: 'Électrique',
  hybride: 'Hybride',
  gnv: 'GNV',
};

/* ── NPV & Finance (M5) ─────────────────────────────────────────────────── */

export interface NPVRequest {
  cash_flows: number[];
  discount_rate?: number;
  currency?: string;
}

export interface NPVResponse {
  npv: number;
  discount_rate: number;
  cash_flow_count: number;
  present_values: number[];
  is_viable: boolean;
  currency: string;
}

export interface PaybackResponse {
  payback_years: number | null;
  cumulative_flows: number[];
  total_investment: number;
  total_return: number;
  currency: string;
}

export interface InvestmentAnalysisResponse {
  npv: Record<string, unknown>;
  irr: Record<string, unknown>;
  payback: Record<string, unknown>;
}

export interface CO2ValorizationRequest {
  fleet_annual_km: number;
  current_motorization?: string;
  target_motorization?: string;
  carbon_price_mad_tco2?: number;
  vehicle_count?: number;
  energy_consumption_kwh_per_km?: number;
  currency?: string;
}

export interface CO2ValorizationResponse {
  current_emissions_tco2: number;
  target_emissions_tco2: number;
  avoided_emissions_tco2: number;
  carbon_price_mad_tco2: number;
  valorization_mad: number;
  valorization_15year_mad: number;
  fleet_annual_km: number;
  vehicle_count: number;
  current_motorization: string;
  target_motorization: string;
  currency: string;
}

export interface PortfolioOptimizeRequest {
  expected_returns: number[];
  covariance_matrix: number[][];
  risk_aversion?: number;
  technology_names?: string[];
}

export interface PortfolioResult {
  expected_return: number;
  risk: number;
  weights: number[];
}

export interface PortfolioOptimizeResponse {
  weights: number[];
  expected_return: number;
  portfolio_variance: number;
  portfolio_std: number;
  sharpe_ratio: number;
  technology_names: string[];
  risk_aversion: number;
}

export interface EfficientFrontierResponse {
  frontier: PortfolioResult[];
  min_risk_portfolio: PortfolioResult;
  max_return_portfolio: PortfolioResult;
  technology_names: string[];
}

export interface SupernetworkLink {
  from_node: number;
  to_node: number;
  free_flow_cost: number;
  capacity: number;
}

export interface SupernetworkDemand {
  origin: number;
  destination: number;
  demand: number;
}

export interface LinkFlow {
  from_node: number;
  to_node: number;
  flow: number;
  cost: number;
}

export interface SupernetworkResponse {
  link_flows: LinkFlow[];
  total_system_cost: number;
  iterations: number;
  converged: boolean;
  gap: number;
}

/* ── Transition Roadmap (M6) ─────────────────────────────────────────────── */

export interface TransitionPlanRequest {
  fleet_size: number;
  total_budget_mad: number;
  start_year?: number;
  scenario_type?: string;
  vehicle_unit_cost_mad?: number;
  irve_cost_per_vehicle_mad?: number;
  currency?: string;
}

export interface PhaseResult {
  name: string;
  technology_wave: string;
  start_year: number;
  end_year: number;
  vehicles_to_convert: number;
  target_pct_electric: number;
  budget_allocated_mad: number;
  vehicle_cost_mad: number;
  infrastructure_cost_mad: number;
  status: string;
}

export interface MilestoneResult {
  year: number;
  description: string;
  target_pct: number;
  vehicles_converted_cumulative: number;
}

export interface TransitionPlanResponse {
  plan_name: string;
  scenario_type: string;
  fleet_size: number;
  total_budget_mad: number;
  phases: PhaseResult[];
  total_phases: number;
  total_vehicles_converted: number;
  total_cost_mad: number;
  budget_surplus_or_deficit_mad: number;
  milestones: MilestoneResult[];
  currency: string;
}

export const SCENARIO_TYPES = ['aggressive', 'moderate', 'conservative'] as const;
export const SCENARIO_LABELS: Record<string, string> = {
  aggressive: 'Agressif (5 ans)',
  moderate: 'Modéré (8 ans)',
  conservative: 'Conservateur (10 ans)',
};

export const WAVE_COLORS: Record<string, string> = {
  pilot: '#0058be',
  scale: '#22c55e',
  full: '#f59e0b',
};
