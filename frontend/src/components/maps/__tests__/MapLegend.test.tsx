import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import type { LayerVisibility } from '@/types/optimization';

const defaultLayers: LayerVisibility = {
  employees: true,
  clusters: true,
  routes: true,
  meetingZones: true,
  accessLegs: false,
  siteMarker: true,
};

describe('MapLegend', () => {
  it('renders all 6 layer labels', async () => {
    const { MapLegend } = await import('../MapLegend');
    render(
      <MapLegend
        layers={defaultLayers}
        onToggle={vi.fn()}
        routeCount={0}
        selectedRouteId={null}
        routeIds={[]}
        onSelectRoute={vi.fn()}
      />,
    );

    expect(screen.getByText('Site')).toBeInTheDocument();
    expect(screen.getByText('Employees')).toBeInTheDocument();
    expect(screen.getByText('Clusters')).toBeInTheDocument();
    expect(screen.getByText('Routes')).toBeInTheDocument();
    expect(screen.getByText('Meeting Zones')).toBeInTheDocument();
    expect(screen.getByText('Access Legs')).toBeInTheDocument();
  });

  it('calls onToggle with correct layer key when checkbox is clicked', async () => {
    const user = userEvent.setup();
    const handleToggle = vi.fn();

    const { MapLegend } = await import('../MapLegend');
    render(
      <MapLegend
        layers={defaultLayers}
        onToggle={handleToggle}
        routeCount={0}
        selectedRouteId={null}
        routeIds={[]}
        onSelectRoute={vi.fn()}
      />,
    );

    // Click the "Access Legs" checkbox (currently unchecked)
    const checkboxes = screen.getAllByRole('checkbox');
    // Checkboxes match LAYER_CONFIG order: siteMarker, employees, clusters, routes, meetingZones, accessLegs
    await user.click(checkboxes[5]);

    expect(handleToggle).toHaveBeenCalledWith('accessLegs');
  });

  it('shows route selector when routeCount > 0', async () => {
    const { MapLegend } = await import('../MapLegend');
    render(
      <MapLegend
        layers={defaultLayers}
        onToggle={vi.fn()}
        routeCount={3}
        selectedRouteId={null}
        routeIds={['r1', 'r2', 'r3']}
        onSelectRoute={vi.fn()}
      />,
    );

    expect(screen.getByText('Routes (3)')).toBeInTheDocument();
    expect(screen.getByText('All routes')).toBeInTheDocument();
    expect(screen.getByText('Route 1')).toBeInTheDocument();
    expect(screen.getByText('Route 2')).toBeInTheDocument();
    expect(screen.getByText('Route 3')).toBeInTheDocument();
  });

  it('does not show route selector when routeCount is 0', async () => {
    const { MapLegend } = await import('../MapLegend');
    render(
      <MapLegend
        layers={defaultLayers}
        onToggle={vi.fn()}
        routeCount={0}
        selectedRouteId={null}
        routeIds={[]}
        onSelectRoute={vi.fn()}
      />,
    );

    expect(screen.queryByText('All routes')).not.toBeInTheDocument();
  });
});
