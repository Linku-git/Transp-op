import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { PhaseResult } from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const BAR_COLORS = {
  vehicle: '#0058be',
  infra: '#f59e0b',
} as const;

const BAR_LABELS: Record<string, string> = {
  vehicle_cost_mad: 'Cout vehicules',
  infrastructure_cost_mad: 'Cout infrastructure',
};

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

function fmtCompact(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`;
  }
  return madFmt.format(value);
}

/* ── Custom tooltip ───────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
  dataKey: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

function BudgetTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  const total = payload.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[200px]">
      <p className="font-sans text-xs font-semibold mb-2 text-on-surface-variant">
        {label}
      </p>
      {payload.map((entry) => (
        <div
          key={entry.dataKey}
          className="flex items-center justify-between gap-4 mb-0.5"
        >
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ background: entry.color }}
            />
            <span className="font-sans text-xs text-on-surface-variant">
              {BAR_LABELS[entry.dataKey] ?? entry.dataKey}
            </span>
          </div>
          <span className="font-sans text-xs font-medium">
            {fmtMAD(entry.value)}
          </span>
        </div>
      ))}
      <div className="mt-1.5 pt-1.5 border-t border-outline-variant/10 flex justify-between">
        <span className="font-sans text-xs font-semibold text-on-surface-variant">
          Total
        </span>
        <span className="font-sans text-xs font-bold text-on-surface">
          {fmtMAD(total)}
        </span>
      </div>
    </div>
  );
}

/* ── Legend formatter ──────────────────────────────────────────────────────── */

function renderLegend(value: string): string {
  return BAR_LABELS[value] ?? value;
}

/* ── Summary card ─────────────────────────────────────────────────────────── */

function SummaryCard({
  label,
  icon,
  value,
  accent,
}: {
  label: string;
  icon: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <div
      className={[
        'rounded-lg p-4 flex flex-col items-center gap-1.5',
        accent
          ? 'bg-primary/10 border border-primary/15'
          : 'bg-surface-container-low',
      ].join(' ')}
    >
      <span
        className={[
          'material-symbols-outlined text-xl',
          accent ? 'text-primary' : 'text-on-surface-variant',
        ].join(' ')}
      >
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p
        className={[
          'font-sans text-lg font-semibold',
          accent ? 'text-primary' : 'text-on-surface',
        ].join(' ')}
      >
        {fmtMAD(value)}
      </p>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function BudgetAllocationChart({
  phases,
}: {
  phases: PhaseResult[];
}) {
  /* Chart data */
  const chartData = useMemo(() => {
    return phases.map((phase) => ({
      name: phase.name,
      vehicle_cost_mad: phase.vehicle_cost_mad,
      infrastructure_cost_mad: phase.infrastructure_cost_mad,
    }));
  }, [phases]);

  /* Totals */
  const totals = useMemo(() => {
    const totalVehicle = phases.reduce(
      (sum, p) => sum + p.vehicle_cost_mad,
      0,
    );
    const totalInfra = phases.reduce(
      (sum, p) => sum + p.infrastructure_cost_mad,
      0,
    );
    return {
      totalBudget: totalVehicle + totalInfra,
      totalVehicle,
      totalInfra,
    };
  }, [phases]);

  if (phases.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <div className="flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            account_balance_wallet
          </span>
          <p className="text-sm">Aucune donnee de budget disponible.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          account_balance_wallet
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Allocation Budgetaire
        </h3>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <SummaryCard
          label="Budget total"
          icon="payments"
          value={totals.totalBudget}
          accent
        />
        <SummaryCard
          label="Cout vehicules"
          icon="directions_bus"
          value={totals.totalVehicle}
        />
        <SummaryCard
          label="Cout infrastructure"
          icon="ev_station"
          value={totals.totalInfra}
        />
      </div>

      {/* Bar chart */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
          Budget par phase
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chartData}
            margin={{ top: 8, right: 16, bottom: 8, left: 16 }}
          >
            <XAxis
              dataKey="name"
              tick={{
                fill: '#424754',
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
              }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{
                fill: '#424754',
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
              }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => fmtCompact(v)}
            />
            <Tooltip
              content={<BudgetTooltip />}
              cursor={{ fill: 'rgba(0,0,0,0.03)' }}
            />
            <Legend
              iconType="circle"
              iconSize={8}
              formatter={renderLegend}
              wrapperStyle={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 10,
                color: '#424754',
              }}
            />

            <Bar
              dataKey="vehicle_cost_mad"
              stackId="budget"
              fill={BAR_COLORS.vehicle}
              radius={[0, 0, 0, 0]}
            />
            <Bar
              dataKey="infrastructure_cost_mad"
              stackId="budget"
              fill={BAR_COLORS.infra}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
