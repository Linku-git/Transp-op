import { api } from './client';
import type {
  Ligne,
  LigneCreate,
  LigneUpdate,
  LigneListParams,
  LigneListResponse,
  FleetContext,
  ODMatrixComputeRequest,
  ODMatrixComputeResponse,
  ODMatrixListResponse,
  ZFEComplianceResponse,
  ZFEPointCheckResponse,
  RangeCorrectionRequest,
  RangeCorrectionResponse,
  TCO15YearRequest,
  TCO15YearResponse,
  BreakevenRequest,
  BreakevenResponse,
  ChargingOptimizationRequest,
  ChargingOptimizationResponse,
  IRVESizingRequest,
  IRVESizingResponse,
} from '../types/sotreg';

const LIGNES = '/api/v1/sotreg/lignes';
const CONTEXT = '/api/v1/sotreg/context';
const OD = '/api/v1/sotreg/od-matrix';
const ZFE = '/api/v1/sotreg/zfe';
const TECH = '/api/v1/sotreg/technologies';

/* ── Lignes ──────────────────────────────────────────────────────────────── */

export const listLignes = async (
  params: LigneListParams = {},
): Promise<LigneListResponse> => {
  const response = await api.get<LigneListResponse>(LIGNES, { params });
  return response.data;
};

export const getLigne = async (id: string): Promise<Ligne> => {
  const response = await api.get<Ligne>(`${LIGNES}/${id}`);
  return response.data;
};

export const createLigne = async (data: LigneCreate): Promise<Ligne> => {
  const response = await api.post<Ligne>(LIGNES, data);
  return response.data;
};

export const updateLigne = async (
  id: string,
  data: LigneUpdate,
): Promise<Ligne> => {
  const response = await api.put<Ligne>(`${LIGNES}/${id}`, data);
  return response.data;
};

export const deleteLigne = async (id: string): Promise<void> => {
  await api.delete(`${LIGNES}/${id}`);
};

export const geocodeLigne = async (
  ligneId: string,
  data: { origin_address?: string; dest_address?: string },
): Promise<{
  ligne_id: string;
  origin_geocoded: boolean;
  dest_geocoded: boolean;
  origin_lat: number | null;
  origin_lng: number | null;
  dest_lat: number | null;
  dest_lng: number | null;
}> => {
  const response = await api.post(`${LIGNES}/${ligneId}/geocode`, data);
  return response.data;
};

/* ── Fleet Context ───────────────────────────────────────────────────────── */

export const getFleetContextSnapshot = async (): Promise<FleetContext> => {
  const response = await api.get<FleetContext>(`${CONTEXT}/snapshot`);
  return response.data;
};

/* ── OD Matrix ───────────────────────────────────────────────────────────── */

export const computeODMatrix = async (
  data: ODMatrixComputeRequest = {},
): Promise<ODMatrixComputeResponse> => {
  const response = await api.post<ODMatrixComputeResponse>(`${OD}/compute`, data);
  return response.data;
};

export const listODMatrix = async (): Promise<ODMatrixListResponse> => {
  const response = await api.get<ODMatrixListResponse>(OD);
  return response.data;
};

export const getODMatrixForLigne = async (
  ligneId: string,
): Promise<ODMatrixListResponse> => {
  const response = await api.get<ODMatrixListResponse>(`${OD}/${ligneId}`);
  return response.data;
};

/* ── ZFE ─────────────────────────────────────────────────────────────────── */

export const getZFECompliance = async (): Promise<ZFEComplianceResponse> => {
  const response = await api.get<ZFEComplianceResponse>(`${ZFE}/lignes`);
  return response.data;
};

export const checkZFEPoint = async (
  lat: number,
  lng: number,
): Promise<ZFEPointCheckResponse> => {
  const response = await api.post<ZFEPointCheckResponse>(`${ZFE}/check`, { lat, lng });
  return response.data;
};

/* ── Technologies (M2) ───────────────────────────────────────────────────── */

export const computeRangeCorrection = async (
  data: RangeCorrectionRequest,
): Promise<RangeCorrectionResponse> => {
  const response = await api.post<RangeCorrectionResponse>(`${TECH}/range-correction`, data);
  return response.data;
};

export const computeTCO15Year = async (
  data: TCO15YearRequest,
): Promise<TCO15YearResponse> => {
  const response = await api.post<TCO15YearResponse>(`${TECH}/tco-15year`, data);
  return response.data;
};

export const computeBreakeven = async (
  data: BreakevenRequest,
): Promise<BreakevenResponse> => {
  const response = await api.post<BreakevenResponse>(`${TECH}/breakeven`, data);
  return response.data;
};

export const computeChargingOptimization = async (
  data: ChargingOptimizationRequest,
): Promise<ChargingOptimizationResponse> => {
  const response = await api.post<ChargingOptimizationResponse>(`${TECH}/charging-optimization`, data);
  return response.data;
};

export const computeIRVESizing = async (
  data: IRVESizingRequest,
): Promise<IRVESizingResponse> => {
  const response = await api.post<IRVESizingResponse>(`${TECH}/irve-sizing`, data);
  return response.data;
};
