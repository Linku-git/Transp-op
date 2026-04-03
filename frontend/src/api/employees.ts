import { api } from './client';
import type { PaginatedResponse } from '../types';
import type {
  Employee,
  EmployeeCreate,
  EmployeeListParams,
  EmployeeSummary,
  EmployeeUpdate,
  CSVUploadResult,
} from '../types/employee';

const BASE_PATH = '/api/v1/employees/';

export const listEmployees = async (
  params: EmployeeListParams = {},
): Promise<PaginatedResponse<Employee>> => {
  const response = await api.get<PaginatedResponse<Employee>>(BASE_PATH, {
    params,
  });
  return response.data;
};

export const getEmployee = async (id: string): Promise<Employee> => {
  const response = await api.get<Employee>(`${BASE_PATH}${id}`);
  return response.data;
};

export const createEmployee = async (
  data: EmployeeCreate,
): Promise<Employee> => {
  const response = await api.post<Employee>(BASE_PATH, data);
  return response.data;
};

export const updateEmployee = async (
  id: string,
  data: EmployeeUpdate,
): Promise<Employee> => {
  const response = await api.patch<Employee>(`${BASE_PATH}${id}`, data);
  return response.data;
};

export const deleteEmployee = async (id: string): Promise<void> => {
  await api.delete(`${BASE_PATH}${id}`);
};

export const uploadEmployeesCSV = async (
  file: File,
): Promise<CSVUploadResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<CSVUploadResult>(
    `${BASE_PATH}upload-csv`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );
  return response.data;
};

export const geocodeEmployees = async (): Promise<{ geocoded: number }> => {
  const response = await api.post<{ geocoded: number }>(
    `${BASE_PATH}geocode`,
  );
  return response.data;
};

export const getEmployeeSummary = async (): Promise<EmployeeSummary> => {
  const response = await api.get<EmployeeSummary>(`${BASE_PATH}summary`);
  return response.data;
};
