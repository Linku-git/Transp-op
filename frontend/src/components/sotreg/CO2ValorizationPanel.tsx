import { useState, useCallback } from 'react';
import { computeCO2Valorization } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  CO2ValorizationRequest,
  CO2ValorizationResponse,
} from '@/types/sotreg';
import {
  MOTORIZATION_OPTIONS,
  MOTORIZATION_LABELS,
} from '@/types/sotreg';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

const madFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

function fmtMAD(value: number): string {
  return `${madFmt.format(value)} MAD`;
}

const numFmt = new Intl.NumberFormat('fr-MA', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

/* ── Emission factor display ─────────────────────────────────────────────── */

const MOTORIZATION_ICONS: Record<string, string> = {
  diesel: 'local_gas_station',
  essence: 'local_gas_station',
  electrique: 'bolt',
  hybride: 'sync_alt',
  gnv: 'propane',
};

/* ── Main component ──────────────────────────────────────────────────────── */

export function CO2ValorizationPanel() {
  /* Form state */
  const [fleetAnnualKm, setFleetAnnualKm] = useState(40000);
  const [vehicleCount, setVehicleCount] = useState(10);
  const [currentMotorization, setCurrentMotorization] = useState<string>('diesel');
  const [targetMotorization, setTargetMotorization] = useState<string>('electrique');
  const [carbonPriceMadTco2, setCarbonPriceMadTco2] = useState(200);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CO2ValorizationResponse | null>(null);

  /* ── Handler ────────────────────────────────────────────────────────────── */

  const handleCompute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: CO2ValorizationRequest = {
        fleet_annual_km: fleetAnnualKm,
        vehicle_count: vehicleCount,
        current_motorization: currentMotorization,
        target_motorization: targetMotorization,
        carbon_price_mad_tco2: carbonPriceMadTco2,
      };
      const res = await computeCO2Valorization(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors du calcul de la valorisation CO2'));
    } finally {
      setLoading(false);
    }
  }, [fleetAnnualKm, vehicleCount, currentMotorization, targetMotorization, carbonPriceMadTco2]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          eco
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Valorisation CO2
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-5">
        {/* Fleet annual km */}
        <div>
          <label
            htmlFor="co2-fleet-km"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Km annuels par vehicule
          </label>
          <input
            id="co2-fleet-km"
            type="number"
            min={1000}
            max={200000}
            step={1000}
            value={fleetAnnualKm}
            onChange={(e) => setFleetAnnualKm(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Vehicle count */}
        <div>
          <label
            htmlFor="co2-vehicle-count"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Nombre de vehicules
          </label>
          <input
            id="co2-vehicle-count"
            type="number"
            min={1}
            max={1000}
            value={vehicleCount}
            onChange={(e) => setVehicleCount(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* Current motorization */}
        <div>
          <label
            htmlFor="co2-current-motor"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Motorisation actuelle
          </label>
          <select
            id="co2-current-motor"
            value={currentMotorization}
            onChange={(e) => setCurrentMotorization(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {MOTORIZATION_OPTIONS.map((m) => (
              <option key={m} value={m}>
                {MOTORIZATION_LABELS[m]}
              </option>
            ))}
          </select>
        </div>

        {/* Target motorization */}
        <div>
          <label
            htmlFor="co2-target-motor"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Motorisation cible
          </label>
          <select
            id="co2-target-motor"
            value={targetMotorization}
            onChange={(e) => setTargetMotorization(e.target.value)}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          >
            {MOTORIZATION_OPTIONS.map((m) => (
              <option key={m} value={m}>
                {MOTORIZATION_LABELS[m]}
              </option>
            ))}
          </select>
        </div>

        {/* Carbon price slider */}
        <div className="sm:col-span-2 lg:col-span-1">
          <label
            htmlFor="co2-carbon-price"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Prix carbone (MAD/tCO2)
          </label>
          <div className="flex items-center gap-3">
            <input
              id="co2-carbon-price"
              type="range"
              min={50}
              max={500}
              step={10}
              value={carbonPriceMadTco2}
              onChange={(e) => setCarbonPriceMadTco2(Number(e.target.value))}
              className="flex-1 accent-primary"
            />
            <span className="text-sm font-medium text-on-surface w-16 text-right">
              {madFmt.format(carbonPriceMadTco2)}
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
              eco
            </span>
            Calculer Valorisation
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
          {/* Big numbers row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Avoided tCO2 */}
            <div className="bg-green-50 rounded-lg p-5 text-center">
              <span className="material-symbols-outlined text-3xl text-green-600 mb-1">
                forest
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Emissions evitees
              </p>
              <p className="font-sans text-3xl font-bold text-green-700">
                {numFmt.format(result.avoided_emissions_tco2)}
              </p>
              <p className="text-xs text-green-600 mt-0.5">tCO2/an</p>
            </div>

            {/* Annual MAD value */}
            <div className="bg-primary/5 rounded-lg p-5 text-center">
              <span className="material-symbols-outlined text-3xl text-primary mb-1">
                savings
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Valeur annuelle
              </p>
              <p className="font-sans text-3xl font-bold text-primary">
                {fmtMAD(result.valorization_mad)}
              </p>
              <p className="text-xs text-on-surface-variant mt-0.5">MAD/an</p>
            </div>

            {/* 15-year MAD value */}
            <div className="bg-amber-50 rounded-lg p-5 text-center">
              <span className="material-symbols-outlined text-3xl text-amber-600 mb-1">
                account_balance
              </span>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Valeur sur 15 ans
              </p>
              <p className="font-sans text-3xl font-bold text-amber-700">
                {fmtMAD(result.valorization_15year_mad)}
              </p>
              <p className="text-xs text-amber-600 mt-0.5">MAD cumule</p>
            </div>
          </div>

          {/* Motorization comparison */}
          <div className="border-t border-outline-variant/10 pt-5">
            <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              Comparaison des motorisations
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Current */}
              <div className="bg-surface-container-low rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-lg text-error">
                    {MOTORIZATION_ICONS[result.current_motorization] ?? 'directions_car'}
                  </span>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                    Actuel — {MOTORIZATION_LABELS[result.current_motorization] ?? result.current_motorization}
                  </p>
                </div>
                <div className="flex items-baseline gap-1">
                  <p className="font-sans text-2xl font-bold text-error">
                    {numFmt.format(result.current_emissions_tco2)}
                  </p>
                  <span className="text-xs text-on-surface-variant">tCO2/an</span>
                </div>
                <div className="mt-2 w-full bg-error/10 rounded-full h-2">
                  <div
                    className="bg-error rounded-full h-2 transition-all"
                    style={{
                      width: result.current_emissions_tco2 > 0
                        ? '100%'
                        : '0%',
                    }}
                  />
                </div>
              </div>

              {/* Target */}
              <div className="bg-surface-container-low rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-lg text-green-600">
                    {MOTORIZATION_ICONS[result.target_motorization] ?? 'directions_car'}
                  </span>
                  <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                    Cible — {MOTORIZATION_LABELS[result.target_motorization] ?? result.target_motorization}
                  </p>
                </div>
                <div className="flex items-baseline gap-1">
                  <p className="font-sans text-2xl font-bold text-green-700">
                    {numFmt.format(result.target_emissions_tco2)}
                  </p>
                  <span className="text-xs text-on-surface-variant">tCO2/an</span>
                </div>
                <div className="mt-2 w-full bg-green-100 rounded-full h-2">
                  <div
                    className="bg-green-500 rounded-full h-2 transition-all"
                    style={{
                      width: result.current_emissions_tco2 > 0
                        ? `${Math.max(2, (result.target_emissions_tco2 / result.current_emissions_tco2) * 100)}%`
                        : '0%',
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Fleet context info */}
          <div className="grid grid-cols-3 gap-3 border-t border-outline-variant/10 pt-4">
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Km annuels flotte
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {madFmt.format(result.fleet_annual_km)} km
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Vehicules
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {result.vehicle_count}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-0.5">
                Prix carbone
              </p>
              <p className="font-sans text-lg font-semibold text-on-surface">
                {madFmt.format(result.carbon_price_mad_tco2)} MAD/tCO2
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="mt-6 flex flex-col items-center justify-center py-12 text-on-surface-variant">
          <span className="material-symbols-outlined text-4xl mb-2 opacity-40">
            eco
          </span>
          <p className="text-sm">
            Configurez les parametres de la flotte et cliquez sur Calculer Valorisation pour estimer les gains CO2.
          </p>
        </div>
      )}
    </div>
  );
}
