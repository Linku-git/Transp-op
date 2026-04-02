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

/** Default histogram fill: primary azure blue */
const DEFAULT_FILL = '#0058be';

interface HistogramBin {
  bin: string;
  count: number;
}

interface HistogramProps {
  data: HistogramBin[];
  height?: number;
  title?: string;
  color?: string;
}

interface TooltipPayloadEntry {
  name: string;
  value: number;
  payload: HistogramBin;
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

export function Histogram({
  data,
  height = 300,
  title,
  color,
}: HistogramProps) {
  const barFill = color ?? DEFAULT_FILL;

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
          data={data}
          margin={{ top: 8, right: 16, bottom: 8, left: 8 }}
          barCategoryGap={0}
          barGap={0}
        >
          <CartesianGrid
            vertical={false}
            stroke={GRID_STROKE}
            strokeDasharray="none"
          />
          <XAxis
            dataKey="bin"
            tick={{ fill: '#44474c', fontFamily: 'Inter, sans-serif', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#44474c', fontFamily: 'Inter, sans-serif', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(215, 228, 236, 0.15)' }} />
          <Bar
            dataKey="count"
            fill={barFill}
            radius={0}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}
