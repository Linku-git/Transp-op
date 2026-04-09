import { api } from './client';

export interface SIRHConnection {
  id: string;
  tenant_id: string;
  provider: string;
  name: string;
  config: Record<string, unknown> | null;
  sync_frequency: string;
  last_sync_at: string | null;
  status: string;
  conflict_strategy: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SyncLog {
  id: string;
  connection_id: string;
  tenant_id: string;
  started_at: string;
  completed_at: string | null;
  records_created: number;
  records_updated: number;
  records_failed: number;
  errors: string[] | null;
  status: string;
  created_at: string;
}

export interface SyncConflict {
  id: string;
  sync_log_id: string;
  employee_id: string;
  field_name: string;
  platform_value: string | null;
  sirh_value: string | null;
  resolution: string;
}

export interface ConnectionCreate {
  provider: string;
  name: string;
  config?: Record<string, unknown>;
  sync_frequency?: string;
  conflict_strategy?: string;
}

const BASE = '/api/v1/sirh';

export const listConnections = async (): Promise<{ data: SIRHConnection[]; total: number }> => {
  const res = await api.get(`${BASE}/connections`);
  return res.data;
};

export const createConnection = async (data: ConnectionCreate): Promise<SIRHConnection> => {
  const res = await api.post(`${BASE}/connections`, data);
  return res.data;
};

export const deleteConnection = async (id: string): Promise<void> => {
  await api.delete(`${BASE}/connections/${id}`);
};

export const triggerSync = async (connectionId: string): Promise<{ sync_log_id: string; status: string; message: string }> => {
  const res = await api.post(`${BASE}/sync/${connectionId}`);
  return res.data;
};

export const getSyncStatus = async (): Promise<{ data: SyncLog[]; total: number }> => {
  const res = await api.get(`${BASE}/sync/status`);
  return res.data;
};

export const getUnresolvedConflicts = async (): Promise<SyncConflict[]> => {
  const res = await api.get(`${BASE}/sync/conflicts`);
  return res.data;
};

export const resolveConflict = async (
  conflictId: string,
  resolution: string,
  manualValue?: string,
): Promise<SyncConflict> => {
  const res = await api.put(`${BASE}/conflicts/${conflictId}/resolve`, {
    resolution,
    manual_value: manualValue,
  });
  return res.data;
};

export const testConnection = async (connectionId: string): Promise<{ sync_log_id: string; status: string }> => {
  return triggerSync(connectionId);
};
