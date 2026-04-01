import { create } from 'zustand';
import {
  listEmployees as apiListEmployees,
  getEmployee as apiGetEmployee,
  createEmployee as apiCreateEmployee,
  updateEmployee as apiUpdateEmployee,
  deleteEmployee as apiDeleteEmployee,
} from '../api/employees';
import type {
  Employee,
  EmployeeCreate,
  EmployeeListParams,
  EmployeeUpdate,
} from '../types/employee';
import type { AxiosError } from 'axios';
import type { ApiError } from '../types';

interface PaginationMeta {
  page: number;
  pages: number;
  total: number;
  page_size: number;
}

interface EmployeeState {
  employees: Employee[];
  currentEmployee: Employee | null;
  meta: PaginationMeta | null;
  isLoading: boolean;
  error: string | null;

  fetchEmployees: (params?: EmployeeListParams) => Promise<void>;
  fetchEmployee: (id: string) => Promise<void>;
  createEmployee: (data: EmployeeCreate) => Promise<Employee>;
  updateEmployee: (id: string, data: EmployeeUpdate) => Promise<Employee>;
  deleteEmployee: (id: string) => Promise<void>;
  clearError: () => void;
}

const extractErrorMessage = (err: unknown): string => {
  const axiosError = err as AxiosError<ApiError>;
  return axiosError.response?.data?.detail ?? 'An unexpected error occurred';
};

const useEmployeeStore = create<EmployeeState>((set, get) => ({
  employees: [],
  currentEmployee: null,
  meta: null,
  isLoading: false,
  error: null,

  fetchEmployees: async (params?: EmployeeListParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiListEmployees(params);
      set({
        employees: response.data,
        meta: response.meta,
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  fetchEmployee: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const employee = await apiGetEmployee(id);
      set({ currentEmployee: employee, isLoading: false });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
    }
  },

  createEmployee: async (data: EmployeeCreate) => {
    set({ isLoading: true, error: null });
    try {
      const employee = await apiCreateEmployee(data);
      const { employees } = get();
      set({ employees: [...employees, employee], isLoading: false });
      return employee;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  updateEmployee: async (id: string, data: EmployeeUpdate) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiUpdateEmployee(id, data);
      const { employees, currentEmployee } = get();
      set({
        employees: employees.map((e) => (e.id === id ? updated : e)),
        currentEmployee: currentEmployee?.id === id ? updated : currentEmployee,
        isLoading: false,
      });
      return updated;
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  deleteEmployee: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiDeleteEmployee(id);
      const { employees, currentEmployee, meta } = get();
      set({
        employees: employees.filter((e) => e.id !== id),
        currentEmployee: currentEmployee?.id === id ? null : currentEmployee,
        meta: meta ? { ...meta, total: meta.total - 1 } : null,
        isLoading: false,
      });
    } catch (err: unknown) {
      set({ error: extractErrorMessage(err), isLoading: false });
      throw err;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));

export { useEmployeeStore };
