export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'drh' | 'daf' | 'salarie' | 'operateur';
  tenant_id: string;
  mfa_enabled: boolean;
}

export interface Site {
  id: string;
  tenant_id: string;
  name: string;
  code: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  is_active: boolean;
}

export interface Employee {
  id: string;
  tenant_id: string;
  site_id: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  is_pmr: boolean;
  is_active: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    pages: number;
    total: number;
    page_size: number;
  };
}

export interface ApiError {
  detail: string;
  code: string;
  field?: string;
}
