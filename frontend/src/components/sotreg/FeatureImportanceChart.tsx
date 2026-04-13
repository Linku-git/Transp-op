/**
 * FeatureImportanceChart -- Horizontal Recharts BarChart for RF/IF
 * feature importances, sorted descending with color gradient.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import { useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export interface FeatureImportance {
  name: string;
  importance: number;
}

export interface FeatureImportanceChartProps {
  features: FeatureImportance[];
  modelType: string;
  onModelTypeChange: (type: string) => void;
}

const MODEL_TABS = [
  { value: 'driver_risk', label: 'Random Forest (RF)', icon: 'forest' },
  { value: 'maintenance_predictor', label: 'Isolation Forest (IF)', icon: 'troubleshoot' },
];

const FEATURE_LABELS: Record<string, string> = {
  nb_alertes_vitesse: 'Alertes Vitesse',
  vitesse_max: 'Vitesse Max',
  nb_alertes_acceleration: 'Alertes Acceleration',
  vitesse_moyenne: 'Vitesse Moyenne',
  nb_alertes_freinage: 'Alertes Freinage',
  nb_alertes_geofencing: 'Alertes Geofencing',
  nb_alertes_temps: 'Alertes Temps',
  score_actuel: 'Score Actuel',
};

function interpolateColor(value: number, maxValue: number): string {
  const ratio = maxValue > 0 ? value / maxValue : 0;
  // From gray (#94a3b8) at 0 to primary blue (#0058be) at 1
  const r = Math.round(148 + (0 - 148) * ratio);
  const g = Math.round(163 + (88 - 163) * ratio);
  const b = Math.round(184 + (190 - 184) * ratio);
  return `rgb(${r}, ${g}, ${b})`;
}

export function FeatureImportanceChart({
  features,
  modelType,
  onModelTypeChange,
}: FeatureImportanceChartProps) {
  const sortedFeatures = useMemo(
    () =>
      [...features]
        .sort((a, b) => b.importance - a.importance)
        .map((f) => ({
          ...f,
          displayName: FEATURE_LABELS[f.name] || f.name,
        })),
    [features],
  );

  const maxImportance = useMemo(
    () => Math.max(...sortedFeatures.map((f) => f.importance), 0),
    [sortedFeatures],
  );

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6"
      data-testid="feature-importance-chart"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Importance des Features
        </h3>
      </div>

      {/* Model type tabs */}
      <div className="flex gap-2 mb-4">
        {MODEL_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onModelTypeChange(tab.value)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              modelType === tab.value
                ? 'bg-primary/10 text-primary'
                : 'text-on-surface-variant hover:bg-surface-container'
            }`}
            data-testid={`feature-tab-${tab.value}`}
          >
            <span className="material-symbols-outlined text-sm">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {features.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-on-surface-variant text-sm">
          <span className="material-symbols-outlined mr-2">data_array</span>
          Aucune feature disponible
        </div>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sortedFeatures}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" strokeOpacity={0.3} />
              <XAxis
                type="number"
                tick={{ fontSize: 10, fill: '#9ca3af' }}
                domain={[0, 'auto']}
              />
              <YAxis
                type="category"
                dataKey="displayName"
                tick={{ fontSize: 10, fill: '#424754' }}
                width={130}
              />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: '1px solid #c2c6d6',
                  backgroundColor: '#fff',
                }}
                formatter={(value: number) => [(value * 100).toFixed(1) + '%', 'Importance']}
              />
              <Bar dataKey="importance" radius={[0, 4, 4, 0]} maxBarSize={24}>
                {sortedFeatures.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={interpolateColor(entry.importance, maxImportance)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
