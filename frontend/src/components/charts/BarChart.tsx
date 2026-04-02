import { useMemo } from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

/** Design-system grid-line color: surface-container-highest at 20% opacity */
const GRID_STROKE = 'rgba(215, 228, 236, 0.2)';

/** Default bar fill: primary azure blue */
const DEFAULT_BAR_FILL = '#0058be';

interface BarDatum {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  data: BarDatum[];
  height?: number;
  xLabel?: string;
  yLabel?: string;
  title?: string;
}

interface TooltipPayloadEntry {
  name: string;
  value: number;
  payload: BarDatum;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
      <p className="font-sans text-sm font-medium">{label}</p>
      <p className="font-sans text-xs text-on-surface-variant">
        {payload[0].value}
      </p>
    </div>
  );
}

export function BarChart({
  data,
  height = 300,
  xLabel,
  yLabel,
  title,
}: BarChartProps) {
  const chartData = useMemo(
    () =>
      data.map((d) => ({
        ...d,
        fill: d.color ?? DEFAULT_BAR_FILL,
      })),
    [data],
  );

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <p className="font-sans text-sm text-on-surface-variant">
          Aucune donnee disponible
        </p>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <h4 className="font-sans text-base font-semibold text-on-surface mb-4">
          {title}
        </h4>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart
          data={chartData}
          margin={{ top: 8, right: 16, bottom: xLabel ? 32 : 8, left: yLabel ? 32 : 8 }}
        >
          <CartesianGrid
            vertical={false}
            stroke={GRID_STROKE}
            strokeDasharray="none"
          />
          <XAxis
            dataKey="label"
            tick={{ fill: '#44474c', fontFamily: 'Inter, sans-serif', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            label={
              xLabel
                ? {
                    value: xLabel,
                    position: 'insideBottom',
                    offset: -20,
                    fill: '#44474c',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12,
                  }
                : undefined
            }
          />
          <YAxis
            tick={{ fill: '#44474c', fontFamily: 'Inter, sans-serif', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            label={
              yLabel
                ? {
                    value: yLabel,
                    angle: -90,
                    position: 'insideLeft',
                    offset: -16,
                    fill: '#44474c',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12,
                  }
                : undefined
            }
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(215, 228, 236, 0.15)' }} />
          <Bar
            dataKey="value"
            radius={[4, 4, 0, 0]}
            maxBarSize={48}
          >
            {/* Individual cell colors handled by the fill property in data */}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}
