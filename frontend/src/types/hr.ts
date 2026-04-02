export interface CoverageBreakdown {
  name: string;
  total: number;
  covered: number;
  pct: number;
}

export interface MobilityCoverage {
  total_employees: number;
  covered_employees: number;
  coverage_pct: number;
  by_site: CoverageBreakdown[];
  by_shift: CoverageBreakdown[];
  by_department: CoverageBreakdown[];
}

export interface MobilityScorePoint {
  date: string;
  site_id: string;
  occupancy_pct: number;
  co2_kg: number;
  score: number;
}

export interface AbsenteeismGroup {
  employee_count: number;
  total_leave_days: number;
  avg_absence_days: number;
  absence_rate_pct: number;
}

export interface AbsenteeismCorrelation {
  with_transport: AbsenteeismGroup;
  without_transport: AbsenteeismGroup;
  maybe_transport: AbsenteeismGroup;
  correlation: {
    delta_pct: number;
    interpretation: string;
  };
}

export interface RetentionImpact {
  total_employees: number;
  departed_total: number;
  departed_with_transport: number;
  departed_without_transport: number;
  turnover_rate_pct: number;
  avg_replacement_cost: number;
  estimated_annual_savings: number;
}

export interface ShadowZoneEmployee {
  id: string;
  name: string;
  quartier: string;
  city: string;
  distance_km: number;
  primary_mode: string;
}

export interface ShadowZones {
  shadow_zone_count: number;
  total_active_employees: number;
  shadow_zone_pct: number;
  threshold_km: number;
  employees: ShadowZoneEmployee[];
}

export interface HRKPIsResponse {
  mobility_coverage: MobilityCoverage;
  mobility_score_evolution: MobilityScorePoint[];
  absenteeism_correlation: AbsenteeismCorrelation;
  retention_impact: RetentionImpact;
  shadow_zones: ShadowZones;
}
