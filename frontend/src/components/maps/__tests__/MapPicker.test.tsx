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
  MapContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="map">{children}</div>,
  TileLayer: () => null,
  Marker: () => <div data-testid="marker" />,
  useMapEvents: () => null,
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (k: string) => k, i18n: { changeLanguage: vi.fn(), language: 'fr' } }),
}));

describe('MapPicker', () => {
  it('renders map and displays coordinates', async () => {
    const { MapPicker } = await import('../MapPicker');
    render(<MapPicker lat={33.57} lng={-7.59} onChange={vi.fn()} />);
    expect(screen.getByTestId('map')).toBeInTheDocument();
    expect(screen.getByText(/33\.57/)).toBeInTheDocument();
  });
});
