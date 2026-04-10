import { useState, useCallback, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { computePayback } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { PaybackResponse } from '@/types/sotreg';

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

/* ── Chart data types ────────────────────────────────────────────────────── */

interface CumulativeEntry {
  name: string;
  year: number;
  cumulative: number;
}

/* ── Custom tooltip ──────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  payload: CumulativeEntry;
  value: number;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

function CumulativeTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const entry = payload[0];
  if (!entry) return null;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[180px]">
      <p className="font-sans text-xs font-semibold mb-1 text-on-surface-variant">
        {label}
      </p>
      <div className="flex items-center justify-between gap-4">
        <span className="font-sans text-xs text-on-surface-variant">
          Cumul
        </span>
        <span
          className="font-sans text-xs font-medium"
          style={{ color: entry.value >= 0 ? '#16a34a' : '#ba1a1a' }}
        >
          {fmtMAD(entry.value)}
        </span>
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */

export function PaybackTimelineChart() {
  /* Form state */
  const [cashFlowsInput, setCashFlowsInput] = useState('-500000,120000,150000,180000,200000,220000');

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PaybackResponse | null>(null);

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
      const res = await computePayback({ cash_flows: cashFlows, currency: 'MAD' });
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul du delai de recuperation'));
    } finally {
      setLoading(false);
    }
  }, [cashFlowsInput]);

  /* ── Chart data ─────────────────────────────────────────────────────────── */

  const chartData = useMemo((): CumulativeEntry[] => {
    if (!result) return [];
    return result.cumulative_flows.map((val, i) => ({
      name: `A${i}`,
      year: i,
      cumulative: val,
    }));
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          timeline
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Delai de Recuperation (Payback)
        </h3>
      </div>

      {/* Form */}
      <div className="mb-5">
        <label
          htmlFor="payback-cash-flows"
          className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
        >
          Flux de tresorerie (MAD)
        </label>
        <input
          id="payback-cash-flows"
          type="text"
          value={cashFlowsInput}
          onChange={(e) => setCashFlowsInput(e.target.value)}
          placeholder="-500000,120000,150000,180000"
          className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
        />
        <p className="mt-1 text-[10px] text-on-surface-variant">
          Separes par des virgules. Negatifs = investissements, Positifs = retours.
        </p>
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
            Calculer
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
          {/* Payback years big number */}
          <div className="flex items-center justify-center gap-4 py-4">
            <span className="material-symbols-outlined text-4xl text-primary">
              schedule
            </span>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Delai de recuperation
              </p>
              {result.payback_years !== null ? (
                <p className="font-sans text-3xl font-bold text-on-surface">
                  {result.payback_years.toFixed(1)}{' '}
                  <span className="text-lg font-semibold text-on-surface-variant">
                    ans
                  </span>
                </p>
              ) : (
                <p className="font-sans text-lg font-semibold text-error">
                  Non atteint
                </p>
              )}
            </div>
          </div>

          {/* Investment / Return cards */}
          <div className="grid grid-cols-2 gap-4 border-t border-outline-variant/10 pt-4">
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <span className="material-symbols-outlined text-xl text-error mb-1">
                trending_down
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Investissement total
              </p>
              <p className="font-sans text-lg font-semibold text-error">
                {fmtMAD(result.total_investment)}
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <span className="material-symbols-outlined text-xl text-green-600 mb-1">
                trending_up
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Retour total
              </p>
              <p className="font-sans text-lg font-semibold text-green-700">
                {fmtMAD(result.total_return)}
              </p>
            </div>
          </div>

          {/* Cumulative line chart with zero crossing */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Flux cumules dans le temps
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={chartData}
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
                  content={<CumulativeTooltip />}
                  cursor={{ stroke: '#c2c6d6', strokeDasharray: '3 3' }}
                />
                <ReferenceLine
                  y={0}
                  stroke="#424754"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  label={{
                    value: 'Seuil de rentabilite',
                    position: 'right',
                    fill: '#424754',
                    fontSize: 10,
                    fontFamily: 'Inter, sans-serif',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="cumulative"
                  stroke="#0058be"
                  strokeWidth={2.5}
                  dot={{
                    fill: '#0058be',
                    stroke: '#ffffff',
                    strokeWidth: 2,
                    r: 5,
                  }}
                  activeDot={{
                    fill: '#0058be',
                    stroke: '#ffffff',
                    strokeWidth: 2,
                    r: 7,
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            timeline
          </span>
          <p className="text-sm">
            Saisissez les flux de tresorerie et cliquez sur Calculer pour determiner le delai de recuperation.
          </p>
        </div>
      )}
    </div>
  );
}
