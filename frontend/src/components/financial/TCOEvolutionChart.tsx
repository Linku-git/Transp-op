import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useTranslation } from 'react-i18next';
import type { TCOYearlyPoint } from '@/types/financial';

interface TCOEvolutionChartProps {
  data: TCOYearlyPoint[];
}

function formatCompact(value: number): string {
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k`;
  }
  return String(value);
}

function formatMAD(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'MAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

interface TooltipPayloadItem {
  value: number;
  dataKey: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: number;
  yearLabel: string;
  tcoLabel: string;
}

function CustomTooltip({
  active,
  payload,
  label,
  yearLabel,
  tcoLabel,
}: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-lg border border-outline-variant/10 px-3 py-2">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
        {yearLabel} {label}
      </p>
      <p className="text-sm font-bold text-on-surface">
        {tcoLabel}: {formatMAD(payload[0].value)}
      </p>
    </div>
  );
}

export function TCOEvolutionChart({ data }: TCOEvolutionChartProps) {
  const { t } = useTranslation();

  if (data.length === 0) {
    return (
      <p className="text-sm text-on-surface-variant">
        {t('common.no_data', 'Aucune donnee')}
      </p>
    );
  }

  return (
    <div data-testid="tco-evolution-chart" className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 8, right: 16, left: 8, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d633" />
          <XAxis
            dataKey="year"
            tick={{ fontSize: 11, fill: '#424754' }}
            tickLine={false}
            axisLine={{ stroke: '#c2c6d633' }}
            label={{
              value: t('financial.year', 'Annee'),
              position: 'insideBottomRight',
              offset: -4,
              fontSize: 10,
              fill: '#424754',
            }}
          />
          <YAxis
            tickFormatter={formatCompact}
            tick={{ fontSize: 11, fill: '#424754' }}
            tickLine={false}
            axisLine={false}
            width={60}
          />
          <Tooltip
            content={
              <CustomTooltip
                yearLabel={t('financial.year', 'Annee')}
                tcoLabel={t('financial.fleet_tco', 'TCO flotte')}
              />
            }
          />
          <Line
            type="monotone"
            dataKey="fleet_tco_total"
            stroke="#0058be"
            strokeWidth={2.5}
            dot={{ r: 4, fill: '#0058be', strokeWidth: 0 }}
            activeDot={{ r: 6, fill: '#0058be', strokeWidth: 2, stroke: '#fff' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
