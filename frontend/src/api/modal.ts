import { api } from './client';
import type {
  EmployeeModal,
  EmployeeModalUpsert,
  ModalStats,
  MobilityScore,
  ShiftModalData,
} from '../types/modal';

const EMPLOYEES_PATH = '/api/v1/employees';
const MODAL_PATH = '/api/v1/modal';

export const getEmployeeModal = async (
  employeeId: string,
): Promise<EmployeeModal> => {
  const response = await api.get<EmployeeModal>(
    `${EMPLOYEES_PATH}/${employeeId}/modal`,
  );
  return response.data;
};

export const upsertEmployeeModal = async (
  employeeId: string,
  data: EmployeeModalUpsert,
): Promise<EmployeeModal> => {
  const response = await api.put<EmployeeModal>(
    `${EMPLOYEES_PATH}/${employeeId}/modal`,
    data,
  );
  return response.data;
};

export const getModalStats = async (
  siteId?: string,
): Promise<ModalStats> => {
  const params = siteId ? { site_id: siteId } : undefined;
  const response = await api.get<ModalStats>(`${MODAL_PATH}/stats`, {
    params,
  });
  return response.data;
};

export const getShiftAnalysis = async (): Promise<ShiftModalData[]> => {
  const response = await api.get<ShiftModalData[]>(
    `${MODAL_PATH}/shift-analysis`,
  );
  return response.data;
};

export const getMobilityScores = async (): Promise<MobilityScore[]> => {
  const response = await api.get<MobilityScore[]>(
    `${MODAL_PATH}/mobility-scores`,
  );
  return response.data;
};
