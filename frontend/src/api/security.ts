import api from './client';

export interface SecurityKpiData {
  avg_score: number;
  total_scored_employees: number;
  risk_distribution: { low: number; medium: number; high: number; critical: number };
  night_shift_coverage_pct: number;
  incident_count_30d: number;
}

export interface RiskMapStop {
  id: string;
  stop_name: string;
  lat: number;
  lng: number;
  composite_risk_score: number;
  is_critical: boolean;
  isolation_score: number;
  lighting_score: number;
  tc_frequency_score: number;
  employee_perception_avg: number;
}

export async function getSecurityKpis(): Promise<SecurityKpiData> {
  const { data } = await api.get('/api/v1/kpis/security');
  return data;
}

export async function getRiskMap(): Promise<{ stops: RiskMapStop[]; total: number }> {
  const { data } = await api.get('/api/v1/security/risk-map');
  return data;
}

export async function getSecurityScores(params?: { risk_level?: string }) {
  const { data } = await api.get('/api/v1/security/scores', { params });
  return data;
}
