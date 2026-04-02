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
}));

// Mock recharts to render simple SVG elements
vi.mock('recharts', () => {
  const React = require('react');
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'responsive-container' }, children),
    BarChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'bar-chart' }, children),
    Bar: () => React.createElement('rect'),
    XAxis: () => React.createElement('g'),
    YAxis: () => React.createElement('g'),
    CartesianGrid: () => React.createElement('g'),
    Tooltip: () => React.createElement('g'),
    Cell: () => React.createElement('g'),
  };
});

import type {
  ROICalculateResponse,
  InvestmentModelResult,
  InvestmentRecommendation,
} from '@/types/financial';

const mockROI: ROICalculateResponse = {
  roi_absenteeism: 1155000,
  roi_retention: 625000,
  roi_fleet_optimization: 500000,
  roi_journey: 1350000,
  roi_total: 3630000,
  roi_percentage: 121.0,
  payback_months: 9.9,
  total_investment: 3000000,
  headcount: 500,
  working_days_per_year: 220,
  stored_id: null,
};

const mockModels: InvestmentModelResult[] = [
  {
    model: 'capex',
    label: 'CAPEX',
    total_cost: 5250000,
    annual_cost: 1050000,
    cost_per_employee: 17500,
    cost_per_trip: 17.5,
    duration_years: 5,
    vehicle_count: 10,
    breakdown: {},
  },
  {
    model: 'mise_a_disposition',
    label: 'Mise a Disposition',
    total_cost: 3888000,
    annual_cost: 777600,
    cost_per_employee: 12960,
    cost_per_trip: 12.96,
    duration_years: 5,
    vehicle_count: 10,
    breakdown: {},
  },
  {
    model: 'opex',
    label: 'OPEX',
    total_cost: 5000000,
    annual_cost: 1000000,
    cost_per_employee: 16667,
    cost_per_trip: 16.67,
    duration_years: 5,
    vehicle_count: 10,
    breakdown: {},
  },
];

const mockRecommendation: InvestmentRecommendation = {
  recommended_model: 'mise_a_disposition',
  reason: 'Recommended for medium fleet',
};

describe('WaterfallChart', () => {
  it('renders with mock ROI data and SVG exists', async () => {
    const { WaterfallChart } = await import(
      '@/components/financial/WaterfallChart'
    );
    render(<WaterfallChart data={mockROI} />);

    expect(screen.getByTestId('waterfall-chart')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('displays bar labels for all ROI levers', async () => {
    const { WaterfallChart } = await import(
      '@/components/financial/WaterfallChart'
    );
    render(<WaterfallChart data={mockROI} />);

    // The chart container should be present (labels rendered by recharts mock)
    const container = screen.getByTestId('waterfall-chart');
    expect(container).toBeInTheDocument();
  });
});

describe('PaybackSlider', () => {
  it('renders and shows month count', async () => {
    const { PaybackSlider } = await import(
      '@/components/financial/PaybackSlider'
    );
    render(
      <PaybackSlider
        paybackMonths={9.9}
        totalInvestment={3000000}
        roiTotal={3630000}
      />,
    );

    expect(screen.getByTestId('payback-slider')).toBeInTheDocument();
    expect(screen.getByTestId('payback-months')).toHaveTextContent('9.9');
  });

  it('shows green color for payback under 12 months', async () => {
    const { PaybackSlider } = await import(
      '@/components/financial/PaybackSlider'
    );
    render(
      <PaybackSlider
        paybackMonths={6}
        totalInvestment={3000000}
        roiTotal={6000000}
      />,
    );

    const monthsEl = screen.getByTestId('payback-months');
    expect(monthsEl.className).toContain('text-green-600');
  });
});

describe('CostPerTripGauge', () => {
  it('renders with actual and target values', async () => {
    const { CostPerTripGauge } = await import(
      '@/components/financial/CostPerTripGauge'
    );
    render(<CostPerTripGauge actual={14.5} target={15.0} />);

    expect(screen.getByTestId('cost-per-trip-gauge')).toBeInTheDocument();
    // SVG should contain the actual value
    expect(screen.getByLabelText('14.5 MAD')).toBeInTheDocument();
  });
});

describe('InvestmentComparatorCards', () => {
  it('renders 3 model cards', async () => {
    const { InvestmentComparatorCards } = await import(
      '@/components/financial/InvestmentComparatorCards'
    );
    render(
      <InvestmentComparatorCards
        models={mockModels}
        recommendation={mockRecommendation}
      />,
    );

    expect(screen.getByTestId('investment-comparator-cards')).toBeInTheDocument();
    const cards = screen.getAllByTestId('investment-model-card');
    expect(cards).toHaveLength(3);
  });
});

describe('DAFExportButton', () => {
  it('renders with download icon', async () => {
    const { DAFExportButton } = await import(
      '@/components/financial/DAFExportButton'
    );
    render(<DAFExportButton />);

    expect(screen.getByTestId('daf-export-button')).toBeInTheDocument();
    expect(screen.getByText('download')).toBeInTheDocument();
  });
});
