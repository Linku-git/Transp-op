import { api } from './client';
import type {
  TCOCalculateRequest,
  TCOCalculateResponse,
  VehicleReference,
} from '../types/financial';

const FINANCIAL_PATH = '/api/v1/financial';

export const calculateTCO = async (
  request: TCOCalculateRequest,
): Promise<TCOCalculateResponse> => {
  const response = await api.post<TCOCalculateResponse>(
    `${FINANCIAL_PATH}/tco/calculate`,
    request,
  );
  return response.data;
};

export const getVehicleReferences = async (): Promise<VehicleReference[]> => {
  const response = await api.get<VehicleReference[]>(
    `${FINANCIAL_PATH}/vehicles`,
  );
  return response.data;
};
