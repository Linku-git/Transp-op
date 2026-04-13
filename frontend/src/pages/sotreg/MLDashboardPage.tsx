/**
 * MLDashboardPage -- ML Operations dashboard for model monitoring,
 * retraining triggers, and feature importance visualization.
 *
 * 3 tabs: Models, Features, Retraining.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import { useCallback, useMemo, useState } from 'react';
import { ModelRegistryTable } from '../../components/sotreg/ModelRegistryTable';
import { ModelMetricsChart } from '../../components/sotreg/ModelMetricsChart';
import { FeatureImportanceChart } from '../../components/sotreg/FeatureImportanceChart';
import { PredictionMonitor } from '../../components/sotreg/PredictionMonitor';
import { RetrainingPanel } from '../../components/sotreg/RetrainingPanel';
import type { MLModelResponse } from '../../api/sotreg';
import type { MetricPoint } from '../../components/sotreg/ModelMetricsChart';
import type { FeatureImportance } from '../../components/sotreg/FeatureImportanceChart';
import type { PredictionPoint } from '../../components/sotreg/PredictionMonitor';

/* ── Demo data ──────────────────────────────────────────────────────────── */

const DEMO_MODELS: MLModelResponse[] = [
  {
    id: 'ml-001',
    tenant_id: 't1',
    model_type: 'demand_forecast',
    version: 4,
    status: 'promoted',
    metrics: { mae: 12.4, rmse: 18.2 },
    file_path: '/models/demand_forecast_v4.h5',
    trained_at: '2026-04-10T08:30:00Z',
    feature_names: ['hour', 'day_of_week', 'is_ramadan', 'temperature', 'rain'],
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
    file_path: '/models/driver_risk_v5.joblib',
    trained_at: '2026-04-11T14:15:00Z',
    feature_names: [
      'nb_alertes_vitesse',
      'vitesse_max',
      'nb_alertes_acceleration',
      'vitesse_moyenne',
      'nb_alertes_freinage',
      'nb_alertes_geofencing',
      'nb_alertes_temps',
      'score_actuel',
    ],
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
    file_path: '/models/maintenance_v3.joblib',
    trained_at: '2026-04-09T22:00:00Z',
    feature_names: ['vibration', 'temperature_moteur', 'pression_pneu', 'km_total'],
    created_at: '2026-04-09T21:30:00Z',
    updated_at: '2026-04-09T22:00:00Z',
  },
];

const DEMO_METRICS_DEMAND: MetricPoint[] = [
  { version: 1, mae: 22.1, rmse: 30.5 },
  { version: 2, mae: 18.3, rmse: 25.1 },
  { version: 3, mae: 15.0, rmse: 21.4 },
  { version: 4, mae: 12.4, rmse: 18.2 },
  { version: 5, mae: 11.1, rmse: 16.8 },
];

const DEMO_METRICS_RISK: MetricPoint[] = [
  { version: 1, accuracy: 0.72, f1: 0.68 },
  { version: 2, accuracy: 0.79, f1: 0.75 },
  { version: 3, accuracy: 0.84, f1: 0.81 },
  { version: 4, accuracy: 0.91, f1: 0.88 },
  { version: 5, accuracy: 0.93, f1: 0.90 },
];

const DEMO_METRICS_MAINT: MetricPoint[] = [
  { version: 1, accuracy: 0.75, f1: 0.70 },
  { version: 2, accuracy: 0.82, f1: 0.77 },
  { version: 3, accuracy: 0.87, f1: 0.83 },
];

const DEMO_METRICS: Record<string, MetricPoint[]> = {
  demand_forecast: DEMO_METRICS_DEMAND,
  driver_risk: DEMO_METRICS_RISK,
  maintenance_predictor: DEMO_METRICS_MAINT,
};

const DEMO_FEATURES_RF: FeatureImportance[] = [
  { name: 'nb_alertes_vitesse', importance: 0.28 },
  { name: 'vitesse_max', importance: 0.18 },
  { name: 'nb_alertes_acceleration', importance: 0.15 },
  { name: 'vitesse_moyenne', importance: 0.12 },
  { name: 'nb_alertes_freinage', importance: 0.10 },
  { name: 'nb_alertes_geofencing', importance: 0.08 },
  { name: 'nb_alertes_temps', importance: 0.05 },
  { name: 'score_actuel', importance: 0.04 },
];

const DEMO_FEATURES_IF: FeatureImportance[] = [
  { name: 'vibration', importance: 0.32 },
  { name: 'temperature_moteur', importance: 0.25 },
  { name: 'pression_pneu', importance: 0.20 },
  { name: 'km_total', importance: 0.12 },
  { name: 'consommation_carburant', importance: 0.06 },
  { name: 'heures_moteur', importance: 0.05 },
];

const DEMO_FEATURES: Record<string, FeatureImportance[]> = {
  driver_risk: DEMO_FEATURES_RF,
  maintenance_predictor: DEMO_FEATURES_IF,
};

function generatePredictionData(count: number): PredictionPoint[] {
  const now = Date.now();
  return Array.from({ length: count }, (_, i) => {
    const actual = 20 + Math.sin(i / 6) * 10 + Math.random() * 4;
    const predicted = actual + (Math.random() - 0.5) * 6;
    return {
      timestamp: new Date(now - (count - i) * 3600000).toISOString(),
      predicted: Math.round(predicted * 10) / 10,
      actual: Math.round(actual * 10) / 10,
    };
  });
}

