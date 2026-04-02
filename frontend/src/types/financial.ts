export interface TCOFleetItem {
  vehicle_type: string;
  motorization: string;
  quantity: number;
  purchase_price?: number;
  annual_maintenance_cost?: number;
  energy_cost_per_km?: number;
  annual_km?: number;
  residual_value?: number;
}

export interface TCOCalculateRequest {
  fleet: TCOFleetItem[];
  duration_years: number;
  include_evolution: boolean;
  include_comparison: boolean;
}

export interface TCOVehicleResult {
  vehicle_type: string;
  motorization: string;
  purchase_price: number;
  annual_maintenance_cost: number;
  energy_cost_per_km: number;
  annual_km: number;
  residual_value: number;
  duration_years: number;
  quantity: number;
  maintenance_total: number;
  energy_total: number;
  tco_per_vehicle: number;
  tco_total: number;
}

export interface TCOFleetResult {
  duration_years: number;
  vehicles: TCOVehicleResult[];
  fleet_tco_total: number;
  vehicle_count: number;
}

export interface TCOYearlyPoint {
  year: number;
  fleet_tco_total: number;
}

export interface TCOMotorizationItem {
  motorization: string;
  tco_per_vehicle: number;
  tco_total: number;
  purchase_price: number;
  annual_maintenance_cost: number;
  energy_cost_per_km: number;
  annual_km: number;
  residual_value: number;
  duration_years: number;
  quantity: number;
  maintenance_total: number;
  energy_total: number;
}

export interface TCOMotorizationComparison {
  vehicle_type: string;
  motorizations: TCOMotorizationItem[];
}

export interface TCOCalculateResponse {
  fleet_tco: TCOFleetResult;
  evolution: TCOYearlyPoint[] | null;
  motorization_comparisons: TCOMotorizationComparison[] | null;
}

export interface VehicleReference {
  id: string;
  type: string;
  capacity_min: number | null;
  capacity_max: number | null;
  motorizations_available: string[];
  recommended_use: string | null;
  reference_tco_5y: Record<string, number>;
  length_meters: number | null;
  zfe_compliant: boolean;
}

export const VEHICLE_TYPES = [
  'minibus',
  'midibus',
  'bus_standard',
  'grand_bus',
  'vehicule_leger',
] as const;

export const MOTORIZATIONS = [
  'diesel',
  'hybrid',
  'electric',
  'hydrogen',
  'gnv',
] as const;

export type VehicleType = (typeof VEHICLE_TYPES)[number];
export type Motorization = (typeof MOTORIZATIONS)[number];

// ROI types
export interface ROICalculateRequest {
  scenario_id?: string;
  headcount: number;
  daily_cost: number;
  baseline_absence_rate: number;
  target_absence_rate: number;
  replacement_cost: number;
  turnover_rate_before: number;
  turnover_rate_after: number;
  annual_travel_hours: number;
  engagement_rate: number;
  training_hour_cost: number;
  total_investment: number;
  current_fleet_annual_cost?: number;
  optimized_fleet_annual_cost?: number;
}

export interface ROICalculateResponse {
  roi_absenteeism: number;
  roi_retention: number;
  roi_fleet_optimization: number;
  roi_journey: number;
  roi_total: number;
  roi_percentage: number;
  payback_months: number | null;
  total_investment: number;
  headcount: number;
  working_days_per_year: number;
  stored_id: string | null;
}

// Investment Comparator types
export interface InvestmentCompareRequest {
  vehicle_count: number;
  headcount: number;
  annual_trips: number;
  duration_years: number;
  capex_purchase_price?: number;
  capex_annual_maintenance?: number;
  capex_annual_fuel?: number;
  capex_annual_insurance?: number;
  capex_annual_driver_cost?: number;
  capex_residual_value?: number;
  mad_monthly_rental?: number;
  mad_annual_fuel?: number;
  mad_management_overhead_rate?: number;
  opex_cost_per_km?: number;
  opex_annual_km?: number;
}

export interface InvestmentModelResult {
  model: string;
  label: string;
  total_cost: number;
  annual_cost: number;
  cost_per_employee: number;
  cost_per_trip: number;
  duration_years: number;
  vehicle_count: number;
  breakdown: Record<string, number>;
}

export interface InvestmentRecommendation {
  recommended_model: string;
  reason: string;
}

export interface InvestmentCompareResponse {
  models: InvestmentModelResult[];
  recommendation: InvestmentRecommendation;
}

// Cost Analysis types
export interface CostAnalysisRequest {
  annual_route_cost: number;
  vehicle_capacity: number;
  fill_rate: number;
  transported_employees: number;
  average_distance_km: number;
  kilometric_allowance_per_km: number;
  working_days?: number;
  trips_per_day?: number;
  total_annual_cost?: number;
}

export interface BreakevenPoint {
  employees: number;
  transport_cost_per_employee: number;
  allowance_cost_per_employee: number;
}

export interface CostAnalysisResponse {
  cost_per_available_seat: number;
  cost_per_occupied_seat: number;
  annual_cost_per_employee: number;
  breakeven_employees: number;
  annual_route_cost: number;
  vehicle_capacity: number;
  fill_rate: number;
  transported_employees: number;
  working_days: number;
  trips_per_day: number;
  annual_allowance_per_employee: number;
  breakeven_chart: BreakevenPoint[];
}
