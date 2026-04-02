import { api } from './client';
import type { RSEKPIsResponse } from '../types/rse';

const BASE_PATH = '/api/v1/kpis/rse';

export const getRSEKPIs = async (): Promise<RSEKPIsResponse> => {
  const response = await api.get<RSEKPIsResponse>(BASE_PATH);
  return response.data;
};

export const exportDPEF = async (): Promise<Blob> => {
  const response = await api.post(`${BASE_PATH}/dpef`, {}, { responseType: 'blob' });
  return response.data as Blob;
};
