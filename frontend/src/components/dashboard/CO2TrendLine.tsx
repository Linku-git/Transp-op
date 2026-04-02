import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { CO2TrendPoint } from '@/types/rse';

interface CO2TrendLineProps {
  trend: CO2TrendPoint[];
  totalSaved: number;
}

interface CO2TooltipPayload {
  value: number;
  name: string;
}

interface CO2TooltipProps {
  active?: boolean;
  label?: string;
  payload?: CO2TooltipPayload[];
}

function CO2Tooltip({ active, label, payload }: CO2TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
      <p className="font-sans text-xs text-on-surface-variant">{label}</p>
      {payload.map((entry) => (
        <p key={entry.name} className="font-sans text-sm font-medium">
          {entry.value.toLocaleString('fr-FR')} kg CO2
        </p>
      ))}
    </div>
  );
}

export function CO2TrendLine({ trend, totalSaved }: CO2TrendLineProps) {
  const { t } = useTranslation();

  const chartData = trend.map((pt) => ({
    date: new Date(pt.date).toLocaleDateString('fr-FR', {
      month: 'short',
      day: 'numeric',
    }),
    co2_saved_kg: pt.co2_saved_kg,
  }));

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-4">
        <span
          className="font-sans text-4xl font-bold text-green-600"
          data-testid="co2-total-saved"
        >
          {totalSaved.toLocaleString('fr-FR')}
        </span>
        <span className="font-sans text-sm text-on-surface-variant">
          kg CO2 {t('rse.saved', 'economises')}
        </span>
      </div>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" opacity={0.3} />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#424754' }} />
            <YAxis
              tick={{ fontSize: 11, fill: '#424754' }}
              label={{
                value: 'kg CO2',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 11, fill: '#424754' },
              }}
            />
            <Tooltip content={<CO2Tooltip />} />
            <Line
              type="monotone"
              dataKey="co2_saved_kg"
              name="CO2"
              stroke="#16a34a"
              strokeWidth={2}
              dot={{ r: 3, fill: '#16a34a' }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p className="font-sans text-sm text-on-surface-variant">
          {t('common.no_data')}
        </p>
      )}
    </div>
  );
}
