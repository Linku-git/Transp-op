export interface CO2TrendPoint {
  date: string;
  co2_saved_kg: number;
}

export interface CO2Savings {
  co2_saved_kg: number;
  co2_baseline_kg: number;
  co2_actual_kg: number;
  co2_saved_pct: number;
  trend: CO2TrendPoint[];
}

export interface PrivateVehiclesAvoided {
  vehicles_avoided: number;
  total_with_car: number;
  adoption_pct: number;
}

export interface ModalModeEntry {
  mode: string;
  count: number;
  pct: number;
}

export interface ModalBeforeAfter {
  before: Record<string, number>;
  after: Record<string, number>;
}

export interface ModalDistribution {
  by_mode: ModalModeEntry[];
  soft_pct: number;
  electric_pct: number;
  shared_pct: number;
  individual_pct: number;
  before_after: ModalBeforeAfter;
}

export interface ZFECompliance {
  compliant_count: number;
  total_count: number;
  compliance_pct: number;
}

export interface RSEKPIsResponse {
  co2_savings: CO2Savings;
  private_vehicles_avoided: PrivateVehiclesAvoided;
  modal_distribution: ModalDistribution;
  zfe_compliance: ZFECompliance;
}
