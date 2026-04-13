import { api } from './client';

/* ── Types ──────────────────────────────────────────────────────────────── */

export interface TripStop {
  id: string;
  stop_name: string;
  scheduled_time: string;
  actual_time: string | null;
  passenger_count: number;
  lat: number;
  lng: number;
  status: 'pending' | 'arrived' | 'departed' | 'skipped';
}

export interface DriverTrip {
  id: string;
  ligne_id: string;
  ligne_name: string;
  vehicle_id: string;
  vehicle_plate: string;
  shift: string;
  status: 'upcoming' | 'in_progress' | 'completed' | 'cancelled';
  scheduled_departure: string;
  scheduled_arrival: string;
  actual_departure: string | null;
  actual_arrival: string | null;
  stops: TripStop[];
  passenger_count_total: number;
}

export interface MaintenanceAlert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  due_date: string;
}

export interface VehicleTelemetry {
  speed_avg_kmh: number;
  distance_today_km: number;
  fuel_consumed_l: number;
  engine_hours: number;
}

export interface DriverVehicle {
  id: string;
  plate: string;
  type: string;
  capacity: number;
  motorization: string;
  fuel_level_pct: number;
  odometer_km: number;
  maintenance_alerts: MaintenanceAlert[];
  telemetry: VehicleTelemetry;
}

export interface DriverRiskProfile {
  driver_id: string;
  risk_score: number;
  risk_category: 'low' | 'medium' | 'high' | 'critical';
  infractions: {
    speed: number;
    acceleration: number;
    braking: number;
    geofence: number;
    driving_time: number;
  };
  score_history: { date: string; score: number }[];
  tips: string[];
}

export interface ScheduleDay {
  date: string;
  day_name: string;
  trips: {
    ligne_name: string;
    vehicle_plate: string;
    shift: string;
    departure: string;
    arrival: string;
    is_lto_optimized: boolean;
  }[];
  rest_hours: number;
  is_rest_day: boolean;
}

/* ── API Functions ──────────────────────────────────────────────────────── */

const DRIVER = '/api/v1/driver';

export const fetchDriverTrips = async (
  date?: string,
): Promise<{ data: DriverTrip[] }> => {
  const params = date ? { date } : {};
  const response = await api.get(`${DRIVER}/trips`, { params });
  return response.data;
};

export const fetchDriverVehicle = async (): Promise<DriverVehicle> => {
  const response = await api.get(`${DRIVER}/vehicle`);
  return response.data;
};

export const fetchDriverRisk = async (): Promise<DriverRiskProfile> => {
  const response = await api.get(`${DRIVER}/risk`);
  return response.data;
};

export const fetchDriverSchedule = async (
  week_offset?: number,
): Promise<{ data: ScheduleDay[] }> => {
  const params = week_offset !== undefined ? { week_offset } : {};
  const response = await api.get(`${DRIVER}/schedule`, { params });
  return response.data;
};

export const reportVehicleIssue = async (data: {
  type: string;
  description: string;
  severity: string;
}): Promise<void> => {
  await api.post(`${DRIVER}/vehicle/report-issue`, data);
};

export const requestShiftSwap = async (
  tripId: string,
  reason: string,
): Promise<void> => {
  await api.post(`${DRIVER}/schedule/swap-request`, {
    trip_id: tripId,
    reason,
  });
};
