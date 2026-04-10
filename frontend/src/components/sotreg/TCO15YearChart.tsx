import { useState, useCallback, useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { computeTCO15Year } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  TCO15YearRequest,
  TCO15YearResponse,
  TCO15YearYearlyBreakdown,
} from '@/types/sotreg';

/* ── Constants ─────────────────────────────────────────────────────────────── */

const GRID_STROKE = 'rgba(215, 228, 236, 0.2)';
const COLOR_DEPRECIATION = '#94a3b8';
const COLOR_MAINTENANCE = '#f59e0b';
const COLOR_ENERGY = '#22c55e';
const COLOR_FINANCING = '#0058be';

/* ── Helpers ───────────────────────────────────────────────────────────────── */

const madFormatter = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFormatter.format(value)} MAD`;
}

function fmtCompact(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`;
  }
  return madFormatter.format(value);
}

/* ── Tooltip ───────────────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
  dataKey: string;
  payload: TCO15YearYearlyBreakdown;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: number;
}

const AREA_LABELS: Record<string, string> = {
  depreciation: 'Amortissement',
  maintenance: 'Maintenance',
  energy: 'Energie',
  financing: 'Financement',
};

function TCOTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  const datum = payload[0].payload;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[220px]">
      <p className="font-sans text-sm font-semibold mb-2">Annee {label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4 mb-0.5">
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ background: entry.color }}
            />
            <span className="font-sans text-xs text-on-surface-variant">
              {AREA_LABELS[entry.dataKey] ?? entry.name}
            </span>
          </div>
          <span className="font-sans text-xs font-medium">
            {fmtMAD(entry.value)}
          </span>
        </div>
      ))}
      <div className="border-t border-outline-variant/10 mt-1.5 pt-1.5 flex justify-between">
        <span className="font-sans text-xs font-semibold text-on-surface-variant">Total annuel</span>
        <span className="font-sans text-xs font-bold">{fmtMAD(datum.year_total)}</span>
      </div>
      <div className="flex justify-between mt-0.5">
        <span className="font-sans text-xs text-on-surface-variant">TCO cumule</span>
        <span className="font-sans text-xs font-medium text-primary">{fmtMAD(datum.cumulative_tco)}</span>
      </div>
    </div>
  );
}

/* ── Summary card ──────────────────────────────────────────────────────────── */

function SummaryCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: string;
}) {
  return (
    <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-1.5">
      <span className="material-symbols-outlined text-lg text-on-surface-variant">
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p className="font-sans text-sm font-semibold text-on-surface text-center">
        {value}
      </p>
    </div>
  );
}

/* ── Gradient defs ─────────────────────────────────────────────────────────── */

function AreaGradientDefs() {
  return (
    <defs>
      <linearGradient id="tcoDepreciation" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={COLOR_DEPRECIATION} stopOpacity={0.6} />
        <stop offset="100%" stopColor={COLOR_DEPRECIATION} stopOpacity={0.1} />
      </linearGradient>
      <linearGradient id="tcoMaintenance" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={COLOR_MAINTENANCE} stopOpacity={0.6} />
        <stop offset="100%" stopColor={COLOR_MAINTENANCE} stopOpacity={0.1} />
      </linearGradient>
      <linearGradient id="tcoEnergy" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={COLOR_ENERGY} stopOpacity={0.6} />
        <stop offset="100%" stopColor={COLOR_ENERGY} stopOpacity={0.1} />
      </linearGradient>
      <linearGradient id="tcoFinancing" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={COLOR_FINANCING} stopOpacity={0.6} />
        <stop offset="100%" stopColor={COLOR_FINANCING} stopOpacity={0.1} />
      </linearGradient>
    </defs>
  );
}

/* ── Legend formatter ───────────────────────────────────────────────────────── */

function renderLegend(value: string): string {
  return AREA_LABELS[value] ?? value;
}

/* ── Main component ────────────────────────────────────────────────────────── */

