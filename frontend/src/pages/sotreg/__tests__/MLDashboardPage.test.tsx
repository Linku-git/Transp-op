/**
 * Tests for MLDashboardPage and its sub-components.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';

/* ── Mock recharts ──────────────────────────────────────────────────────── */

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  LineChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="line-chart">{children}</div>
  ),
  Line: () => <div />,
  AreaChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="area-chart">{children}</div>
  ),
  Area: () => <div />,
  BarChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Bar: () => <div />,
  Cell: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
  ReferenceLine: () => <div />,
}));

/* ── Imports ────────────────────────────────────────────────────────────── */

import { ModelRegistryTable } from '../../../components/sotreg/ModelRegistryTable';
import { ModelMetricsChart } from '../../../components/sotreg/ModelMetricsChart';
import { FeatureImportanceChart } from '../../../components/sotreg/FeatureImportanceChart';
import { RetrainingPanel } from '../../../components/sotreg/RetrainingPanel';
import { PredictionMonitor } from '../../../components/sotreg/PredictionMonitor';
import type { MLModelResponse } from '../../../api/sotreg';
import type { MetricPoint } from '../../../components/sotreg/ModelMetricsChart';
import type { FeatureImportance } from '../../../components/sotreg/FeatureImportanceChart';
import type { PredictionPoint } from '../../../components/sotreg/PredictionMonitor';

/* ── Test data ──────────────────────────────────────────────────────────── */

const MOCK_MODELS: MLModelResponse[] = [
  {
    id: 'ml-001',
    tenant_id: 't1',
    model_type: 'demand_forecast',
    version: 4,
    status: 'promoted',
    metrics: { mae: 12.4, rmse: 18.2 },
    file_path: '/models/demand_v4.h5',
    trained_at: '2026-04-10T08:30:00Z',
    feature_names: ['hour', 'day_of_week'],
    created_at: '2026-04-10T08:00:00Z',
    updated_at: '2026-04-10T08:30:00Z',
  },
  {
    id: 'ml-002',
    tenant_id: 't1',
    model_type: 'driver_risk',
    version: 5,
    status: 'ready',
    metrics: { accuracy: 0.93, f1: 0.90 },
    file_path: '/models/risk_v5.joblib',
    trained_at: '2026-04-11T14:15:00Z',
    feature_names: ['nb_alertes_vitesse'],
    created_at: '2026-04-11T14:00:00Z',
    updated_at: '2026-04-11T14:15:00Z',
  },
  {
    id: 'ml-003',
    tenant_id: 't1',
    model_type: 'maintenance_predictor',
    version: 3,
    status: 'promoted',
    metrics: { accuracy: 0.87, f1: 0.83 },
    file_path: null,
    trained_at: '2026-04-09T22:00:00Z',
    feature_names: null,
    created_at: '2026-04-09T21:30:00Z',
    updated_at: '2026-04-09T22:00:00Z',
  },
];

const MOCK_METRICS: MetricPoint[] = [
  { version: 1, mae: 22.1, rmse: 30.5 },
  { version: 2, mae: 18.3, rmse: 25.1 },
  { version: 3, mae: 15.0, rmse: 21.4 },
  { version: 4, mae: 12.4, rmse: 18.2 },
  { version: 5, mae: 11.1, rmse: 16.8 },
];

const MOCK_FEATURES: FeatureImportance[] = [
  { name: 'nb_alertes_vitesse', importance: 0.28 },
  { name: 'vitesse_max', importance: 0.18 },
  { name: 'nb_alertes_acceleration', importance: 0.15 },
  { name: 'vitesse_moyenne', importance: 0.12 },
  { name: 'nb_alertes_freinage', importance: 0.10 },
];

const MOCK_PREDICTIONS: PredictionPoint[] = [
  { timestamp: '2026-04-12T10:00:00Z', predicted: 22.5, actual: 20.0 },
  { timestamp: '2026-04-12T11:00:00Z', predicted: 25.1, actual: 24.0 },
  { timestamp: '2026-04-12T12:00:00Z', predicted: 30.2, actual: 28.5 },
];

/* ── Tests ──────────────────────────────────────────────────────────────── */

