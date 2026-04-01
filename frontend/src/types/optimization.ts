export interface RouteStop {
  employee_id: string | null;
  lat: number;
  lng: number;
  is_pickup: boolean;
  eta_seconds: number;
  cumulative_distance_meters: number;
}

export interface OptimizationRoute {
  id: string;
  optimization_id: string;
  vehicle_id: string | null;
  site_id: string;
  ordered_stops: RouteStop[];
  total_distance_km: number | null;
  total_time_minutes: number | null;
  polyline: string | null;
  rti_compliance_pct: number | null;
  created_at: string;
  vehicle_type: string | null;
  vehicle_capacity: number | null;
  site_name: string | null;
}

export interface ClusterEmployee {
  employee_id: string;
  first_name: string;
  last_name: string;
  lat: number | null;
  lng: number | null;
  is_pmr: boolean;
}

export interface OptimizationCluster {
  id: string;
  optimization_id: string;
  site_id: string;
  centroid_lat: number;
  centroid_lng: number;
  employee_count: number;
  pmr_count: number;
  employee_ids: string[];
  created_at: string;
  employees?: ClusterEmployee[];
}

export interface OptimizationMetrics {
  total_employees: number;
  employees_assigned: number;
  employees_excluded_leave: number;
  total_clusters: number;
  total_vehicles_used: number;
  avg_occupancy_rate: number;
  total_distance_km: number;
  total_duration_minutes: number;
  estimated_fuel_liters: number;
  estimated_fuel_cost_mad: number;
  co2_estimate_kg: number;
  time_saved_vs_individual_hours: number;
  unassigned_clusters: number;
}

export interface Optimization {
  id: string;
  tenant_id: string;
  site_id: string | null;
  condition_type: string;
  status: string;
  params: Record<string, unknown>;
  metrics: OptimizationMetrics | Record<string, unknown>;
  target_date: string | null;
  created_at: string;
  completed_at: string | null;
  clusters: OptimizationCluster[];
  routes: OptimizationRoute[];
}

export interface OptimizationStatus {
  optimization_id: string;
  status: string;
  progress: number;
  step: string;
  error: string | null;
}

export interface OptimizationHistoryItem {
  id: string;
  site_id: string | null;
  condition_type: string;
  status: string;
  metrics: Record<string, unknown>;
  target_date: string | null;
  created_at: string;
  completed_at: string | null;
  site_name: string | null;
}

export interface OptimizationRunParams {
  site_id: string;
  condition_type?: string;
  target_date?: string;
  algorithm?: string;
  eps_meters?: number;
  min_samples?: number;
  n_clusters?: number;
  max_cluster_size?: number;
  max_walking_distance_meters?: number;
  max_route_duration_seconds?: number;
  include_volunteers?: boolean;
  use_osrm?: boolean;
}

export interface MeetingZone {
  cluster_index: number;
  lat: number;
  lng: number;
  road_name: string | null;
  snap_distance_meters: number;
  pmr_accessible: boolean;
  employee_count: number;
  pmr_count: number;
  employee_ids: string[];
  all_within_constraint: boolean;
}

export interface LayerVisibility {
  employees: boolean;
  clusters: boolean;
  routes: boolean;
  meetingZones: boolean;
  accessLegs: boolean;
  siteMarker: boolean;
}
