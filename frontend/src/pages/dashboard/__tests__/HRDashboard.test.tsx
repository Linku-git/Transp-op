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

const mockGetHRKPIs = vi.fn();

vi.mock('@/api/hr', () => ({
  getHRKPIs: (...args: unknown[]) => mockGetHRKPIs(...args),
}));

vi.mock('recharts', () => {
  const React = require('react');
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) =>
      React.createElement('div', { 'data-testid': 'responsive-container' }, children),
    LineChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'line-chart' }, children),
    ScatterChart: ({ children }: { children: React.ReactNode }) =>
      React.createElement('svg', { 'data-testid': 'scatter-chart' }, children),
    Line: () => React.createElement('line'),
    Scatter: () => React.createElement('circle'),
    XAxis: () => React.createElement('g'),
    YAxis: () => React.createElement('g'),
    CartesianGrid: () => React.createElement('g'),
    Tooltip: () => React.createElement('g'),
    Legend: () => React.createElement('g'),
  };
});

import { HRDashboardPage } from '../HRDashboardPage';
import { HeatmapTable } from '@/components/charts/HeatmapTable';
import { ScatterPlot } from '@/components/charts/ScatterPlot';
import { RetentionImpactCard } from '@/components/dashboard/RetentionImpactCard';
import { ShadowZonesList } from '@/components/dashboard/ShadowZonesList';
import { MobilityAlerts } from '@/components/dashboard/MobilityAlerts';
import type {
  HRKPIsResponse,
  MobilityCoverage,
  ShadowZones,
  RetentionImpact,
} from '@/types/hr';

const mockData: HRKPIsResponse = {
  mobility_coverage: {
    total_employees: 500,
    covered_employees: 350,
    coverage_pct: 70.0,
    by_site: [
      { name: 'Site A', total: 200, covered: 150, pct: 75.0 },
      { name: 'Site B', total: 300, covered: 200, pct: 66.7 },
    ],
    by_shift: [{ name: '08:00', total: 300, covered: 220, pct: 73.3 }],
    by_department: [{ name: 'Engineering', total: 100, covered: 80, pct: 80.0 }],
  },
  mobility_score_evolution: [
    { date: '2026-03-01T10:00:00', site_id: 'uuid1', occupancy_pct: 78, co2_kg: 150, score: 85.0 },
    { date: '2026-03-15T10:00:00', site_id: 'uuid1', occupancy_pct: 80, co2_kg: 140, score: 88.0 },
  ],
  absenteeism_correlation: {
    with_transport: { employee_count: 200, total_leave_days: 400, avg_absence_days: 2.0, absence_rate_pct: 0.91 },
    without_transport: { employee_count: 150, total_leave_days: 500, avg_absence_days: 3.3, absence_rate_pct: 1.52 },
    maybe_transport: { employee_count: 100, total_leave_days: 250, avg_absence_days: 2.5, absence_rate_pct: 1.14 },
    correlation: { delta_pct: 0.61, interpretation: 'Transport reduit l\'absenteisme' },
  },
  retention_impact: {
    total_employees: 500,
    departed_total: 40,
    departed_with_transport: 10,
    departed_without_transport: 30,
    turnover_rate_pct: 8.0,
    avg_replacement_cost: 25000,
    estimated_annual_savings: 225000,
  },
  shadow_zones: {
    shadow_zone_count: 35,
    total_active_employees: 500,
    shadow_zone_pct: 7.0,
    threshold_km: 30,
    employees: [
      { id: 'emp1', name: 'John Doe', quartier: 'Q1', city: 'Casablanca', distance_km: 45, primary_mode: 'voiture' },
      { id: 'emp2', name: 'Jane Smith', quartier: 'Q2', city: 'Rabat', distance_km: 38, primary_mode: 'bus' },
    ],
  },
};

describe('HRDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockGetHRKPIs.mockReturnValue(new Promise(() => {}));
    render(<HRDashboardPage />);
    expect(screen.getByTestId('hr-loading')).toBeDefined();
  });

  it('renders dashboard content after loading', async () => {
    mockGetHRKPIs.mockResolvedValue(mockData);
    render(<HRDashboardPage />);
    await waitFor(() => {
      expect(screen.getByTestId('coverage-pct')).toBeDefined();
    });
    expect(screen.getByText('70.0%')).toBeDefined();
  });
});

describe('HeatmapTable', () => {
  it('displays coverage data with color coding', () => {
    const data = [
      { name: 'Site A', total: 200, covered: 150, pct: 75.0 },
      { name: 'Site B', total: 100, covered: 30, pct: 30.0 },
      { name: 'Site C', total: 100, covered: 60, pct: 60.0 },
    ];
    render(<HeatmapTable data={data} title="Test Heatmap" />);

    expect(screen.getByText('Site A')).toBeDefined();
    expect(screen.getByText('Site B')).toBeDefined();

    const badges = screen.getAllByTestId('coverage-badge');
    expect(badges).toHaveLength(3);

    // 75% = green
    expect(badges[0].className).toContain('green');
    // 30% = red/error
    expect(badges[1].className).toContain('error');
    // 60% = amber
    expect(badges[2].className).toContain('amber');
  });
});

describe('ScatterPlot', () => {
  it('renders SVG with data points', () => {
    const data = [
      { x: 2, y: 0.91, label: 'Avec transport' },
      { x: 3.3, y: 1.52, label: 'Sans transport' },
    ];
    render(<ScatterPlot data={data} xLabel="X" yLabel="Y" />);
    expect(screen.getByTestId('scatter-chart')).toBeDefined();
  });
});

describe('RetentionImpactCard', () => {
  it('shows savings and turnover rate', () => {
    const retention: RetentionImpact = mockData.retention_impact;
    render(<RetentionImpactCard data={retention} />);

    expect(screen.getByTestId('annual-savings')).toBeDefined();
    expect(screen.getByTestId('turnover-rate').textContent).toBe('8.0%');
    expect(screen.getByTestId('departure-bar')).toBeDefined();
  });
});

describe('ShadowZonesList', () => {
  it('renders employee entries', () => {
    const zones: ShadowZones = mockData.shadow_zones;
    render(<ShadowZonesList data={zones} />);

    const rows = screen.getAllByTestId('shadow-zone-row');
    expect(rows).toHaveLength(2);
    expect(screen.getByText('John Doe')).toBeDefined();
    expect(screen.getByText('Jane Smith')).toBeDefined();
  });
});

describe('MobilityAlerts', () => {
  it('shows warning when coverage is below 60%', () => {
    const lowCoverage: MobilityCoverage = {
      ...mockData.mobility_coverage,
      coverage_pct: 45.0,
    };
    const highShadow: ShadowZones = {
      ...mockData.shadow_zones,
      shadow_zone_pct: 15.0,
    };

    render(<MobilityAlerts coverage={lowCoverage} shadowZones={highShadow} />);

    expect(screen.getByTestId('mobility-alerts')).toBeDefined();
    expect(screen.getByTestId('alert-critical')).toBeDefined();
    expect(screen.getByTestId('alert-warning')).toBeDefined();
  });

  it('shows no alerts when coverage is good', () => {
    const goodCoverage: MobilityCoverage = {
      ...mockData.mobility_coverage,
      coverage_pct: 80.0,
    };
    const lowShadow: ShadowZones = {
      ...mockData.shadow_zones,
      shadow_zone_pct: 5.0,
    };

    const { container } = render(
      <MobilityAlerts coverage={goodCoverage} shadowZones={lowShadow} />,
    );

    expect(container.querySelector('[data-testid="mobility-alerts"]')).toBeNull();
  });
});
