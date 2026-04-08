import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface TrendPoint {
  date: string;
  compliance_pct: number;
}

export function ComplianceTrendChart({
  data,
  targetPct = 95,
  period = 'day',
  onPeriodChange,
}: {
  data: TrendPoint[];
  targetPct?: number;
  period?: string;
  onPeriodChange?: (period: string) => void;
}) {
  const periods = [
    { key: 'day', label: 'Jour' },
    { key: 'week', label: 'Semaine' },
    { key: 'month', label: 'Mois' },
  ];

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Tendance conformité
        </p>
        {onPeriodChange && (
          <div className="flex gap-1">
            {periods.map((p) => (
              <button
                key={p.key}
                onClick={() => onPeriodChange(p.key)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  period === p.key
                    ? 'bg-primary/10 text-primary'
                    : 'text-on-surface-variant hover:bg-surface-container-high'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {data.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-12">Pas de données</p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(215,228,236,0.2)" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: '#72767F' }}
              tickFormatter={(v) => v.slice(5)}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10, fill: '#72767F' }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Conformité']}
              contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
            />
            <ReferenceLine
              y={targetPct}
              stroke="#0058be"
              strokeDasharray="4 4"
              label={{ value: `Cible ${targetPct}%`, fill: '#0058be', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="compliance_pct"
              stroke="#0058be"
              strokeWidth={2}
              dot={{ r: 3, fill: '#0058be' }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
