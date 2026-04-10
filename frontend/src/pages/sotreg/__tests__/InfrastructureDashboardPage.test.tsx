import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@/api/sotreg', () => ({
  generateStops: vi.fn(),
  computeStopCapacity: vi.fn(),
  computeDepotCostEstimate: vi.fn(),
  computeDepotLayout: vi.fn(),
}));

vi.mock('@vis.gl/react-google-maps', () => ({
  APIProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Map: ({ children }: { children?: React.ReactNode }) => <div data-testid="google-map">{children}</div>,
  AdvancedMarker: () => <div data-testid="map-marker" />,
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  Cell: () => <div />,
}));

describe('InfrastructureDashboardPage', () => {
  it('renders with all tabs', async () => {
    const { InfrastructureDashboardPage } = await import('../InfrastructureDashboardPage');
    render(
      <MemoryRouter>
        <InfrastructureDashboardPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByText(/Infrastructure/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Arr.ts/i).length).toBeGreaterThanOrEqual(1);
  });
});
