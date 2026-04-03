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
  correspondance_tb: string | null;
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
  correspondance_tb?: string | null;
  observations?: string | null;
}

export type PointArretUpdate = Partial<PointArretCreate>;

export interface HoraireTravail {
  id: string;
  tenant_id: string;
  site_id: string | null;
  site_name: string | null;
  type_horaire: string;
  depart_h1: string | null;
  retour_h1: string | null;
  depart_h2: string | null;
  retour_h2: string | null;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface HoraireTravailCreate {
  type_horaire: string;
  site_id?: string | null;
  depart_h1?: string | null;
  retour_h1?: string | null;
  depart_h2?: string | null;
  retour_h2?: string | null;
  observations?: string | null;
}

export type HoraireTravailUpdate = Partial<HoraireTravailCreate>;

export interface ConfigurationPlan {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  is_current: boolean;
  source: string | null;
  row_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationPlanCreate {
  name: string;
  description?: string | null;
  is_active?: boolean;
  is_current?: boolean;
  source?: string | null;
}

export type ConfigurationPlanUpdate = Partial<ConfigurationPlanCreate>;

export interface ConfigurationTransport {
  id: string;
  tenant_id: string;
  plan_id: string;
  site_id: string | null;
  site_name: string | null;
  conducteur: string | null;
  poste: string | null;
  prestataire: string | null;
  mle_vehicule: string | null;
  type_vehicule: string | null;
  type_moteur: string | null;
  secteur: string | null;
  entite: string | null;
  aller_retour: string | null;
  shift: string | null;
  heure_depart: string | null;
  point_depart: string | null;
  point_arrivee: string | null;
  heure_arrivee: string | null;
  arrets_circuit: string | null;
  duree_trajet_min: number | null;
  km: number | null;
  rot: number | null;
  t_km: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConfigurationTransportCreate {
  plan_id: string;
  site_id?: string | null;
  conducteur?: string | null;
  poste?: string | null;
  prestataire?: string | null;
  mle_vehicule?: string | null;
  type_vehicule?: string | null;
  type_moteur?: string | null;
  secteur?: string | null;
  entite?: string | null;
  aller_retour?: string | null;
  shift?: string | null;
  heure_depart?: string | null;
  point_depart?: string | null;
  point_arrivee?: string | null;
  heure_arrivee?: string | null;
  arrets_circuit?: string | null;
  duree_trajet_min?: number | null;
  km?: number | null;
  rot?: number | null;
  t_km?: number | null;
  is_active?: boolean;
}

export type ConfigurationTransportUpdate = Partial<Omit<ConfigurationTransportCreate, 'plan_id'>>;
