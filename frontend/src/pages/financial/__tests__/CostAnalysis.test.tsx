import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/api/financial', () => ({
  calculateTCO: vi.fn().mockResolvedValue({}),
  getVehicleReferences: vi.fn().mockResolvedValue([]),
  calculateROI: vi.fn().mockResolvedValue({}),
  compareInvestments: vi.fn().mockResolvedValue({ models: [], recommendation: { recommended_model: '', reason: '' } }),
  calculateCostAnalysis: vi.fn().mockResolvedValue({}),
}));

// Mock recharts to render simple SVG elements
vi.mock('recharts', () => {
  const React = require('react');
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'responsive-container' }, children),
    LineChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'line-chart' }, children),
    Line: () => React.createElement('line'),
    XAxis: () => React.createElement('g'),
    YAxis: () => React.createElement('g'),
    CartesianGrid: () => React.createElement('g'),
    Tooltip: () => React.createElement('g'),
    Legend: () => React.createElement('g'),
    ReferenceLine: () => React.createElement('line'),
  };
});

import type { BreakevenPoint } from '@/types/financial';

const mockChartData: BreakevenPoint[] = [
  { employees: 1, transport_cost_per_employee: 120000, allowance_cost_per_employee: 1650 },
  { employees: 50, transport_cost_per_employee: 2400, allowance_cost_per_employee: 1650 },
  { employees: 73, transport_cost_per_employee: 1644, allowance_cost_per_employee: 1650 },
  { employees: 100, transport_cost_per_employee: 1200, allowance_cost_per_employee: 1650 },
];

describe('CostAnalysisPanel', () => {
  it('renders form with vehicle capacity and annual cost inputs', async () => {
    const { CostAnalysisPanel } = await import(
      '@/components/financial/CostAnalysisPanel'
    );
    render(<CostAnalysisPanel />);

    expect(screen.getByTestId('cost-analysis-panel')).toBeInTheDocument();
    expect(screen.getByLabelText(/Capacite vehicule/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Cout annuel des lignes/i)).toBeInTheDocument();
  });
});

describe('BreakevenChart', () => {
  it('renders with mock data and SVG exists', async () => {
    const { BreakevenChart } = await import(
      '@/components/financial/BreakevenChart'
    );
    render(<BreakevenChart data={mockChartData} breakevenEmployees={73} />);

    expect(screen.getByTestId('breakeven-chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
});
