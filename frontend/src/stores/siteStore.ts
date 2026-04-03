import { create } from 'zustand';
import {
  listSites as apiListSites,
  getSite as apiGetSite,
  createSite as apiCreateSite,
  updateSite as apiUpdateSite,
  deleteSite as apiDeleteSite,
} from '../api/sites';
import type { Site, SiteCreate, SiteListParams, SiteUpdate } from '../types/site';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

interface PaginationMeta {
  page: number;
  pages: number;
  total: number;
  page_size: number;
}

interface SiteState {
  sites: Site[];
  currentSite: Site | null;
  meta: PaginationMeta | null;
  isLoading: boolean;
  error: string | null;

  fetchSites: (params?: SiteListParams) => Promise<void>;
  fetchSite: (id: string) => Promise<void>;
  createSite: (data: SiteCreate) => Promise<Site>;
  updateSite: (id: string, data: SiteUpdate) => Promise<Site>;
  deleteSite: (id: string) => Promise<void>;
  clearError: () => void;
}

const extractErrorMessage = (err: unknown): string => {
  const axiosError = err as AxiosError<ApiError>;
  const detail = axiosError.response?.data?.detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join('; ');
  }
  if (typeof detail === 'string' && detail.length > 0) return detail;
  return 'An unexpected error occurred';
};

const useSiteStore = create<SiteState>((set, get) => ({
  sites: [],
  currentSite: null,
  meta: null,
  isLoading: false,
  error: null,

  fetchSites: async (params?: SiteListParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiListSites(params);
      set({
        sites: response.data,
        meta: response.meta,
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  fetchSite: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const site = await apiGetSite(id);
      set({ currentSite: site, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  createSite: async (data: SiteCreate) => {
    set({ isLoading: true, error: null });
    try {
      const site = await apiCreateSite(data);
      const { sites } = get();
      set({ sites: [...sites, site], isLoading: false });
      return site;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  updateSite: async (id: string, data: SiteUpdate) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiUpdateSite(id, data);
      const { sites, currentSite } = get();
      set({
        sites: sites.map((s) => (s.id === id ? updated : s)),
        currentSite: currentSite?.id === id ? updated : currentSite,
        isLoading: false,
      });
      return updated;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  deleteSite: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiDeleteSite(id);
      const { sites, currentSite, meta } = get();
      set({
        sites: sites.filter((s) => s.id !== id),
        currentSite: currentSite?.id === id ? null : currentSite,
        meta: meta ? { ...meta, total: meta.total - 1 } : null,
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

export { useSiteStore };
