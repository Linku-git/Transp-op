import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import type { OptimizationCluster } from '@/types/optimization';

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
  Circle: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="circle">{children}</div>
  ),
  Popup: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="popup">{children}</div>
  ),
}));

const mockCluster: OptimizationCluster = {
  id: 'cluster-1',
  optimization_id: 'opt-1',
  site_id: 's-1',
  centroid_lat: 33.55,
  centroid_lng: -7.60,
  employee_count: 8,
  pmr_count: 2,
  employee_ids: ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8'],
  created_at: '2026-04-01T10:00:00Z',
};

describe('ClusterRegion', () => {
  it('renders a Circle element for a cluster', async () => {
    const { ClusterRegion } = await import('../ClusterRegion');
    render(<ClusterRegion cluster={mockCluster} />);
    expect(screen.getByTestId('circle')).toBeInTheDocument();
  });

  it('shows employee count in popup', async () => {
    const { ClusterRegion } = await import('../ClusterRegion');
    render(<ClusterRegion cluster={mockCluster} />);
    expect(screen.getByText('Cluster (8 employees)')).toBeInTheDocument();
  });

  it('shows PMR count when cluster has PMR employees', async () => {
    const { ClusterRegion } = await import('../ClusterRegion');
    render(<ClusterRegion cluster={mockCluster} />);
    expect(screen.getByText('PMR: 2')).toBeInTheDocument();
  });

  it('does not show PMR line when pmr_count is 0', async () => {
    const { ClusterRegion } = await import('../ClusterRegion');
    const clusterNoPmr = { ...mockCluster, pmr_count: 0 };
    render(<ClusterRegion cluster={clusterNoPmr} />);
    expect(screen.queryByText(/PMR:/)).not.toBeInTheDocument();
  });
});
