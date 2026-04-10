import { useState, useCallback, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { computeNPV } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { NPVRequest, NPVResponse } from '@/types/sotreg';

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

function parseCashFlows(input: string): number[] | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  const parts = trimmed.split(',').map((s) => s.trim());
  const values: number[] = [];
  for (const part of parts) {
    if (part === '') continue;
    const num = Number(part);
    if (Number.isNaN(num)) return null;
    values.push(num);
  }
  return values.length > 0 ? values : null;
}

/* ── Waterfall bar data builder ──────────────────────────────────────────── */

interface WaterfallEntry {
  name: string;
  value: number;
  fill: string;
  /** invisible base portion for stacking to create waterfall effect */
  base: number;
  /** visible bar portion */
  bar: number;
}

function buildWaterfallData(presentValues: number[]): WaterfallEntry[] {
  return presentValues.map((pv, i) => ({
    name: `A${i}`,
    value: pv,
    fill: pv >= 0 ? '#0058be' : '#ba1a1a',
    base: pv >= 0 ? 0 : pv,
    bar: Math.abs(pv),
  }));
}

/* ── Custom tooltip ──────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  payload: WaterfallEntry;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

function WaterfallTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const entry = payload[0]?.payload;
  if (!entry) return null;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[180px]">
      <p className="font-sans text-xs font-semibold mb-1 text-on-surface-variant">
        {label}
      </p>
      <div className="flex items-center justify-between gap-4">
        <span className="font-sans text-xs text-on-surface-variant">
          Valeur actuelle
        </span>
        <span
          className="font-sans text-xs font-medium"
          style={{ color: entry.fill }}
        >
          {fmtMAD(entry.value)}
        </span>
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */

export function NPVWaterfallChart() {
  /* Form state */
  const [cashFlowsInput, setCashFlowsInput] = useState('-500000,120000,150000,180000,200000,220000');
  const [discountRate, setDiscountRate] = useState(10);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<NPVResponse | null>(null);

  /* ── Handler ────────────────────────────────────────────────────────────── */

  const handleCompute = useCallback(async () => {
    const cashFlows = parseCashFlows(cashFlowsInput);
    if (!cashFlows) {
      setError('Saisissez des flux de tresorerie valides, separes par des virgules (ex: -500000,120000,150000).');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const req: NPVRequest = {
        cash_flows: cashFlows,
        discount_rate: discountRate / 100,
      };
      const res = await computeNPV(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul de la VAN'));
    } finally {
      setLoading(false);
    }
  }, [cashFlowsInput, discountRate]);

  /* ── Chart data ─────────────────────────────────────────────────────────── */

  const waterfallData = useMemo(() => {
    if (!result) return [];
    return buildWaterfallData(result.present_values);
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          waterfall_chart
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Valeur Actuelle Nette (VAN)
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        {/* Cash flows input */}
        <div>
          <label
            htmlFor="npv-cash-flows"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Flux de tresorerie (MAD)
          </label>
          <input
            id="npv-cash-flows"
            type="text"
            value={cashFlowsInput}
            onChange={(e) => setCashFlowsInput(e.target.value)}
            placeholder="-500000,120000,150000,180000"
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
          <p className="mt-1 text-[10px] text-on-surface-variant">
            Separes par des virgules. Negatifs = investissements.
          </p>
        </div>

        {/* Discount rate slider */}
        <div>
          <label
            htmlFor="npv-discount-rate"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Taux d&apos;actualisation
          </label>
          <div className="flex items-center gap-3">
            <input
              id="npv-discount-rate"
              type="range"
              min={0}
              max={20}
              step={0.5}
              value={discountRate}
              onChange={(e) => setDiscountRate(Number(e.target.value))}
              className="flex-1 accent-primary"
            />
            <span className="text-sm font-medium text-on-surface w-12 text-right">
              {discountRate.toFixed(1)}%
            </span>
          </div>
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
            Calculer VAN
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
          {/* Big number: NPV */}
          <div className="flex items-center justify-center gap-4 py-4">
            <span className="material-symbols-outlined text-4xl text-primary">
              account_balance
            </span>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Valeur Actuelle Nette
              </p>
              <p
                className="font-sans text-3xl font-bold"
                style={{ color: result.npv >= 0 ? '#16a34a' : '#ba1a1a' }}
              >
                {fmtMAD(result.npv)}
              </p>
            </div>
          </div>

          {/* Viability badge + meta */}
          <div className="flex items-center justify-center gap-6 border-t border-outline-variant/10 pt-4">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Viabilite
              </p>
              {result.is_viable ? (
                <span className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 rounded-full px-3 py-1 text-xs font-semibold">
                  <span className="material-symbols-outlined text-sm">
                    check_circle
                  </span>
                  Projet viable
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 bg-error-container/30 text-error rounded-full px-3 py-1 text-xs font-semibold">
                  <span className="material-symbols-outlined text-sm">
                    cancel
                  </span>
                  Projet non viable
                </span>
              )}
            </div>

            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Taux d&apos;actualisation
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {(result.discount_rate * 100).toFixed(1)}%
              </p>
            </div>

            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Periodes
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {result.cash_flow_count}
              </p>
            </div>
          </div>

          {/* Waterfall chart */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Valeurs actuelles par annee
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={waterfallData}
                margin={{ top: 8, right: 16, bottom: 4, left: 8 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#c2c6d620"
                  vertical={false}
                />
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
                  content={<WaterfallTooltip />}
                  cursor={{ fill: 'rgba(0,0,0,0.03)' }}
                />
                <ReferenceLine y={0} stroke="#424754" strokeWidth={1} />
                {/* Invisible base for waterfall positioning */}
                <Bar dataKey="base" stackId="waterfall" fill="transparent" />
                {/* Visible bar */}
                <Bar
                  dataKey="bar"
                  stackId="waterfall"
                  radius={[4, 4, 0, 0]}
                  isAnimationActive
                >
                  {waterfallData.map((entry, index) => (
                    <rect key={index} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-2">
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#0058be]" />
                <span className="text-[10px] text-on-surface-variant">Positif</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#ba1a1a]" />
                <span className="text-[10px] text-on-surface-variant">Negatif</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            waterfall_chart
          </span>
          <p className="text-sm">
            Saisissez les flux de tresorerie et cliquez sur Calculer VAN pour analyser la rentabilite.
          </p>
        </div>
      )}
    </div>
  );
}
