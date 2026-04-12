/**
 * Tests for OperationsDashboardPage and its sub-components.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';

vi.mock('@/hooks/useSocketIO', () => ({
  useSocketIO: () => ({
    status: 'disconnected',
    positions: new Map(),
    alerts: [],
    subscribe: vi.fn(),
    unsubscribe: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
  }),
}));

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  AreaChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="area-chart">{children}</div>
  ),
  Area: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
}));

describe('OperationsDashboardPage', () => {
  it('renders with all sections', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('operations-dashboard')).toBeDefined();
    expect(screen.getByText('Operations Temps Reel')).toBeDefined();
  });

  it('renders live fleet map', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('live-fleet-map')).toBeDefined();
  });

  it('renders demand forecast chart', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('demand-forecast-chart')).toBeDefined();
  });

  it('renders driver risk heatmap', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('driver-risk-heatmap')).toBeDefined();
  });

  it('renders route optimization panel with 3 strategies', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('route-optimization-panel')).toBeDefined();
    expect(screen.getByText('OR-Tools CVRP')).toBeDefined();
    expect(screen.getByText('Clarke & Wright')).toBeDefined();
    expect(screen.getByText('Algorithme Genetique')).toBeDefined();
  });

  it('renders alert feed', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('alert-feed')).toBeDefined();
  });

  it('shows connection status indicator', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByText('disconnected')).toBeDefined();
  });

  it('renders driver risk list sorted by score', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByText('Ahmed Tazi')).toBeDefined();
    expect(screen.getByText('Hassan Ouali')).toBeDefined();
  });

  it('shows risk category filter buttons', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByText('Faible')).toBeDefined();
    expect(screen.getByText('Critique')).toBeDefined();
  });

  it('shows forecast data in chart area', async () => {
    const mod = await import('../OperationsDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Prevision Demande/)).toBeDefined();
  });
});
