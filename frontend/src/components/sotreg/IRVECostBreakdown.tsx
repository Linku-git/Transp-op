import { useState, useCallback, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { computeDepotCostEstimate } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  DepotCostEstimateRequest,
  DepotCostEstimateResponse,
} from '@/types/sotreg';
import { CHARGER_TYPES, CHARGER_LABELS } from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const COST_COLORS = {
  hardware: '#0058be',
  installation: '#0d9488',
  electrical: '#4f46e5',
  transformer: '#7c3aed',
  grid: '#ea580c',
  civil: '#d97706',
  contingency: '#64748b',
} as const;

const COST_LABELS: Record<string, string> = {
  hardware: 'Materiel',
  installation: 'Installation',
  electrical: 'Electrique',
  transformer: 'Transformateur',
  grid: 'Raccordement',
  civil: 'Genie civil',
  contingency: 'Contingence',
};

const COST_ICONS: Record<string, string> = {
  hardware: 'hardware',
  installation: 'construction',
  electrical: 'electric_bolt',
  transformer: 'power',
  grid: 'cable',
  civil: 'foundation',
  contingency: 'shield',
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

/* ── Cost component card ──────────────────────────────────────────────────── */

function CostComponentCard({
  costKey,
  value,
}: {
  costKey: string;
  value: number;
}) {
  const color = COST_COLORS[costKey as keyof typeof COST_COLORS] ?? '#64748b';

  return (
    <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-1.5">
      <span className="material-symbols-outlined text-xl" style={{ color }}>
        {COST_ICONS[costKey] ?? 'payments'}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {COST_LABELS[costKey] ?? costKey}
      </p>
      <p className="font-sans text-sm font-semibold text-on-surface">
        {fmtMAD(value)}
      </p>
    </div>
  );
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
}

function CostTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[200px]">
      <p className="font-sans text-xs font-semibold mb-2 text-on-surface-variant">
        Ventilation des couts
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
              {COST_LABELS[entry.dataKey] ?? entry.dataKey}
            </span>
          </div>
          <span className="font-sans text-xs font-medium">
            {fmtMAD(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ── Legend formatter ─────────────────────────────────────────────────────── */

function renderLegend(value: string): string {
  return COST_LABELS[value] ?? value;
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function IRVECostBreakdown() {
  /* Form state */
  const [chargerCount, setChargerCount] = useState(3);
  const [chargerType, setChargerType] = useState<string>(CHARGER_TYPES[1]);
  const [contingencyPct, setContingencyPct] = useState(10);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DepotCostEstimateResponse | null>(null);

  /* ── Handler ────────────────────────────────────────────────────────────── */

  const handleEstimate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: DepotCostEstimateRequest = {
        charger_count: chargerCount,
        charger_type: chargerType,
        contingency_pct: contingencyPct,
      };
      const res = await computeDepotCostEstimate(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de l\'estimation des couts IRVE'));
    } finally {
      setLoading(false);
    }
  }, [chargerCount, chargerType, contingencyPct]);

  /* ── Chart data ─────────────────────────────────────────────────────────── */

  const chartData = useMemo(() => {
    if (!result) return [];
    return [
      {
        name: 'Couts',
        hardware: result.charger_hardware_mad,
        installation: result.installation_mad,
        electrical: result.electrical_upgrade_mad,
        transformer: result.transformer_mad,
        grid: result.grid_connection_mad,
        civil: result.civil_works_mad,
        contingency: result.contingency_mad,
      },
    ];
  }, [result]);

  /* Cost components array for the grid */
  const costComponents = useMemo(() => {
    if (!result) return [];
    return [
      { key: 'hardware', value: result.charger_hardware_mad },
      { key: 'installation', value: result.installation_mad },
      { key: 'electrical', value: result.electrical_upgrade_mad },
      { key: 'transformer', value: result.transformer_mad },
      { key: 'grid', value: result.grid_connection_mad },
      { key: 'civil', value: result.civil_works_mad },
      { key: 'contingency', value: result.contingency_mad },
    ];
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          payments
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Couts IRVE
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        {/* Charger count */}
        <div>
          <label
            htmlFor="irve-cost-count"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Nombre de chargeurs
          </label>
          <input
            id="irve-cost-count"
            type="number"
            min={1}
            max={100}
            value={chargerCount}
            onChange={(e) => setChargerCount(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Charger type */}
        <div>
          <label
            htmlFor="irve-cost-type"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Type de chargeur
          </label>
          <select
            id="irve-cost-type"
            value={chargerType}
            onChange={(e) => setChargerType(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {CHARGER_TYPES.map((ct) => (
              <option key={ct} value={ct}>
                {CHARGER_LABELS[ct]}
              </option>
            ))}
          </select>
        </div>

        {/* Contingency slider */}
        <div>
          <label
            htmlFor="irve-cost-contingency"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Contingence
          </label>
          <div className="flex items-center gap-3">
            <input
              id="irve-cost-contingency"
              type="range"
              min={0}
              max={50}
              step={1}
              value={contingencyPct}
              onChange={(e) => setContingencyPct(Number(e.target.value))}
              className="flex-1 accent-primary"
            />
            <span className="text-sm font-medium text-on-surface w-10 text-right">
              {contingencyPct}%
            </span>
          </div>
        </div>
      </div>

      {/* Estimate button */}
      <button
        type="button"
        onClick={handleEstimate}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Estimation en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              calculate
            </span>
            Estimer Cout
          </>
        )}
      </button>

      {/* Error state */}
      {error && (
        <div className="mt-4 flex items-start gap-2 bg-error-container/30 text-error rounded-lg px-4 py-3">
          <span className="material-symbols-outlined text-base mt-0.5">
            error
          </span>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="mt-6 space-y-6">
          {/* Big number: total cost */}
          <div className="flex items-center justify-center gap-4 py-4">
            <span className="material-symbols-outlined text-4xl text-primary">
              account_balance
            </span>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Cout total estime
              </p>
              <p className="font-sans text-3xl font-bold text-on-surface">
                {fmtMAD(result.total_cost_mad)}
              </p>
            </div>
          </div>

          {/* Cost per charger + power info */}
          <div className="grid grid-cols-3 gap-3 border-t border-outline-variant/10 pt-4">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Cout par chargeur
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {fmtMAD(result.cost_per_charger_mad)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Puissance totale
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {madFmt.format(result.total_power_kw)} kW
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Chargeurs
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {result.charger_count} &times; {CHARGER_LABELS[result.charger_type] ?? result.charger_type}
              </p>
            </div>
          </div>

          {/* Horizontal stacked bar chart */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Repartition des couts
            </p>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
              >
                <XAxis
                  type="number"
                  tick={{
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                  }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => fmtCompact(v)}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={false}
                  axisLine={false}
                  tickLine={false}
                  width={0}
                />
                <Tooltip
                  content={<CostTooltip />}
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
                  dataKey="hardware"
                  stackId="cost"
                  fill={COST_COLORS.hardware}
                  radius={[4, 0, 0, 4]}
                />
                <Bar
                  dataKey="installation"
                  stackId="cost"
                  fill={COST_COLORS.installation}
                />
                <Bar
                  dataKey="electrical"
                  stackId="cost"
                  fill={COST_COLORS.electrical}
                />
                <Bar
                  dataKey="transformer"
                  stackId="cost"
                  fill={COST_COLORS.transformer}
                />
                <Bar
                  dataKey="grid"
                  stackId="cost"
                  fill={COST_COLORS.grid}
                />
                <Bar
                  dataKey="civil"
                  stackId="cost"
                  fill={COST_COLORS.civil}
                />
                <Bar
                  dataKey="contingency"
                  stackId="cost"
                  fill={COST_COLORS.contingency}
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Cost component cards */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Detail par composant
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {costComponents.map((c) => (
                <CostComponentCard key={c.key} costKey={c.key} value={c.value} />
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            payments
          </span>
          <p className="text-sm">
            Configurez les parametres et cliquez sur Estimer Cout pour calculer les couts IRVE.
          </p>
        </div>
      )}
    </div>
  );
}
