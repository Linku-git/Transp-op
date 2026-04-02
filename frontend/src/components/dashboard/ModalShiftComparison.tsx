import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface ModalShiftComparisonProps {
  beforeAfter: {
    before: Record<string, number>;
    after: Record<string, number>;
  };
}

const MODE_COLORS: Record<string, string> = {
  voiture: '#6b7280',
  transport_commun: '#0058be',
  transport_entreprise: '#2170e4',
  velo: '#16a34a',
  marche: '#22c55e',
  covoiturage: '#495e8a',
};

function getModeColor(mode: string): string {
  return MODE_COLORS[mode] ?? '#924700';
}

interface ComparisonTooltipPayload {
  value: number;
  name: string;
  color: string;
}

interface ComparisonTooltipProps {
  active?: boolean;
  label?: string;
  payload?: ComparisonTooltipPayload[];
}

function ComparisonTooltip({ active, label, payload }: ComparisonTooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
      <p className="font-sans text-xs font-medium text-on-surface-variant mb-1">
        {label}
      </p>
      {payload.map((entry) => (
        <p key={entry.name} className="font-sans text-xs">
          <span style={{ color: entry.color }}>{entry.name}</span>: {entry.value}%
        </p>
      ))}
    </div>
  );
}

export function ModalShiftComparison({ beforeAfter }: ModalShiftComparisonProps) {
  const { t } = useTranslation();

  const { chartData, allModes } = useMemo(() => {
    const modes = new Set<string>();
    Object.keys(beforeAfter.before).forEach((m) => modes.add(m));
    Object.keys(beforeAfter.after).forEach((m) => modes.add(m));
    const modeList = Array.from(modes);

    const data = [
      {
        period: t('rse.before', 'Avant'),
        ...Object.fromEntries(modeList.map((m) => [m, beforeAfter.before[m] ?? 0])),
      },
      {
        period: t('rse.after', 'Apres'),
        ...Object.fromEntries(modeList.map((m) => [m, beforeAfter.after[m] ?? 0])),
      },
    ];

    return { chartData: data, allModes: modeList };
  }, [beforeAfter, t]);

  if (allModes.length === 0) {
    return (
      <p className="font-sans text-sm text-on-surface-variant">
        {t('common.no_data')}
      </p>
    );
  }

  return (
    <div data-testid="modal-shift-comparison">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" opacity={0.3} />
          <XAxis dataKey="period" tick={{ fontSize: 12, fill: '#424754', fontWeight: 600 }} />
          <YAxis
            tick={{ fontSize: 11, fill: '#424754' }}
            label={{
              value: '%',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 11, fill: '#424754' },
            }}
          />
          <Tooltip content={<ComparisonTooltip />} />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            iconSize={8}
            formatter={(value: string) => (
              <span className="font-sans text-xs text-on-surface-variant">{value}</span>
            )}
          />
          {allModes.map((mode) => (
            <Bar key={mode} dataKey={mode} name={mode} fill={getModeColor(mode)} radius={[2, 2, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
