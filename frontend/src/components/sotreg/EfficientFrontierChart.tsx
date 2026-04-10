import { useState, useCallback, useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Line,
} from 'recharts';
import { computeEfficientFrontier } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  EfficientFrontierResponse,
  PortfolioResult,
} from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

function pctFmt(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

/* ── Row type ─────────────────────────────────────────────────────────────── */

interface TechRow {
  name: string;
  expected_return: string;
  variance: string;
}

function emptyRow(): TechRow {
  return { name: '', expected_return: '', variance: '' };
}

/* ── Scatter tooltip ──────────────────────────────────────────────────────── */

interface ScatterPayload {
  risk: number;
  expected_return: number;
  label?: string;
}

interface ScatterTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: ScatterPayload }>;
}

function FrontierTooltip({ active, payload }: ScatterTooltipProps) {
  if (!active || !payload?.length) return null;
  const pt = payload[0].payload;

  return (
    <div className="bg-surface-container-lowest text-on-surface rounded-lg px-4 py-3 shadow-lg border border-outline-variant/10 min-w-[180px]">
      {pt.label && (
        <p className="font-sans text-xs font-semibold mb-1 text-primary">
          {pt.label}
        </p>
      )}
      <div className="flex items-center justify-between gap-4 mb-0.5">
        <span className="font-sans text-xs text-on-surface-variant">Risque (ecart-type)</span>
        <span className="font-sans text-xs font-medium">{pctFmt(pt.risk)}</span>
      </div>
      <div className="flex items-center justify-between gap-4">
        <span className="font-sans text-xs text-on-surface-variant">Rendement attendu</span>
        <span className="font-sans text-xs font-medium">{pctFmt(pt.expected_return)}</span>
      </div>
    </div>
  );
}

/* ── Weight table ─────────────────────────────────────────────────────────── */

