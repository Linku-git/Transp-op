export interface ScenarioRequest {
  site_id: string;
  condition_type: string;
  demand_multiplier?: number | null;
  custom_params?: Record<string, unknown> | null;
  name?: string | null;
}

export interface ScenarioMetrics {
  total_employees: number;
  employees_assigned: number;
  total_clusters: number;
  total_vehicles_used: number;
  avg_occupancy_rate: number;
  total_distance_km: number;
  total_duration_minutes: number;
  estimated_fuel_liters: number;
  estimated_fuel_cost_mad: number;
  co2_estimate_kg: number;
  demand_multiplier_applied: number;
}

export interface Scenario {
  id: string;
  tenant_id: string;
  site_id: string;
  baseline_optimization_id: string | null;
  condition_type: string;
  demand_multiplier: number;
  custom_params: Record<string, unknown>;
  estimated_metrics: ScenarioMetrics;
  name: string | null;
  created_at: string;
}

export interface MetricDelta {
  scenario_a_id: string;
  scenario_b_id: string;
  vehicles_delta: number;
  cost_delta_mad: number;
  co2_delta_kg: number;
  distance_delta_km: number;
  duration_delta_minutes: number;
  occupancy_delta_pct: number;
}

export interface ScenarioComparison {
  scenarios: Scenario[];
  deltas: MetricDelta[];
}

export interface WeatherForecast {
  id: string;
  site_id: string;
  date: string;
  condition_summary: string | null;
  precipitation_mm: number | null;
  temp_min_c: number | null;
  temp_max_c: number | null;
  wind_kph: number | null;
}

export interface ScenarioSuggestion {
  date: string;
  condition_summary: string;
  suggested_condition_type: string;
  reason: string;
}

export interface WeatherSuggestions {
  site_id: string;
  suggestions: ScenarioSuggestion[];
}
