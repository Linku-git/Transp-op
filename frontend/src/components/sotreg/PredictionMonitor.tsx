/**
 * PredictionMonitor -- Recharts AreaChart showing predicted vs actual
 * values over time with rolling window selector and drift detection.
 *
 * Session 123 -- ML Dashboard & Retraining UI.
 */
import { useMemo } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export interface PredictionPoint {
  timestamp: string;
  predicted: number;
  actual: number;
}

export interface PredictionMonitorProps {
  data: PredictionPoint[];
  window: string;
  onWindowChange: (w: string) => void;
  driftDetected: boolean;
}

const WINDOWS = [
  { value: '24h', label: '24h' },
  { value: '7d', label: '7 jours' },
  { value: '30d', label: '30 jours' },
];

export function PredictionMonitor({
  data,
  window: selectedWindow,
  onWindowChange,
  driftDetected,
}: PredictionMonitorProps) {
  const chartData = useMemo(
    () =>
      data.map((d) => ({
        ...d,
        time: new Date(d.timestamp).toLocaleString('fr-FR', {
          day: '2-digit',
          month: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        }),
        error: Math.abs(d.predicted - d.actual),
      })),
    [data],
  );

  const mape = useMemo(() => {
    if (data.length === 0) return 0;
    const sum = data.reduce((acc, d) => {
      if (d.actual === 0) return acc;
      return acc + Math.abs(d.predicted - d.actual) / Math.abs(d.actual);
    }, 0);
    return (sum / data.length) * 100;
  }, [data]);

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6"
      data-testid="prediction-monitor"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            Predit vs Reel
          </h3>
          {driftDetected && (
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-error-container/30 text-error"
              data-testid="drift-badge"
            >
              <span className="material-symbols-outlined text-xs">warning</span>
              Drift detecte
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-on-surface-variant font-mono">
            MAPE: {mape.toFixed(1)}%
          </span>
          <div className="flex gap-1">
            {WINDOWS.map((w) => (
              <button
                key={w.value}
                onClick={() => onWindowChange(w.value)}
                className={`px-2 py-1 rounded text-[10px] font-medium transition-colors ${
                  selectedWindow === w.value
                    ? 'bg-primary/10 text-primary'
                    : 'text-on-surface-variant hover:bg-surface-container'
                }`}
                data-testid={`window-${w.value}`}
              >
                {w.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-on-surface-variant text-sm">
          <span className="material-symbols-outlined mr-2">monitoring</span>
          Aucune donnee de prediction
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" strokeOpacity={0.3} />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#9ca3af' }} />
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
              <Area
                type="monotone"
                dataKey="predicted"
                name="Predit"
                stroke="#0058be"
                fill="#0058be"
                fillOpacity={0.1}
                strokeWidth={2}
                dot={false}
              />
              <Area
                type="monotone"
                dataKey="actual"
                name="Reel"
                stroke="#16a34a"
                fill="#16a34a"
                fillOpacity={0.05}
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