function WeightsTable({
  portfolio,
  names,
  title,
}: {
  portfolio: PortfolioResult;
  names: string[];
  title: string;
}) {
  return (
    <div>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
        {title}
      </p>
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-surface-container-low/50">
              <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                Technologie
              </th>
              <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                Poids
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10">
            {names.map((n, i) => (
              <tr key={n} className="hover:bg-surface-bright">
                <td className="px-3 py-2 font-sans text-on-surface">{n}</td>
                <td className="px-3 py-2 text-right font-sans font-medium text-on-surface">
                  {pctFmt(portfolio.weights[i] ?? 0)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-2 flex items-center gap-4 text-xs text-on-surface-variant">
        <span>Rendement: <strong className="text-on-surface">{pctFmt(portfolio.expected_return)}</strong></span>
        <span>Risque: <strong className="text-on-surface">{pctFmt(portfolio.risk)}</strong></span>
      </div>
    </div>
  );
}

/* ── Main component ───────────────────────────────────────────────────────── */

export function EfficientFrontierChart() {
  /* Form state: technology rows */
  const [rows, setRows] = useState<TechRow[]>([
    { name: 'Diesel', expected_return: '0.05', variance: '0.01' },
    { name: 'Electrique', expected_return: '0.12', variance: '0.04' },
    { name: 'Hybride', expected_return: '0.08', variance: '0.02' },
  ]);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EfficientFrontierResponse | null>(null);

  /* ── Row management ─────────────────────────────────────────────────────── */

  const updateRow = useCallback(
    (index: number, field: keyof TechRow, value: string) => {
      setRows((prev) => {
        const next = [...prev];
        next[index] = { ...next[index], [field]: value };
        return next;
      });
    },
    [],
  );

  const addRow = useCallback(() => {
    setRows((prev) => [...prev, emptyRow()]);
  }, []);

  const removeRow = useCallback((index: number) => {
    setRows((prev) => prev.filter((_, i) => i !== index));
  }, []);

  /* ── Compute ────────────────────────────────────────────────────────────── */

  const canCompute = useMemo(() => {
    if (rows.length < 2) return false;
    return rows.every(
      (r) =>
        r.name.trim().length > 0 &&
        !isNaN(parseFloat(r.expected_return)) &&
        !isNaN(parseFloat(r.variance)) &&
        parseFloat(r.variance) > 0,
    );
  }, [rows]);

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const expected_returns = rows.map((r) => parseFloat(r.expected_return));
      const n = rows.length;

      /* Build simple diagonal covariance matrix from variances.
         Off-diagonal elements set to 0 (uncorrelated assumption). */
      const covariance_matrix: number[][] = Array.from({ length: n }, (_, i) =>
        Array.from({ length: n }, (_, j) =>
          i === j ? parseFloat(rows[i].variance) : 0,
        ),
      );

      const technology_names = rows.map((r) => r.name.trim());

      const res = await computeEfficientFrontier({
        expected_returns,
        covariance_matrix,
        technology_names,
      });
      setResult(res);
    } catch (err) {
      setError(
        extractApiError(err, 'Erreur lors du calcul de la frontiere efficiente'),
      );
    } finally {
      setLoading(false);
    }
  }, [rows]);

  /* ── Chart data ─────────────────────────────────────────────────────────── */

  const chartData = useMemo(() => {
    if (!result) return { frontier: [], minRisk: [], maxReturn: [] };

    const frontier = result.frontier.map((p) => ({
      risk: p.risk,
      expected_return: p.expected_return,
    }));

    const minRisk = [
      {
        risk: result.min_risk_portfolio.risk,
        expected_return: result.min_risk_portfolio.expected_return,
        label: 'Min risque',
      },
    ];

    const maxReturn = [
      {
        risk: result.max_return_portfolio.risk,
        expected_return: result.max_return_portfolio.expected_return,
        label: 'Max rendement',
      },
    ];

    return { frontier, minRisk, maxReturn };
  }, [result]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          show_chart
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Frontiere efficiente (Markowitz)
        </h3>
      </div>

      {/* Technology inputs table */}
      <div className="mb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          Technologies
        </p>
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Nom
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Rendement attendu
                </th>
                <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  Variance
                </th>
                <th className="w-10" />
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {rows.map((row, idx) => (
                <tr key={idx} className="hover:bg-surface-bright">
                  <td className="px-3 py-1.5">
                    <input
                      type="text"
                      value={row.name}
                      onChange={(e) => updateRow(idx, 'name', e.target.value)}
                      placeholder="ex: Diesel"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      step="0.01"
                      value={row.expected_return}
                      onChange={(e) =>
                        updateRow(idx, 'expected_return', e.target.value)
                      }
                      placeholder="0.10"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-3 py-1.5">
                    <input
                      type="number"
                      step="0.001"
                      value={row.variance}
                      onChange={(e) =>
                        updateRow(idx, 'variance', e.target.value)
                      }
                      placeholder="0.01"
                      className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </td>
                  <td className="px-2 py-1.5 text-center">
                    <button
                      type="button"
                      onClick={() => removeRow(idx)}
                      disabled={rows.length <= 2}
                      className="text-on-surface-variant hover:text-error disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                      title="Supprimer"
                    >
                      <span className="material-symbols-outlined text-lg">
                        close
                      </span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <button
          type="button"
          onClick={addRow}
          className="mt-2 inline-flex items-center gap-1.5 text-primary text-sm font-medium hover:opacity-80 transition-opacity"
        >
          <span className="material-symbols-outlined text-base">add</span>
          Ajouter une technologie
        </button>
      </div>

      {/* Compute button */}
      <button
        type="button"
        onClick={handleCompute}
        disabled={loading || !canCompute}
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
            Calculer Frontiere
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
          {/* Scatter chart */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Frontiere efficiente
            </p>
            <ResponsiveContainer width="100%" height={360}>
              <ScatterChart margin={{ top: 16, right: 24, bottom: 32, left: 16 }}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#c2c6d620"
                />
                <XAxis
                  dataKey="risk"
                  type="number"
                  name="Risque"
                  label={{
                    value: 'Risque (ecart-type)',
                    position: 'insideBottom',
                    offset: -16,
                    style: {
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 11,
                      fill: '#424754',
                    },
                  }}
                  tick={{
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                  }}
                  tickFormatter={(v: number) => pctFmt(v)}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  dataKey="expected_return"
                  type="number"
                  name="Rendement"
                  label={{
                    value: 'Rendement attendu',
                    angle: -90,
                    position: 'insideLeft',
                    offset: 4,
                    style: {
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 11,
                      fill: '#424754',
                    },
                  }}
                  tick={{
                    fill: '#424754',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                  }}
                  tickFormatter={(v: number) => pctFmt(v)}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<FrontierTooltip />} />

                {/* Frontier line connecting points */}
                <Scatter
                  name="Frontiere"
                  data={chartData.frontier}
                  fill="#0058be"
                  fillOpacity={0.5}
                  r={4}
                  line={{ stroke: '#0058be', strokeWidth: 2 }}
                  lineType="monotone"
                />

                {/* Min risk point (green) */}
                <Scatter
                  name="Min risque"
                  data={chartData.minRisk}
                  fill="#22c55e"
                  r={8}
                  shape="circle"
                />

                {/* Max return point (blue) */}
                <Scatter
                  name="Max rendement"
                  data={chartData.maxReturn}
                  fill="#0058be"
                  r={8}
                  shape="diamond"
                />
              </ScatterChart>
            </ResponsiveContainer>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 mt-2">
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 rounded-full bg-[#0058be] opacity-50" />
                <span className="text-xs text-on-surface-variant">Frontiere</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 rounded-full bg-green-500" />
                <span className="text-xs text-on-surface-variant">Min risque</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="inline-block w-3 h-3 rounded-full bg-[#0058be]" />
                <span className="text-xs text-on-surface-variant">Max rendement</span>
              </div>
            </div>
          </div>

          {/* Weight tables */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-outline-variant/10 pt-6">
            <WeightsTable
              portfolio={result.min_risk_portfolio}
              names={result.technology_names}
              title="Portefeuille min risque"
            />
            <WeightsTable
              portfolio={result.max_return_portfolio}
              names={result.technology_names}
              title="Portefeuille max rendement"
            />
          </div>

          {/* Full frontier weights table */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              Points de la frontiere ({madFmt.format(result.frontier.length)} points)
            </p>
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden max-h-64 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0">
                  <tr className="bg-surface-container-low/50">
                    <th className="text-left px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      #
                    </th>
                    <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Risque
                    </th>
                    <th className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Rendement
                    </th>
                    {result.technology_names.map((n) => (
                      <th
                        key={n}
                        className="text-right px-3 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant"
                      >
                        {n}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {result.frontier.map((pt, idx) => (
                    <tr key={idx} className="hover:bg-surface-bright">
                      <td className="px-3 py-1.5 text-on-surface-variant">
                        {idx + 1}
                      </td>
                      <td className="px-3 py-1.5 text-right font-medium text-on-surface">
                        {pctFmt(pt.risk)}
                      </td>
                      <td className="px-3 py-1.5 text-right font-medium text-on-surface">
                        {pctFmt(pt.expected_return)}
                      </td>
                      {pt.weights.map((w, wi) => (
                        <td
                          key={wi}
                          className="px-3 py-1.5 text-right text-on-surface"
                        >
                          {pctFmt(w)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            show_chart
          </span>
          <p className="text-sm">
            Ajoutez au moins 2 technologies et cliquez sur Calculer Frontiere.
          </p>
        </div>
      )}
    </div>
  );
}
