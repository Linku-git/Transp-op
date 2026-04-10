import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/api/sotreg', () => ({
  computeRangeCorrection: vi.fn(),
  computeTCO15Year: vi.fn(),
  computeBreakeven: vi.fn(),
  computeChargingOptimization: vi.fn(),
  computeIRVESizing: vi.fn(),
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  AreaChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Area: () => <div />,
  LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  ReferenceLine: () => <div />,
}));

describe('TechnologiesDashboardPage', () => {
  it('renders page title and all tab labels', async () => {
    const { TechnologiesDashboardPage } = await import('../TechnologiesDashboardPage');
    render(
      <MemoryRouter>
        <TechnologiesDashboardPage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Technologies/i)).toBeDefined();
    expect(screen.getAllByText(/Autonomie/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/TCO 15/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Seuil/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/IRVE/i).length).toBeGreaterThanOrEqual(1);
  });
});
