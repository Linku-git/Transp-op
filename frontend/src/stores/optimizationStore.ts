import { create } from 'zustand';
import type {
  Optimization,
  OptimizationHistoryItem,
  OptimizationRunParams,
  OptimizationStatus,
  LayerVisibility,
} from '../types/optimization';
import {
  launchOptimization as apiLaunch,
  getOptimization as apiGetOptimization,
  getOptimizationStatus as apiGetStatus,
  getLatestOptimization as apiGetLatest,
  getOptimizationHistory as apiGetHistory,
} from '../api/optimization';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

interface OptimizationState {
  current: Optimization | null;
  status: OptimizationStatus | null;
  history: OptimizationHistoryItem[];

  isLoading: boolean;
  isRunning: boolean;
  error: string | null;

  layers: LayerVisibility;
  selectedRouteId: string | null;

  launch: (params: OptimizationRunParams) => Promise<void>;
  fetchResult: (id: string) => Promise<void>;
  fetchLatest: () => Promise<void>;
  fetchHistory: (siteId?: string) => Promise<void>;
  pollStatus: (id: string) => Promise<void>;
  toggleLayer: (layer: keyof LayerVisibility) => void;
  selectRoute: (routeId: string | null) => void;
  clearError: () => void;
}

const extractErrorMessage = (err: unknown): string => {
  const axiosError = err as AxiosError<ApiError>;
  const detail = axiosError.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join('; ');
  }
  if (typeof detail === 'string') return detail;
  return 'An unexpected error occurred';
};

const useOptimizationStore = create<OptimizationState>((set, get) => ({
  current: null,
  status: null,
  history: [],
  isLoading: false,
  isRunning: false,
  error: null,
  layers: {
    employees: true,
    clusters: true,
    routes: true,
    meetingZones: true,
    accessLegs: false,
    siteMarker: true,
  },
  selectedRouteId: null,

  launch: async (params) => {
    set({ isRunning: true, error: null });
    try {
      const result = await apiLaunch(params);
      set({
        status: {
          optimization_id: result.optimization_id,
          status: result.status,
          progress: 0,
          step: 'Started',
          error: null,
        },
      });

      const id = result.optimization_id;
      const poll = setInterval(async () => {
        try {
          const s = await apiGetStatus(id);
          set({ status: s });
          if (s.status === 'completed' || s.status === 'failed') {
            clearInterval(poll);
            set({ isRunning: false });
            if (s.status === 'completed') {
              await get().fetchResult(id);
            } else if (s.error) {
              set({ error: s.error });
            }
          }
        } catch {
          clearInterval(poll);
          set({ isRunning: false });
        }
      }, 2000);
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isRunning: false });
    }
  },

  fetchResult: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiGetOptimization(id);
      set({ current: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  fetchLatest: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiGetLatest();
      set({ current: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  fetchHistory: async (siteId?) => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiGetHistory(siteId);
      set({ history: data, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  pollStatus: async (id) => {
    try {
      const s = await apiGetStatus(id);
      set({ status: s });
    } catch {
      // Silent — polling failures should not surface errors
    }
  },

  toggleLayer: (layer) => {
    set((state) => ({
      layers: { ...state.layers, [layer]: !state.layers[layer] },
    }));
  },

  selectRoute: (routeId) => set({ selectedRouteId: routeId }),

  clearError: () => {
    set({ error: null });
  },
}));

export { useOptimizationStore };
