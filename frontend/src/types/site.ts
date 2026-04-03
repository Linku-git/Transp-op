export type SecurityProfile = 'normal' | 'elevated' | 'critical';

export type ShiftType = 'Poste 1' | 'Poste 2' | 'Poste 3' | 'Normal' | 'Sirène' | 'Personnalisé';

export const SHIFT_PRESETS: Record<ShiftType, {
  depart_h1: string; retour_h1: string; depart_h2: string | null; retour_h2: string | null;
}> = {
  'Poste 1':      { depart_h1: '05:50', retour_h1: '14:45', depart_h2: null,    retour_h2: '15:45' },
  'Poste 2':      { depart_h1: '13:50', retour_h1: '22:45', depart_h2: null,    retour_h2: '23:45' },
  'Poste 3':      { depart_h1: '21:50', retour_h1: '06:45', depart_h2: null,    retour_h2: '07:45' },
  'Normal':       { depart_h1: '07:00', retour_h1: '16:00', depart_h2: null,    retour_h2: null    },
  'Sirène':       { depart_h1: '07:00', retour_h1: '12:00', depart_h2: '14:00', retour_h2: '18:00' },
  'Personnalisé': { depart_h1: '',      retour_h1: '',       depart_h2: null,    retour_h2: null    },
};

export const ALL_SHIFT_TYPES: ShiftType[] = ['Poste 1', 'Poste 2', 'Poste 3', 'Normal', 'Sirène', 'Personnalisé'];

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

  shift_1_type: string | null;
  shift_1_entry: string | null;
  shift_1_exit: string | null;
  shift_1_depart_h2: string | null;
  shift_1_retour_h2: string | null;

  shift_2_type: string | null;
  shift_2_entry: string | null;
  shift_2_exit: string | null;
  shift_2_depart_h2: string | null;
  shift_2_retour_h2: string | null;

  shift_3_type: string | null;
  shift_3_entry: string | null;
  shift_3_exit: string | null;
  shift_3_depart_h2: string | null;
  shift_3_retour_h2: string | null;

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
  active_shift_ids: string[];
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

  shift_1_type?: string | null;
  shift_1_entry?: string | null;
  shift_1_exit?: string | null;
  shift_1_depart_h2?: string | null;
  shift_1_retour_h2?: string | null;

  shift_2_type?: string | null;
  shift_2_entry?: string | null;
  shift_2_exit?: string | null;
  shift_2_depart_h2?: string | null;
  shift_2_retour_h2?: string | null;

  shift_3_type?: string | null;
  shift_3_entry?: string | null;
  shift_3_exit?: string | null;
  shift_3_depart_h2?: string | null;
  shift_3_retour_h2?: string | null;

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
  active_shift_ids?: string[];
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
