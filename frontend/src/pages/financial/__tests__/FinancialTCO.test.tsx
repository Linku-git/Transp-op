import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockCalculateTCO = vi.fn();

vi.mock('@/api/financial', () => ({
  calculateTCO: (...args: unknown[]) => mockCalculateTCO(...args),
  getVehicleReferences: vi.fn().mockResolvedValue([]),
}));

// Mock recharts to render a simple SVG
vi.mock('recharts', () => {
  const React = require('react');
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'responsive-container' }, children),
    LineChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'line-chart' }, children),
    BarChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'bar-chart' }, children),
    Line: () => React.createElement('line'),
    Bar: () => React.createElement('rect'),
    XAxis: () => React.createElement('g'),
    YAxis: () => React.createElement('g'),
    CartesianGrid: () => React.createElement('g'),
    Tooltip: () => React.createElement('g'),
    Legend: () => React.createElement('g'),
  };
});

import type {
  TCOVehicleResult,
  TCOYearlyPoint,
  TCOMotorizationComparison,
  TCOFleetResult,
  TCOCalculateResponse,
} from '@/types/financial';

const mockVehicle: TCOVehicleResult = {
  vehicle_type: 'minibus',
  motorization: 'diesel',
  purchase_price: 400000,
  annual_maintenance_cost: 20000,
  energy_cost_per_km: 1.2,
  annual_km: 30000,
  residual_value: 80000,
  duration_years: 5,
  quantity: 3,
  maintenance_total: 300000,
  energy_total: 180000,
  tco_per_vehicle: 320000,
  tco_total: 960000,
};

const mockVehicle2: TCOVehicleResult = {
  ...mockVehicle,
  vehicle_type: 'midibus',
  motorization: 'electric',
  tco_per_vehicle: 280000,
  tco_total: 840000,
};

const mockVehicle3: TCOVehicleResult = {
  ...mockVehicle,
  vehicle_type: 'bus_standard',
  motorization: 'hybrid',
  tco_per_vehicle: 350000,
  tco_total: 1050000,
};

const mockFleetResult: TCOFleetResult = {
  duration_years: 5,
  vehicles: [mockVehicle, mockVehicle2, mockVehicle3],
  fleet_tco_total: 2850000,
  vehicle_count: 9,
};

const mockEvolution: TCOYearlyPoint[] = [
  { year: 1, fleet_tco_total: 1200000 },
  { year: 2, fleet_tco_total: 1600000 },
  { year: 3, fleet_tco_total: 2000000 },
  { year: 4, fleet_tco_total: 2400000 },
  { year: 5, fleet_tco_total: 2850000 },
];

const mockComparisons: TCOMotorizationComparison[] = [
  {
    vehicle_type: 'minibus',
    motorizations: [
      {
        motorization: 'diesel',
        tco_per_vehicle: 320000,
        tco_total: 960000,
        purchase_price: 400000,
        annual_maintenance_cost: 20000,
        energy_cost_per_km: 1.2,
        annual_km: 30000,
        residual_value: 80000,
        duration_years: 5,
        quantity: 3,
        maintenance_total: 300000,
        energy_total: 180000,
      },
      {
        motorization: 'electric',
        tco_per_vehicle: 280000,
        tco_total: 840000,
        purchase_price: 600000,
        annual_maintenance_cost: 10000,
        energy_cost_per_km: 0.5,
        annual_km: 30000,
        residual_value: 120000,
        duration_years: 5,
        quantity: 3,
        maintenance_total: 150000,
        energy_total: 75000,
      },
    ],
  },
];

const mockResponse: TCOCalculateResponse = {
  fleet_tco: mockFleetResult,
  evolution: mockEvolution,
  motorization_comparisons: mockComparisons,
};

describe('TCOCalculatorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockCalculateTCO.mockResolvedValue(mockResponse);
  });

  it('renders with form inputs and calculate button', async () => {
    const { TCOCalculatorPage } = await import('../TCOCalculatorPage');
    render(<TCOCalculatorPage />);

    expect(screen.getByText('Calculateur TCO')).toBeInTheDocument();
    expect(screen.getByTestId('vehicle-type-select')).toBeInTheDocument();
    expect(screen.getByTestId('calculate-button')).toBeInTheDocument();
  });

  it('submits form and displays results', async () => {
    const { TCOCalculatorPage } = await import('../TCOCalculatorPage');
    render(<TCOCalculatorPage />);

    const calcButton = screen.getByTestId('calculate-button');
    fireEvent.click(calcButton);

    await waitFor(() => {
      expect(mockCalculateTCO).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(screen.getByTestId('tco-results')).toBeInTheDocument();
    });
  });
});

describe('TCOComparisonCards', () => {
  it('renders correct number of cards', async () => {
    const { TCOComparisonCards } = await import(
      '@/components/financial/TCOComparisonCards'
    );
    render(
      <TCOComparisonCards
        vehicles={[mockVehicle, mockVehicle2, mockVehicle3]}
      />,
    );

    const cards = screen.getAllByTestId('tco-comparison-card');
    expect(cards).toHaveLength(3);
  });
});

describe('TCOEvolutionChart', () => {
  it('renders chart container', async () => {
    const { TCOEvolutionChart } = await import(
      '@/components/financial/TCOEvolutionChart'
    );
    render(<TCOEvolutionChart data={mockEvolution} />);

    expect(screen.getByTestId('tco-evolution-chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
});

describe('MotorizationTable', () => {
  it('renders rows for each motorization', async () => {
    const { MotorizationTable } = await import(
      '@/components/financial/MotorizationTable'
    );
    render(<MotorizationTable comparisons={mockComparisons} />);

    expect(screen.getByTestId('motorization-table')).toBeInTheDocument();
    const rows = screen.getAllByTestId('motorization-row');
    expect(rows).toHaveLength(2);
  });
});

describe('VehicleTCOBreakdown', () => {
  it('renders bar chart', async () => {
    const { VehicleTCOBreakdown } = await import(
      '@/components/financial/VehicleTCOBreakdown'
    );
    render(
      <VehicleTCOBreakdown
        vehicles={[mockVehicle, mockVehicle2, mockVehicle3]}
      />,
    );

    expect(screen.getByTestId('vehicle-tco-breakdown')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });
});

describe('FleetAggregation', () => {
  it('displays fleet total', async () => {
    const { FleetAggregation } = await import(
      '@/components/financial/FleetAggregation'
    );
    render(<FleetAggregation fleetResult={mockFleetResult} />);

    expect(screen.getByTestId('fleet-aggregation')).toBeInTheDocument();
    expect(screen.getByTestId('fleet-tco-total')).toBeInTheDocument();
    // Check the total is displayed (formatted as MAD)
    expect(screen.getByTestId('fleet-tco-total').textContent).toContain(
      '2',
    );
  });
});
