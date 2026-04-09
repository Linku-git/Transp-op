import { api } from './client';

export interface OperatorSizingPlan {
  id: string;
  version: number;
  format: string;
  status: string;
  file_url: string | null;
  content_summary: Record<string, number> | null;
  acknowledged: boolean;
  acknowledged_at: string | null;
  created_at: string;
}

export interface ServiceIssueCreate {
  issue_type: string;
  description: string;
  affected_route?: string;
  incident_date?: string;
}

const BASE = '/api/v1/operator';

export const listSizingPlans = async (): Promise<{ data: OperatorSizingPlan[]; total: number }> => {
  const res = await api.get(`${BASE}/sizing-plans`);
  return res.data;
};

export const getSizingPlan = async (id: string): Promise<OperatorSizingPlan> => {
  const res = await api.get(`${BASE}/sizing-plans/${id}`);
  return res.data;
};

export const acknowledgePlan = async (id: string): Promise<{ acknowledged: boolean }> => {
  const res = await api.post(`${BASE}/sizing-plans/${id}/acknowledge`);
  return res.data;
};

export const reportServiceIssue = async (data: ServiceIssueCreate): Promise<{ id: string }> => {
  const res = await api.post(`${BASE}/service-issues`, data);
  return res.data;
};
