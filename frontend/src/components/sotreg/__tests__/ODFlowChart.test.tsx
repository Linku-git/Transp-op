import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Cell: () => <div />,
}));

describe('ODFlowChart', () => {
  it('renders Sankey/bar chart with OD data', async () => {
    const { ODFlowChart } = await import('../ODFlowChart');
    render(
      <ODFlowChart
        entries={[
          {
            id: 'od1',
            tenant_id: 't1',
            ligne_id: 'l1',
            origin_zone: 'Zone A',
            destination_zone: 'Zone B',
            flow_estimate: 120.5,
            distance_km: 15.3,
            gravity_score: 0.85,
            beta_used: 0.08,
            computed_at: '2026-04-10T08:00:00Z',
            created_at: '2026-04-10T08:00:00Z',
            updated_at: '2026-04-10T08:00:00Z',
          },
          {
            id: 'od2',
            tenant_id: 't1',
            ligne_id: 'l2',
            origin_zone: 'Zone C',
            destination_zone: 'Zone D',
            flow_estimate: 85.2,
            distance_km: 22.1,
            gravity_score: 0.62,
            beta_used: 0.08,
            computed_at: '2026-04-10T08:00:00Z',
            created_at: '2026-04-10T08:00:00Z',
            updated_at: '2026-04-10T08:00:00Z',
          },
        ]}
      />,
    );

    expect(screen.getByText(/Flux Origine-Destination/i)).toBeDefined();
    expect(screen.getByTestId('bar-chart')).toBeDefined();
  });

  it('renders empty state when no entries', async () => {
    const { ODFlowChart } = await import('../ODFlowChart');
    render(<ODFlowChart entries={[]} />);

    expect(screen.getByText(/Aucune matrice OD/i)).toBeDefined();
  });
});
