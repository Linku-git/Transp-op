import { api } from './client';
import type {
  OptimizationSettings,
  ConstraintParam,
  ConstraintCreate,
  ConstraintUpdate,
} from '../types/settings';

const SETTINGS_PATH = '/api/v1/settings';
const CONSTRAINTS_PATH = '/api/v1/constraints';

export const getSettings = async (): Promise<OptimizationSettings> => {
  const response = await api.get<OptimizationSettings>(SETTINGS_PATH);
  return response.data;
};

export const updateSettings = async (
  data: Partial<OptimizationSettings>,
): Promise<OptimizationSettings> => {
  const response = await api.put<OptimizationSettings>(SETTINGS_PATH, data);
  return response.data;
};

export const listConstraints = async (
  category?: string,
): Promise<ConstraintParam[]> => {
  const params: Record<string, string> = {};
  if (category) params.category = category;
  const response = await api.get<ConstraintParam[]>(CONSTRAINTS_PATH, {
    params,
  });
  return response.data;
};

export const createConstraint = async (
  data: ConstraintCreate,
): Promise<ConstraintParam> => {
  const response = await api.post<ConstraintParam>(CONSTRAINTS_PATH, data);
  return response.data;
};

export const updateConstraint = async (
  id: string,
  data: ConstraintUpdate,
): Promise<ConstraintParam> => {
  const response = await api.put<ConstraintParam>(
    `${CONSTRAINTS_PATH}/${id}`,
    data,
  );
  return response.data;
};

export const deleteConstraint = async (id: string): Promise<void> => {
  await api.delete(`${CONSTRAINTS_PATH}/${id}`);
};

export const bulkImportConstraints = async (
  constraints: ConstraintCreate[],
): Promise<ConstraintParam[]> => {
  const response = await api.post<ConstraintParam[]>(
    `${CONSTRAINTS_PATH}/bulk`,
    constraints,
  );
  return response.data;
};
