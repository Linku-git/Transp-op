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
  useMapEvents: () => null,
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const m: Record<string, string> = { 'sites.create_title': 'Nouveau site', 'common.save': 'Enregistrer', 'common.cancel': 'Annuler' };
      return m[key] ?? key;
    },
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));
vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({ createSite: vi.fn(), isLoading: false, error: null, clearError: vi.fn() }),
}));

describe('SiteCreatePage', () => {
  it('renders form with required fields', async () => {
    const { SiteCreatePage } = await import('../SiteCreatePage');
    render(<MemoryRouter><SiteCreatePage /></MemoryRouter>);
    expect(screen.getByRole('heading', { name: 'Nouveau site' })).toBeInTheDocument();
    expect(screen.getByText('Enregistrer')).toBeInTheDocument();
  });
});
