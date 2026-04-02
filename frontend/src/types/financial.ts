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
