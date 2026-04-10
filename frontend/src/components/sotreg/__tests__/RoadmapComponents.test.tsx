import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@/api/sotreg', () => ({ generateTransitionPlan: vi.fn() }));
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />, XAxis: () => <div />, YAxis: () => <div />,
  CartesianGrid: () => <div />, Tooltip: () => <div />, Legend: () => <div />,
}));

const MOCK_PHASES = [
  { name: 'Pilot', technology_wave: 'pilot', start_year: 2026, end_year: 2028, vehicles_to_convert: 5, target_pct_electric: 10, budget_allocated_mad: 1950000, vehicle_cost_mad: 1500000, infrastructure_cost_mad: 450000, status: 'planned' },
  { name: 'Scale', technology_wave: 'scale', start_year: 2028, end_year: 2031, vehicles_to_convert: 20, target_pct_electric: 50, budget_allocated_mad: 7800000, vehicle_cost_mad: 6000000, infrastructure_cost_mad: 1800000, status: 'planned' },
];

const MOCK_MILESTONES = [
  { year: 2028, description: 'Phase pilote terminee', target_pct: 10, vehicles_converted_cumulative: 5 },
  { year: 2031, description: 'Montee en charge terminee', target_pct: 50, vehicles_converted_cumulative: 25 },
];

describe('TransitionPlanWizard', () => {
  it('renders wizard', async () => {
    const { TransitionPlanWizard } = await import('../TransitionPlanWizard');
    render(<TransitionPlanWizard />);
    expect(screen.getAllByText(/Flotte|G.n.rer|Plan/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('GanttChart', () => {
  it('renders SVG bars for phases', async () => {
    const { GanttChart } = await import('../GanttChart');
    render(<GanttChart phases={MOCK_PHASES} />);
    const svg = document.querySelector('svg');
    expect(svg).not.toBeNull();
  });
});

describe('BudgetAllocationChart', () => {
  it('renders budget chart', async () => {
    const { BudgetAllocationChart } = await import('../BudgetAllocationChart');
    render(<BudgetAllocationChart phases={MOCK_PHASES} />);
    expect(screen.getAllByText(/Budget|Co.t/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('MilestoneTracker', () => {
  it('renders milestone timeline', async () => {
    const { MilestoneTracker } = await import('../MilestoneTracker');
    render(<MilestoneTracker milestones={MOCK_MILESTONES} />);
    expect(screen.getAllByText(/2028|2031|pilote|charge/i).length).toBeGreaterThanOrEqual(1);
  });
});
