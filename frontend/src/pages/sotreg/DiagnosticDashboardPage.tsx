import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import {
  getFleetContextSnapshot,
  listLignes,
  getZFECompliance,
  listODMatrix,
  computeODMatrix,
} from '@/api/sotreg';
import type {
  FleetContext,
  LigneListResponse,
  ZFEComplianceResponse,
  ODMatrixListResponse,
  ODMatrixEntry,
} from '@/types/sotreg';

/* ------------------------------------------------------------------ */
/*  Number formatting helpers                                          */
/* ------------------------------------------------------------------ */

const fmtInt = new Intl.NumberFormat('fr-FR', {
  maximumFractionDigits: 0,
});

const fmtDec1 = new Intl.NumberFormat('fr-FR', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const fmtPct = new Intl.NumberFormat('fr-FR', {
  style: 'percent',
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function formatLargeNumber(n: number): string {
  if (n >= 1_000_000) return `${fmtDec1.format(n / 1_000_000)}M`;
  if (n >= 1_000) return `${fmtDec1.format(n / 1_000)}k`;
  return fmtInt.format(n);
}

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

function KpiCardSkeleton() {
  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="w-10 h-10 rounded-full bg-surface-container-high" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 w-24 rounded bg-surface-container-high" />
        <div className="h-8 w-16 rounded bg-surface-container-high" />
      </div>
    </div>
  );
}

interface KpiCardProps {
  icon: string;
  iconBg: string;
  label: string;
  value: string;
  subtitle?: string;
  isLoading: boolean;
}

function KpiCard({ icon, iconBg, label, value, subtitle, isLoading }: KpiCardProps) {
  if (isLoading) return <KpiCardSkeleton />;

  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10">
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${iconBg}`}>
          <span className="material-symbols-outlined text-xl">{icon}</span>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          {label}
        </p>
        <p className="text-3xl font-black text-on-surface mt-1 tabular-nums">
          {value}
        </p>
        {subtitle && (
          <p className="text-xs text-on-surface-variant mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  );
}

/* ── Mini donut for motorization split ─────────────────────────────── */

interface MotoSlice {
  label: string;
  pct: number;
  color: string;
}

function MiniDonut({ slices }: { slices: MotoSlice[] }) {
  const total = slices.reduce((sum, s) => sum + s.pct, 0);
  if (total === 0) return null;

  let cumulative = 0;
  const radius = 40;
  const cx = 50;
  const cy = 50;

  function coordsForPct(pct: number) {
    const angle = pct * 2 * Math.PI - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  }

  return (
    <svg viewBox="0 0 100 100" className="w-full h-full">
      {slices.map((slice) => {
        if (slice.pct <= 0) return null;
        const normalizedPct = slice.pct / total;
        const startPct = cumulative;
        cumulative += normalizedPct;

        const start = coordsForPct(startPct);
        const end = coordsForPct(cumulative);
        const largeArc = normalizedPct > 0.5 ? 1 : 0;

        if (normalizedPct >= 0.999) {
          return (
            <circle key={slice.label} cx={cx} cy={cy} r={radius} fill={slice.color} />
          );
        }

        return (
          <path
            key={slice.label}
            d={`M ${cx} ${cy} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y} Z`}
            fill={slice.color}
          />
        );
      })}
      <circle cx={cx} cy={cy} r={22} fill="white" />
    </svg>
  );
}

function MotorizationCard({
  fleet,
  isLoading,
}: {
  fleet: FleetContext | null;
  isLoading: boolean;
}) {
  const slices = useMemo<MotoSlice[]>(() => {
    if (!fleet) return [];
    return [
      { label: 'Diesel', pct: fleet.pct_diesel, color: '#64748b' },
      { label: 'Electrique', pct: fleet.pct_electric, color: '#0058be' },
      { label: 'Hybride', pct: fleet.pct_hybrid, color: '#924700' },
    ].filter((s) => s.pct > 0);
  }, [fleet]);

  if (isLoading) return <KpiCardSkeleton />;

  return (
    <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10">
      <div className="flex items-start justify-between">
        <div className="w-10 h-10 rounded-full flex items-center justify-center bg-amber-50 text-amber-700">
          <span className="material-symbols-outlined text-xl">local_gas_station</span>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Motorisation
        </p>
        {slices.length === 0 ? (
          <p className="text-xs text-on-surface-variant mt-2">Aucune donnee</p>
        ) : (
          <div className="flex items-center gap-3 mt-2">
            <div className="w-14 h-14 flex-shrink-0">
              <MiniDonut slices={slices} />
            </div>
            <div className="flex-1 space-y-1 min-w-0">
              {slices.map((s) => (
                <div key={s.label} className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: s.color }}
                  />
                  <span className="text-[10px] text-on-surface truncate flex-1">
                    {s.label}
                  </span>
                  <span className="text-[10px] font-semibold text-on-surface tabular-nums">
                    {fmtInt.format(Math.round(s.pct))}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── ZFE compliance summary card ───────────────────────────────────── */

function ZFEComplianceCard({
  zfe,
  isLoading,
}: {
  zfe: ZFEComplianceResponse | null;
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 animate-pulse">
        <div className="h-4 w-48 rounded bg-surface-container-high mb-4" />
        <div className="space-y-3">
          <div className="h-3 w-full rounded bg-surface-container-high" />
          <div className="h-3 w-3/4 rounded bg-surface-container-high" />
          <div className="h-8 w-full rounded bg-surface-container-high" />
        </div>
      </div>
    );
  }

  if (!zfe) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          Conformite ZFE
        </h3>
        <p className="text-sm text-on-surface-variant">Aucune donnee ZFE disponible.</p>
      </div>
    );
  }

  const compliancePct =
    zfe.total_lignes > 0 ? zfe.lignes_in_zfe / zfe.total_lignes : 0;
  const affectedCount = zfe.lignes_in_zfe;

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-lg text-primary">shield</span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Conformite ZFE
        </h3>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-5">
        <div>
          <p className="text-2xl font-black text-on-surface tabular-nums">
            {fmtInt.format(zfe.total_lignes)}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-0.5">
            Lignes totales
          </p>
        </div>
        <div>
          <p className="text-2xl font-black text-amber-700 tabular-nums">
            {fmtInt.format(affectedCount)}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-0.5">
            En zone ZFE
          </p>
        </div>
        <div>
          <p className="text-2xl font-black text-on-surface tabular-nums">
            {fmtPct.format(compliancePct)}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-0.5">
            Taux ZFE
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 rounded-full bg-surface-container-high mb-5">
        <div
          className="h-full rounded-full bg-gradient-to-r from-amber-500 to-amber-600 transition-all duration-500"
          style={{ width: `${Math.min(compliancePct * 100, 100)}%` }}
        />
      </div>

      {/* Affected lignes preview */}
      {zfe.results.length > 0 && (
        <div className="mb-5">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
            Lignes affectees
          </p>
          <div className="space-y-1.5 max-h-40 overflow-y-auto">
            {zfe.results
              .filter((r) => r.any_endpoint_in_zfe)
              .slice(0, 5)
              .map((r) => (
                <div
                  key={r.ligne_id}
                  className="flex items-center gap-2 text-xs"
                >
                  <span className="material-symbols-outlined text-sm text-amber-600">
                    warning
                  </span>
                  <span className="font-medium text-on-surface">
                    {r.ligne_code}
                  </span>
                  <span className="text-on-surface-variant truncate flex-1">
                    {r.ligne_name}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Quick link buttons */}
      <div className="flex flex-wrap gap-2">
        <Link
          to="/sotreg/lignes"
          className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-primary bg-surface-container-lowest border border-outline-variant/15 rounded-lg shadow-sm hover:bg-blue-50 transition-colors"
        >
          <span className="material-symbols-outlined text-sm">list</span>
          Voir les lignes
        </Link>
        <Link
          to="/sotreg/lignes/new"
          className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-on-primary bg-gradient-to-br from-primary to-primary-container rounded-lg shadow-lg shadow-primary/20 hover:opacity-90 transition-opacity"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          Nouvelle ligne
        </Link>
      </div>
    </div>
  );
}

/* ── OD flow summary card ──────────────────────────────────────────── */

function ODFlowSummaryCard({
  od,
  isLoading,
  onCompute,
  isComputing,
}: {
  od: ODMatrixListResponse | null;
  isLoading: boolean;
  onCompute: () => void;
  isComputing: boolean;
}) {
  const topFlows = useMemo<ODMatrixEntry[]>(() => {
    if (!od?.data) return [];
    return [...od.data]
      .sort((a, b) => b.flow_estimate - a.flow_estimate)
      .slice(0, 5);
  }, [od]);

  if (isLoading) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 animate-pulse">
        <div className="h-4 w-48 rounded bg-surface-container-high mb-4" />
        <div className="space-y-3">
          <div className="h-3 w-full rounded bg-surface-container-high" />
          <div className="h-3 w-3/4 rounded bg-surface-container-high" />
          <div className="h-3 w-1/2 rounded bg-surface-container-high" />
        </div>
      </div>
    );
  }

  const totalFlows = od?.total ?? 0;
  const hasData = od !== null && od.data.length > 0;

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-lg text-primary">
          swap_calls
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Matrice OD (Origine-Destination)
        </h3>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 mb-5">
        <div>
          <p className="text-2xl font-black text-on-surface tabular-nums">
            {fmtInt.format(totalFlows)}
          </p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-0.5">
            Flux totaux
          </p>
        </div>
        {od && (
          <div>
            <p className="text-2xl font-black text-on-surface tabular-nums">
              {fmtDec1.format(od.beta_used)}
            </p>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mt-0.5">
              Beta (Wilson)
            </p>
          </div>
        )}
      </div>

      {/* Top 5 flows */}
      {hasData && (
        <div className="mb-5">
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
            Top 5 flux
          </p>
          <div className="space-y-2">
            {topFlows.map((flow) => {
              const maxFlow = topFlows[0]?.flow_estimate ?? 1;
              const barWidth = Math.max((flow.flow_estimate / maxFlow) * 100, 4);

              return (
                <div key={flow.id} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-on-surface font-medium truncate flex-1 mr-2">
                      {flow.origin_zone}
                      <span className="text-on-surface-variant mx-1">
                        &rarr;
                      </span>
                      {flow.destination_zone}
                    </span>
                    <span className="text-on-surface-variant tabular-nums flex-shrink-0">
                      {fmtDec1.format(flow.flow_estimate)}
                    </span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-surface-container-high">
                    <div
                      className="h-full rounded-full bg-primary/70 transition-all duration-300"
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!hasData && (
        <div className="text-center py-6 mb-4">
          <span className="material-symbols-outlined text-3xl text-on-surface-variant/50 mb-2 block">
            hub
          </span>
          <p className="text-sm text-on-surface-variant">
            Aucun flux OD calcule.
          </p>
          <p className="text-xs text-on-surface-variant/70 mt-1">
            Lancez le calcul pour generer la matrice.
          </p>
        </div>
      )}

      {/* Compute button */}
      <button
        type="button"
        onClick={onCompute}
        disabled={isComputing}
        className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-on-primary bg-gradient-to-br from-primary to-primary-container rounded-lg shadow-lg shadow-primary/20 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isComputing ? (
          <>
            <div className="w-3.5 h-3.5 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
            Calcul en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-sm">calculate</span>
            {hasData ? 'Recalculer la matrice OD' : 'Calculer la matrice OD'}
          </>
        )}
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main page component                                                */
/* ------------------------------------------------------------------ */

export function DiagnosticDashboardPage() {
  const { t } = useTranslation();

  /* ── State ──────────────────────────────────────────────────────── */
  const [fleet, setFleet] = useState<FleetContext | null>(null);
  const [lignes, setLignes] = useState<LigneListResponse | null>(null);
  const [zfe, setZFE] = useState<ZFEComplianceResponse | null>(null);
  const [od, setOD] = useState<ODMatrixListResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isComputing, setIsComputing] = useState(false);

  /* ── Data fetching ──────────────────────────────────────────────── */
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [fleetRes, lignesRes, zfeRes, odRes] = await Promise.allSettled([
        getFleetContextSnapshot(),
        listLignes({ page_size: 100 }),
        getZFECompliance(),
        listODMatrix(),
      ]);

      if (fleetRes.status === 'fulfilled') setFleet(fleetRes.value);
      if (lignesRes.status === 'fulfilled') setLignes(lignesRes.value);
      if (zfeRes.status === 'fulfilled') setZFE(zfeRes.value);
      if (odRes.status === 'fulfilled') setOD(odRes.value);

      // If all failed, show error
      const allFailed = [fleetRes, lignesRes, zfeRes, odRes].every(
        (r) => r.status === 'rejected',
      );
      if (allFailed) {
        setError(t('common.error', 'Erreur lors du chargement des donnees.'));
      }
    } catch {
      setError(t('common.error', 'Erreur lors du chargement des donnees.'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  /* ── Compute OD matrix handler ──────────────────────────────────── */
  const handleComputeOD = useCallback(async () => {
    setIsComputing(true);
    try {
      const result = await computeODMatrix({});
      // Refresh the OD list after computation
      const refreshed = await listODMatrix();
      setOD(refreshed);
      void result; // used for the compute call
    } catch {
      // Silently handle — user sees no data and can retry
    } finally {
      setIsComputing(false);
    }
  }, []);

  /* ── Derived values ─────────────────────────────────────────────── */
  const ligneCount = lignes?.meta?.total ?? 0;
  const isDataLoading = loading;

  /* ── Error state ────────────────────────────────────────────────── */
  if (error && !fleet && !lignes && !zfe && !od) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4">
        <span className="material-symbols-outlined text-4xl text-error">error</span>
        <p className="font-sans text-sm text-on-surface-variant">{error}</p>
        <button
          type="button"
          onClick={() => void fetchData()}
          className="bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-4 py-2 font-sans text-sm font-medium"
        >
          Reessayer
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* ── Page header ─────────────────────────────────────────────── */}
      <div>
        <h1 className="font-sans text-xl font-bold text-on-surface">
          Diagnostic Flotte
        </h1>
        <p className="font-sans text-sm text-on-surface-variant mt-1">
          Module M1 — Contexte &amp; Analyse
        </p>
      </div>

      {/* ── Fleet KPI summary cards ─────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          icon="directions_bus"
          iconBg="bg-primary/10 text-primary"
          label="Total vehicules"
          value={fleet ? fmtInt.format(fleet.total_vehicles) : '—'}
          isLoading={isDataLoading}
        />
        <KpiCard
          icon="straighten"
          iconBg="bg-blue-50 text-blue-700"
          label="Km annuels"
          value={fleet ? formatLargeNumber(fleet.total_km_annual) : '—'}
          subtitle={fleet ? `${fmtInt.format(fleet.total_km_annual)} km` : undefined}
          isLoading={isDataLoading}
        />
        <KpiCard
          icon="eco"
          iconBg="bg-green-50 text-green-700"
          label="tCO2/an"
          value={fleet ? fmtDec1.format(fleet.total_tco2_annual) : '—'}
          isLoading={isDataLoading}
        />
        <KpiCard
          icon="schedule"
          iconBg="bg-purple-50 text-purple-700"
          label="Age moyen"
          value={
            fleet && fleet.average_age_years !== null
              ? `${fmtDec1.format(fleet.average_age_years)} ans`
              : '—'
          }
          isLoading={isDataLoading}
        />
        <MotorizationCard fleet={fleet} isLoading={isDataLoading} />
        <KpiCard
          icon="route"
          iconBg="bg-amber-50 text-amber-700"
          label="Lignes actives"
          value={lignes ? fmtInt.format(ligneCount) : '—'}
          isLoading={isDataLoading}
        />
      </div>

      {/* ── Two-column layout: ZFE + OD ─────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ZFEComplianceCard zfe={zfe} isLoading={isDataLoading} />
        <ODFlowSummaryCard
          od={od}
          isLoading={isDataLoading}
          onCompute={() => void handleComputeOD()}
          isComputing={isComputing}
        />
      </div>
    </div>
  );
}
