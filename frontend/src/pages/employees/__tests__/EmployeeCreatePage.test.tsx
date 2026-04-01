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
  CircleMarker: () => null,
  useMapEvents: () => null,
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('@/stores/employeeStore', () => ({
  useEmployeeStore: () => ({
    createEmployee: vi.fn(),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  }),
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [{ id: 's1', code: 'S01', name: 'Test Site', num_shifts: 1 }],
    fetchSites: vi.fn(),
  }),
}));

describe('EmployeeCreatePage', () => {
  it('renders form', async () => {
    const { EmployeeCreatePage } = await import('../EmployeeCreatePage');
    render(
      <MemoryRouter>
        <EmployeeCreatePage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText(/Nouvel employ/i).length).toBeGreaterThan(0);
  });
});
