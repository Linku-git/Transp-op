import { useState, useCallback } from 'react';
import { computeRangeCorrection } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  RangeCorrectionRequest,
  RangeCorrectionResponse,
} from '@/types/sotreg';
import {
  PENTE_PROFILES,
  PENTE_LABELS,
  SAISON_PROFILES,
  SAISON_LABELS,
  VITESSE_PROFILES,
  VITESSE_LABELS,
} from '@/types/sotreg';

/* ── Helpers ───────────────────────────────────────────────────────────────── */

function fmt(value: number, decimals = 1): string {
  return value.toLocaleString('fr-MA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function pctColor(pct: number): string {
  if (pct < 10) return 'bg-green-500';
  if (pct < 25) return 'bg-amber-500';
  return 'bg-red-500';
}

/* ── Factor card ───────────────────────────────────────────────────────────── */

function FactorCard({
  label,
  icon,
  value,
}: {
  label: string;
  icon: string;
  value: number;
}) {
  const isReduction = value < 1;
  return (
    <div className="bg-surface-container-low rounded-lg p-4 flex flex-col items-center gap-2">
      <span className="material-symbols-outlined text-xl text-on-surface-variant">
        {icon}
      </span>
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant text-center">
        {label}
      </p>
      <p
        className={[
          'font-sans text-xl font-semibold',
          isReduction ? 'text-red-600' : 'text-green-600',
        ].join(' ')}
      >
        {fmt(value, 3)}
      </p>
    </div>
  );
}

/* ── Main component ────────────────────────────────────────────────────────── */

export function RangeCorrectionPanel() {
  /* Form state */
  const [penteProfile, setPenteProfile] = useState<string>(PENTE_PROFILES[0]);
  const [saisonProfile, setSaisonProfile] = useState<string>(SAISON_PROFILES[0]);
  const [vitesseProfile, setVitesseProfile] = useState<string>(VITESSE_PROFILES[0]);
  const [nominalRange, setNominalRange] = useState<number>(300);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RangeCorrectionResponse | null>(null);

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: RangeCorrectionRequest = {
        nominal_range_km: nominalRange,
        pente_profile: penteProfile,
        saison_profile: saisonProfile,
        vitesse_profile: vitesseProfile,
      };
      const res = await computeRangeCorrection(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul de correction'));
    } finally {
      setLoading(false);
    }
  }, [nominalRange, penteProfile, saisonProfile, vitesseProfile]);

  /* ── Render ──────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          battery_charging_full
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Correction d&apos;autonomie
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        {/* Pente */}
        <div>
          <label
            htmlFor="rc-pente"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Profil pente
          </label>
          <select
            id="rc-pente"
            value={penteProfile}
            onChange={(e) => setPenteProfile(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {PENTE_PROFILES.map((p) => (
              <option key={p} value={p}>
                {PENTE_LABELS[p]}
              </option>
            ))}
          </select>
        </div>

        {/* Saison */}
        <div>
          <label
            htmlFor="rc-saison"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Profil saison
          </label>
          <select
            id="rc-saison"
            value={saisonProfile}
            onChange={(e) => setSaisonProfile(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {SAISON_PROFILES.map((s) => (
              <option key={s} value={s}>
                {SAISON_LABELS[s]}
              </option>
            ))}
          </select>
        </div>

        {/* Vitesse */}
        <div>
          <label
            htmlFor="rc-vitesse"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Profil vitesse
          </label>
          <select
            id="rc-vitesse"
            value={vitesseProfile}
            onChange={(e) => setVitesseProfile(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {VITESSE_PROFILES.map((v) => (
              <option key={v} value={v}>
                {VITESSE_LABELS[v]}
              </option>
            ))}
          </select>
        </div>

        {/* Nominal range */}
        <div>
          <label
            htmlFor="rc-range"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Autonomie nominale (km)
          </label>
          <input
            id="rc-range"
            type="number"
            min={10}
            max={1000}
            step={10}
            value={nominalRange}
            onChange={(e) => setNominalRange(Number(e.target.value))}
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
        <div className="mt-6 space-y-5">
          {/* Big number: corrected range */}
          <div className="flex flex-col items-center py-4">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
              Autonomie corrigee
            </p>
            <p className="font-sans text-4xl font-bold text-on-surface">
              {fmt(result.corrected_range_km, 0)}{' '}
              <span className="text-lg font-normal text-on-surface-variant">km</span>
            </p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-sm text-on-surface-variant">
                Nominale : {fmt(result.nominal_range_km, 0)} km
              </span>
              <span className="material-symbols-outlined text-base text-red-500">
                arrow_downward
              </span>
              <span className="text-sm font-medium text-red-600">
                -{fmt(result.range_reduction_pct, 1)}%
              </span>
            </div>
          </div>

          {/* Factor cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <FactorCard
              label="Facteur pente"
              icon="terrain"
              value={result.k_pente}
            />
            <FactorCard
              label="Facteur saison"
              icon="thermostat"
              value={result.k_saison}
            />
            <FactorCard
              label="Facteur vitesse"
              icon="speed"
              value={result.k_vitesse}
            />
          </div>

          {/* Correction factor badge */}
          <div className="flex items-center justify-center gap-3">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
              Facteur global
            </p>
            <span
              className={[
                'inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-semibold',
                result.correction_factor < 0.8
                  ? 'bg-red-50 text-red-700'
                  : result.correction_factor < 0.95
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-green-50 text-green-700',
              ].join(' ')}
            >
              {fmt(result.correction_factor, 3)}
            </span>
          </div>

          {/* Range reduction bar */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                Reduction d&apos;autonomie
              </p>
              <p className="text-xs font-medium text-on-surface">
                {fmt(result.range_reduction_pct, 1)}%
              </p>
            </div>
            <div className="w-full h-3 bg-surface-container rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${pctColor(result.range_reduction_pct)}`}
                style={{
                  width: `${Math.min(result.range_reduction_pct, 100)}%`,
                  background:
                    result.range_reduction_pct >= 25
                      ? 'linear-gradient(90deg, #f87171, #dc2626)'
                      : result.range_reduction_pct >= 10
                        ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
                        : 'linear-gradient(90deg, #34d399, #10b981)',
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
