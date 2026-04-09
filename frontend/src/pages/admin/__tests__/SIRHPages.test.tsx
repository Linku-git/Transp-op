import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, dv?: string) => dv ?? key,
    i18n: { language: 'fr' },
  }),
}));

vi.mock('@/api/sirh', () => ({
  listConnections: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'c1',
        tenant_id: 't1',
        provider: 'sap',
        name: 'SAP SuccessFactors',
        config: null,
        sync_frequency: 'daily',
        last_sync_at: '2026-04-09T10:00:00Z',
        status: 'active',
        conflict_strategy: 'sirh_wins',
        is_active: true,
        created_at: '2026-04-01T00:00:00Z',
        updated_at: '2026-04-09T10:00:00Z',
      },
    ],
    total: 1,
  }),
  createConnection: vi.fn().mockResolvedValue({}),
  deleteConnection: vi.fn().mockResolvedValue(undefined),
  triggerSync: vi.fn().mockResolvedValue({ status: 'completed' }),
  getSyncStatus: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'log1',
        connection_id: 'c1',
        tenant_id: 't1',
        started_at: '2026-04-09T10:00:00Z',
        completed_at: '2026-04-09T10:01:00Z',
        records_created: 5,
        records_updated: 10,
        records_failed: 1,
        errors: ['Employee X: missing email'],
        status: 'completed_with_errors',
        created_at: '2026-04-09T10:00:00Z',
      },
    ],
    total: 1,
  }),
  getUnresolvedConflicts: vi.fn().mockResolvedValue([
    {
      id: 'conf1',
      sync_log_id: 'log1',
      employee_id: 'emp-123',
      field_name: 'department',
      platform_value: 'Engineering',
      sirh_value: 'IT',
      resolution: 'unresolved',
    },
  ]),
  resolveConflict: vi.fn().mockResolvedValue({}),
}));

describe('SIRHConnectionsPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders connections page with title', async () => {
    const { SIRHConnectionsPage } = await import('../SIRHConnectionsPage');
    render(
      <MemoryRouter>
        <SIRHConnectionsPage />
      </MemoryRouter>,
    );
    const heading = await screen.findByText('Connexions SIRH');
    expect(heading).toBeDefined();
  });

  it('renders connection card', async () => {
    const { SIRHConnectionsPage } = await import('../SIRHConnectionsPage');
    render(
      <MemoryRouter>
        <SIRHConnectionsPage />
      </MemoryRouter>,
    );
    const name = await screen.findByText('SAP SuccessFactors');
    expect(name).toBeDefined();
  });

  it('renders add connection button', async () => {
    const { SIRHConnectionsPage } = await import('../SIRHConnectionsPage');
    render(
      <MemoryRouter>
        <SIRHConnectionsPage />
      </MemoryRouter>,
    );
    expect(screen.getByText('Ajouter une connexion')).toBeDefined();
  });
});

describe('SIRHSyncDashboardPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders sync dashboard with title', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    const heading = await screen.findByText('Tableau de bord synchronisation');
    expect(heading).toBeDefined();
  });

  it('renders sync history table', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    const history = await screen.findByText('Historique de synchronisation');
    expect(history).toBeDefined();
  });

  it('renders conflict resolution queue', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    const queue = await screen.findByText(/Conflits non résolus/);
    expect(queue).toBeDefined();
  });

  it('renders conflict data', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    const field = await screen.findByText('department');
    expect(field).toBeDefined();
    expect(screen.getByText('Engineering')).toBeDefined();
    expect(screen.getByText('IT')).toBeDefined();
  });

  it('renders resolution buttons', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    // Wait for data to load, then check buttons exist
    await screen.findByText('department');
    const platformBtns = screen.getAllByText('Plateforme');
    expect(platformBtns.length).toBeGreaterThanOrEqual(1);
  });

  it('renders error expandable', async () => {
    const { SIRHSyncDashboardPage } = await import('../SIRHSyncDashboardPage');
    render(
      <MemoryRouter>
        <SIRHSyncDashboardPage />
      </MemoryRouter>,
    );
    const errorLink = await screen.findByText('1 erreur(s)');
    expect(errorLink).toBeDefined();
  });
});
