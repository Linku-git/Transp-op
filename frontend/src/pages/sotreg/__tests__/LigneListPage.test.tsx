import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

const mockListLignes = vi.fn().mockResolvedValue({
  data: [
    {
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
      created_at: '2026-04-10T08:00:00Z',
      updated_at: '2026-04-10T08:00:00Z',
    },
    {
      id: 'l2',
      tenant_id: 't1',
      code: 'L002',
      name: 'Liaison Ain Sebaa',
      service_type: 'liaison',
      distance_km: 18.7,
      rotations_per_day: 6,
      operating_days_per_year: 300,
      km_annual: 33660,
      motorization: 'electrique',
      is_active: false,
      site_id: null,
      origin_lat: 33.62,
      origin_lng: -7.52,
      dest_lat: 33.57,
      dest_lng: -7.58,
      passenger_count_avg: 20,
      shift_type: 'soir',
      pente_moyenne_pct: 2.5,
      created_at: '2026-04-10T08:00:00Z',
      updated_at: '2026-04-10T08:00:00Z',
    },
  ],
  meta: { page: 1, pages: 1, total: 2, page_size: 20 },
});

const mockDeleteLigne = vi.fn();

vi.mock('@/api/sotreg', () => ({
  listLignes: (...args: unknown[]) => mockListLignes(...args),
  deleteLigne: (...args: unknown[]) => mockDeleteLigne(...args),
}));

describe('LigneListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders table with lignes', async () => {
    const { LigneListPage } = await import('../LigneListPage');
    render(
      <MemoryRouter>
        <LigneListPage />
      </MemoryRouter>,
    );

    // Wait for data to render
    const title = await screen.findByText('Lignes de Transport');
    expect(title).toBeDefined();
  });

  it('renders service type badges', async () => {
    const { LigneListPage } = await import('../LigneListPage');
    render(
      <MemoryRouter>
        <LigneListPage />
      </MemoryRouter>,
    );

    // Should show the ligne codes after loading
    expect(await screen.findByText('L001')).toBeDefined();
    expect(screen.getByText('L002')).toBeDefined();
  });

  it('has link to create new ligne', async () => {
    const { LigneListPage } = await import('../LigneListPage');
    render(
      <MemoryRouter>
        <LigneListPage />
      </MemoryRouter>,
    );

    const newLink = document.querySelector('a[href="/sotreg/lignes/new"]');
    expect(newLink).not.toBeNull();
  });

  it('calls listLignes on mount', async () => {
    const { LigneListPage } = await import('../LigneListPage');
    render(
      <MemoryRouter>
        <LigneListPage />
      </MemoryRouter>,
    );

    expect(mockListLignes).toHaveBeenCalled();
  });
});
