import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockFetchHistory = vi.fn();
const mockClearError = vi.fn();

vi.mock('@/stores/optimizationStore', () => ({
  useOptimizationStore: vi.fn(),
}));

import { useOptimizationStore } from '@/stores/optimizationStore';

const mockHistory = [
  {
    id: 'opt1',
    site_id: 's1',
    condition_type: 'normal',
    status: 'completed',
    metrics: { total_vehicles_used: 3, total_distance_km: 50.0, total_duration_minutes: 120 },
    target_date: '2026-04-01',
    created_at: '2026-04-01T10:00:00Z',
    completed_at: '2026-04-01T10:05:00Z',
    site_name: 'Site Alpha',
  },
  {
    id: 'opt2',
    site_id: 's2',
    condition_type: 'ramadan',
    status: 'failed',
    metrics: {},
    target_date: '2026-04-02',
    created_at: '2026-04-02T08:00:00Z',
    completed_at: null,
    site_name: 'Site Beta',
  },
];

describe('OptimizationHistoryPage', () => {
  beforeEach(() => {
    vi.mocked(useOptimizationStore).mockReturnValue({
      history: mockHistory,
      isLoading: false,
      error: null,
      fetchHistory: mockFetchHistory,
      clearError: mockClearError,
    } as unknown as ReturnType<typeof useOptimizationStore>);
  });

  it('renders the page heading', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Optimization History')).toBeInTheDocument();
  });

  it('calls fetchHistory on mount', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(mockFetchHistory).toHaveBeenCalled();
  });

  it('renders history table with site names', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Site Alpha')).toBeInTheDocument();
    expect(screen.getByText('Site Beta')).toBeInTheDocument();
  });

  it('renders status chips for each row', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('completed')).toBeInTheDocument();
    expect(screen.getByText('failed')).toBeInTheDocument();
  });

  it('renders condition type for each row', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('normal')).toBeInTheDocument();
    expect(screen.getByText('ramadan')).toBeInTheDocument();
  });

  it('renders metrics values from completed optimization', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    // total_vehicles_used: 3
    expect(screen.getByText('3')).toBeInTheDocument();
    // total_distance_km: 50.0 => "50.0 km"
    expect(screen.getByText('50.0 km')).toBeInTheDocument();
  });

  it('renders table column headers', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Site')).toBeInTheDocument();
    expect(screen.getByText('Condition')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Vehicles')).toBeInTheDocument();
    expect(screen.getByText('Distance')).toBeInTheDocument();
  });

  it('renders View links for each history item', async () => {
    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    const viewLinks = screen.getAllByText('View');
    expect(viewLinks).toHaveLength(2);
  });

  it('shows loading state when isLoading is true and history is empty', async () => {
    vi.mocked(useOptimizationStore).mockReturnValue({
      history: [],
      isLoading: true,
      error: null,
      fetchHistory: mockFetchHistory,
      clearError: mockClearError,
    } as unknown as ReturnType<typeof useOptimizationStore>);

    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when history is empty and not loading', async () => {
    vi.mocked(useOptimizationStore).mockReturnValue({
      history: [],
      isLoading: false,
      error: null,
      fetchHistory: mockFetchHistory,
      clearError: mockClearError,
    } as unknown as ReturnType<typeof useOptimizationStore>);

    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('No optimization runs found')).toBeInTheDocument();
  });

  it('shows error banner when error is present', async () => {
    vi.mocked(useOptimizationStore).mockReturnValue({
      history: mockHistory,
      isLoading: false,
      error: 'Something went wrong',
      fetchHistory: mockFetchHistory,
      clearError: mockClearError,
    } as unknown as ReturnType<typeof useOptimizationStore>);

    const { OptimizationHistoryPage } = await import('../OptimizationHistoryPage');
    render(
      <MemoryRouter>
        <OptimizationHistoryPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Dismiss')).toBeInTheDocument();
  });
});
