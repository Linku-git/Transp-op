import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  CartesianGrid: () => null,
}));

describe('BarChart', () => {
  it('renders with data', async () => {
    const { BarChart } = await import('../BarChart');
    render(
      <BarChart
        data={[
          { label: 'Oui', value: 40 },
          { label: 'Non', value: 20 },
        ]}
        title="Potentiel"
      />,
    );

    expect(screen.getByText('Potentiel')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });
});
