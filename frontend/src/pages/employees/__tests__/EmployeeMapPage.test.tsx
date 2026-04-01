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
  CircleMarker: ({ children }: { children?: React.ReactNode }) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/stores/employeeStore', () => ({
  useEmployeeStore: () => ({
    employees: [
      { id: '1', first_name: 'Alice', last_name: 'D', matricule: 'E1', site_id: 's1', site_name: 'Site A', lat: 33.5, lng: -7.5, is_pmr: false, shift_time: 'Matin', active: true },
    ],
    meta: null,
    isLoading: false,
    error: null,
    fetchEmployees: vi.fn(),
  }),
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [{ id: 's1', code: 'S01', name: 'Site A', city: 'Casa', lat: 33.57, lng: -7.59, num_shifts: 1 }],
    fetchSites: vi.fn(),
  }),
}));

describe('EmployeeMapPage', () => {
  it('renders map with markers', async () => {
    const { EmployeeMapPage } = await import('../EmployeeMapPage');
    render(
      <MemoryRouter>
        <EmployeeMapPage />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('map')).toBeInTheDocument();
    expect(screen.getAllByTestId('marker').length).toBeGreaterThan(0);
  });
});
