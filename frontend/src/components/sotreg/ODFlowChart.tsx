import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { ODMatrixEntry } from '@/types/sotreg';

/** Design-system grid-line color */
const GRID_STROKE = 'rgba(215, 228, 236, 0.2)';

/** Primary blue gradient endpoints */
const PRIMARY = '#0058be';
const PRIMARY_CONTAINER = '#2170e4';

/** Maximum OD pairs to display */
const TOP_N = 15;

/** Truncate a string to maxLen characters with ellipsis */
function truncate(text: string, maxLen: number): string {
  return text.length > maxLen ? `${text.slice(0, maxLen - 1)}…` : text;
}

/** Format a number with locale-aware separators */
function fmt(value: number, decimals = 0): string {
  return value.toLocaleString('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/* ── Chart data shape ────────────────────────────────────────────────────── */

interface ChartDatum {
  name: string;
  fullName: string;
  flow: number;
  distance: number;
}

/* ── Custom tooltip ──────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  name: string;
  value: number;
  payload: ChartDatum;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
}

function ODTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  const datum = payload[0].payload;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[200px]">
      <p className="font-sans text-sm font-semibold mb-1">{datum.fullName}</p>
      <div className="flex justify-between gap-4">
        <span className="font-sans text-xs text-on-surface-variant">Flux estimé</span>
        <span className="font-sans text-xs font-medium">{fmt(datum.flow)}</span>
      </div>
      <div className="flex justify-between gap-4 mt-0.5">
        <span className="font-sans text-xs text-on-surface-variant">Distance</span>
        <span className="font-sans text-xs font-medium">{fmt(datum.distance, 1)} km</span>
      </div>
    </div>
  );
}

/* ── Gradient definition ─────────────────────────────────────────────────── */

function BarGradientDef() {
  return (
    <defs>
      <linearGradient id="odFlowGradient" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stopColor={PRIMARY} />
        <stop offset="100%" stopColor={PRIMARY_CONTAINER} />
      </linearGradient>
    </defs>
  );
}

/* ── Props ────────────────────────────────────────────────────────────────── */

interface ODFlowChartProps {
  entries: ODMatrixEntry[];
  className?: string;
}

/* ── Component ───────────────────────────────────────────────────────────── */

export function ODFlowChart({ entries, className }: ODFlowChartProps) {
  const chartData = useMemo<ChartDatum[]>(() => {
    if (entries.length === 0) return [];

    // Group by origin_zone -> destination_zone pair, take highest flow_estimate per pair
    const pairMap = new Map<string, { flow: number; distance: number }>();

    for (const entry of entries) {
      const key = `${entry.origin_zone} → ${entry.destination_zone}`;
      const existing = pairMap.get(key);
      if (!existing || entry.flow_estimate > existing.flow) {
        pairMap.set(key, {
          flow: entry.flow_estimate,
          distance: entry.distance_km,
        });
      }
    }

    // Sort descending by flow, take top N
    const sorted = [...pairMap.entries()]
      .sort(([, a], [, b]) => b.flow - a.flow)
      .slice(0, TOP_N);

    // Reverse so the highest flow appears at the top in vertical layout
    return sorted
      .map(([fullName, { flow, distance }]) => ({
        name: truncate(fullName, 30),
        fullName,
        flow,
        distance,
      }))
      .reverse();
  }, [entries]);

  const summary = useMemo(() => {
    if (entries.length === 0) return null;
    const totalFlow = entries.reduce((sum, e) => sum + e.flow_estimate, 0);
    const avgDistance =
      entries.reduce((sum, e) => sum + e.distance_km, 0) / entries.length;
    const beta = entries[0]?.beta_used ?? 0;
    return { totalFlow, pairCount: entries.length, avgDistance, beta };
  }, [entries]);

  /* ── Empty state ───────────────────────────────────────────────────────── */

  if (entries.length === 0) {
    return (
      <div
        className={`bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 ${className ?? ''}`}
      >
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
          Flux Origine-Destination
        </h3>
        <div className="flex items-center justify-center h-[200px]">
          <p className="font-sans text-sm text-on-surface-variant text-center max-w-xs">
            Aucune matrice OD calculée. Lancez le calcul depuis le tableau de bord.
          </p>
        </div>
      </div>
    );
  }

  /* ── Chart ─────────────────────────────────────────────────────────────── */

  return (
    <div
      className={`bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 ${className ?? ''}`}
    >
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
          Flux Origine-Destination
        </h3>
        <p className="font-sans text-xs text-on-surface-variant">
          Top {Math.min(TOP_N, chartData.length)} paires sur {summary?.pairCount ?? 0} entrées
          {summary?.beta ? ` — \u03B2 = ${fmt(summary.beta, 2)}` : ''}
        </p>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 24, bottom: 4, left: 12 }}
        >
          <BarGradientDef />
          <CartesianGrid
            horizontal={false}
            stroke={GRID_STROKE}
            strokeDasharray="none"
          />
          <YAxis
            dataKey="name"
            type="category"
            width={180}
            tick={{
              fill: '#424754',
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
            }}
            axisLine={false}
            tickLine={false}
          />
          <XAxis
            type="number"
            tick={{
              fill: '#424754',
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
            }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => fmt(v)}
          />
          <Tooltip
            content={<ODTooltip />}
            cursor={{ fill: 'rgba(215, 228, 236, 0.15)' }}
          />
          <Bar
            dataKey="flow"
            fill="url(#odFlowGradient)"
            radius={[0, 4, 4, 0]}
            maxBarSize={28}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Summary row */}
      {summary && (
        <div className="mt-4 grid grid-cols-3 gap-4 border-t border-outline-variant/10 pt-4">
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
              Total flux
            </p>
            <p className="font-sans text-lg font-semibold text-on-surface">
              {fmt(summary.totalFlow)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
              Paires OD
            </p>
            <p className="font-sans text-lg font-semibold text-on-surface">
              {fmt(summary.pairCount)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
              Distance moyenne
            </p>
            <p className="font-sans text-lg font-semibold text-on-surface">
              {fmt(summary.avgDistance, 1)} km
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
