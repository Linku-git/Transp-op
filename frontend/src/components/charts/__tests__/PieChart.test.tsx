import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock recharts to avoid canvas/SVG issues in jsdom
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => null,
  Tooltip: () => null,
  Legend: () => null,
}));

describe('PieChart', () => {
  it('renders with data', async () => {
    const { PieChart } = await import('../PieChart');
    render(
      <PieChart
        data={[
          { name: 'Voiture', value: 60 },
          { name: 'Bus', value: 30 },
          { name: 'Velo', value: 10 },
        ]}
        title="Distribution"
      />,
    );

    expect(screen.getByText('Distribution')).toBeInTheDocument();
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
  });
});