export function TCO15YearChart() {
  /* Form state */
  const [purchasePrice, setPurchasePrice] = useState(300000);
  const [annualMaintenance, setAnnualMaintenance] = useState(6000);
  const [energyCostPerKm, setEnergyCostPerKm] = useState(0.06);
  const [annualKm, setAnnualKm] = useState(40000);
  const [loanRatePct, setLoanRatePct] = useState(5);
  const [durationYears, setDurationYears] = useState(15);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TCO15YearResponse | null>(null);

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: TCO15YearRequest = {
        purchase_price: purchasePrice,
        annual_maintenance_cost: annualMaintenance,
        energy_cost_per_km: energyCostPerKm,
        annual_km: annualKm,
        loan_rate_pct: loanRatePct,
        duration_years: durationYears,
      };
      const res = await computeTCO15Year(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul TCO'));
    } finally {
      setLoading(false);
    }
  }, [purchasePrice, annualMaintenance, energyCostPerKm, annualKm, loanRatePct, durationYears]);

  /* Y-axis domain */
  const yMax = useMemo(() => {
    if (!result) return 0;
    const maxYearTotal = Math.max(...result.yearly_breakdown.map((y) => y.year_total));
    return Math.ceil(maxYearTotal / 10000) * 10000;
  }, [result]);

  /* ── Render ──────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          monitoring
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          TCO 15 ans
        </h3>
      </div>

      {/* Form grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-5">
        {/* Purchase price */}
        <div>
          <label
            htmlFor="tco-purchase"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Prix d&apos;achat (MAD)
          </label>
          <input
            id="tco-purchase"
            type="number"
            min={0}
            step={10000}
            value={purchasePrice}
            onChange={(e) => setPurchasePrice(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Annual maintenance */}
        <div>
          <label
            htmlFor="tco-maintenance"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Maintenance annuelle (MAD)
          </label>
          <input
            id="tco-maintenance"
            type="number"
            min={0}
            step={500}
            value={annualMaintenance}
            onChange={(e) => setAnnualMaintenance(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Energy cost per km */}
        <div>
          <label
            htmlFor="tco-energy"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Cout energie / km (MAD)
          </label>
          <input
            id="tco-energy"
            type="number"
            min={0}
            step={0.01}
            value={energyCostPerKm}
            onChange={(e) => setEnergyCostPerKm(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Annual km */}
        <div>
          <label
            htmlFor="tco-km"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Kilometrage annuel
          </label>
          <input
            id="tco-km"
            type="number"
            min={0}
            step={1000}
            value={annualKm}
            onChange={(e) => setAnnualKm(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Loan rate */}
        <div>
          <label
            htmlFor="tco-rate"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Taux emprunt (%)
          </label>
          <input
            id="tco-rate"
            type="number"
            min={0}
            max={30}
            step={0.5}
            value={loanRatePct}
            onChange={(e) => setLoanRatePct(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Duration */}
        <div>
          <label
            htmlFor="tco-duration"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Duree (annees)
          </label>
          <input
            id="tco-duration"
            type="number"
            min={1}
            max={30}
            step={1}
            value={durationYears}
            onChange={(e) => setDurationYears(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>
      </div>

      {/* Compute button */}
      <button
        type="button"
        onClick={handleCompute}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Calcul en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              calculate
            </span>
            Calculer TCO
          </>
        )}
      </button>

      {/* Error */}
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
          {/* Summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <SummaryCard
              label="TCO Total"
              value={fmtMAD(result.total_tco)}
              icon="account_balance"
            />
            <SummaryCard
              label="Financement"
              value={fmtMAD(result.financing_total)}
              icon="credit_card"
            />
            <SummaryCard
              label="Energie"
              value={fmtMAD(result.energy_total)}
              icon="bolt"
            />
            <SummaryCard
              label="Maintenance"
              value={fmtMAD(result.maintenance_total)}
              icon="build"
            />
            <SummaryCard
              label="Amortissement"
              value={fmtMAD(result.depreciation_total)}
              icon="trending_down"
            />
            <SummaryCard
              label="Valeur residuelle"
              value={fmtMAD(result.residual_value)}
              icon="savings"
            />
          </div>

          {/* Area chart */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Decomposition annuelle
            </p>
            <ResponsiveContainer width="100%" height={380}>
              <AreaChart
                data={result.yearly_breakdown}
                margin={{ top: 8, right: 16, bottom: 4, left: 8 }}
              >
                <AreaGradientDefs />
                <CartesianGrid
                  stroke={GRID_STROKE}
                  strokeDasharray="none"
                  vertical={false}
                />
                <XAxis
                  dataKey="year"
                  tick={{
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                  }}
                  axisLine={false}
                  tickLine={false}
                  label={{
                    value: 'Annee',
                    position: 'insideBottomRight',
                    offset: -4,
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10,
                  }}
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
                  domain={[0, yMax || 'auto']}
                  label={{
                    value: 'MAD',
                    angle: -90,
                    position: 'insideLeft',
                    offset: 10,
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10,
                  }}
                />
                <Tooltip
                  content={<TCOTooltip />}
                  cursor={{ stroke: '#c2c6d6', strokeDasharray: '4 4' }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  formatter={renderLegend}
                  wrapperStyle={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    color: '#424754',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="depreciation"
                  stackId="tco"
                  stroke={COLOR_DEPRECIATION}
                  fill="url(#tcoDepreciation)"
                  strokeWidth={1.5}
                />
                <Area
                  type="monotone"
                  dataKey="maintenance"
                  stackId="tco"
                  stroke={COLOR_MAINTENANCE}
                  fill="url(#tcoMaintenance)"
                  strokeWidth={1.5}
                />
                <Area
                  type="monotone"
                  dataKey="energy"
                  stackId="tco"
                  stroke={COLOR_ENERGY}
                  fill="url(#tcoEnergy)"
                  strokeWidth={1.5}
                />
                <Area
                  type="monotone"
                  dataKey="financing"
                  stackId="tco"
                  stroke={COLOR_FINANCING}
                  fill="url(#tcoFinancing)"
                  strokeWidth={1.5}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
