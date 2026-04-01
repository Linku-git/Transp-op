import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

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
  MapContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="map-view">{children}</div>,
  TileLayer: () => null,
}));

describe('MapView', () => {
  it('renders map container with children', async () => {
    const { MapView } = await import('../MapView');
    render(
      <MapView>
        <div data-testid="child">Hello</div>
      </MapView>,
    );
    expect(screen.getByTestId('map-view')).toBeInTheDocument();
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});
