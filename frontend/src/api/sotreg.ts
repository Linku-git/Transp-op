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
  StopGenerateRequest,
  StopGenerateResponse,
  StopCapacityRequest,
  StopCapacityResponse,
  DepotCostEstimateRequest,
  DepotCostEstimateResponse,
  DepotLayoutRequest,
  DepotLayoutResponse,
  NPVRequest,
  NPVResponse,
  InvestmentAnalysisResponse,
  CO2ValorizationRequest,
  CO2ValorizationResponse,
  PortfolioOptimizeRequest,
  PortfolioOptimizeResponse,
  EfficientFrontierResponse,
  SupernetworkLink,
  SupernetworkDemand,
  SupernetworkResponse,
  PaybackResponse,
  TransitionPlanRequest,
  TransitionPlanResponse,
  MCDARequest,
  MCDAResponse,
  SensitivityRequest,
  SensitivityResponse,
  ModalChoiceRequest,
  ModalChoiceResponse,
} from '../types/sotreg';

const LIGNES = '/api/v1/sotreg/lignes';
const CONTEXT = '/api/v1/sotreg/context';
const OD = '/api/v1/sotreg/od-matrix';
const ZFE = '/api/v1/sotreg/zfe';
const TECH = '/api/v1/sotreg/technologies';
const STOPS = '/api/v1/sotreg/stops';
const DEPOT = '/api/v1/sotreg/depot';

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

/* ── Stops (M3) ──────────────────────────────────────────────────────────── */

export const generateStops = async (
  data: StopGenerateRequest = {},
): Promise<StopGenerateResponse> => {
  const response = await api.post<StopGenerateResponse>(`${STOPS}/generate`, data);
  return response.data;
};

export const computeStopCapacity = async (
  data: StopCapacityRequest = {},
): Promise<StopCapacityResponse> => {
  const response = await api.post<StopCapacityResponse>(`${STOPS}/capacity`, data);
  return response.data;
};

/* ── Depot (M3) ──────────────────────────────────────────────────────────── */

export const computeDepotCostEstimate = async (
  data: DepotCostEstimateRequest,
): Promise<DepotCostEstimateResponse> => {
  const response = await api.post<DepotCostEstimateResponse>(`${DEPOT}/cost-estimate`, data);
  return response.data;
};

export const computeDepotLayout = async (
  data: DepotLayoutRequest,
): Promise<DepotLayoutResponse> => {
  const response = await api.post<DepotLayoutResponse>(`${DEPOT}/layout-plan`, data);
  return response.data;
};

/* ── Finance (M5) ────────────────────────────────────────────────────────── */

const FINANCE = '/api/v1/sotreg/finance';

export const computeNPV = async (
  data: NPVRequest,
): Promise<NPVResponse> => {
  const response = await api.post<NPVResponse>(`${FINANCE}/npv`, data);
  return response.data;
};

export const computeInvestmentAnalysis = async (
  data: { cash_flows: number[]; discount_rate?: number; currency?: string },
): Promise<InvestmentAnalysisResponse> => {
  const response = await api.post<InvestmentAnalysisResponse>(`${FINANCE}/investment-analysis`, data);
  return response.data;
};

export const computePayback = async (
  data: { cash_flows: number[]; currency?: string },
): Promise<PaybackResponse> => {
  const response = await api.post<PaybackResponse>(`${FINANCE}/payback`, data);
  return response.data;
};

export const computeCO2Valorization = async (
  data: CO2ValorizationRequest,
): Promise<CO2ValorizationResponse> => {
  const response = await api.post<CO2ValorizationResponse>(`${FINANCE}/co2-valorization`, data);
  return response.data;
};

export const computePortfolioOptimize = async (
  data: PortfolioOptimizeRequest,
): Promise<PortfolioOptimizeResponse> => {
  const response = await api.post<PortfolioOptimizeResponse>(`${FINANCE}/portfolio-optimize`, data);
  return response.data;
};

export const computeEfficientFrontier = async (
  data: { expected_returns: number[]; covariance_matrix: number[][]; n_points?: number; technology_names?: string[] },
): Promise<EfficientFrontierResponse> => {
  const response = await api.post<EfficientFrontierResponse>(`${FINANCE}/efficient-frontier`, data);
  return response.data;
};

