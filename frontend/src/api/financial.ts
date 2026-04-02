import { api } from './client';
import type {
  TCOCalculateRequest,
  TCOCalculateResponse,
  VehicleReference,
  ROICalculateRequest,
  ROICalculateResponse,
  InvestmentCompareRequest,
  InvestmentCompareResponse,
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

export const calculateROI = async (
  request: ROICalculateRequest,
): Promise<ROICalculateResponse> => {
  const response = await api.post<ROICalculateResponse>(
    `${FINANCIAL_PATH}/roi/calculate`,
    request,
  );
  return response.data;
};

export const compareInvestments = async (
  request: InvestmentCompareRequest,
): Promise<InvestmentCompareResponse> => {
  const response = await api.post<InvestmentCompareResponse>(
    `${FINANCIAL_PATH}/compare`,
    request,
  );
  return response.data;
};
