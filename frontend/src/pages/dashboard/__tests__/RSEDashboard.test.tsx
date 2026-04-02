import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string | Record<string, unknown>) => {
      if (typeof fallback === 'string') return fallback;
      return key;
    },
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockGetRSEKPIs = vi.fn();

vi.mock('@/api/rse', () => ({
  getRSEKPIs: (...args: unknown[]) => mockGetRSEKPIs(...args),
  exportDPEF: vi.fn().mockResolvedValue(new Blob()),
}));

vi.mock('recharts', () => {
  const React = require('react');
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'responsive-container' }, children),
    LineChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'line-chart' }, children),
    BarChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'bar-chart' }, children),
    PieChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'pie-chart' }, children),
    Pie: () => React.createElement('circle'),
    Cell: () => React.createElement('circle'),
    Line: () => React.createElement('line'),
    Bar: () => React.createElement('rect'),
    XAxis: () => React.createElement('g'),
    YAxis: () => React.createElement('g'),
    CartesianGrid: () => React.createElement('g'),
    Tooltip: () => React.createElement('g'),
    Legend: () => React.createElement('g'),
  };
});

import { RSEDashboardPage } from '../RSEDashboardPage';
import { CO2TrendLine } from '@/components/dashboard/CO2TrendLine';
import { ZFEComplianceGauge } from '@/components/dashboard/ZFEComplianceGauge';
import { ModalShiftComparison } from '@/components/dashboard/ModalShiftComparison';
import type { RSEKPIsResponse } from '@/types/rse';

const mockData: RSEKPIsResponse = {
  co2_savings: {
    co2_saved_kg: 15000,
    co2_baseline_kg: 45000,
    co2_actual_kg: 30000,
    co2_saved_pct: 33.3,
    trend: [
      { date: '2026-03-01', co2_saved_kg: 5000 },
      { date: '2026-03-15', co2_saved_kg: 10000 },
    ],
  },
  private_vehicles_avoided: {
    vehicles_avoided: 120,
    total_with_car: 300,
    adoption_pct: 40.0,
  },
  modal_distribution: {
    by_mode: [
      { mode: 'voiture', count: 200, pct: 40 },
      { mode: 'transport_entreprise', count: 150, pct: 30 },
    ],
    soft_pct: 10,
    electric_pct: 5,
    shared_pct: 45,
    individual_pct: 40,
    before_after: {
      before: { voiture: 60, transport_commun: 25, velo: 15 },
      after: { transport_entreprise: 45, voiture: 35, velo: 20 },
    },
  },
  zfe_compliance: {
    compliant_count: 8,
    total_count: 10,
    compliance_pct: 80.0,
  },
};

describe('RSEDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockGetRSEKPIs.mockReturnValue(new Promise(() => {}));
    render(<RSEDashboardPage />);
    expect(screen.getByTestId('rse-loading')).toBeDefined();
  });

  it('renders dashboard content after loading', async () => {
    mockGetRSEKPIs.mockResolvedValue(mockData);
    render(<RSEDashboardPage />);
    await waitFor(() => {
      expect(screen.getByTestId('co2-saved-card')).toBeDefined();
    });
    expect(screen.getByTestId('vehicles-avoided-card')).toBeDefined();
    expect(screen.getByTestId('zfe-compliance-card')).toBeDefined();
    expect(screen.getByTestId('dpef-export-btn')).toBeDefined();
  });
});

describe('CO2TrendLine', () => {
  it('renders SVG line chart with total saved', () => {
    render(
      <CO2TrendLine
        trend={mockData.co2_savings.trend}
        totalSaved={15000}
      />,
    );
    expect(screen.getByTestId('co2-total-saved')).toBeDefined();
    expect(screen.getByTestId('line-chart')).toBeDefined();
  });
});

describe('ZFEComplianceGauge', () => {
  it('shows compliance percentage', () => {
    render(
      <ZFEComplianceGauge
        compliantCount={8}
        totalCount={10}
        compliancePct={80}
      />,
    );
    expect(screen.getByTestId('zfe-gauge')).toBeDefined();
    expect(screen.getByTestId('zfe-pct').textContent).toBe('80%');
  });
});

describe('ModalShiftComparison', () => {
  it('renders before/after bar chart', () => {
    render(
      <ModalShiftComparison
        beforeAfter={mockData.modal_distribution.before_after}
      />,
    );
    expect(screen.getByTestId('modal-shift-comparison')).toBeDefined();
    expect(screen.getByTestId('bar-chart')).toBeDefined();
  });
});

describe('DPEF export button', () => {
  it('is present and clickable', async () => {
    mockGetRSEKPIs.mockResolvedValue(mockData);
    render(<RSEDashboardPage />);
    await waitFor(() => {
      expect(screen.getByTestId('dpef-export-btn')).toBeDefined();
    });
    const btn = screen.getByTestId('dpef-export-btn');
    expect(btn.getAttribute('disabled')).toBeNull();
  });
});
