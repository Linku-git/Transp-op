/**
 * RetrainingPanel -- Cards for triggering ML model retraining,
 * with progress indicators, metric comparison, and history log.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import { useState } from 'react';

export interface RetrainingPanelProps {
  onRetrain: (modelType: string) => void;
  retrainingStatus: Record<string, { status: string; progress: number }>;
}

interface ModelCard {
  type: string;
  label: string;
  icon: string;
  description: string;
  lastTrained: string;
  currentMetrics: Record<string, number>;
  newMetrics: Record<string, number> | null;
  autoPromoteThreshold: number;
}

const INITIAL_MODELS: ModelCard[] = [
  {
    type: 'demand_forecast',
    label: 'Prevision Demande (LSTM)',
    icon: 'trending_up',
    description: '336 timesteps, is_ramadan, TensorFlow/Keras',
    lastTrained: '2026-04-10T08:30:00Z',
    currentMetrics: { mae: 12.4, rmse: 18.2 },
    newMetrics: null,
    autoPromoteThreshold: 15,
  },
  {
    type: 'driver_risk',
    label: 'Risque Conducteur (RF)',
    icon: 'security',
    description: '8 features telematiques, penalty scoring',
    lastTrained: '2026-04-11T14:15:00Z',
    currentMetrics: { accuracy: 0.91, f1: 0.88 },
    newMetrics: null,
    autoPromoteThreshold: 0.85,
  },
  {
    type: 'maintenance_predictor',
    label: 'Maintenance Predictive (IF)',
    icon: 'build',
    description: 'IsolationForest, anomaly detection telemetrie',
    lastTrained: '2026-04-09T22:00:00Z',
    currentMetrics: { accuracy: 0.87, f1: 0.83 },
    newMetrics: null,
    autoPromoteThreshold: 0.80,
  },
];

interface HistoryEntry {
  type: string;
  timestamp: string;
  status: string;
  version: number;
}

function formatMetricValue(key: string, value: number): string {
  if (key === 'accuracy' || key === 'f1') {
    return `${(value * 100).toFixed(1)}%`;
  }
  return value.toFixed(2);
}

export function RetrainingPanel({ onRetrain, retrainingStatus }: RetrainingPanelProps) {
  const [models] = useState<ModelCard[]>(INITIAL_MODELS);
  const [autoPromote, setAutoPromote] = useState<Record<string, boolean>>({
    demand_forecast: true,
    driver_risk: true,
    maintenance_predictor: false,
  });
  const [history] = useState<HistoryEntry[]>([
    { type: 'driver_risk', timestamp: '2026-04-11T14:15:00Z', status: 'promoted', version: 5 },
    { type: 'demand_forecast', timestamp: '2026-04-10T08:30:00Z', status: 'promoted', version: 4 },
    { type: 'maintenance_predictor', timestamp: '2026-04-09T22:00:00Z', status: 'ready', version: 3 },
    { type: 'demand_forecast', timestamp: '2026-04-08T09:00:00Z', status: 'retired', version: 3 },
    { type: 'driver_risk', timestamp: '2026-04-07T16:45:00Z', status: 'promoted', version: 4 },
  ]);

  return (
    <div
      className="space-y-4"
      data-testid="retraining-panel"
    >
      {/* Model cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {models.map((model) => {
          const status = retrainingStatus[model.type];
          const isTraining = status?.status === 'training';
          const progress = status?.progress ?? 0;

          return (
            <div
              key={model.type}
              className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5"
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-primary text-lg">
                    {model.icon}
                  </span>
                </div>
                <div className="min-w-0">
                  <h4 className="text-sm font-semibold text-on-surface truncate">
                    {model.label}
                  </h4>
                  <p className="text-[10px] text-on-surface-variant">
                    {model.description}
                  </p>
                </div>
              </div>

              {/* Last trained */}
              <div className="flex items-center gap-1.5 text-[10px] text-on-surface-variant mb-3">
                <span className="material-symbols-outlined text-sm">schedule</span>
                Dernier: {new Date(model.lastTrained).toLocaleDateString('fr-FR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>

              {/* Current metrics */}
              <div className="mb-3">
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                  Metriques actuelles
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {Object.entries(model.currentMetrics).map(([k, v]) => (
                    <span
                      key={k}
                      className="inline-flex items-center gap-1 text-[10px] bg-surface-container-high/50 rounded px-1.5 py-0.5"
                    >
                      <span className="font-bold uppercase text-on-surface-variant">{k}</span>
                      <span className="text-on-surface font-mono">{formatMetricValue(k, v)}</span>
                    </span>
                  ))}
                </div>
              </div>

              {/* New metrics comparison (after retraining) */}
              {model.newMetrics && (
                <div className="mb-3">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-green-700 mb-1">
                    Nouvelles metriques
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries(model.newMetrics).map(([k, v]) => (
                      <span
                        key={k}
                        className="inline-flex items-center gap-1 text-[10px] bg-green-50 rounded px-1.5 py-0.5"
                      >
                        <span className="font-bold uppercase text-green-700">{k}</span>
                        <span className="text-green-800 font-mono">{formatMetricValue(k, v)}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Progress bar */}
              {isTraining && (
                <div className="mb-3">
                  <div className="flex items-center justify-between text-[10px] text-on-surface-variant mb-1">
                    <span>Entrainement en cours...</span>
                    <span className="font-mono">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary to-primary-container rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                      data-testid={`progress-${model.type}`}
                    />
                  </div>
                </div>
              )}

              {/* Auto-promote toggle */}
              <div className="flex items-center justify-between mb-3 py-2 border-t border-outline-variant/10">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] text-on-surface-variant">Auto-promotion</span>
                  <span className="text-[10px] font-mono text-on-surface-variant opacity-60">
                    (seuil: {formatMetricValue(
                      Object.keys(model.currentMetrics)[0],
                      model.autoPromoteThreshold,
                    )})
                  </span>
                </div>
                <button
                  onClick={() =>
                    setAutoPromote((prev) => ({
                      ...prev,
                      [model.type]: !prev[model.type],
                    }))
                  }
                  className={`relative w-8 h-4.5 rounded-full transition-colors ${
                    autoPromote[model.type] ? 'bg-primary' : 'bg-outline-variant/30'
                  }`}
                  aria-label={`Toggle auto-promote for ${model.label}`}
                >
                  <span
                    className={`absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white shadow transition-transform ${
                      autoPromote[model.type] ? 'translate-x-4' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>

              {/* Retrain button */}
              <button
                onClick={() => onRetrain(model.type)}
                disabled={isTraining}
                className="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg py-2 text-xs font-semibold shadow-lg shadow-primary/20 disabled:opacity-50 flex items-center justify-center gap-1.5"
                data-testid={`retrain-${model.type}`}
              >
                {isTraining ? (
                  <>
                    <span className="material-symbols-outlined animate-spin text-sm">
                      progress_activity
                    </span>
                    Entrainement...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm">model_training</span>
                    Lancer le reentrainement
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Retraining history */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
          Historique des Entrainements
        </h3>
        {history.length === 0 ? (
          <p className="text-sm text-on-surface-variant text-center py-4">
            Aucun historique
          </p>
        ) : (
          <div className="space-y-1.5">
            {history.map((entry, idx) => {
              const modelCfg = INITIAL_MODELS.find((m) => m.type === entry.type);
              const statusColor =
                entry.status === 'promoted'
                  ? 'text-green-600'
                  : entry.status === 'retired'
                    ? 'text-gray-500'
                    : 'text-primary';
              return (
                <div
                  key={idx}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg bg-surface-container-high/30"
                >
                  <span className="material-symbols-outlined text-sm text-on-surface-variant">
                    {modelCfg?.icon || 'model_training'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-medium text-on-surface">
                      {modelCfg?.label || entry.type}
                    </span>
                    <span className="text-[10px] text-on-surface-variant ml-2">v{entry.version}</span>
                  </div>
                  <span className={`text-[10px] font-bold uppercase ${statusColor}`}>
                    {entry.status}
                  </span>
                  <span className="text-[10px] text-on-surface-variant">
                    {new Date(entry.timestamp).toLocaleDateString('fr-FR', {
                      day: '2-digit',
                      month: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
