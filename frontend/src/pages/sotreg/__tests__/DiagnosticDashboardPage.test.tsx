import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { language: 'fr' },
  }),
}));

vi.mock('@/api/sotreg', () => ({
  getFleetContextSnapshot: vi.fn().mockResolvedValue({
    id: 'fc-1',
    tenant_id: 't1',
    total_vehicles: 106,
    total_km_annual: 2450000,
    total_tco2_annual: 385.2,
    average_age_years: 4.8,
    pct_diesel: 62.5,
    pct_electric: 15.0,
    pct_hybrid: 22.5,
    currency: 'MAD',
    snapshot_date: '2026-04-10',
    created_at: '2026-04-10T08:00:00Z',
    updated_at: '2026-04-10T08:00:00Z',
  }),
  listLignes: vi.fn().mockResolvedValue({
    data: [
      { id: 'l1', code: 'L001', name: 'Navette Casa Nord', is_active: true },
      { id: 'l2', code: 'L002', name: 'Liaison Ain Sebaa', is_active: true },
    ],
    meta: { page: 1, pages: 1, total: 2, page_size: 100 },
  }),
  getZFECompliance: vi.fn().mockResolvedValue({
    total_lignes: 2,
    lignes_in_zfe: 1,
    results: [],
  }),
  listODMatrix: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'od1',
        origin_zone: 'Zone A',
        destination_zone: 'Zone B',
        flow_estimate: 120.5,
        distance_km: 15.3,
        gravity_score: 0.85,
        beta_used: 0.08,
      },
    ],
    total: 1,
    beta_used: 0.08,
  }),
  computeODMatrix: vi.fn(),
}));

vi.mock('@vis.gl/react-google-maps', () => ({
  APIProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Map: ({ children }: { children?: React.ReactNode }) => <div data-testid="google-map">{children}</div>,
  AdvancedMarker: () => <div data-testid="map-marker" />,
  InfoWindow: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Cell: () => <div />,
  PieChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Pie: () => <div />,
  Legend: () => <div />,
}));

describe('DiagnosticDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title', async () => {
    const { DiagnosticDashboardPage } = await import('../DiagnosticDashboardPage');
    render(
      <MemoryRouter>
        <DiagnosticDashboardPage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Diagnostic/i)).toBeDefined();
  });

  it('renders navigation links to lignes after data loads', async () => {
    const { DiagnosticDashboardPage } = await import('../DiagnosticDashboardPage');
    render(
      <MemoryRouter>
        <DiagnosticDashboardPage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      const links = document.querySelectorAll('a[href*="sotreg"]');
      expect(links.length).toBeGreaterThan(0);
    });
  });
});
