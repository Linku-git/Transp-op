/**
 * ModelRegistryTable -- Table of all registered ML models with status badges,
 * metrics summary, and promote/retire action buttons.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import type { MLModelResponse } from '../../api/sotreg';

export interface ModelRegistryTableProps {
  models: MLModelResponse[];
  onPromote: (modelId: string) => void;
  onRetire: (modelId: string) => void;
}

const STATUS_CONFIG: Record<string, { label: string; bg: string; text: string }> = {
  training: { label: 'En cours', bg: 'bg-amber-50', text: 'text-amber-700' },
  ready: { label: 'Pret', bg: 'bg-primary/10', text: 'text-primary' },
  promoted: { label: 'Promu', bg: 'bg-green-50', text: 'text-green-700' },
  retired: { label: 'Retire', bg: 'bg-gray-100', text: 'text-gray-500' },
};

const MODEL_TYPE_LABELS: Record<string, string> = {
  demand_forecast: 'Prevision Demande (LSTM)',
  driver_risk: 'Risque Conducteur (RF)',
  maintenance_predictor: 'Maintenance Predictive (IF)',
};

function formatMetric(key: string, value: number): string {
  if (key === 'accuracy' || key === 'f1') {
    return `${(value * 100).toFixed(1)}%`;
  }
  return value.toFixed(3);
}

export function ModelRegistryTable({ models, onPromote, onRetire }: ModelRegistryTableProps) {
  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden"
      data-testid="model-registry-table"
    >
      <div className="px-6 py-4 border-b border-outline-variant/10">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Registre des Modeles
        </h3>
      </div>

      {models.length === 0 ? (
        <div className="px-6 py-10 text-center text-sm text-on-surface-variant">
          <span className="material-symbols-outlined text-2xl block mb-2">model_training</span>
          Aucun modele enregistre
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full" data-testid="model-table">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Modele
                </th>
                <th className="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Version
                </th>
                <th className="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Statut
                </th>
                <th className="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Metriques
                </th>
                <th className="px-4 py-3 text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Entraine le
                </th>
                <th className="px-4 py-3 text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {models.map((model) => {
                const statusCfg = STATUS_CONFIG[model.status] || STATUS_CONFIG.training;
                return (
                  <tr key={model.id} className="hover:bg-surface-bright transition-colors">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-on-surface">
                        {MODEL_TYPE_LABELS[model.model_type] || model.model_type}
                      </div>
                      <div className="text-[10px] text-on-surface-variant font-mono">
                        {model.model_type}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-semibold text-on-surface">
                        v{model.version}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${statusCfg.bg} ${statusCfg.text}`}
                      >
                        {statusCfg.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {model.metrics ? (
                        <div className="flex flex-wrap gap-1.5">
                          {Object.entries(model.metrics).map(([k, v]) => (
                            <span
                              key={k}
                              className="inline-flex items-center gap-1 text-[10px] bg-surface-container-high/50 rounded px-1.5 py-0.5"
                            >
                              <span className="font-bold uppercase text-on-surface-variant">
                                {k}
                              </span>
                              <span className="text-on-surface font-mono">
                                {formatMetric(k, v)}
                              </span>
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-on-surface-variant">--</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-xs text-on-surface-variant">
                      {model.trained_at
                        ? new Date(model.trained_at).toLocaleDateString('fr-FR', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : '--'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {model.status === 'ready' && (
                          <button
                            onClick={() => onPromote(model.id)}
                            className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-bold uppercase rounded-lg bg-green-50 text-green-700 hover:bg-green-100 transition-colors"
                            data-testid={`promote-${model.id}`}
                          >
                            <span className="material-symbols-outlined text-sm">
                              arrow_upward
                            </span>
                            Promouvoir
                          </button>
                        )}
                        {model.status === 'promoted' && (
                          <button
                            onClick={() => onRetire(model.id)}
                            className="inline-flex items-center gap-1 px-2 py-1 text-[10px] font-bold uppercase rounded-lg bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors"
                            data-testid={`retire-${model.id}`}
                          >
                            <span className="material-symbols-outlined text-sm">
                              archive
                            </span>
                            Retirer
                          </button>
                        )}
                        {model.status !== 'ready' && model.status !== 'promoted' && (
                          <span className="text-[10px] text-on-surface-variant">--</span>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
