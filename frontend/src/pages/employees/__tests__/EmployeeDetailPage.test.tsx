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
  Popup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useParams: () => ({ id: '123' }), useNavigate: () => vi.fn() };
});

vi.mock('@/stores/employeeStore', () => ({
  useEmployeeStore: () => ({
    currentEmployee: {
      id: '123', matricule: 'EMP001', first_name: 'Alice', last_name: 'Dupont',
      site_id: 's1', site_name: 'Site Alpha', shift_time: 'Matin',
      address: '10 Rue Test', city: 'Casablanca', lat: 33.57, lng: -7.59,
      is_pmr: true, active: true, department: 'IT', phone: '0612345678',
      current_transport_mode: 'Bus', opt_in_company_transport: 'Oui',
      has_private_car: false, volunteer_driver: false, carpool_seats: 0,
      transport_required: true,
    },
    isLoading: false,
    error: null,
    fetchEmployee: vi.fn(),
    deleteEmployee: vi.fn(),
  }),
}));

vi.mock('@/api/sites', () => ({
  getSite: vi.fn().mockResolvedValue({ id: 's1', name: 'Site Alpha', lat: 33.58, lng: -7.60 }),
}));

describe('EmployeeDetailPage', () => {
  it('displays employee profile', async () => {
    const { EmployeeDetailPage } = await import('../EmployeeDetailPage');
    render(
      <MemoryRouter>
        <EmployeeDetailPage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Alice Dupont/)).toBeInTheDocument();
    expect(screen.getAllByText('EMP001').length).toBeGreaterThan(0);
  });
});
