import { api } from './client';
import type { ReportHistoryResponse } from '@/types/reports';

interface ReportHistoryParams {
  report_type?: string;
  page?: number;
  page_size?: number;
}

export const getReportHistory = async (
  params?: ReportHistoryParams,
): Promise<ReportHistoryResponse> => {
  const response = await api.get<ReportHistoryResponse>(
    '/api/v1/export/history',
    { params },
  );
  return response.data;
};

const ENDPOINT_MAP: Record<string, string> = {
  modal_analysis: '/api/v1/export/modal-report',
  fleet_utilization: '/api/v1/export/fleet-report',
  volunteer_driver: '/api/v1/export/volunteer-report',
  hr_mobility: '/api/v1/export/hr-mobility',
};

export const generateReport = async (
  reportType: string,
  format: string,
): Promise<Blob> => {
  const url = ENDPOINT_MAP[reportType];
  if (!url) {
    throw new Error(`Unsupported report type: ${reportType}`);
  }
  const response = await api.get<Blob>(url, {
    params: { report_format: format },
    responseType: 'blob',
  });
  return response.data;
};
