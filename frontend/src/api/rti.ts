import api from './client';

export interface RTIKpiData {
  compliance_pct: number;
  avg_wait_seconds: number;
  active_violations: number;
  total_events: number;
  trend: { date: string; compliance_pct: number }[];
  period: string;
}

export interface RiskStop {
  id: string;
  stop_name: string;
  lat: number;
  lng: number;
  composite_risk_score: number;
  is_critical: boolean;
  isolation_score: number;
  lighting_score: number;
}

export interface ViolationEvent {
  id: string;
  vehicle_id: string;
  stop_id: string | null;
  event_type: string;
  scheduled_at: string | null;
  actual_at: string | null;
  wait_duration_seconds: number | null;
  created_at: string;
}

export async function getRtiKpis(period: string = 'day'): Promise<RTIKpiData> {
  const { data } = await api.get('/api/v1/kpis/rti', { params: { period } });
  return data;
}

export async function getRiskStops(params?: {
  site_id?: string;
  is_critical?: boolean;
}): Promise<{ data: RiskStop[]; total: number }> {
  const { data } = await api.get('/api/v1/rti/risk-stops', { params });
  return data;
}

export async function getViolationEvents(): Promise<ViolationEvent[]> {
  // Uses RTI events endpoint filtered for violations (wait > 90s)
  const { data } = await api.get('/api/v1/rti/compliance');
  return data.violations || [];
}
