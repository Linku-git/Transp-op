import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import type { OptimizationRoute } from '@/types/optimization';

vi.mock('leaflet', () => ({
  default: { Icon: { Default: { prototype: {}, mergeOptions: vi.fn() } }, icon: vi.fn(() => ({})) },
  Icon: { Default: { prototype: {}, mergeOptions: vi.fn() } },
  icon: vi.fn(() => ({})),
}));
vi.mock('leaflet/dist/leaflet.css', () => ({}));
vi.mock('leaflet/dist/images/marker-icon.png', () => ({ default: '' }));
vi.mock('leaflet/dist/images/marker-icon-2x.png', () => ({ default: '' }));
vi.mock('leaflet/dist/images/marker-shadow.png', () => ({ default: '' }));
vi.mock('react-leaflet', () => ({
  Polyline: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="polyline">{children}</div>
  ),
  Popup: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="popup">{children}</div>
  ),
}));

const mockRoute: OptimizationRoute = {
  id: 'route-1',
  optimization_id: 'opt-1',
  vehicle_id: 'v-1',
  site_id: 's-1',
  ordered_stops: [
    { employee_id: 'e1', lat: 33.55, lng: -7.60, is_pickup: true, eta_seconds: 0, cumulative_distance_meters: 0 },
    { employee_id: 'e2', lat: 33.56, lng: -7.58, is_pickup: true, eta_seconds: 300, cumulative_distance_meters: 1200 },
    { employee_id: null, lat: 33.57, lng: -7.59, is_pickup: false, eta_seconds: 600, cumulative_distance_meters: 2500 },
  ],
  total_distance_km: 2.5,
  total_time_minutes: 10,
  polyline: null,
  rti_compliance_pct: null,
  created_at: '2026-04-01T10:00:00Z',
  vehicle_type: 'Minibus',
  vehicle_capacity: 15,
  site_name: 'Site Alpha',
};

describe('RoutePolyline', () => {
  it('renders without crashing when given a route with stops', async () => {
    const { RoutePolyline } = await import('../RoutePolyline');
    const { container } = render(
      <RoutePolyline route={mockRoute} index={0} />,
    );
    expect(container).toBeTruthy();
  });

  it('renders a polyline element', async () => {
    const { RoutePolyline } = await import('../RoutePolyline');
    render(<RoutePolyline route={mockRoute} index={0} />);
    expect(screen.getByTestId('polyline')).toBeInTheDocument();
  });

  it('renders route details in popup', async () => {
    const { RoutePolyline } = await import('../RoutePolyline');
    render(<RoutePolyline route={mockRoute} index={0} />);
    expect(screen.getByText(/Minibus/)).toBeInTheDocument();
    expect(screen.getByText(/2\.5 km/)).toBeInTheDocument();
  });
});
