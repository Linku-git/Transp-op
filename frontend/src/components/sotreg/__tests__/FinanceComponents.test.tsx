import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@/api/sotreg', () => ({
  computeNPV: vi.fn(), computePayback: vi.fn(), computeInvestmentAnalysis: vi.fn(),
  computeCO2Valorization: vi.fn(), computePortfolioOptimize: vi.fn(),
  computeEfficientFrontier: vi.fn(), computeSupernetworkEquilibrium: vi.fn(),
}));
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div />, LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => <div />, ScatterChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Scatter: () => <div />, XAxis: () => <div />, YAxis: () => <div />,
  CartesianGrid: () => <div />, Tooltip: () => <div />, Legend: () => <div />,
  ReferenceLine: () => <div />, Cell: () => <div />,
}));

describe('NPVWaterfallChart', () => {
  it('renders with calculate button', async () => {
    const { NPVWaterfallChart } = await import('../NPVWaterfallChart');
    render(<NPVWaterfallChart />);
    expect(screen.getAllByText(/Calculer|VAN/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('PaybackTimelineChart', () => {
  it('renders with calculate button', async () => {
    const { PaybackTimelineChart } = await import('../PaybackTimelineChart');
    render(<PaybackTimelineChart />);
    expect(screen.getAllByText(/Calculer|Payback|Retour/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('CO2ValorizationPanel', () => {
  it('renders with CO2 controls', async () => {
    const { CO2ValorizationPanel } = await import('../CO2ValorizationPanel');
    render(<CO2ValorizationPanel />);
    expect(screen.getAllByText(/CO|Valoris|Carbone/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('EfficientFrontierChart', () => {
  it('renders with frontier controls', async () => {
    const { EfficientFrontierChart } = await import('../EfficientFrontierChart');
    render(<EfficientFrontierChart />);
    expect(screen.getAllByText(/Fronti|Portefeuille|Calculer/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('SupernetworkFlowDiagram', () => {
  it('renders with network controls', async () => {
    const { SupernetworkFlowDiagram } = await import('../SupernetworkFlowDiagram');
    render(<SupernetworkFlowDiagram />);
    expect(screen.getAllByText(/Calculer|Equilibre|Supernetwork|Reseau/i).length).toBeGreaterThanOrEqual(1);
  });
});
