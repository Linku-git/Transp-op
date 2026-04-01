import { useMemo } from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

/**
 * Teal-to-navy palette for pie slices. Avoids pure black, stays
 * within the design-system surface/secondary spectrum.
 */
const SLICE_PALETTE = [
  '#006b5c', // secondary (teal)
  '#041627', // primary (deep navy)
  '#007261', // on-secondary-container
  '#1a2b3c', // primary-container
  '#68fadd', // secondary-container
  '#44474c', // on-surface-variant
  '#dde8f0', // surface-container-high
  '#e3f0f8', // surface-container
] as const;

interface PieSlice {
  name: string;
  value: number;
  color?: string;
}

interface PieChartProps {
  data: PieSlice[];
  height?: number;
  showLegend?: boolean;
  title?: string;
}

interface TooltipPayloadEntry {
  name: string;
  value: number;
  payload: PieSlice & { percent?: number };
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  const entry = payload[0];
  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-md px-3 py-2 shadow-sm">
      <p className="font-sans text-sm font-medium">{entry.name}</p>
      <p className="font-sans text-xs text-on-surface-variant">
        {entry.value}
        {entry.payload.percent != null &&
          ` (${(entry.payload.percent * 100).toFixed(1)}%)`}
      </p>
    </div>
  );
}

export function PieChart({
  data,
  height = 300,
  showLegend = true,
  title,
}: PieChartProps) {
  const coloredData = useMemo(
    () =>
      data.map((slice, index) => ({
        ...slice,
        fill: slice.color ?? SLICE_PALETTE[index % SLICE_PALETTE.length],
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
        <h4 className="font-display text-base font-semibold text-on-surface mb-4">
          {title}
        </h4>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={coloredData}
            cx="50%"
            cy="50%"
            innerRadius={0}
            outerRadius="75%"
            paddingAngle={2}
            dataKey="value"
            nameKey="name"
            stroke="none"
          >
            {coloredData.map((entry) => (
              <Cell key={`cell-${entry.name}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          {showLegend && (
            <Legend
              verticalAlign="bottom"
              iconType="circle"
              iconSize={8}
              formatter={(value: string) => (
                <span className="font-sans text-sm text-on-surface-variant">
                  {value}
                </span>
              )}
            />
          )}
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
}
