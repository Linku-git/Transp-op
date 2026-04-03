import { api } from './client';

const BASE = '/api/v1/transport-optimization';

export interface StopStat {
  id: string; code: string; nom: string; ville: string | null;
  lat: number | null; lng: number | null; prestataire: string | null; is_active: boolean;
  usage_count: number; utilization_score: number; walking_score: number; coverage_radius_m: number;
}
export interface StopsAnalysis {
  total_stops: number; active_stops: number;
  cities: { name: string; count: number; active: number }[];
  stops: StopStat[]; avg_usage: number; coverage_pct: number;
}

export interface FleetAnalysis {
  plan_id: string; plan_name: string; total_trips: number; total_postes: number;
  total_km: number; total_tkm: number; shifts: Record<string, number>;
  vehicle_dist: Record<string, number>; secteurs: Record<string, number>;
  avg_fill_pct: number; routes_below_70: number; routes_above_100: number;
  estimated_daily_cost_mad: number; current_score: Record<string, number>;
}

export interface OptimizedTrip {
  trip_id: string; poste: string | null; shift: string | null; aller_retour: string | null;
  current_vehicle: string | null; suggested_vehicle: string | null;
  current_capacity: number; suggested_capacity: number; estimated_passengers: number;
  current_fill_pct: number; suggested_fill_pct: number;
  current_cost: number; suggested_cost: number; saving_mad: number; action: string;
}
export interface OptimizationResult {
  plan_id: string; total_trips: number; trips_optimized: number; trips_kept: number;
  trips_downsized: number; trips_upsized: number; total_saving_mad: number;
  total_saving_pct: number; fill_improvement_pct: number;
  new_score: Record<string, number>; optimized_trips: OptimizedTrip[];
  summary: string; can_generate_plan: boolean;
}

export interface TripItem {
  id: string; poste: string | null; conducteur: string | null;
  shift: string | null; aller_retour: string | null; secteur: string | null;
  entite: string | null; prestataire: string | null; type_vehicule: string | null;
  mle_vehicule: string | null; heure_depart: string | null; heure_arrivee: string | null;
  point_depart: string | null; point_arrivee: string | null; arrets_circuit: string | null;
  km: number | null; rot: number | null; t_km: number | null; duree_trajet_min: number | null;
  capacity: number; estimated_passengers: number; fill_pct: number;
  stops_list: string[]; estimated_cost_mad: number;
}
export interface TripsListResponse {
  plan_id: string; plan_name: string; total: number; trips: TripItem[];
}

export interface TripDetail {
  trip: TripItem;
  start_point: { lat: number | null; lng: number | null; label: string } | null;
  end_point: { lat: number | null; lng: number | null; label: string } | null;
  waypoints: { code: string; label: string; lat: number | null; lng: number | null }[];
  google_maps_url: string;
}

export async function getStopsAnalysis(): Promise<StopsAnalysis> {
  const r = await api.get<StopsAnalysis>(`${BASE}/stops`);
  return r.data;
}
export async function getFleetAnalysis(planId: string): Promise<FleetAnalysis> {
  const r = await api.get<FleetAnalysis>(`${BASE}/plan/${planId}/analysis`);
  return r.data;
}
export async function runFleetOptimizer(planId: string, params: {
  min_fill_rate?: number; fill_assumption?: number;
  prefer_smaller?: boolean; shift_filter?: string | null; secteur_filter?: string | null;
}): Promise<OptimizationResult> {
  const r = await api.post<OptimizationResult>(`${BASE}/plan/${planId}/optimize`, params);
  return r.data;
}
export async function getPlanTrips(planId: string, filters?: Record<string, unknown>): Promise<TripsListResponse> {
  const r = await api.get<TripsListResponse>(`${BASE}/plan/${planId}/trips`, { params: filters });
  return r.data;
}
export async function getTripDetail(tripId: string): Promise<TripDetail> {
  const r = await api.get<TripDetail>(`${BASE}/trip/${tripId}`);
  return r.data;
}