export const computeSupernetworkEquilibrium = async (
  data: { links: SupernetworkLink[]; od_demands: SupernetworkDemand[]; max_iterations?: number; tolerance?: number },
): Promise<SupernetworkResponse> => {
  const response = await api.post<SupernetworkResponse>(`${FINANCE}/supernetwork-equilibrium`, data);
  return response.data;
};

/* ── Roadmap (M6) ────────────────────────────────────────────────────────── */

const ROADMAP = '/api/v1/sotreg/roadmap';

export const generateTransitionPlan = async (
  data: TransitionPlanRequest,
): Promise<TransitionPlanResponse> => {
  const response = await api.post<TransitionPlanResponse>(`${ROADMAP}/plan`, data);
  return response.data;
};

/* ── MCDA Scoring (M7) ─────────────────────────────────────────────────── */

const SCORING = '/api/v1/sotreg/scoring';

export const computeMCDA = async (
  data: MCDARequest,
): Promise<MCDAResponse> => {
  const response = await api.post<MCDAResponse>(`${SCORING}/mcda`, data);
  return response.data;
};

export const computeSensitivity = async (
  data: SensitivityRequest,
): Promise<SensitivityResponse> => {
  const response = await api.post<SensitivityResponse>(`${SCORING}/sensitivity`, data);
  return response.data;
};

export const computeModalChoice = async (
  data: ModalChoiceRequest,
): Promise<ModalChoiceResponse> => {
  const response = await api.post<ModalChoiceResponse>(`${SCORING}/modal-choice`, data);
  return response.data;
};

export const downloadMCDAReportPdf = async (
  scenarioId: string,
): Promise<Blob> => {
  const response = await api.post(`${SCORING}/report/pdf/${scenarioId}`, null, {
    responseType: 'blob',
  });
  return response.data as Blob;
};

export const downloadMCDAReportExcel = async (
  scenarioId: string,
): Promise<Blob> => {
  const response = await api.post(`${SCORING}/report/excel/${scenarioId}`, null, {
    responseType: 'blob',
  });
  return response.data as Blob;
};

/* ── ML Model Registry (M8 — Session 123) ─────────────────────────────── */

const ML = '/api/v1/sotreg/ml';

export interface MLModelResponse {
  id: string;
  tenant_id: string;
  model_type: string;
  version: number;
  status: string;
  metrics: Record<string, number> | null;
  file_path: string | null;
  trained_at: string | null;
  feature_names: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface MLModelListResponse {
  data: MLModelResponse[];
  total: number;
}

export interface RetrainResponse {
  model_type: string;
  status: string;
  message: string;
  task_id: string | null;
}

export interface FeatureResponse {
  entity_type: string;
  entity_id: string;
  features: Record<string, number>;
  window: string;
  computed_at: string | null;
}

export const fetchModelRegistry = async (
  modelType?: string,
): Promise<MLModelListResponse> => {
  const params = modelType ? { model_type: modelType } : {};
  const response = await api.get<MLModelListResponse>(`${ML}/models`, { params });
  return response.data;
};

export const triggerRetraining = async (
  modelType: string,
  force = false,
): Promise<RetrainResponse> => {
  const response = await api.post<RetrainResponse>(`${ML}/retrain/${modelType}`, { force });
  return response.data;
};

export const getRetrainingStatus = async (
  taskId: string,
): Promise<{ state: string; progress: number }> => {
  const response = await api.get(`/api/v1/tasks/${taskId}/status`);
  return response.data;
};

export const fetchFeatureImportance = async (
  entityType: string,
  entityId: string,
  window = '24h',
): Promise<FeatureResponse> => {
  const response = await api.get<FeatureResponse>(
    `${ML}/features/${entityType}/${entityId}`,
    { params: { window } },
  );
  return response.data;
};

export const fetchPredictionAccuracy = async (
  ligneId: string,
): Promise<{
  ligne_id: string;
  forecast: number[];
  timestamps: string[];
  metrics: Record<string, number>;
}> => {
  const response = await api.get(`${ML}/forecast/demand/${ligneId}`);
  return response.data;
};

export const promoteModel = async (modelId: string): Promise<void> => {
  await api.post(`${ML}/models/${modelId}/promote`);
};

export const retireModel = async (modelId: string): Promise<void> => {
  await api.post(`${ML}/models/${modelId}/retire`);
};
