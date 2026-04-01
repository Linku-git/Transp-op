import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import type { OptimizationMetrics } from '@/types/optimization';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockMetrics: OptimizationMetrics = {
  total_employees: 50,
  employees_assigned: 42,
  employees_excluded_leave: 3,
  total_clusters: 8,
  total_vehicles_used: 5,
  avg_occupancy_rate: 0.85,
  total_distance_km: 125.5,
  total_duration_minutes: 180,
  estimated_fuel_liters: 18.8,
  estimated_fuel_cost_mad: 225.6,
  co2_estimate_kg: 50.4,
  time_saved_vs_individual_hours: 12.5,
  unassigned_clusters: 1,
};

describe('MetricsPanel', () => {
  it('renders vehicle count', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders employee assigned fraction', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    expect(screen.getByText('42/50')).toBeInTheDocument();
  });

  it('renders total distance', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    // total_distance_km.toFixed(1) => "125.5"
    expect(screen.getByText('125.5')).toBeInTheDocument();
    expect(screen.getByText('km')).toBeInTheDocument();
  });

  it('renders CO2 estimate value', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    // co2_estimate_kg.toFixed(1) => "50.4"
    expect(screen.getByText('50.4')).toBeInTheDocument();
  });

  it('renders fuel cost', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    // estimated_fuel_cost_mad.toFixed(0) => "226"
    expect(screen.getByText('226')).toBeInTheDocument();
    expect(screen.getByText('MAD')).toBeInTheDocument();
  });

  it('renders occupancy gauge with percentage', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    // avg_occupancy_rate 0.85 => 85%
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('renders metric labels', async () => {
    const { MetricsPanel } = await import('../MetricsPanel');
    render(<MetricsPanel metrics={mockMetrics} />);

    expect(screen.getByText('Vehicules utilises')).toBeInTheDocument();
    expect(screen.getByText('Employes affectes')).toBeInTheDocument();
    expect(screen.getByText('Distance totale')).toBeInTheDocument();
    expect(screen.getByText('CO2 economise')).toBeInTheDocument();
  });
});
