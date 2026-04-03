import { api } from './client';

export interface DashboardKpiData {
  total_vehicles: number;
  total_distance_km: number;
  avg_occupancy_rate: number;
  fuel_cost_mad: number;
  co2_saved_kg: number;
  bus_users: number;
  car_users: number;
  total_employees: number;
  total_circuits: number;
}

export async function getDashboardKpis(): Promise<DashboardKpiData> {
  const res = await api.get<DashboardKpiData>('/api/v1/kpis/dashboard');
  return res.data;
}
