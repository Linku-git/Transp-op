import { api } from './client';
import type {
  Vehicle,
  VehicleCreate,
  VehicleListParams,
  VehicleUpdate,
  KmConsommation,
  KmConsommationCreate,
  KmConsommationUpdate,
  PointArret,
  PointArretCreate,
  PointArretUpdate,
  ConfigurationTransport,
  ConfigurationTransportCreate,
  ConfigurationTransportUpdate,
} from '../types/vehicle';

interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Vehicles ────────────────────────────────────────────────────────────────

const V_PATH = '/api/v1/vehicles';

export const listVehicles = async (params: VehicleListParams = {}): Promise<ListResponse<Vehicle>> => {
  const response = await api.get<ListResponse<Vehicle>>(V_PATH, { params });
  return response.data;
};

export const getVehicle = async (id: string): Promise<Vehicle> => {
  const response = await api.get<Vehicle>(`${V_PATH}/${id}`);
  return response.data;
};

export const createVehicle = async (data: VehicleCreate): Promise<Vehicle> => {
  const response = await api.post<Vehicle>(V_PATH, data);
  return response.data;
};

export const updateVehicle = async (id: string, data: VehicleUpdate): Promise<Vehicle> => {
  const response = await api.patch<Vehicle>(`${V_PATH}/${id}`, data);
  return response.data;
};

export const deleteVehicle = async (id: string): Promise<void> => {
  await api.delete(`${V_PATH}/${id}`);
};

// ─── Km & Consommation ───────────────────────────────────────────────────────

const KC_PATH = '/api/v1/km-consommation';

export const listKmConsommation = async (params?: Record<string, unknown>): Promise<ListResponse<KmConsommation>> => {
  const response = await api.get<ListResponse<KmConsommation>>(KC_PATH, { params });
  return response.data;
};

export const createKmConsommation = async (data: KmConsommationCreate): Promise<KmConsommation> => {
  const response = await api.post<KmConsommation>(KC_PATH, data);
  return response.data;
};

export const updateKmConsommation = async (id: string, data: KmConsommationUpdate): Promise<KmConsommation> => {
  const response = await api.patch<KmConsommation>(`${KC_PATH}/${id}`, data);
  return response.data;
};

export const deleteKmConsommation = async (id: string): Promise<void> => {
  await api.delete(`${KC_PATH}/${id}`);
};

// ─── Points Arrêt ────────────────────────────────────────────────────────────

const PA_PATH = '/api/v1/points-arret';

export const listPointsArret = async (params?: Record<string, unknown>): Promise<ListResponse<PointArret>> => {
  const response = await api.get<ListResponse<PointArret>>(PA_PATH, { params });
  return response.data;
};

export const createPointArret = async (data: PointArretCreate): Promise<PointArret> => {
  const response = await api.post<PointArret>(PA_PATH, data);
  return response.data;
};

export const updatePointArret = async (id: string, data: PointArretUpdate): Promise<PointArret> => {
  const response = await api.patch<PointArret>(`${PA_PATH}/${id}`, data);
  return response.data;
};

export const deletePointArret = async (id: string): Promise<void> => {
  await api.delete(`${PA_PATH}/${id}`);
};

// ─── Configuration Transport ─────────────────────────────────────────────────

const CT_PATH = '/api/v1/configuration-transport';

export const listConfigurationTransport = async (params?: Record<string, unknown>): Promise<ListResponse<ConfigurationTransport>> => {
  const response = await api.get<ListResponse<ConfigurationTransport>>(CT_PATH, { params });
  return response.data;
};

export const createConfigurationTransport = async (data: ConfigurationTransportCreate): Promise<ConfigurationTransport> => {
  const response = await api.post<ConfigurationTransport>(CT_PATH, data);
  return response.data;
};

export const updateConfigurationTransport = async (id: string, data: ConfigurationTransportUpdate): Promise<ConfigurationTransport> => {
  const response = await api.patch<ConfigurationTransport>(`${CT_PATH}/${id}`, data);
  return response.data;
};

export const deleteConfigurationTransport = async (id: string): Promise<void> => {
  await api.delete(`${CT_PATH}/${id}`);
};
