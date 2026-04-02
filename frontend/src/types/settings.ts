export interface OptimizationSettings {
  id: string;
  tenant_id: string;
  meeting_radius_meters: number;
  max_walking_distance_meters: number;
  max_route_duration_seconds: number;
  fuel_cost_per_liter: number;
  fuel_consumption_l_per_100km: number;
  co2_kg_per_liter: number;
  rti_threshold_minutes: number;
  night_mode_start: string;
  night_mode_end: string;
  min_night_group_size: number;
  created_at: string;
  updated_at: string;
}

export interface ConstraintParam {
  id: string;
  tenant_id: string;
  key: string;
  value: string;
  category: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConstraintCreate {
  key: string;
  value: string;
  category?: string;
  description?: string;
}

export interface ConstraintUpdate {
  value?: string;
  category?: string;
  description?: string;
  is_active?: boolean;
}
