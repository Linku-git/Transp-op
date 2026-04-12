/**
 * DemandForecastChart — Recharts AreaChart showing 48h demand forecast
 * with confidence band (upper/lower) and ligne filter.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useMemo } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { ForecastPoint } from '../../stores/operationsStore';

interface DemandForecastChartProps {
  data: ForecastPoint[];
  lignes?: { id: string; name: string }[];
  selectedLigneId: string | null;
  onSelectLigne: (id: string) => void;
}

export function DemandForecastChart({
  data,
  lignes = [],
  selectedLigneId,
  onSelectLigne,
}: DemandForecastChartProps) {
  const chartData = useMemo(
    () =>
      data.map((d) => ({
        ...d,
        time: new Date(d.timestamp).toLocaleTimeString('fr-FR', {
          hour: '2-digit',
          minute: '2-digit',
        }),
      })),
    [data],
  );

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5"
      data-testid="demand-forecast-chart"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Prevision Demande (48h)
        </h3>
        {lignes.length > 0 && (
          <select
            value={selectedLigneId || ''}
            onChange={(e) => onSelectLigne(e.target.value)}
            className="text-xs bg-surface-container-high/50 border-none rounded-lg px-2 py-1 text-on-surface"
          >
            {lignes.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {data.length === 0 ? (
        <div className="h-48 flex items-center justify-center text-on-surface-variant text-sm">
          <span className="material-symbols-outlined mr-2">show_chart</span>
          Aucune donnee de prevision
        </div>
      ) : (
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#c2c6d6"
                strokeOpacity={0.3}
              />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 8,
                  border: '1px solid #c2c6d6',
                }}
              />
              <Area
                type="monotone"
                dataKey="upper"
                stroke="none"
                fill="#0058be"
                fillOpacity={0.08}
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="none"
                fill="#fff"
                fillOpacity={1}
              />
              <Area
                type="monotone"
                dataKey="demand"
                stroke="#0058be"
                fill="#0058be"
                fillOpacity={0.15}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
