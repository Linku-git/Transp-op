import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  type TooltipProps,
} from 'recharts';
import { useTranslation } from 'react-i18next';

import type { ROICalculateResponse } from '@/types/financial';

interface WaterfallChartProps {
  data: ROICalculateResponse;
}

interface WaterfallItem {
  name: string;
  value: number;
  fill: string;
}

function formatMAD(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k`;
  }
  return value.toFixed(0);
}

function CustomTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload || payload.length === 0) return null;
  const item = payload[0];
  const raw = item.value as number;
  return (
    <div className="bg-surface-container-lowest rounded-lg shadow-lg border border-outline-variant/10 px-3 py-2">
      <p className="text-xs font-bold text-on-surface">{item.name}</p>
      <p className="text-sm text-on-surface-variant">
        {formatMAD(raw)} MAD
      </p>
    </div>
  );
}

export function WaterfallChart({ data }: WaterfallChartProps) {
  const { t } = useTranslation();

  const chartData: WaterfallItem[] = useMemo(
    () => [
      {
        name: t('financial.roi_absenteeism', 'Absenteisme'),
        value: data.roi_absenteeism,
        fill: '#16a34a',
      },
      {
        name: t('financial.roi_retention', 'Retention'),
        value: data.roi_retention,
        fill: '#22c55e',
      },
      {
        name: t('financial.roi_fleet', 'Flotte'),
        value: data.roi_fleet_optimization,
        fill: '#4ade80',
      },
      {
        name: t('financial.roi_journey', 'Trajet'),
        value: data.roi_journey,
        fill: '#86efac',
      },
      {
        name: t('financial.roi_total_label', 'TOTAL'),
        value: data.roi_total,
        fill: '#0058be',
      },
    ],
    [data, t],
  );

  return (
    <div data-testid="waterfall-chart" className="w-full h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 16, right: 16, bottom: 8, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d620" vertical={false} />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#424754' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={formatMAD}
            tick={{ fontSize: 11, fill: '#424754' }}
            axisLine={false}
            tickLine={false}
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value" radius={[6, 6, 0, 0]} barSize={48}>
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
