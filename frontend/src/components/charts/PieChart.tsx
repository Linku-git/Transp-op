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
 * Azure Velocity palette for pie slices. Primary blue anchored,
 * extended with secondary slate-blue, tertiary amber, and tints.
 */
const SLICE_PALETTE = [
  '#0058be', // primary (azure blue)
  '#495e8a', // secondary (slate-blue)
  '#924700', // tertiary (burnt amber)
  '#2170e4', // primary lighter
  '#b75b00', // tertiary lighter
  '#304671', // secondary darker
  '#adc6ff', // primary-container
  '#ffb786', // tertiary-container
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
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-3 py-2 shadow-sm border border-outline-variant/10">
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
        <h4 className="font-sans text-base font-semibold text-on-surface mb-4">
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
