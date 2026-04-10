import { useState, useCallback, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';
import { computeBreakeven } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { BreakevenRequest, BreakevenResponse } from '@/types/sotreg';

/* ── Constants ─────────────────────────────────────────────────────────────── */

const GRID_STROKE = 'rgba(215, 228, 236, 0.2)';
const COLOR_DIESEL = '#dc2626';
const COLOR_ELECTRIC = '#0058be';
const KM_MAX = 100_000;
const KM_STEP = 5_000;

/* ── Helpers ───────────────────────────────────────────────────────────────── */

const madFormatter = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFormatter.format(value)} MAD`;
}

function fmtKm(value: number): string {
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(0)}K`;
  }
  return madFormatter.format(value);
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

/* ── Chart data point ──────────────────────────────────────────────────────── */

interface ChartDatum {
  km: number;
  diesel: number;
  electric: number;
}

/* ── Tooltip ───────────────────────────────────────────────────────────────── */

interface TooltipPayloadEntry {
  name: string;
  value: number;
  color: string;
  dataKey: string;
  payload: ChartDatum;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: number;
}

function BreakevenTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[200px]">
      <p className="font-sans text-sm font-semibold mb-2">
        {madFormatter.format(label ?? 0)} km
      </p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4 mb-0.5">
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ background: entry.color }}
            />
            <span className="font-sans text-xs text-on-surface-variant">
              {entry.dataKey === 'diesel' ? 'Diesel' : 'Electrique'}
            </span>
          </div>
          <span className="font-sans text-xs font-medium">
            {fmtMAD(entry.value)}
          </span>
        </div>
      ))}
      {payload.length >= 2 && (
        <div className="border-t border-outline-variant/10 mt-1.5 pt-1.5 flex justify-between">
          <span className="font-sans text-xs text-on-surface-variant">Delta</span>
          <span className="font-sans text-xs font-semibold">
            {fmtMAD(Math.abs(payload[0].value - payload[1].value))}
          </span>
        </div>
      )}
    </div>
  );
}

/* ── Legend formatter ───────────────────────────────────────────────────────── */

const LINE_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  electric: 'Electrique',
};

function renderLegend(value: string): string {
  return LINE_LABELS[value] ?? value;
}

/* ── Main component ────────────────────────────────────────────────────────── */

