import { useCallback, useState } from 'react';
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { NormalizedAlternative } from '../../types/sotreg';
import { MCDA_ALT_COLORS, MCDA_CRITERIA, MCDA_CRITERIA_LABELS } from '../../types/sotreg';

interface RadarComparisonChartProps {
  alternatives: NormalizedAlternative[];
}

export function RadarComparisonChart({ alternatives }: RadarComparisonChartProps) {
  const [visible, setVisible] = useState<Set<string>>(
    () => new Set(alternatives.map((a) => a.name)),
  );

  const toggleAlt = useCallback((name: string) => {
    setVisible((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        if (next.size > 1) next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  }, []);

  // Reshape data for Recharts: one entry per criterion, one key per alternative
  const data = MCDA_CRITERIA.map((c) => {
    const entry: Record<string, string | number> = {
      criterion: MCDA_CRITERIA_LABELS[c],
    };
    for (const alt of alternatives) {
      entry[alt.name] = alt.normalized_values[c] ?? 0;
    }
    return entry;
  });

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Graphique radar (6 axes)
      </h3>

      <div className="h-[340px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
            <PolarGrid stroke="#c2c6d6" strokeOpacity={0.4} />
            <PolarAngleAxis
              dataKey="criterion"
              tick={{ fontSize: 11, fill: '#424754', fontWeight: 600 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 5]}
              tickCount={6}
              tick={{ fontSize: 9, fill: '#9ca3af' }}
            />
            {alternatives.map((alt, i) =>
              visible.has(alt.name) ? (
                <Radar
                  key={alt.name}
                  name={alt.name}
                  dataKey={alt.name}
                  stroke={MCDA_ALT_COLORS[i % MCDA_ALT_COLORS.length]}
                  fill={MCDA_ALT_COLORS[i % MCDA_ALT_COLORS.length]}
                  fillOpacity={0.12}
                  strokeWidth={2}
                />
              ) : null,
            )}
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #c2c6d6',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Legend / toggles */}
      <div className="flex flex-wrap gap-3 mt-3 justify-center">
        {alternatives.map((alt, i) => {
          const color = MCDA_ALT_COLORS[i % MCDA_ALT_COLORS.length];
          const active = visible.has(alt.name);
          return (
            <button
              key={alt.name}
              type="button"
              onClick={() => toggleAlt(alt.name)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${
                active
                  ? 'border-transparent shadow-sm'
                  : 'border-outline-variant/20 opacity-40'
              }`}
              style={{
                backgroundColor: active ? `${color}15` : undefined,
                color: active ? color : '#9ca3af',
              }}
            >
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: color, opacity: active ? 1 : 0.3 }}
              />
              {alt.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
