export interface EmployeeModal {
  id: string;
  employee_id: string;
  employee_name: string | null;
  primary_mode: string;
  alternative_mode: string | null;
  distance_km: number | null;
  travel_time_min: number | null;
  frequency: string | null;
  interest_company_transport: string | null;
  accepts_common_pickup: boolean;
  max_pickup_distance_meters: number;
  has_private_car: boolean;
  volunteer_driver: boolean;
  carpool_seats_available: number;
  max_detour_minutes: number | null;
  bonus_opt_in: boolean;
  observations: string | null;
}

export interface EmployeeModalUpsert {
  primary_mode: string;
  alternative_mode?: string | null;
  distance_km?: number | null;
  travel_time_min?: number | null;
  frequency?: string | null;
  interest_company_transport?: string | null;
  accepts_common_pickup?: boolean;
  max_pickup_distance_meters?: number;
  has_private_car?: boolean;
  volunteer_driver?: boolean;
  carpool_seats_available?: number;
  max_detour_minutes?: number | null;
  bonus_opt_in?: boolean;
  observations?: string | null;
}

export interface ModalDistribution {
  mode: string;
  count: number;
  percentage: number;
}

export interface ModalSiteDistribution {
  site_id: string;
  site_name: string;
  distribution: ModalDistribution[];
}

export interface ModalStats {
  total: number;
  distribution: ModalDistribution[];
  by_site: ModalSiteDistribution[];
}

export interface ShiftModalData {
  shift_time: string;
  total: number;
  distribution: ModalDistribution[];
}

export interface MobilityScore {
  employee_id: string;
  employee_name: string;
  score: number;
  factors: Record<string, number>;
}