export function BreakevenChart() {
  /* Form state */
  const [capexDiesel, setCapexDiesel] = useState(180000);
  const [capexElectric, setCapexElectric] = useState(300000);
  const [opexDiesel, setOpexDiesel] = useState(0.15);
  const [opexElectric, setOpexElectric] = useState(0.06);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BreakevenResponse | null>(null);

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: BreakevenRequest = {
        capex_diesel: capexDiesel,
        capex_electric: capexElectric,
        opex_per_km_diesel: opexDiesel,
        opex_per_km_electric: opexElectric,
      };
      const res = await computeBreakeven(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul du seuil de rentabilite'));
    } finally {
      setLoading(false);
    }
  }, [capexDiesel, capexElectric, opexDiesel, opexElectric]);

  /* Chart data: generate data points from 0 to KM_MAX in steps of KM_STEP */
  const chartData = useMemo<ChartDatum[]>(() => {
    const points: ChartDatum[] = [];
    for (let km = 0; km <= KM_MAX; km += KM_STEP) {
      points.push({
        km,
        diesel: capexDiesel + opexDiesel * km,
        electric: capexElectric + opexElectric * km,
      });
    }
    return points;
  }, [capexDiesel, capexElectric, opexDiesel, opexElectric]);

  /* Y-axis domain */
  const yMax = useMemo(() => {
    if (chartData.length === 0) return 0;
    const maxVal = Math.max(
      ...chartData.map((d) => Math.max(d.diesel, d.electric)),
    );
    return Math.ceil(maxVal / 50000) * 50000;
  }, [chartData]);

  /* ── Render ──────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          balance
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Seuil de rentabilite Diesel vs Electrique
        </h3>
      </div>

      {/* Form grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        {/* CAPEX Diesel */}
        <div>
          <label
            htmlFor="be-capex-diesel"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            CAPEX Diesel (MAD)
          </label>
          <input
            id="be-capex-diesel"
            type="number"
            min={0}
            step={10000}
            value={capexDiesel}
            onChange={(e) => setCapexDiesel(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* CAPEX Electric */}
        <div>
          <label
            htmlFor="be-capex-elec"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            CAPEX Electrique (MAD)
          </label>
          <input
            id="be-capex-elec"
            type="number"
            min={0}
            step={10000}
            value={capexElectric}
            onChange={(e) => setCapexElectric(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* OPEX Diesel */}
        <div>
          <label
            htmlFor="be-opex-diesel"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            OPEX Diesel / km (MAD)
          </label>
          <input
            id="be-opex-diesel"
            type="number"
            min={0}
            step={0.01}
            value={opexDiesel}
            onChange={(e) => setOpexDiesel(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* OPEX Electric */}
        <div>
          <label
            htmlFor="be-opex-elec"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            OPEX Electrique / km (MAD)
          </label>
          <input
            id="be-opex-elec"
            type="number"
            min={0}
            step={0.01}
            value={opexElectric}
            onChange={(e) => setOpexElectric(Number(e.target.value))}
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
            Calculer Seuil
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
          {/* Top metrics row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Big number: km_seuil */}
            <div className="bg-surface-container-low rounded-lg p-5 flex flex-col items-center gap-2 sm:col-span-2 lg:col-span-1">
              <span className="material-symbols-outlined text-2xl text-primary">
                swap_horiz
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Seuil km/an
              </p>
              <p className="font-sans text-3xl font-bold text-on-surface">
                {result.km_seuil !== null
                  ? madFormatter.format(Math.round(result.km_seuil))
                  : '---'}
              </p>
            </div>

            {/* Viability badge */}
            <div className="bg-surface-container-low rounded-lg p-5 flex flex-col items-center justify-center gap-2">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Viabilite
              </p>
              <span
                className={[
                  'inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-semibold',
                  result.is_electric_viable
                    ? 'bg-green-50 text-green-700'
                    : 'bg-red-50 text-red-700',
                ].join(' ')}
              >
                <span className="material-symbols-outlined text-base">
                  {result.is_electric_viable ? 'check_circle' : 'cancel'}
                </span>
                {result.is_electric_viable ? 'Viable' : 'Non viable'}
              </span>
            </div>

            {/* Delta CAPEX and delta OPEX */}
            <div className="bg-surface-container-low rounded-lg p-5 flex flex-col items-center gap-1.5">
              <span className="material-symbols-outlined text-lg text-on-surface-variant">
                difference
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
                Delta CAPEX
              </p>
              <p className="font-sans text-sm font-semibold text-on-surface">
                {fmtMAD(result.delta_capex)}
              </p>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center mt-1">
                Delta OPEX/km
              </p>
              <p className="font-sans text-sm font-semibold text-on-surface">
                {result.delta_opex_per_km.toLocaleString('fr-MA', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}{' '}
                MAD
              </p>
            </div>

            {/* Payback */}
            <div className="bg-surface-container-low rounded-lg p-5 flex flex-col items-center gap-2">
              <span className="material-symbols-outlined text-lg text-on-surface-variant">
                schedule
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
                Retour sur investissement
              </p>
              <p className="font-sans text-2xl font-bold text-on-surface">
                {result.payback_years_at_reference_km !== null
                  ? `${result.payback_years_at_reference_km.toLocaleString('fr-MA', {
                      minimumFractionDigits: 1,
                      maximumFractionDigits: 1,
                    })} ans`
                  : '---'}
              </p>
              <p className="text-xs text-on-surface-variant">
                a {madFormatter.format(result.annual_km_reference)} km/an
              </p>
            </div>
          </div>

          {/* Line chart */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Cout total en fonction du kilometrage annuel
            </p>
            <ResponsiveContainer width="100%" height={380}>
              <LineChart
                data={chartData}
                margin={{ top: 8, right: 16, bottom: 4, left: 8 }}
              >
                <CartesianGrid
                  stroke={GRID_STROKE}
                  strokeDasharray="none"
                  vertical={false}
                />
                <XAxis
                  dataKey="km"
                  tick={{
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                  }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v: number) => fmtKm(v)}
                  label={{
                    value: 'km/an',
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
                  content={<BreakevenTooltip />}
                  cursor={{ stroke: '#c2c6d6', strokeDasharray: '4 4' }}
                />
                <Legend
                  iconType="line"
                  iconSize={16}
                  formatter={renderLegend}
                  wrapperStyle={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    color: '#424754',
                  }}
                />

                {/* Vertical reference line at breakeven km */}
                {result.km_seuil !== null && (
                  <ReferenceLine
                    x={result.km_seuil}
                    stroke="#424754"
                    strokeDasharray="6 4"
                    strokeWidth={1.5}
                    label={{
                      value: `Seuil: ${madFormatter.format(Math.round(result.km_seuil))} km`,
                      position: 'top',
                      fill: '#424754',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 11,
                    }}
                  />
                )}

                <Line
                  type="monotone"
                  dataKey="diesel"
                  stroke={COLOR_DIESEL}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: COLOR_DIESEL,
                    stroke: '#fff',
                    strokeWidth: 2,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="electric"
                  stroke={COLOR_ELECTRIC}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{
                    r: 5,
                    fill: COLOR_ELECTRIC,
                    stroke: '#fff',
                    strokeWidth: 2,
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
