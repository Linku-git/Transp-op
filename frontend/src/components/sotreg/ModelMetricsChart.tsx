/**
 * ModelMetricsChart -- Recharts LineChart showing metric evolution
 * across model versions (MAE, RMSE, accuracy, F1).
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export interface MetricPoint {
  version: number;
  mae?: number;
  rmse?: number;
  accuracy?: number;
  f1?: number;
}

export interface ModelMetricsChartProps {
  data: MetricPoint[];
  modelType: string;
  onModelTypeChange: (type: string) => void;
}

const MODEL_TYPES = [
  { value: 'demand_forecast', label: 'Prevision Demande' },
  { value: 'driver_risk', label: 'Risque Conducteur' },
  { value: 'maintenance_predictor', label: 'Maintenance Predictive' },
];

const METRIC_COLORS: Record<string, string> = {
  mae: '#0058be',
  rmse: '#924700',
  accuracy: '#16a34a',
  f1: '#7c3aed',
};

const THRESHOLD_VALUES: Record<string, number> = {
  demand_forecast: 15,
  driver_risk: 0.85,
  maintenance_predictor: 0.80,
};

export function ModelMetricsChart({
  data,
  modelType,
  onModelTypeChange,
}: ModelMetricsChartProps) {
  const hasErrorMetrics = data.some((d) => d.mae !== undefined || d.rmse !== undefined);
  const hasClassMetrics = data.some((d) => d.accuracy !== undefined || d.f1 !== undefined);
  const threshold = THRESHOLD_VALUES[modelType];

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6"
      data-testid="model-metrics-chart"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Evolution Metriques
        </h3>
        <select
          value={modelType}
          onChange={(e) => onModelTypeChange(e.target.value)}
          className="text-xs bg-surface-container-high/50 border-none rounded-lg px-2 py-1 text-on-surface focus:ring-2 focus:ring-primary/20"
          data-testid="model-type-selector"
        >
          {MODEL_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-on-surface-variant text-sm">
          <span className="material-symbols-outlined mr-2">show_chart</span>
          Aucune donnee de metriques
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" strokeOpacity={0.3} />
              <XAxis
                dataKey="version"
                tick={{ fontSize: 10, fill: '#9ca3af' }}
                label={{ value: 'Version', position: 'insideBottom', offset: -5, fontSize: 10 }}
              />
              <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: '1px solid #c2c6d6',
                  backgroundColor: '#fff',
                }}
              />
              <Legend wrapperStyle={{ fontSize: 10 }} />
              {hasErrorMetrics && (
                <>
                  <Line
                    type="monotone"
                    dataKey="mae"
                    name="MAE"
                    stroke={METRIC_COLORS.mae}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="rmse"
                    name="RMSE"
                    stroke={METRIC_COLORS.rmse}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                    connectNulls
                  />
                </>
              )}
              {hasClassMetrics && (
                <>
                  <Line
                    type="monotone"
                    dataKey="accuracy"
                    name="Accuracy"
                    stroke={METRIC_COLORS.accuracy}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="f1"
                    name="F1 Score"
                    stroke={METRIC_COLORS.f1}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                    connectNulls
                  />
                </>
              )}
              {threshold !== undefined && (
                <ReferenceLine
                  y={threshold}
                  stroke="#ba1a1a"
                  strokeDasharray="5 5"
                  label={{
                    value: 'Seuil',
                    position: 'insideTopRight',
                    fontSize: 10,
                    fill: '#ba1a1a',
                  }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
