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
  MapContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="map">{children}</div>,
  TileLayer: () => null,
  Marker: () => null,
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (k: string) => k, i18n: { changeLanguage: vi.fn(), language: 'fr' } }),
}));
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useParams: () => ({ id: '123' }), useNavigate: () => vi.fn() };
});
vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    currentSite: {
      id: '123', code: 'S01', name: 'Site Test', address: '123 Rue', city: 'Casablanca',
      lat: 33.57, lng: -7.59, num_shifts: 1, zfe_zone: false, security_profile: 'normal',
      working_days: 'Lundi-Vendredi', days_per_week: 5,
    },
    isLoading: false, error: null, fetchSite: vi.fn(), deleteSite: vi.fn(),
  }),
}));

describe('SiteDetailPage', () => {
  it('displays site info', async () => {
    const { SiteDetailPage } = await import('../SiteDetailPage');
    render(<MemoryRouter><SiteDetailPage /></MemoryRouter>);
    expect(screen.getAllByText('Site Test').length).toBeGreaterThan(0);
    expect(screen.getByText('Casablanca')).toBeInTheDocument();
  });
});
