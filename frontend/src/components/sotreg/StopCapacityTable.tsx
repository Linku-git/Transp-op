import { useState, useCallback } from 'react';
import { computeStopCapacity } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { StopCapacityRequest, StopCapacityResponse } from '@/types/sotreg';
import { LOS_COLORS, LOS_LABELS } from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

function fmtNum(value: number, decimals = 1): string {
  return value.toLocaleString('fr-MA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function losTextColor(grade: string): string {
  switch (grade) {
    case 'A': return 'text-green-700';
    case 'B': return 'text-lime-700';
    case 'C': return 'text-yellow-700';
    case 'D': return 'text-orange-700';
    case 'E': return 'text-red-600';
    case 'F': return 'text-red-900';
    default: return 'text-on-surface';
  }
}

function losBgColor(grade: string): string {
  switch (grade) {
    case 'A': return 'bg-green-50';
    case 'B': return 'bg-lime-50';
    case 'C': return 'bg-yellow-50';
    case 'D': return 'bg-orange-50';
    case 'E': return 'bg-red-50';
    case 'F': return 'bg-red-100';
    default: return 'bg-surface-container-low';
  }
}

/* ── Metric card ─────────────────────────────────────────────────────────── */

function MetricCard({
  label,
  icon,
  value,
  unit,
}: {
  label: string;
  icon: string;
  value: string;
  unit?: string;
}) {
  return (
    <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-2">
      <span className="material-symbols-outlined text-xl text-on-surface-variant">
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p className="font-sans text-xl font-semibold text-on-surface">
        {value}
        {unit && (
          <span className="text-sm font-normal text-on-surface-variant ml-1">{unit}</span>
        )}
      </p>
    </div>
  );
}

/* ── Utilization bar ─────────────────────────────────────────────────────── */

function UtilizationBar({ utilization }: { utilization: number }) {
  const pct = Math.min(utilization * 100, 100);
  const barColor =
    pct < 50
      ? 'from-green-400 to-green-500'
      : pct < 75
        ? 'from-amber-400 to-amber-500'
        : 'from-red-400 to-red-500';

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Taux d&apos;utilisation
        </p>
        <p className="text-xs font-medium text-on-surface">
          {fmtNum(pct, 1)}%
        </p>
      </div>
      <div className="w-full h-3 bg-surface-container rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 bg-gradient-to-r ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */

export function StopCapacityTable() {
  /* Form state */
  const [nBerths, setNBerths] = useState<number>(1);
  const [dwellTimeS, setDwellTimeS] = useState<number>(30);
  const [demandBph, setDemandBph] = useState<number>(6);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StopCapacityResponse | null>(null);

  const handleAnalyze = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: StopCapacityRequest = {
        n_berths: nBerths,
        dwell_time_s: dwellTimeS,
        demand_buses_per_hour: demandBph,
      };
      const res = await computeStopCapacity(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de l\'analyse de capacite'));
    } finally {
      setLoading(false);
    }
  }, [nBerths, dwellTimeS, demandBph]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          groups
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Capacite des arrets (HCM 2000)
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        {/* n_berths */}
        <div>
          <label
            htmlFor="sc-berths"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Nombre de quais
          </label>
          <input
            id="sc-berths"
            type="number"
            min={1}
            max={10}
            step={1}
            value={nBerths}
            onChange={(e) => setNBerths(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* dwell_time_s */}
        <div>
          <label
            htmlFor="sc-dwell"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Temps d&apos;arret (s)
          </label>
          <input
            id="sc-dwell"
            type="number"
            min={5}
            max={300}
            step={5}
            value={dwellTimeS}
            onChange={(e) => setDwellTimeS(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* demand_buses_per_hour */}
        <div>
          <label
            htmlFor="sc-demand"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Demande (bus/h)
          </label>
          <input
            id="sc-demand"
            type="number"
            min={1}
            max={120}
            step={1}
            value={demandBph}
            onChange={(e) => setDemandBph(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>
      </div>

      {/* Analyze button */}
      <button
        type="button"
        onClick={handleAnalyze}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Analyse en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              analytics
            </span>
            Analyser
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
        <div className="mt-6 space-y-5">
          {/* Big number + LOS badge */}
          <div className="flex flex-col items-center py-4">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              Capacite
            </p>
            <p className="font-sans text-4xl font-bold text-on-surface">
              {fmtNum(result.capacity_buses_per_hour, 0)}
              <span className="text-lg font-normal text-on-surface-variant ml-2">bus/h</span>
            </p>

            {/* LOS badge */}
            <div className="mt-3 flex items-center gap-3">
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-bold ${losBgColor(result.los_grade)} ${losTextColor(result.los_grade)}`}
              >
                <span
                  className="inline-block w-3 h-3 rounded-full flex-shrink-0"
                  style={{ background: LOS_COLORS[result.los_grade] ?? '#6b7280' }}
                />
                LOS {result.los_grade} &mdash; {LOS_LABELS[result.los_grade] ?? result.los_grade}
              </span>
            </div>
          </div>

          {/* Metric cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard
              label="Utilisation"
              icon="donut_large"
              value={fmtNum(result.utilization * 100, 1)}
              unit="%"
            />
            <MetricCard
              label="Attente moy."
              icon="schedule"
              value={fmtNum(result.avg_wait_seconds, 0)}
              unit="s"
            />
            <MetricCard
              label="Arret effectif"
              icon="timer"
              value={fmtNum(result.effective_dwell_s, 1)}
              unit="s"
            />
            <MetricCard
              label="Quais"
              icon="dock"
              value={String(result.n_berths)}
            />
          </div>

          {/* Utilization bar */}
          <UtilizationBar utilization={result.utilization} />

          {/* LOS description */}
          {result.los_description && (
            <div className="bg-surface-container-low rounded-lg p-4">
              <div className="flex items-start gap-2">
                <span className="material-symbols-outlined text-base text-on-surface-variant mt-0.5">
                  info
                </span>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                    Description du niveau de service
                  </p>
                  <p className="text-sm text-on-surface leading-relaxed">
                    {result.los_description}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Parameters used summary */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-outline-variant/10">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Parametres
            </p>
            <span className="bg-surface-container-low rounded-md px-2 py-0.5 text-xs text-on-surface-variant">
              quais={result.n_berths}
            </span>
            <span className="bg-surface-container-low rounded-md px-2 py-0.5 text-xs text-on-surface-variant">
              g/C={fmtNum(result.green_ratio, 2)}
            </span>
            <span className="bg-surface-container-low rounded-md px-2 py-0.5 text-xs text-on-surface-variant">
              z={fmtNum(result.z_factor, 2)}
            </span>
            <span className="bg-surface-container-low rounded-md px-2 py-0.5 text-xs text-on-surface-variant">
              cv={fmtNum(result.cv_dwell, 2)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
