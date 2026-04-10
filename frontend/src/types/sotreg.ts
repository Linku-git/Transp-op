/* ── SOTREG types — Transport Lines, Fleet Context, OD Matrix, ZFE ────────── */

/* ── Ligne (transport line) ──────────────────────────────────────────────── */

export interface Ligne {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  site_id: string | null;

  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;

  distance_km: number;
  rotations_per_day: number;
  operating_days_per_year: number;
  km_annual: number;

  vehicle_type: string | null;
  motorization: string | null;
  passenger_count_avg: number | null;
  shift_type: string | null;
  service_type: string;
  pente_moyenne_pct: number | null;
  is_active: boolean;

  created_at: string;
  updated_at: string;
}

export interface LigneCreate {
  code: string;
  name: string;
  site_id?: string | null;
  origin_lat: number;
  origin_lng: number;
  dest_lat: number;
  dest_lng: number;
  distance_km: number;
  rotations_per_day: number;
  operating_days_per_year: number;
  vehicle_type?: string | null;
  motorization?: string | null;
  passenger_count_avg?: number | null;
  shift_type?: string | null;
  service_type: string;
  pente_moyenne_pct?: number | null;
}

export interface LigneUpdate {
  name?: string;
  site_id?: string | null;
  origin_lat?: number;
  origin_lng?: number;
  dest_lat?: number;
  dest_lng?: number;
  distance_km?: number;
  rotations_per_day?: number;
  operating_days_per_year?: number;
  vehicle_type?: string | null;
  motorization?: string | null;
  passenger_count_avg?: number | null;
  shift_type?: string | null;
  service_type?: string;
  pente_moyenne_pct?: number | null;
  is_active?: boolean;
}

export interface LigneListMeta {
  page: number;
  pages: number;
  total: number;
  page_size: number;
}

export interface LigneListResponse {
  data: Ligne[];
  meta: LigneListMeta;
}

export interface LigneListParams {
  page?: number;
  page_size?: number;
  service_type?: string;
  site_id?: string;
  is_active?: boolean;
}

/* ── Fleet Context ───────────────────────────────────────────────────────── */

export interface FleetContext {
  id: string;
  tenant_id: string;
  total_vehicles: number;
  total_km_annual: number;
  total_tco2_annual: number;
  average_age_years: number | null;
  pct_diesel: number;
  pct_electric: number;
  pct_hybrid: number;
  currency: string;
  snapshot_date: string;
  created_at: string;
  updated_at: string;
}

/* ── OD Matrix ───────────────────────────────────────────────────────────── */

export interface ODMatrixEntry {
  id: string;
  tenant_id: string;
  ligne_id: string | null;
  origin_zone: string;
  destination_zone: string;
  flow_estimate: number;
  distance_km: number;
  gravity_score: number;
  beta_used: number;
  computed_at: string;
  created_at: string;
  updated_at: string;
}

export interface ODMatrixListResponse {
  data: ODMatrixEntry[];
  total: number;
  beta_used: number;
}

export interface ODMatrixComputeRequest {
  beta?: number;
  k?: number;
}

export interface ODMatrixComputeResponse {
  entries_computed: number;
  beta_used: number;
  k_used: number;
  entries: ODMatrixEntry[];
}

/* ── ZFE ─────────────────────────────────────────────────────────────────── */

export interface ZFEEndpointResult {
  lat: number;
  lng: number;
  is_in_zfe: boolean;
  zone_name: string | null;
  restriction_level: string | null;
  allowed_crit_air: number[] | null;
}

export interface ZFELigneResult {
  ligne_id: string;
  ligne_code: string;
  ligne_name: string;
  origin: ZFEEndpointResult;
  dest: ZFEEndpointResult;
  any_endpoint_in_zfe: boolean;
  checked_at: string;
}

export interface ZFEComplianceResponse {
  total_lignes: number;
  lignes_in_zfe: number;
  results: ZFELigneResult[];
}

export interface ZFEPointCheckResponse {
  is_in_zfe: boolean;
  zone_name: string | null;
  restriction_level: string | null;
  allowed_crit_air: number[] | null;
  checked_at: string;
}

/* ── Service type helpers ────────────────────────────────────────────────── */

export const SERVICE_TYPE_OPTIONS = ['navette', 'liaison', 'vip', 'mixte'] as const;

export const SERVICE_TYPE_LABELS: Record<string, string> = {
  navette: 'Navette',
  liaison: 'Liaison',
  vip: 'VIP',
  mixte: 'Mixte',
};

export const MOTORIZATION_OPTIONS = ['diesel', 'essence', 'electrique', 'hybride', 'gnv'] as const;

export const MOTORIZATION_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  essence: 'Essence',
  electrique: 'Électrique',
  hybride: 'Hybride',
  gnv: 'GNV',
};
