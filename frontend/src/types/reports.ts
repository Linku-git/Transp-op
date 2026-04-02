export interface GeneratedReport {
  id: string;
  report_type: string;
  format: string | null;
  params: Record<string, unknown>;
  file_url: string | null;
  generated_at: string | null;
  generated_by: string | null;
}

export interface ReportHistoryResponse {
  data: GeneratedReport[];
  total: number;
  page: number;
  pages: number;
}

export const REPORT_TYPES = [
  { key: 'modal_analysis', label: 'Analyse modale', icon: 'pie_chart' },
  { key: 'fleet_utilization', label: 'Utilisation flotte', icon: 'directions_bus' },
  { key: 'volunteer_driver', label: 'Conducteurs volontaires', icon: 'person' },
  { key: 'hr_mobility', label: 'Mobilite RH', icon: 'groups' },
  { key: 'financial_tco', label: 'TCO Financier', icon: 'account_balance' },
  { key: 'financial_roi', label: 'ROI Financier', icon: 'trending_up' },
  { key: 'rse_dpef', label: 'DPEF/RSE', icon: 'eco' },
] as const;

export type ReportTypeKey = (typeof REPORT_TYPES)[number]['key'];

export const REPORT_FORMATS = ['pdf', 'xlsx'] as const;

export type ReportFormat = (typeof REPORT_FORMATS)[number];
