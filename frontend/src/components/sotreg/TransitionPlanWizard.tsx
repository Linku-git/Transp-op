import { useState, useCallback } from 'react';
import { generateTransitionPlan } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type { TransitionPlanRequest, TransitionPlanResponse } from '@/types/sotreg';
import { SCENARIO_TYPES, SCENARIO_LABELS } from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const STEP_LABELS = ['Flotte', 'Scenario', 'Apercu'] as const;
const STEP_ICONS = ['directions_bus', 'tune', 'preview'] as const;

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
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

/* ── Main component ───────────────────────────────────────────────────────── */

export function TransitionPlanWizard({
  onPlanGenerated,
}: {
  onPlanGenerated?: (plan: TransitionPlanResponse) => void;
}) {
  /* Step navigation */
  const [step, setStep] = useState(0);

  /* Step 0: Fleet inputs */
  const [fleetSize, setFleetSize] = useState(50);
  const [totalBudget, setTotalBudget] = useState(20_000_000);

  /* Step 1: Scenario inputs */
  const [scenarioType, setScenarioType] = useState<string>(SCENARIO_TYPES[1]);
  const [startYear, setStartYear] = useState(2026);
  const [vehicleUnitCost, setVehicleUnitCost] = useState(300_000);
  const [irveCost, setIrveCost] = useState(90_000);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TransitionPlanResponse | null>(null);

  /* ── Handlers ───────────────────────────────────────────────────────────── */

  const handleGenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: TransitionPlanRequest = {
        fleet_size: fleetSize,
        total_budget_mad: totalBudget,
        start_year: startYear,
        scenario_type: scenarioType,
        vehicle_unit_cost_mad: vehicleUnitCost,
        irve_cost_per_vehicle_mad: irveCost,
      };
      const res = await generateTransitionPlan(req);
      setResult(res);
      setStep(2);
      onPlanGenerated?.(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de la generation du plan'));
    } finally {
      setLoading(false);
    }
  }, [fleetSize, totalBudget, startYear, scenarioType, vehicleUnitCost, irveCost, onPlanGenerated]);

  const handleNext = useCallback(() => {
    if (step === 1) {
      void handleGenerate();
    } else {
      setStep((s) => Math.min(s + 1, 2));
    }
  }, [step, handleGenerate]);

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
          route
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Plan de Transition
        </h3>
      </div>

      {/* Step indicator */}
      <StepIndicator activeStep={step} />

      {/* ── Step 0: Flotte ─────────────────────────────────────────────────── */}
      {step === 0 && (
        <div className="space-y-4">
          <div>
            <label
              htmlFor="tp-fleet-size"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Taille de la flotte
            </label>
            <input
              id="tp-fleet-size"
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
              htmlFor="tp-total-budget"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Budget total (MAD)
            </label>
            <input
              id="tp-total-budget"
              type="number"
              min={0}
              step={1_000_000}
              value={totalBudget}
              onChange={(e) => setTotalBudget(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
            <p className="text-xs text-on-surface-variant mt-1">
              {fmtMAD(totalBudget)}
            </p>
          </div>
        </div>
      )}

      {/* ── Step 1: Scenario ───────────────────────────────────────────────── */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label
              htmlFor="tp-scenario-type"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Type de scenario
            </label>
            <select
              id="tp-scenario-type"
              value={scenarioType}
              onChange={(e) => setScenarioType(e.target.value)}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            >
              {SCENARIO_TYPES.map((st) => (
                <option key={st} value={st}>
                  {SCENARIO_LABELS[st]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              htmlFor="tp-start-year"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Annee de demarrage
            </label>
            <input
              id="tp-start-year"
              type="number"
              min={2024}
              max={2040}
              value={startYear}
              onChange={(e) => setStartYear(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="tp-vehicle-unit-cost"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Cout unitaire vehicule (MAD)
            </label>
            <input
              id="tp-vehicle-unit-cost"
              type="number"
              min={0}
              step={10_000}
              value={vehicleUnitCost}
              onChange={(e) => setVehicleUnitCost(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
            <p className="text-xs text-on-surface-variant mt-1">
              {fmtMAD(vehicleUnitCost)}
            </p>
          </div>

          <div>
            <label
              htmlFor="tp-irve-cost"
              className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
            >
              Cout IRVE par vehicule (MAD)
            </label>
            <input
              id="tp-irve-cost"
              type="number"
              min={0}
              step={5_000}
              value={irveCost}
              onChange={(e) => setIrveCost(Number(e.target.value))}
              className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
            />
            <p className="text-xs text-on-surface-variant mt-1">
              {fmtMAD(irveCost)}
            </p>
          </div>
        </div>
      )}

      {/* ── Step 2: Apercu (Preview) ─────────────────────────────────────── */}
      {step === 2 && result && (
        <div className="space-y-5">
          {/* Plan summary headline */}
          <div className="flex items-center justify-center gap-4 py-3">
            <span className="material-symbols-outlined text-4xl text-primary">
              electric_car
            </span>
            <div className="text-center">
              <p className="font-sans text-2xl font-bold text-on-surface">
                {result.plan_name}
              </p>
              <p className="text-sm text-on-surface-variant">
                {SCENARIO_LABELS[result.scenario_type] ?? result.scenario_type} &middot; {result.fleet_size} vehicules
              </p>
            </div>
          </div>

          {/* Summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-outline-variant/10 pt-4">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Total phases
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {result.total_phases}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Vehicules convertis
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {result.total_vehicles_converted}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Cout total
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {fmtMAD(result.total_cost_mad)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Surplus / Deficit
              </p>
              <p
                className={[
                  'font-sans text-lg font-semibold',
                  result.budget_surplus_or_deficit_mad >= 0
                    ? 'text-green-700'
                    : 'text-error',
                ].join(' ')}
              >
                {result.budget_surplus_or_deficit_mad >= 0 ? '+' : ''}
                {fmtMAD(result.budget_surplus_or_deficit_mad)}
              </p>
            </div>
          </div>

          {/* Phases table */}
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              Phases du plan
            </p>
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="text-left px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Phase
                    </th>
                    <th className="text-left px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Vague
                    </th>
                    <th className="text-center px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Periode
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Vehicules
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      Budget alloue
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {result.phases.map((phase) => (
                    <tr key={phase.name} className="hover:bg-surface-bright">
                      <td className="px-4 py-2.5 font-medium text-on-surface">
                        {phase.name}
                      </td>
                      <td className="px-4 py-2.5">
                        <span
                          className="inline-block px-2 py-0.5 rounded text-xs font-medium text-white"
                          style={{
                            backgroundColor:
                              phase.technology_wave === 'pilot'
                                ? '#0058be'
                                : phase.technology_wave === 'scale'
                                  ? '#22c55e'
                                  : '#f59e0b',
                          }}
                        >
                          {phase.technology_wave}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-center text-on-surface-variant">
                        {phase.start_year} &ndash; {phase.end_year}
                      </td>
                      <td className="px-4 py-2.5 text-right text-on-surface">
                        {phase.vehicles_to_convert}
                      </td>
                      <td className="px-4 py-2.5 text-right text-on-surface">
                        {fmtMAD(phase.budget_allocated_mad)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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

        {/* Next / Generate button */}
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
                Generation en cours...
              </>
            ) : step === 1 ? (
              <>
                <span className="material-symbols-outlined text-base">
                  auto_awesome
                </span>
                Generer Plan
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

        {/* Reset on preview step */}
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
            Nouveau plan
          </button>
        )}
      </div>
    </div>
  );
}
