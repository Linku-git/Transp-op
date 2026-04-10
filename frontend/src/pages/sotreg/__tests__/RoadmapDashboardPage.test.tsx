import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/api/sotreg', () => ({ generateTransitionPlan: vi.fn() }));
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => <div />, XAxis: () => <div />, YAxis: () => <div />,
  CartesianGrid: () => <div />, Tooltip: () => <div />, Legend: () => <div />,
}));

describe('RoadmapDashboardPage', () => {
  it('renders with tabs', async () => {
    const { RoadmapDashboardPage } = await import('../RoadmapDashboardPage');
    render(<MemoryRouter><RoadmapDashboardPage /></MemoryRouter>);
    expect(screen.getAllByText(/Feuille|Route|Planification|Budget|Jalon/i).length).toBeGreaterThanOrEqual(1);
  });
});
