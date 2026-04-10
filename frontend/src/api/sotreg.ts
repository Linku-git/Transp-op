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
} from '../types/sotreg';

const LIGNES = '/api/v1/sotreg/lignes';
const CONTEXT = '/api/v1/sotreg/context';
const OD = '/api/v1/sotreg/od-matrix';
const ZFE = '/api/v1/sotreg/zfe';

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