describe('MLDashboardPage', () => {
  it('renders with 3 tabs (Models, Features, Retraining)', async () => {
    const mod = await import('../MLDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );
    expect(screen.getByTestId('ml-dashboard')).toBeDefined();
    expect(screen.getByTestId('tab-models')).toBeDefined();
    expect(screen.getByTestId('tab-features')).toBeDefined();
    expect(screen.getByTestId('tab-retraining')).toBeDefined();
    expect(screen.getByText('ML Operations')).toBeDefined();
  });
});

describe('ModelRegistryTable', () => {
  it('renders model rows with version and status', () => {
    render(
      <ModelRegistryTable
        models={MOCK_MODELS}
        onPromote={vi.fn()}
        onRetire={vi.fn()}
      />,
    );
    expect(screen.getByTestId('model-registry-table')).toBeDefined();
    expect(screen.getByText('v4')).toBeDefined();
    expect(screen.getByText('v5')).toBeDefined();
    expect(screen.getByText('v3')).toBeDefined();
    expect(screen.getByText('Pret')).toBeDefined();
    // Two "Promu" badges (demand_forecast and maintenance_predictor)
    expect(screen.getAllByText('Promu')).toHaveLength(2);
  });

  it('promote button triggers callback', () => {
    const onPromote = vi.fn();
    render(
      <ModelRegistryTable
        models={MOCK_MODELS}
        onPromote={onPromote}
        onRetire={vi.fn()}
      />,
    );
    // Only model ml-002 has status=ready => promote button
    const promoteBtn = screen.getByTestId('promote-ml-002');
    fireEvent.click(promoteBtn);
    expect(onPromote).toHaveBeenCalledWith('ml-002');
  });
});

describe('ModelMetricsChart', () => {
  it('renders LineChart with version data', () => {
    render(
      <ModelMetricsChart
        data={MOCK_METRICS}
        modelType="demand_forecast"
        onModelTypeChange={vi.fn()}
      />,
    );
    expect(screen.getByTestId('model-metrics-chart')).toBeDefined();
    expect(screen.getByTestId('line-chart')).toBeDefined();
    expect(screen.getByTestId('model-type-selector')).toBeDefined();
  });
});

describe('FeatureImportanceChart', () => {
  it('renders horizontal bars sorted by importance', () => {
    render(
      <FeatureImportanceChart
        features={MOCK_FEATURES}
        modelType="driver_risk"
        onModelTypeChange={vi.fn()}
      />,
    );
    expect(screen.getByTestId('feature-importance-chart')).toBeDefined();
    expect(screen.getByTestId('bar-chart')).toBeDefined();
    expect(screen.getByTestId('feature-tab-driver_risk')).toBeDefined();
    expect(screen.getByTestId('feature-tab-maintenance_predictor')).toBeDefined();
  });
});

describe('RetrainingPanel', () => {
  it('renders trigger button and progress indicator', () => {
    const onRetrain = vi.fn();
    render(
      <RetrainingPanel
        onRetrain={onRetrain}
        retrainingStatus={{
          demand_forecast: { status: 'training', progress: 45 },
        }}
      />,
    );
    expect(screen.getByTestId('retraining-panel')).toBeDefined();
    // Demand forecast is training
    expect(screen.getByTestId('progress-demand_forecast')).toBeDefined();
    // Driver risk and maintenance should have retrain buttons
    expect(screen.getByTestId('retrain-driver_risk')).toBeDefined();
    expect(screen.getByTestId('retrain-maintenance_predictor')).toBeDefined();
    // Click retrain on driver_risk
    fireEvent.click(screen.getByTestId('retrain-driver_risk'));
    expect(onRetrain).toHaveBeenCalledWith('driver_risk');
  });
});

describe('PredictionMonitor', () => {
  it('renders rolling accuracy chart', () => {
    render(
      <PredictionMonitor
        data={MOCK_PREDICTIONS}
        window="24h"
        onWindowChange={vi.fn()}
        driftDetected={false}
      />,
    );
    expect(screen.getByTestId('prediction-monitor')).toBeDefined();
    expect(screen.getByTestId('area-chart')).toBeDefined();
    expect(screen.getByTestId('window-24h')).toBeDefined();
    expect(screen.getByTestId('window-7d')).toBeDefined();
    expect(screen.getByTestId('window-30d')).toBeDefined();
    // MAPE should be displayed
    expect(screen.getByText(/MAPE:/)).toBeDefined();
  });
});

describe('Tab switching', () => {
  it('displays correct panel content when switching tabs', async () => {
    const mod = await import('../MLDashboardPage');
    const Page = mod.default;
    render(
      <MemoryRouter>
        <Page />
      </MemoryRouter>,
    );

    // Models tab is active by default
    expect(screen.getByTestId('tab-panel-models')).toBeDefined();

    // Switch to Features tab
    fireEvent.click(screen.getByTestId('tab-features'));
    expect(screen.getByTestId('tab-panel-features')).toBeDefined();

    // Switch to Retraining tab
    fireEvent.click(screen.getByTestId('tab-retraining'));
    expect(screen.getByTestId('tab-panel-retraining')).toBeDefined();
  });
});
