import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (_key: string, defaultValue?: string) => defaultValue ?? _key,
    i18n: { changeLanguage: vi.fn(), language: 'fr' },
  }),
}));

const mockListScenarios = vi.fn();
const mockCompareScenarios = vi.fn();

vi.mock('@/api/scenarios', () => ({
  listScenarios: (...args: unknown[]) => mockListScenarios(...args),
  compareScenarios: (...args: unknown[]) => mockCompareScenarios(...args),
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
      estimated_fuel_cost_mad: 250,
      co2_estimate_kg: 38.1,
      demand_multiplier_applied: 1.0,
    },
  },
  {
    id: 'sc-2',
    tenant_id: 't1',
    site_id: 'site-1',
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
      estimated_fuel_cost_mad: 380,
      co2_estimate_kg: 55.4,
      demand_multiplier_applied: 1.3,
    },
  },
  {
    id: 'sc-3',
    tenant_id: 't1',
    site_id: 'site-2',
    baseline_optimization_id: null,
    condition_type: 'strike',
    demand_multiplier: 1.5,
    custom_params: {},
    name: null,
    created_at: '2026-04-02T12:00:00Z',
    estimated_metrics: {
      total_employees: 70,
      employees_assigned: 65,
      total_clusters: 7,
      total_vehicles_used: 6,
      avg_occupancy_rate: 0.72,
      total_distance_km: 220.0,
      total_duration_minutes: 170,
      estimated_fuel_liters: 28.0,
      estimated_fuel_cost_mad: 460,
      co2_estimate_kg: 70.5,
      demand_multiplier_applied: 1.5,
    },
  },
];

const mockComparisonResult = {
  scenarios: [mockScenarios[0], mockScenarios[1]],
  deltas: [
    {
      scenario_a_id: 'sc-1',
      scenario_b_id: 'sc-2',
      vehicles_delta: 2,
      cost_delta_mad: 130,
      co2_delta_kg: 17.3,
      distance_delta_km: 59.5,
      duration_delta_minutes: 50,
      occupancy_delta_pct: -7.0,
    },
  ],
};

describe('ScenarioComparePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListScenarios.mockResolvedValue(mockScenarios);
    mockCompareScenarios.mockResolvedValue(mockComparisonResult);
  });

  it('renders the page title', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('Scenario Comparison'),
    ).toBeInTheDocument();
  });

  it('renders scenario selector dropdowns', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');
    // The mock t() returns the default value with unresolved interpolation
    const labels = screen.getAllByText('Scenario {{n}}');
    expect(labels).toHaveLength(3);
  });

  it('renders the Compare button', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');
    const button = screen.getByText('Compare').closest('button');
    expect(button).toBeInTheDocument();
  });

  it('disables Compare button when fewer than 2 scenarios selected', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');
    const button = screen.getByText('Compare').closest('button');
    expect(button).toBeDisabled();
  });

  it('shows empty state when no scenarios available', async () => {
    mockListScenarios.mockResolvedValue([]);
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('No scenarios available'),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Simulate scenarios from the optimization page first.',
      ),
    ).toBeInTheDocument();
  });

  it('shows error banner when API fails', async () => {
    mockListScenarios.mockRejectedValue(new Error('Network error'));
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Network error')).toBeInTheDocument();
    expect(screen.getByText('Dismiss')).toBeInTheDocument();
  });

  it('dismisses error when Dismiss is clicked', async () => {
    mockListScenarios.mockRejectedValue(new Error('Network error'));
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Network error');
    fireEvent.click(screen.getByText('Dismiss'));
    expect(screen.queryByText('Network error')).not.toBeInTheDocument();
  });

  it('calls compareScenarios when Compare button is clicked with 2 selected', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter initialEntries={['/?ids=sc-1,sc-2']}>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    // The auto-compare effect should trigger because IDs are in URL
    await waitFor(() => {
      expect(mockCompareScenarios).toHaveBeenCalledWith(['sc-1', 'sc-2']);
    });
  });

  it('renders side-by-side metrics table after comparison', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter initialEntries={['/?ids=sc-1,sc-2']}>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('Side-by-Side Metrics'),
    ).toBeInTheDocument();
    // Metric labels appear in both side-by-side and deltas tables
    expect(screen.getAllByText('Vehicles').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Occupancy').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Distance').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Duration').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Fuel Cost').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('CO2').length).toBeGreaterThanOrEqual(1);
  });

  it('renders deltas section after comparison', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter initialEntries={['/?ids=sc-1,sc-2']}>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Deltas')).toBeInTheDocument();
  });

  it('renders recommendations section after comparison', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter initialEntries={['/?ids=sc-1,sc-2']}>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('Recommendations'),
    ).toBeInTheDocument();
  });

  it('shows comparison error when compare API fails', async () => {
    mockCompareScenarios.mockRejectedValue(new Error('Compare failed'));
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter initialEntries={['/?ids=sc-1,sc-2']}>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText('Compare failed')).toBeInTheDocument();
    });
  });

  it('renders the back link to scenarios', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');
    const backLink = screen.getByText('Back');
    expect(backLink).toBeInTheDocument();
    expect(backLink.closest('a')).toHaveAttribute('href', '/scenarios');
  });

  it('renders scenario names in dropdown options', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');

    const selects = screen.getAllByRole('combobox');
    const options = selects[0].querySelectorAll('option');
    // 1 empty + 3 scenarios
    expect(options.length).toBe(4);
  });

  it('renders select hint when fewer than 2 scenarios are selected', async () => {
    const { ScenarioComparePage } = await import('../ScenarioComparePage');
    render(
      <MemoryRouter>
        <ScenarioComparePage />
      </MemoryRouter>,
    );

    await screen.findByText('Scenario Comparison');
    // The mock t() returns the default value with unresolved interpolation
    expect(
      screen.getByText('Select at least {{min}} scenarios to compare.'),
    ).toBeInTheDocument();
  });
});
