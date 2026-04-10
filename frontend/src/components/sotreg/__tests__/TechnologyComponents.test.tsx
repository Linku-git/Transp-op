import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@/api/sotreg', () => ({
  computeRangeCorrection: vi.fn(),
  computeTCO15Year: vi.fn(),
  computeBreakeven: vi.fn(),
  computeChargingOptimization: vi.fn(),
  computeIRVESizing: vi.fn(),
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  AreaChart: ({ children }: { children: React.ReactNode }) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div />,
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  ReferenceLine: () => <div />,
}));

describe('RangeCorrectionPanel', () => {
  it('renders with calculate button', async () => {
    const { RangeCorrectionPanel } = await import('../RangeCorrectionPanel');
    render(<RangeCorrectionPanel />);
    expect(screen.getByText(/Calculer/i)).toBeDefined();
  });
});

describe('TCO15YearChart', () => {
  it('renders TCO form with calculate button', async () => {
    const { TCO15YearChart } = await import('../TCO15YearChart');
    render(<TCO15YearChart />);
    expect(screen.getAllByText(/TCO/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Calculer TCO/i)).toBeDefined();
  });
});

describe('BreakevenChart', () => {
  it('renders breakeven form', async () => {
    const { BreakevenChart } = await import('../BreakevenChart');
    render(<BreakevenChart />);
    expect(screen.getAllByText(/Seuil/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('IRVESizingWizard', () => {
  it('renders wizard first step', async () => {
    const { IRVESizingWizard } = await import('../IRVESizingWizard');
    render(<IRVESizingWizard />);
    expect(screen.getAllByText(/Flotte/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('ChargingScheduleTimeline', () => {
  it('renders charging form', async () => {
    const { ChargingScheduleTimeline } = await import('../ChargingScheduleTimeline');
    render(<ChargingScheduleTimeline />);
    expect(screen.getAllByText(/SOC/i).length).toBeGreaterThanOrEqual(1);
  });
});
