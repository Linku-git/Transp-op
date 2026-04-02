export interface Vehicle {
  id: string;
  tenant_id: string;
  matricule: string | null;
  type: string;
  brand_model: string | null;
  capacity: number;
  year: number | null;
  circulation_date: string | null;
  owner_type: string | null;
  prestataire: string | null;
  monthly_cost_mad: number | null;
  monthly_km: number | null;
  condition: string;
  site_id: string | null;
  site_name: string | null;
  is_pmr_accessible: boolean;
  fuel_consumption: number | null;
  cost_per_km: number | null;
  motorization: string | null;
  length_meters: number | null;
  zfe_compliant: boolean;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface VehicleCreate {
  matricule?: string | null;
  type: string;
  brand_model?: string | null;
  capacity: number;
  year?: number | null;
  circulation_date?: string | null;
  owner_type?: string | null;
  prestataire?: string | null;
  monthly_cost_mad?: number | null;
  monthly_km?: number | null;
  condition?: string;
  site_id?: string | null;
  is_pmr_accessible?: boolean;
  fuel_consumption?: number | null;
  cost_per_km?: number | null;
  motorization?: string | null;
  length_meters?: number | null;
  zfe_compliant?: boolean;
  observations?: string | null;
}

export type VehicleUpdate = Partial<VehicleCreate>;

export interface VehicleListParams {
  site_id?: string;
  condition?: string;
  page?: number;
  page_size?: number;
}

export const VEHICLE_TYPES = [
  'Minibus',
  'Midibus',
  'Bus standard',
  'Berline',
  'SUV',
  'Van',
  'Utilitaire',
  'Autre',
];

export const CONDITIONS = ['Bon', 'Moyen', 'Mauvais'];
export const MOTORIZATIONS = ['diesel', 'hybrid', 'electric', 'hydrogen', 'gnv'];
export const OWNER_TYPES = ['proprietaire', 'loueur', 'sous-traitant'];

export interface KmConsommation {
  id: string;
  tenant_id: string;
  site_id: string | null;
  site_name: string | null;
  prestataire: string;
  vehicle_type: string;
  vehicle_count_peak: number | null;
  km_avg: number | null;
  km_min: number | null;
  km_max: number | null;
  seat_count: number | null;
  fuel_consumption_l100km: number | null;
  monthly_cost_per_vehicle_mad: number | null;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface KmConsommationCreate {
  prestataire: string;
  vehicle_type: string;
  site_id?: string | null;
  vehicle_count_peak?: number | null;
  km_avg?: number | null;
  km_min?: number | null;
  km_max?: number | null;
  seat_count?: number | null;
  fuel_consumption_l100km?: number | null;
  monthly_cost_per_vehicle_mad?: number | null;
  observations?: string | null;
}

export type KmConsommationUpdate = Partial<KmConsommationCreate>;

export interface PointArret {
  id: string;
  tenant_id: string;
  site_id: string | null;
  site_name: string | null;
  code: string;
  nom: string;
  adresse: string | null;
  ville: string | null;
  lat: number;
  lng: number;
  prestataire: string | null;
  is_active: boolean;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface PointArretCreate {
  code: string;
  nom: string;
  lat: number;
  lng: number;
  adresse?: string | null;
  ville?: string | null;
  prestataire?: string | null;
  site_id?: string | null;
  is_active?: boolean;
  observations?: string | null;
}

export type PointArretUpdate = Partial<PointArretCreate>;

export interface ConfigurationTransport {
  id: string;
  tenant_id: string;
  site_id: string | null;
  site_name: string | null;
  ligne: string;
  prestataire: string;
  vehicle_type: string | null;
  vehicle_count: number | null;
  shift: string | null;
  point_depart_id: string | null;
  point_arrivee_id: string | null;
  point_depart_nom: string | null;
  point_arrivee_nom: string | null;
  circuit: string | null;
  is_active: boolean;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationTransportCreate {
  ligne: string;
  prestataire: string;
  site_id?: string | null;
  vehicle_type?: string | null;
  vehicle_count?: number | null;
  shift?: string | null;
  point_depart_id?: string | null;
  point_arrivee_id?: string | null;
  circuit?: string | null;
  is_active?: boolean;
  observations?: string | null;
}

export type ConfigurationTransportUpdate = Partial<ConfigurationTransportCreate>;
