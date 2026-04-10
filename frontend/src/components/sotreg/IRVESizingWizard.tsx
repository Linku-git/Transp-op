import { useState, useCallback } from 'react';
import { computeIRVESizing } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { IRVESizingRequest, IRVESizingResponse } from '@/types/sotreg';
import { CHARGER_TYPES, CHARGER_LABELS } from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const STEP_LABELS = ['Flotte', 'Chargeur', 'Resultats'] as const;
const STEP_ICONS = ['directions_bus', 'ev_charger', 'analytics'] as const;

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

function fmtNum(value: number, decimals = 1): string {
  return value.toLocaleString('fr-MA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/* ── Step indicator ───────────────────────────────────────────────────────── */

function StepIndicator({ activeStep }: { activeStep: number }) {
  return (
    <div className="flex items-center justify-center gap-6 mb-6">
      {STEP_LABELS.map((label, index) => {
        const isActive = index === activeStep;
        const isDone = index < activeStep;

        return (
          <div key={label} className="flex items-center gap-2">
            {/* connector line before (except first) */}
            {index > 0 && (
              <div
                className={[
                  'w-8 h-0.5 rounded-full -ml-4 mr-2',
                  isDone ? 'bg-primary' : 'bg-outline-variant/20',
                ].join(' ')}
              />
            )}

            {/* circle */}
            <div
              className={[
                'flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold transition-colors',
                isActive
                  ? 'bg-gradient-to-br from-primary to-primary-container text-on-primary shadow-lg shadow-primary/20'
                  : isDone
                    ? 'bg-primary/10 text-primary'
                    : 'bg-surface-container-high/50 text-on-surface-variant',
              ].join(' ')}
            >
              {isDone ? (
                <span className="material-symbols-outlined text-base">
                  check
                </span>
              ) : (
                <span className="material-symbols-outlined text-base">
                  {STEP_ICONS[index]}
                </span>
              )}
            </div>

            {/* label */}
            <span
              className={[
                'text-xs font-medium',
                isActive
                  ? 'text-primary'
                  : isDone
                    ? 'text-on-surface'
                    : 'text-on-surface-variant',
              ].join(' ')}
            >
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ── Cost card ────────────────────────────────────────────────────────────── */

function CostCard({
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

export function IRVESizingWizard() {
  /* Step navigation */
  const [step, setStep] = useState(0);

  /* Step 0: Fleet inputs */
  const [fleetSize, setFleetSize] = useState(10);
  const [dailyKm, setDailyKm] = useState(150);
  const [batteryCapacity, setBatteryCapacity] = useState(60);

  /* Step 1: Charger inputs */
  const [chargerType, setChargerType] = useState<string>(CHARGER_TYPES[1]);
  const [chargingWindow, setChargingWindow] = useState(8);
  const [utilizationTarget, setUtilizationTarget] = useState(0.75);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IRVESizingResponse | null>(null);

  /* ── Handlers ───────────────────────────────────────────────────────────── */

  const handleCalculate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: IRVESizingRequest = {
        fleet_size: fleetSize,
        daily_km_per_vehicle: dailyKm,
        battery_capacity_kwh: batteryCapacity,
        preferred_charger_type: chargerType,
        charging_window_hours: chargingWindow,
        charger_utilization_target: utilizationTarget,
      };
      const res = await computeIRVESizing(req);
      setResult(res);
      setStep(2);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du dimensionnement IRVE'));
    } finally {
      setLoading(false);
    }
  }, [fleetSize, dailyKm, batteryCapacity, chargerType, chargingWindow, utilizationTarget]);

  const handleNext = useCallback(() => {
    if (step === 1) {
      void handleCalculate();
    } else {
      setStep((s) => Math.min(s + 1, 2));
    }
  }, [step, handleCalculate]);

  const handleBack = useCallback(() => {
    setError(null);
    setStep((s) => Math.max(s - 1, 0));
  }, []);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          ev_station
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Dimensionnement IRVE
        </h3>
      </div>

      {/* Step indicator */}
      <StepIndicator activeStep={step} />

      {/* ── Step 0: Fleet ─────────────────────────────────────────────────── */}
      {step === 0 && (
        <div className="space-y-4">
          <div>
            <label
              htmlFor="irve-fleet-size"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Taille de la flotte
            </label>
            <input
              id="irve-fleet-size"
              type="number"
              min={1}
              max={5000}
              value={fleetSize}
              onChange={(e) => setFleetSize(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="irve-daily-km"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Km quotidiens par vehicule
            </label>
            <input
              id="irve-daily-km"
              type="number"
              min={1}
              max={1000}
              value={dailyKm}
              onChange={(e) => setDailyKm(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="irve-battery"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Capacite batterie (kWh)
            </label>
            <input
              id="irve-battery"
              type="number"
              min={10}
              max={500}
              value={batteryCapacity}
              onChange={(e) => setBatteryCapacity(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>
        </div>
      )}

      {/* ── Step 1: Charger ───────────────────────────────────────────────── */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label
              htmlFor="irve-charger-type"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Type de chargeur
            </label>
            <select
              id="irve-charger-type"
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

          <div>
            <label
              htmlFor="irve-window"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Fenetre de charge (heures)
            </label>
            <input
              id="irve-window"
              type="number"
              min={1}
              max={24}
              step={0.5}
              value={chargingWindow}
              onChange={(e) => setChargingWindow(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="irve-utilization"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Taux d&apos;utilisation cible
            </label>
            <div className="flex items-center gap-3">
              <input
                id="irve-utilization"
                type="range"
                min={0.3}
                max={1.0}
                step={0.05}
                value={utilizationTarget}
                onChange={(e) => setUtilizationTarget(Number(e.target.value))}
                className="flex-1 accent-primary"
              />
              <span className="text-sm font-medium text-on-surface w-12 text-right">
                {(utilizationTarget * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* ── Step 2: Results ───────────────────────────────────────────────── */}
      {step === 2 && result && (
        <div className="space-y-5">
          {/* Charger headline */}
          <div className="flex items-center justify-center gap-4 py-3">
            <span className="material-symbols-outlined text-4xl text-primary">
              ev_station
            </span>
            <div className="text-center">
              <p className="font-sans text-3xl font-bold text-on-surface">
                {result.charger_count}
              </p>
              <p className="text-sm text-on-surface-variant">
                chargeurs {CHARGER_LABELS[result.charger_type] ?? result.charger_type}
              </p>
            </div>
          </div>

          {/* Power & demand summary */}
          <div className="grid grid-cols-3 gap-3 border-t border-outline-variant/10 pt-4">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Puissance installee
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {fmtNum(result.total_installed_power_kw, 0)} kW
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Demande journaliere
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {fmtNum(result.daily_energy_demand_kwh, 0)} kWh
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Vehicules / chargeur
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {fmtNum(result.vehicles_per_charger, 1)}
              </p>
            </div>
          </div>

          {/* Cost breakdown */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Ventilation des couts
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <CostCard
                label="Materiel"
                icon="hardware"
                value={result.hardware_cost_mad}
              />
              <CostCard
                label="Installation"
                icon="construction"
                value={result.installation_cost_mad}
              />
              <CostCard
                label="Transformateur"
                icon="electric_bolt"
                value={result.transformer_cost_mad}
              />
              <CostCard
                label="Raccordement"
                icon="cable"
                value={result.grid_connection_cost_mad}
              />
              <CostCard
                label="Electricite annuelle"
                icon="payments"
                value={result.annual_electricity_cost_mad}
              />
              <CostCard
                label="CAPEX total"
                icon="account_balance"
                value={result.total_capex_mad}
                accent
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Error state ───────────────────────────────────────────────────── */}
      {error && (
        <div className="mt-4 flex items-start gap-2 bg-error-container/30 text-error rounded-lg px-4 py-3">
          <span className="material-symbols-outlined text-base mt-0.5">
            error
          </span>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* ── Navigation buttons ────────────────────────────────────────────── */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t border-outline-variant/10">
        {/* Back button */}
        {step > 0 ? (
          <button
            type="button"
            onClick={handleBack}
            className="inline-flex items-center gap-2 bg-surface-container-lowest text-primary border border-outline-variant/15 rounded-lg shadow-sm px-4 py-2 text-sm font-medium transition-opacity hover:opacity-80"
          >
            <span className="material-symbols-outlined text-base">
              arrow_back
            </span>
            Precedent
          </button>
        ) : (
          <div />
        )}

        {/* Next / Calculate button */}
        {step < 2 && (
          <button
            type="button"
            onClick={handleNext}
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
            ) : step === 1 ? (
              <>
                <span className="material-symbols-outlined text-base">
                  calculate
                </span>
                Calculer
              </>
            ) : (
              <>
                Suivant
                <span className="material-symbols-outlined text-base">
                  arrow_forward
                </span>
              </>
            )}
          </button>
        )}

        {/* Reset on results step */}
        {step === 2 && (
          <button
            type="button"
            onClick={() => {
              setStep(0);
              setResult(null);
              setError(null);
            }}
            className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90"
          >
            <span className="material-symbols-outlined text-base">
              restart_alt
            </span>
            Nouveau calcul
          </button>
        )}
      </div>
    </div>
  );
}