const DEMO_PREDICTIONS: Record<string, PredictionPoint[]> = {
  '24h': generatePredictionData(24),
  '7d': generatePredictionData(168),
  '30d': generatePredictionData(720),
};

/* ── Tabs ───────────────────────────────────────────────────────────────── */

type TabKey = 'models' | 'features' | 'retraining';

const TABS: { key: TabKey; label: string; icon: string }[] = [
  { key: 'models', label: 'Modeles', icon: 'model_training' },
  { key: 'features', label: 'Features', icon: 'data_array' },
  { key: 'retraining', label: 'Reentrainement', icon: 'replay' },
];

/* ── Page Component ─────────────────────────────────────────────────────── */

export default function MLDashboardPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('models');
  const [metricsModelType, setMetricsModelType] = useState('demand_forecast');
  const [featureModelType, setFeatureModelType] = useState('driver_risk');
  const [predictionWindow, setPredictionWindow] = useState('24h');
  const [retrainingStatus, setRetrainingStatus] = useState<
    Record<string, { status: string; progress: number }>
  >({});

  const activeModels = useMemo(
    () => DEMO_MODELS.filter((m) => m.status === 'promoted' || m.status === 'ready'),
    [],
  );

  const needsRetrain = useMemo(
    () =>
      DEMO_MODELS.filter((m) => {
        if (!m.trained_at) return true;
        const daysSinceTrained =
          (Date.now() - new Date(m.trained_at).getTime()) / (1000 * 60 * 60 * 24);
        return daysSinceTrained > 3;
      }),
    [],
  );

  const handlePromote = useCallback((modelId: string) => {
    // In production, call promoteModel(modelId)
    void modelId;
  }, []);

  const handleRetire = useCallback((modelId: string) => {
    // In production, call retireModel(modelId)
    void modelId;
  }, []);

  const handleRetrain = useCallback((modelType: string) => {
    setRetrainingStatus((prev) => ({
      ...prev,
      [modelType]: { status: 'training', progress: 0 },
    }));

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setRetrainingStatus((prev) => ({
          ...prev,
          [modelType]: { status: 'complete', progress: 100 },
        }));
      } else {
        setRetrainingStatus((prev) => ({
          ...prev,
          [modelType]: { status: 'training', progress },
        }));
      }
    }, 500);
  }, []);

  const currentMetrics = DEMO_METRICS[metricsModelType] || [];
  const currentFeatures = DEMO_FEATURES[featureModelType] || [];
  const currentPredictions = DEMO_PREDICTIONS[predictionWindow] || [];
  const driftDetected = predictionWindow === '30d';

  return (
    <div
      className="flex flex-col gap-4 p-4 max-w-[1600px] mx-auto"
      data-testid="ml-dashboard"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">ML Operations</h1>
          <p className="text-sm text-on-surface-variant">
            Module M8 -- Registre, metriques et reentrainement des modeles
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* Health summary */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-50">
              <span className="material-symbols-outlined text-sm text-green-600">
                check_circle
              </span>
              <span className="text-xs font-medium text-green-700">
                {activeModels.length} actifs
              </span>
            </div>
            {needsRetrain.length > 0 && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-50">
                <span className="material-symbols-outlined text-sm text-amber-600">
                  update
                </span>
                <span className="text-xs font-medium text-amber-700">
                  {needsRetrain.length} a reentrainer
                </span>
              </div>
            )}
          </div>
          {/* Last updated */}
          <div className="text-[10px] text-on-surface-variant">
            <span className="material-symbols-outlined text-xs align-middle mr-0.5">
              schedule
            </span>
            {new Date().toLocaleTimeString('fr-FR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-container rounded-lg p-1">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-primary/10 text-primary'
                : 'text-on-surface-variant hover:bg-surface-container-high/50'
            }`}
            data-testid={`tab-${tab.key}`}
          >
            <span className="material-symbols-outlined text-lg">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'models' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="tab-panel-models">
          <div className="lg:col-span-2">
            <ModelRegistryTable
              models={DEMO_MODELS}
              onPromote={handlePromote}
              onRetire={handleRetire}
            />
          </div>
          <div className="lg:col-span-2">
            <ModelMetricsChart
              data={currentMetrics}
              modelType={metricsModelType}
              onModelTypeChange={setMetricsModelType}
            />
          </div>
        </div>
      )}

      {activeTab === 'features' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="tab-panel-features">
          <FeatureImportanceChart
            features={currentFeatures}
            modelType={featureModelType}
            onModelTypeChange={setFeatureModelType}
          />
          <PredictionMonitor
            data={currentPredictions}
            window={predictionWindow}
            onWindowChange={setPredictionWindow}
            driftDetected={driftDetected}
          />
        </div>
      )}

      {activeTab === 'retraining' && (
        <div data-testid="tab-panel-retraining">
          <RetrainingPanel
            onRetrain={handleRetrain}
            retrainingStatus={retrainingStatus}
          />
        </div>
      )}
    </div>
  );
}
