import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

vi.mock('@/api/sotreg', () => ({
  createLigne: vi.fn().mockResolvedValue({ id: 'new-1', code: 'L010' }),
  updateLigne: vi.fn().mockResolvedValue({ id: 'l1', code: 'L001' }),
  getLigne: vi.fn().mockResolvedValue({
    id: 'l1',
    tenant_id: 't1',
    code: 'L001',
    name: 'Navette Casa Nord',
    service_type: 'navette',
    distance_km: 25.4,
    rotations_per_day: 4,
    operating_days_per_year: 250,
    km_annual: 25400,
    motorization: 'diesel',
    is_active: true,
    site_id: null,
    origin_lat: 33.6,
    origin_lng: -7.5,
    dest_lat: 33.55,
    dest_lng: -7.6,
    passenger_count_avg: 35,
    shift_type: 'matin',
    pente_moyenne_pct: null,
    vehicle_type: 'bus',
    created_at: '2026-04-10T08:00:00Z',
    updated_at: '2026-04-10T08:00:00Z',
  }),
}));

vi.mock('@vis.gl/react-google-maps', () => ({
  APIProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Map: ({ children }: { children?: React.ReactNode }) => <div data-testid="google-map">{children}</div>,
  AdvancedMarker: () => <div data-testid="map-marker" />,
}));

vi.mock('@/components/ui/Card', () => ({
  Card: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}));

describe('LigneFormPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders create form', async () => {
    const { LigneFormPage } = await import('../LigneFormPage');
    render(
      <MemoryRouter initialEntries={['/sotreg/lignes/new']}>
        <Routes>
          <Route path="/sotreg/lignes/new" element={<LigneFormPage />} />
        </Routes>
      </MemoryRouter>,
    );

    // Should show form heading for creation
    expect(screen.getByText(/Nouvelle Ligne/i)).toBeDefined();
  });

  it('renders edit form with pre-filled data', async () => {
    const { LigneFormPage } = await import('../LigneFormPage');
    render(
      <MemoryRouter initialEntries={['/sotreg/lignes/l1/edit']}>
        <Routes>
          <Route path="/sotreg/lignes/:id/edit" element={<LigneFormPage />} />
        </Routes>
      </MemoryRouter>,
    );

    // Should show edit heading or load data
    await screen.findByDisplayValue('Navette Casa Nord');
    expect(screen.getByDisplayValue('Navette Casa Nord')).toBeDefined();
  });

  it('shows map for coordinate selection', async () => {
    const { LigneFormPage } = await import('../LigneFormPage');
    render(
      <MemoryRouter initialEntries={['/sotreg/lignes/new']}>
        <Routes>
          <Route path="/sotreg/lignes/new" element={<LigneFormPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByTestId('google-map')).toBeDefined();
  });
});
