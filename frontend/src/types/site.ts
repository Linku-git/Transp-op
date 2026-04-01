export type SecurityProfile = 'normal' | 'elevated' | 'critical';

export interface Site {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  address: string;
  city: string;
  lat: number;
  lng: number;
  num_shifts: number;
  shift_1_entry: string | null;
  shift_1_exit: string | null;
  shift_2_entry: string | null;
  shift_2_exit: string | null;
  shift_3_entry: string | null;
  shift_3_exit: string | null;
  working_days: string;
  days_per_week: number;
  contact_name: string | null;
  contact_phone: string | null;
  access_notes: string | null;
  parking_notes: string | null;
  zfe_zone: boolean;
  security_profile: SecurityProfile;
  timezone: string;
  observations: string | null;
  created_at: string;
  updated_at: string;
}

export interface SiteCreate {
  code: string;
  name: string;
  address: string;
  city: string;
  lat: number;
  lng: number;
  num_shifts: number;
  shift_1_entry?: string | null;
  shift_1_exit?: string | null;
  shift_2_entry?: string | null;
  shift_2_exit?: string | null;
  shift_3_entry?: string | null;
  shift_3_exit?: string | null;
  working_days: string;
  days_per_week: number;
  contact_name?: string | null;
  contact_phone?: string | null;
  access_notes?: string | null;
  parking_notes?: string | null;
  zfe_zone?: boolean;
  security_profile?: SecurityProfile;
  timezone?: string;
  observations?: string | null;
}

export interface SiteUpdate extends Partial<SiteCreate> {}

export interface SiteSummary {
  id: string;
  code: string;
  name: string;
  city: string;
  employee_count: number;
  vehicle_count: number;
  pmr_count: number;
}

export interface SiteListParams {
  page?: number;
  page_size?: number;
  city?: string;
  zfe_zone?: boolean;
  q?: string;
}
