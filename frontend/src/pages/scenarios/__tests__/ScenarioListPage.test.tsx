import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockListScenarios = vi.fn();
const mockDeleteScenario = vi.fn();

vi.mock('@/api/scenarios', () => ({
  listScenarios: (...args: unknown[]) => mockListScenarios(...args),
  deleteScenario: (...args: unknown[]) => mockDeleteScenario(...args),
}));

const mockFetchSites = vi.fn();
vi.mock('@/stores/siteStore', () => ({
  useSiteStore: () => ({
    sites: [
      { id: 'site-1', name: 'Site Alpha' },
      { id: 'site-2', name: 'Site Beta' },
    ],
    fetchSites: mockFetchSites,
  }),
}));

const mockScenarios = [
  {
    id: 'sc-1',
    tenant_id: 't1',
    site_id: 'site-1',
    baseline_optimization_id: null,
    condition_type: 'normal',
    demand_multiplier: 1.0,
    custom_params: {},
    name: 'Scenario Normal',
    created_at: '2026-04-01T10:00:00Z',
    estimated_metrics: {
      total_employees: 50,
      employees_assigned: 48,
      total_clusters: 5,
      total_vehicles_used: 3,
      avg_occupancy_rate: 0.85,
      total_distance_km: 120.5,
      total_duration_minutes: 90,
      estimated_fuel_liters: 15.2,
      estimated_fuel_cost_mad: 250.5,
      co2_estimate_kg: 38.1,
      demand_multiplier_applied: 1.0,
    },
  },
  {
    id: 'sc-2',
    tenant_id: 't1',
    site_id: 'site-2',
    baseline_optimization_id: null,
    condition_type: 'rain',
    demand_multiplier: 1.3,
    custom_params: {},
    name: 'Scenario Pluie',
    created_at: '2026-04-02T08:00:00Z',
    estimated_metrics: {
      total_employees: 60,
      employees_assigned: 58,
      total_clusters: 6,
      total_vehicles_used: 5,
      avg_occupancy_rate: 0.78,
      total_distance_km: 180.0,
      total_duration_minutes: 140,
      estimated_fuel_liters: 22.0,
      estimated_fuel_cost_mad: 380.0,
      co2_estimate_kg: 55.4,
      demand_multiplier_applied: 1.3,
    },
  },
];

describe('ScenarioListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListScenarios.mockResolvedValue(mockScenarios);
    mockDeleteScenario.mockResolvedValue(undefined);
  });

  it('renders the page heading', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Scenarios')).toBeInTheDocument();
  });

  it('calls fetchSites on mount', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(mockFetchSites).toHaveBeenCalled();
  });

  it('calls listScenarios on mount', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    expect(mockListScenarios).toHaveBeenCalled();
  });

  it('renders scenario names in the table', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Scenario Normal')).toBeInTheDocument();
    expect(screen.getByText('Scenario Pluie')).toBeInTheDocument();
  });

  it('renders condition chips', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Normal')).toBeInTheDocument();
    expect(screen.getByText('Pluie')).toBeInTheDocument();
  });

  it('renders vehicle counts', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders table column headers', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    expect(screen.getByText('Nom')).toBeInTheDocument();
    expect(screen.getByText('Condition')).toBeInTheDocument();
    expect(screen.getByText('Vehicules')).toBeInTheDocument();
    expect(screen.getByText('Cout (MAD)')).toBeInTheDocument();
    expect(screen.getByText('CO2 (kg)')).toBeInTheDocument();
    expect(screen.getByText('Date')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('renders the New Scenario button', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    expect(screen.getByText('Nouveau scenario')).toBeInTheDocument();
  });

  it('navigates to optimization on New Scenario click', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    fireEvent.click(screen.getByText('Nouveau scenario'));
    expect(mockNavigate).toHaveBeenCalledWith('/optimization');
  });

  it('renders the Compare button disabled when fewer than 2 selected', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    const compareButton = screen.getByText('Comparer ({{count}})').closest('button');
    expect(compareButton).toBeDisabled();
  });

  it('renders site filter dropdown with site options', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();

    const options = select.querySelectorAll('option');
    expect(options.length).toBe(3); // "All sites" + 2 sites
  });

  it('shows empty state when no scenarios', async () => {
    mockListScenarios.mockResolvedValue([]);
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Aucun scenario')).toBeInTheDocument();
  });

  it('shows error banner when API fails', async () => {
    mockListScenarios.mockRejectedValue({
      response: { data: { detail: 'Server error' } },
    });
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Server error')).toBeInTheDocument();
    expect(screen.getByText('Fermer')).toBeInTheDocument();
  });

  it('renders View and Delete buttons for each scenario', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    const viewButtons = screen.getAllByText('Voir');
    const deleteButtons = screen.getAllByText('Supprimer');
    expect(viewButtons).toHaveLength(2);
    expect(deleteButtons).toHaveLength(2);
  });

  it('renders checkboxes for scenario selection', async () => {
    const { ScenarioListPage } = await import('../ScenarioListPage');
    render(
      <MemoryRouter>
        <ScenarioListPage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Normal');
    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes).toHaveLength(2);
  });
});
