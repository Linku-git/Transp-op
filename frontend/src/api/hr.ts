import { api } from './client';
import type { HRKPIsResponse } from '../types/hr';

const BASE_PATH = '/api/v1/kpis/hr';

export const getHRKPIs = async (): Promise<HRKPIsResponse> => {
  const response = await api.get<HRKPIsResponse>(BASE_PATH);
  return response.data;
};
