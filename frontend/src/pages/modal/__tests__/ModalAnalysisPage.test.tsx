import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, defaultValue?: string) => defaultValue ?? key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => null,
  Cell: () => null,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  Legend: () => null,
  CartesianGrid: () => null,
}));

vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [{ id: 's1', code: 'S01', name: 'Site A' }],
    fetchSites: vi.fn(),
  }),
}));

vi.mock('@/api/modal', () => ({
  getModalStats: vi.fn().mockResolvedValue({
    total: 100,
    distribution: [
      { mode: 'vehicule_particulier', count: 60, percentage: 60 },
      { mode: 'transport_public', count: 40, percentage: 40 },
    ],
    by_site: [],
  }),
  getShiftAnalysis: vi.fn().mockResolvedValue([]),
  getMobilityScores: vi.fn().mockResolvedValue([
    { employee_id: 'e1', employee_name: 'Alice', score: 85, factors: {} },
  ]),
}));

describe('ModalAnalysisPage', () => {
  it('renders charts with data', async () => {
    const { ModalAnalysisPage } = await import('../ModalAnalysisPage');
    render(
      <MemoryRouter>
        <ModalAnalysisPage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getAllByTestId('pie-chart').length).toBeGreaterThan(0);
    });
  });
});
