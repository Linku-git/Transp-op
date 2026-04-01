import { api } from './client';
import type {
  Optimization,
  OptimizationHistoryItem,
  OptimizationRunParams,
  OptimizationStatus,
} from '../types/optimization';

const BASE_PATH = '/api/v1/optimize';

export const launchOptimization = async (
  params: OptimizationRunParams,
): Promise<{ optimization_id: string; status: string; message?: string }> => {
  const response = await api.post<{
    optimization_id: string;
    status: string;
    message?: string;
  }>(BASE_PATH, params);
  return response.data;
};

export const getOptimization = async (id: string): Promise<Optimization> => {
  const response = await api.get<Optimization>(`${BASE_PATH}/${id}`);
  return response.data;
};

export const getOptimizationStatus = async (
  id: string,
): Promise<OptimizationStatus> => {
  const response = await api.get<OptimizationStatus>(
    `${BASE_PATH}/${id}/status`,
  );
  return response.data;
};

export const getLatestOptimization = async (): Promise<Optimization> => {
  const response = await api.get<Optimization>(`${BASE_PATH}/latest/result`);
  return response.data;
};

export const getOptimizationHistory = async (
  siteId?: string,
  page: number = 1,
  pageSize: number = 20,
): Promise<OptimizationHistoryItem[]> => {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (siteId) params.site_id = siteId;
  const response = await api.get<OptimizationHistoryItem[]>(
    `${BASE_PATH}/history/list`,
    { params },
  );
  return response.data;
};
