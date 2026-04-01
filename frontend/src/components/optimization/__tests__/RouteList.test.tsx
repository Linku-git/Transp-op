import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import type { OptimizationRoute } from '@/types/optimization';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockRoutes: OptimizationRoute[] = [
  {
    id: 'r1',
    optimization_id: 'o1',
    vehicle_id: 'v1',
    site_id: 's1',
    ordered_stops: [
      {
        employee_id: null,
        lat: 33.5,
        lng: -7.6,
        is_pickup: false,
        eta_seconds: 0,
        cumulative_distance_meters: 0,
      },
      {
        employee_id: 'e1-abcd-1234-efgh-5678',
        lat: 33.51,
        lng: -7.61,
        is_pickup: true,
        eta_seconds: 300,
        cumulative_distance_meters: 5000,
      },
    ],
    total_distance_km: 12.5,
    total_time_minutes: 25,
    polyline: null,
    rti_compliance_pct: null,
    created_at: '2026-04-01',
    vehicle_type: 'Minibus',
    vehicle_capacity: 15,
    site_name: 'Site A',
  },
];

describe('RouteList', () => {
  it('renders empty state when no routes are provided', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={[]} />);

    expect(screen.getByText('Aucune route disponible')).toBeInTheDocument();
  });

  it('renders route header with vehicle type and capacity', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    expect(screen.getByText(/Minibus/)).toBeInTheDocument();
    expect(screen.getByText(/15/)).toBeInTheDocument();
    expect(screen.getByText(/places/)).toBeInTheDocument();
  });

  it('shows pickup stop count', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    // Only 1 pickup stop (the second stop has is_pickup: true)
    expect(screen.getByText('1 arrets')).toBeInTheDocument();
  });

  it('shows route distance', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    expect(screen.getByText('12.5 km')).toBeInTheDocument();
  });

  it('shows route duration', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    expect(screen.getByText('25 min')).toBeInTheDocument();
  });

  it('expands to show stop details when clicked', async () => {
    const user = userEvent.setup();
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    // Before expanding, stop details should not be visible
    expect(screen.queryByText('Prise en charge')).not.toBeInTheDocument();

    // Click the route row button to expand
    const expandButton = screen.getByRole('button');
    await user.click(expandButton);

    // After expanding, stop details should be visible
    expect(screen.getByText('Depot')).toBeInTheDocument();
    expect(screen.getByText('Prise en charge')).toBeInTheDocument();
  });

  it('shows ETA for stops when expanded', async () => {
    const user = userEvent.setup();
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    const expandButton = screen.getByRole('button');
    await user.click(expandButton);

    // ETA for second stop: 300 seconds = 5m00s
    expect(screen.getByText('ETA 5m00s')).toBeInTheDocument();
  });

  it('shows cumulative distance for stops when expanded', async () => {
    const user = userEvent.setup();
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    const expandButton = screen.getByRole('button');
    await user.click(expandButton);

    // cumulative_distance_meters 5000 => 5.0 km
    expect(screen.getByText('5.0 km')).toBeInTheDocument();
  });

  it('renders column headers', async () => {
    const { RouteList } = await import('../RouteList');
    render(<RouteList routes={mockRoutes} />);

    expect(screen.getByText('Vehicule')).toBeInTheDocument();
    expect(screen.getByText('Arrets')).toBeInTheDocument();
    expect(screen.getByText('Dist.')).toBeInTheDocument();
    expect(screen.getByText('Duree')).toBeInTheDocument();
  });
});
