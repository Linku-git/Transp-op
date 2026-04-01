export type OptInChoice = 'Oui' | 'Non' | 'Sous conditions';

export interface Employee {
  id: string;
  tenant_id: string;
  matricule: string;
  first_name: string;
  last_name: string;
  site_id: string;
  site_name: string | null;
  shift_time: string | null;
  address: string | null;
  quartier: string | null;
  city: string | null;
  lat: number | null;
  lng: number | null;
  preferred_pickup_address: string | null;
  preferred_pickup_lat: number | null;
  preferred_pickup_lng: number | null;
  is_pmr: boolean;
  function_role: string | null;
  phone: string | null;
  department: string | null;
  transport_required: boolean;
  current_transport_mode: string | null;
  opt_in_company_transport: OptInChoice;
  has_private_car: boolean;
  volunteer_driver: boolean;
  carpool_seats: number;
  active: boolean;
  sirh_external_id: string | null;
  hire_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  matricule: string;
  first_name: string;
  last_name: string;
  site_id: string;
  shift_time?: string | null;
  address?: string | null;
  quartier?: string | null;
  city?: string | null;
  lat?: number | null;
  lng?: number | null;
  preferred_pickup_address?: string | null;
  preferred_pickup_lat?: number | null;
  preferred_pickup_lng?: number | null;
  is_pmr?: boolean;
  function_role?: string | null;
  phone?: string | null;
  department?: string | null;
  transport_required?: boolean;
  current_transport_mode?: string | null;
  opt_in_company_transport?: OptInChoice;
  has_private_car?: boolean;
  volunteer_driver?: boolean;
  carpool_seats?: number;
  sirh_external_id?: string | null;
  hire_date?: string | null;
  end_date?: string | null;
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {}

export interface EmployeeListParams {
  page?: number;
  page_size?: number;
  site_id?: string;
  is_pmr?: boolean;
  shift_time?: string;
  department?: string;
  active?: boolean;
  q?: string;
}

export interface EmployeeSummary {
  total_count: number;
  active_count: number;
  pmr_count: number;
  by_site: { site_id: string; site_name: string; count: number }[];
  by_department: { department: string; count: number }[];
}

export interface CSVUploadResult {
  total_rows: number;
  created: number;
  errors: { row: number; field: string; message: string }[];
}
