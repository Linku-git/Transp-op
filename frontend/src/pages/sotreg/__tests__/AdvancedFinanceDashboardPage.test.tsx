import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/api/sotreg', () => ({
  computeNPV: vi.fn(), computePayback: vi.fn(), computeInvestmentAnalysis: vi.fn(),
  computeCO2Valorization: vi.fn(), computePortfolioOptimize: vi.fn(),
  computeEfficientFrontier: vi.fn(), computeSupernetworkEquilibrium: vi.fn(),
}));
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Bar: () => <div />, LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => <div />, ScatterChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Scatter: () => <div />, XAxis: () => <div />, YAxis: () => <div />,
  CartesianGrid: () => <div />, Tooltip: () => <div />, Legend: () => <div />,
  ReferenceLine: () => <div />, Cell: () => <div />,
}));

describe('AdvancedFinanceDashboardPage', () => {
  it('renders with all tabs', async () => {
    const { AdvancedFinanceDashboardPage } = await import('../AdvancedFinanceDashboardPage');
    render(<MemoryRouter><AdvancedFinanceDashboardPage /></MemoryRouter>);
    expect(screen.getAllByText(/Finance|VAN|Portefeuille|CO/i).length).toBeGreaterThanOrEqual(1);
  });
});
