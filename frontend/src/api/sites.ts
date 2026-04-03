import { api } from './client';
import type { PaginatedResponse } from '../types';
import type {
  Site,
  SiteCreate,
  SiteListParams,
  SiteSummary,
  SiteUpdate,
} from '../types/site';

const BASE = '/api/v1/sites/';

export const listSites = async (
  params: SiteListParams = {},
): Promise<PaginatedResponse<Site>> => {
  const response = await api.get<PaginatedResponse<Site>>(BASE, { params });
  return response.data;
};

export const getSite = async (id: string): Promise<Site> => {
  const response = await api.get<Site>(`${BASE}${id}`);
  return response.data;
};

export const getSiteByCode = async (code: string): Promise<Site> => {
  const response = await api.get<Site>(`${BASE}by-code/${code}`);
  return response.data;
};

export const createSite = async (data: SiteCreate): Promise<Site> => {
  const response = await api.post<Site>(BASE, data);
  return response.data;
};

export const updateSite = async (id: string, data: SiteUpdate): Promise<Site> => {
  const response = await api.patch<Site>(`${BASE}${id}`, data);
  return response.data;
};

export const deleteSite = async (id: string): Promise<void> => {
  await api.delete(`${BASE}${id}`);
};

export const getSiteSummary = async (id: string): Promise<SiteSummary> => {
  const response = await api.get<SiteSummary>(`${BASE}${id}/summary`);
  return response.data;
};

export const exportSitesCSV = async (): Promise<void> => {
  const response = await api.get(`${BASE}export/csv`, { responseType: 'blob' });
  const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'sites.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export interface ImportCSVResult {
  created: number;
  updated: number;
  skipped: number;
  errors: string[];
}

export const importSitesCSV = async (file: File): Promise<ImportCSVResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ImportCSVResult>(
    `${BASE}import/csv`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return response.data;
};
