import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, dv?: string) => dv ?? key,
    i18n: { language: 'fr' },
  }),
}));

vi.mock('@/api/operator', () => ({
  listSizingPlans: vi.fn().mockResolvedValue({
    data: [
      {
        id: 'plan-1',
        version: 3,
        format: 'json',
        status: 'completed',
        file_url: '/exports/plan.json',
        content_summary: { vehicles: 12, routes: 5, passengers: 200, pmr: 8 },
        acknowledged: false,
        acknowledged_at: null,
        created_at: '2026-04-09T10:00:00Z',
      },
    ],
    total: 1,
  }),
  getSizingPlan: vi.fn().mockResolvedValue({
    id: 'plan-1',
    version: 3,
    format: 'json',
    status: 'completed',
    content_summary: { vehicles: 12, routes: 5, passengers: 200, pmr: 8, distance_km: 150 },
    acknowledged: false,
    created_at: '2026-04-09T10:00:00Z',
  }),
  acknowledgePlan: vi.fn().mockResolvedValue({ acknowledged: true }),
  reportServiceIssue: vi.fn().mockResolvedValue({ id: 'issue-1' }),
}));

vi.mock('@/lib/apiError', () => ({
  extractApiError: (_err: unknown, fallback: string) => fallback,
}));

describe('OperatorDashboardPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders portal title', async () => {
    const { OperatorDashboardPage } = await import('../OperatorDashboardPage');
    render(<MemoryRouter><OperatorDashboardPage /></MemoryRouter>);
    const heading = await screen.findByText('Portail Opérateur');
    expect(heading).toBeDefined();
  });

  it('renders sizing plan card', async () => {
    const { OperatorDashboardPage } = await import('../OperatorDashboardPage');
    render(<MemoryRouter><OperatorDashboardPage /></MemoryRouter>);
    const plan = await screen.findByText('Plan v3');
    expect(plan).toBeDefined();
  });

  it('shows plan summary data', async () => {
    const { OperatorDashboardPage } = await import('../OperatorDashboardPage');
    render(<MemoryRouter><OperatorDashboardPage /></MemoryRouter>);
    await screen.findByText('Plan v3');
    expect(screen.getByText('12 véhicules')).toBeDefined();
    expect(screen.getByText('5 routes')).toBeDefined();
    expect(screen.getByText('200 passagers')).toBeDefined();
  });

  it('renders confirm button for unacknowledged plan', async () => {
    const { OperatorDashboardPage } = await import('../OperatorDashboardPage');
    render(<MemoryRouter><OperatorDashboardPage /></MemoryRouter>);
    const btn = await screen.findByText('Confirmer');
    expect(btn).toBeDefined();
  });

  it('renders report issue link', async () => {
    const { OperatorDashboardPage } = await import('../OperatorDashboardPage');
    render(<MemoryRouter><OperatorDashboardPage /></MemoryRouter>);
    expect(screen.getByText('Signaler un incident')).toBeDefined();
  });
});

describe('ReportIssuePage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders issue form', async () => {
    const { ReportIssuePage } = await import('../ReportIssuePage');
    render(<MemoryRouter><ReportIssuePage /></MemoryRouter>);
    expect(screen.getAllByText("Signaler un incident").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Type d'incident *")).toBeDefined();
    expect(screen.getByText('Description *')).toBeDefined();
    expect(screen.getByText('Soumettre')).toBeDefined();
  });

  it('renders all issue types', async () => {
    const { ReportIssuePage } = await import('../ReportIssuePage');
    render(<MemoryRouter><ReportIssuePage /></MemoryRouter>);
    expect(screen.getByText('Retard')).toBeDefined();
    expect(screen.getByText('Panne véhicule')).toBeDefined();
    expect(screen.getByText('Problème sécurité')).toBeDefined();
  });
});
