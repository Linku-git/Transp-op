import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export interface ScatterPoint {
  x: number;
  y: number;
  label: string;
}

interface ScatterPlotProps {
  data: ScatterPoint[];
  xLabel: string;
  yLabel: string;
  height?: number;
}

interface ScatterTooltipPayload {
  payload: ScatterPoint;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: ScatterTooltipPayload[];
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;
  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
      <p className="font-sans text-sm font-medium">{point.label}</p>
      <p className="font-sans text-xs text-on-surface-variant">
        x: {point.x}, y: {point.y}
      </p>
    </div>
  );
}

export function ScatterPlot({
  data,
  xLabel,
  yLabel,
  height = 300,
}: ScatterPlotProps) {
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
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#c2c6d6" opacity={0.3} />
        <XAxis
          type="number"
          dataKey="x"
          name={xLabel}
          label={{
            value: xLabel,
            position: 'insideBottom',
            offset: -10,
            style: { fontSize: 11, fill: '#424754' },
          }}
          tick={{ fontSize: 11, fill: '#424754' }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name={yLabel}
          label={{
            value: yLabel,
            angle: -90,
            position: 'insideLeft',
            offset: 5,
            style: { fontSize: 11, fill: '#424754' },
          }}
          tick={{ fontSize: 11, fill: '#424754' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Scatter data={data} fill="#0058be" fillOpacity={0.7} r={5} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
