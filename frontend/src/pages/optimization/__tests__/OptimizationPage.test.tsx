import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

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
  MapContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="map-container">{children}</div>
  ),
  TileLayer: () => null,
  Circle: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="circle">{children}</div>
  ),
  CircleMarker: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="circle-marker">{children}</div>
  ),
  Polyline: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="polyline">{children}</div>
  ),
  Popup: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="popup">{children}</div>
  ),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/stores/optimizationStore', () => ({
  useOptimizationStore: () => ({
    current: null,
    status: null,
    isLoading: false,
    isRunning: false,
    error: null,
    layers: {
      employees: true,
      clusters: true,
      routes: true,
      meetingZones: true,
      accessLegs: false,
      siteMarker: true,
    },
    selectedRouteId: null,
    launch: vi.fn(),
    fetchLatest: vi.fn(),
    toggleLayer: vi.fn(),
    selectRoute: vi.fn(),
    clearError: vi.fn(),
  }),
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [
      { id: 's1', code: 'S01', name: 'Site Alpha', city: 'Casablanca', lat: 33.57, lng: -7.59, num_shifts: 1 },
      { id: 's2', code: 'S02', name: 'Site Beta', city: 'Rabat', lat: 34.02, lng: -6.83, num_shifts: 2 },
    ],
    fetchSites: vi.fn(),
  }),
}));

describe('OptimizationPage', () => {
  it('renders the page title', async () => {
    const { OptimizationPage } = await import('../OptimizationPage');
    render(
      <MemoryRouter>
        <OptimizationPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Optimization')).toBeInTheDocument();
  });

  it('renders the site selector with options', async () => {
    const { OptimizationPage } = await import('../OptimizationPage');
    render(
      <MemoryRouter>
        <OptimizationPage />
      </MemoryRouter>,
    );

    const siteOptions = screen.getAllByText('-- Select a site --');
    expect(siteOptions.length).toBeGreaterThan(0);
    expect(screen.getByText('Site Alpha (S01)')).toBeInTheDocument();
    expect(screen.getByText('Site Beta (S02)')).toBeInTheDocument();
  });

  it('renders the Run Optimization button', async () => {
    const { OptimizationPage } = await import('../OptimizationPage');
    render(
      <MemoryRouter>
        <OptimizationPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole('button', { name: 'Run Optimization' })).toBeInTheDocument();
  });

  it('disables the button when no site is selected', async () => {
    const { OptimizationPage } = await import('../OptimizationPage');
    render(
      <MemoryRouter>
        <OptimizationPage />
      </MemoryRouter>,
    );

    const button = screen.getByRole('button', { name: 'Run Optimization' });
    expect(button).toBeDisabled();
  });
});
