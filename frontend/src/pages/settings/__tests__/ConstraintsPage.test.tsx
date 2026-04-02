import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockListConstraints = vi.fn();
const mockCreateConstraint = vi.fn();
const mockUpdateConstraint = vi.fn();
const mockDeleteConstraint = vi.fn();

vi.mock('@/api/settings', () => ({
  listConstraints: (...args: unknown[]) => mockListConstraints(...args),
  createConstraint: (...args: unknown[]) => mockCreateConstraint(...args),
  updateConstraint: (...args: unknown[]) => mockUpdateConstraint(...args),
  deleteConstraint: (...args: unknown[]) => mockDeleteConstraint(...args),
}));

const mockConstraints = [
  {
    id: 'c-1',
    tenant_id: 't1',
    key: 'max_vehicles_per_route',
    value: '10',
    category: 'routing',
    description: 'Maximum vehicles per route',
    is_active: true,
    created_at: '2026-04-01T00:00:00Z',
    updated_at: '2026-04-01T00:00:00Z',
  },
  {
    id: 'c-2',
    tenant_id: 't1',
    key: 'min_occupancy_rate',
    value: '0.7',
    category: 'vehicle',
    description: null,
    is_active: false,
    created_at: '2026-04-01T00:00:00Z',
    updated_at: '2026-04-01T00:00:00Z',
  },
];

describe('ConstraintsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListConstraints.mockResolvedValue(mockConstraints);
  });

  it('renders the page heading', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    expect(await screen.findByText('Contraintes')).toBeInTheDocument();
  });

  it('renders the Add Constraint button', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('Contraintes');
    expect(
      screen.getByText('Ajouter une contrainte'),
    ).toBeInTheDocument();
  });

  it('calls listConstraints on mount', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('max_vehicles_per_route');
    expect(mockListConstraints).toHaveBeenCalled();
  });

  it('renders constraint keys in the table', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    expect(
      await screen.findByText('max_vehicles_per_route'),
    ).toBeInTheDocument();
    expect(screen.getByText('min_occupancy_rate')).toBeInTheDocument();
  });

  it('renders table column headers', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('max_vehicles_per_route');
    expect(screen.getByText('Cle')).toBeInTheDocument();
    expect(screen.getByText('Valeur')).toBeInTheDocument();
    expect(screen.getByText('Categorie')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Actif')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('renders Edit and Delete buttons for each constraint', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('max_vehicles_per_route');
    const editButtons = screen.getAllByText('Modifier');
    const deleteButtons = screen.getAllByText('Supprimer');
    expect(editButtons).toHaveLength(2);
    expect(deleteButtons).toHaveLength(2);
  });

  it('renders category chips', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('max_vehicles_per_route');
    // Categories appear both in the filter dropdown and in the table chip
    const routingElements = screen.getAllByText('routing');
    expect(routingElements.length).toBeGreaterThanOrEqual(1);
    const vehicleElements = screen.getAllByText('vehicle');
    expect(vehicleElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows empty state when no constraints', async () => {
    mockListConstraints.mockResolvedValue([]);
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    expect(
      await screen.findByText('Aucune contrainte'),
    ).toBeInTheDocument();
  });

  it('shows error banner when API fails', async () => {
    mockListConstraints.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    });
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    expect(await screen.findByText('Server error')).toBeInTheDocument();
  });

  it('renders active/inactive status indicators', async () => {
    const { ConstraintsPage } = await import('../ConstraintsPage');
    render(<ConstraintsPage />);

    await screen.findByText('max_vehicles_per_route');
    expect(screen.getByText('Oui')).toBeInTheDocument();
    expect(screen.getByText('Non')).toBeInTheDocument();
  });
});
