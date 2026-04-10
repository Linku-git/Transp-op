import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

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

describe('StopGeneratorPanel', () => {
  it('renders with generate button', async () => {
    const { StopGeneratorPanel } = await import('../StopGeneratorPanel');
    render(<StopGeneratorPanel />);
    expect(screen.getAllByText(/G.n.rer/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('StopCapacityTable', () => {
  it('renders with analyze button', async () => {
    const { StopCapacityTable } = await import('../StopCapacityTable');
    render(<StopCapacityTable />);
    expect(screen.getAllByText(/Analy|Capacit/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('DepotLayoutViewer', () => {
  it('renders with plan button', async () => {
    const { DepotLayoutViewer } = await import('../DepotLayoutViewer');
    render(<DepotLayoutViewer />);
    expect(screen.getAllByText(/Planifier|D.p.t|Layout/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('IRVECostBreakdown', () => {
  it('renders with estimate button', async () => {
    const { IRVECostBreakdown } = await import('../IRVECostBreakdown');
    render(<IRVECostBreakdown />);
    expect(screen.getAllByText(/Estimer|Co.t/i).length).toBeGreaterThanOrEqual(1);
  });
});
