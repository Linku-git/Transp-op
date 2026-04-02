import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { calculateTCO } from '@/api/financial';
import { Button } from '@/components/ui/Button';
import { FleetAggregation } from '@/components/financial/FleetAggregation';
import { TCOComparisonCards } from '@/components/financial/TCOComparisonCards';
import { TCOEvolutionChart } from '@/components/financial/TCOEvolutionChart';
import { MotorizationTable } from '@/components/financial/MotorizationTable';
import { VehicleTCOBreakdown } from '@/components/financial/VehicleTCOBreakdown';
import {
  VEHICLE_TYPES,
  MOTORIZATIONS,
  type TCOFleetItem,
  type TCOCalculateResponse,
} from '@/types/financial';

const VEHICLE_TYPE_LABELS: Record<string, string> = {
  minibus: 'Minibus',
  midibus: 'Midibus',
  bus_standard: 'Bus Standard',
  grand_bus: 'Grand Bus',
  vehicule_leger: 'Vehicule Leger',
};

const MOTORIZATION_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  hybrid: 'Hybride',
  electric: 'Electrique',
  hydrogen: 'Hydrogene',
  gnv: 'GNV',
};

function createEmptyFleetItem(): TCOFleetItem {
  return {
    vehicle_type: VEHICLE_TYPES[0],
    motorization: MOTORIZATIONS[0],
    quantity: 1,
  };
}

export function TCOCalculatorPage() {
  const { t } = useTranslation();

  const [fleet, setFleet] = useState<TCOFleetItem[]>([createEmptyFleetItem()]);
  const [durationYears, setDurationYears] = useState(5);
  const [includeEvolution, setIncludeEvolution] = useState(true);
  const [includeComparison, setIncludeComparison] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TCOCalculateResponse | null>(null);

  const updateFleetItem = useCallback(
    (index: number, field: keyof TCOFleetItem, value: string | number) => {
      setFleet((prev) => {
        const next = [...prev];
        next[index] = { ...next[index], [field]: value };
        return next;
      });
    },
    [],
  );

  const addFleetItem = useCallback(() => {
    setFleet((prev) => [...prev, createEmptyFleetItem()]);
  }, []);

  const removeFleetItem = useCallback((index: number) => {
    setFleet((prev) => {
      if (prev.length <= 1) return prev;
      return prev.filter((_, i) => i !== index);
    });
  }, []);

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await calculateTCO({
        fleet,
        duration_years: durationYears,
        include_evolution: includeEvolution,
        include_comparison: includeComparison,
      });
      setResult(response);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : t('common.error', 'Une erreur est survenue');
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [fleet, durationYears, includeEvolution, includeComparison, t]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-on-surface font-sans">
            {t('financial.tco_title', 'Calculateur TCO')}
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {t(
              'financial.tco_subtitle',
              'Calculez le cout total de possession de votre flotte de vehicules.',
            )}
          </p>
        </div>
      </div>

      {/* Fleet Form */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {t('financial.fleet_composition', 'Composition de la flotte')}
        </h3>

        <div className="space-y-3">
          {fleet.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 bg-surface-container-low/50 rounded-lg"
            >
              <div className="flex-1 min-w-0">
                <label className="text-[10px] font-bold uppercase tracking-widest text-outline block mb-1">
                  {t('financial.vehicle_type', 'Type de vehicule')}
                </label>
                <select
                  value={item.vehicle_type}
                  onChange={(e) =>
                    updateFleetItem(index, 'vehicle_type', e.target.value)
                  }
                  data-testid="vehicle-type-select"
                  className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 focus:outline-none"
                >
                  {VEHICLE_TYPES.map((vt) => (
                    <option key={vt} value={vt}>
                      {VEHICLE_TYPE_LABELS[vt] ?? vt}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1 min-w-0">
                <label className="text-[10px] font-bold uppercase tracking-widest text-outline block mb-1">
                  {t('financial.motorization', 'Motorisation')}
                </label>
                <select
                  value={item.motorization}
                  onChange={(e) =>
                    updateFleetItem(index, 'motorization', e.target.value)
                  }
                  className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 focus:outline-none"
                >
                  {MOTORIZATIONS.map((m) => (
                    <option key={m} value={m}>
                      {MOTORIZATION_LABELS[m] ?? m}
                    </option>
                  ))}
                </select>
              </div>

              <div className="w-24">
                <label className="text-[10px] font-bold uppercase tracking-widest text-outline block mb-1">
                  {t('financial.quantity', 'Quantite')}
                </label>
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={item.quantity}
                  onChange={(e) =>
                    updateFleetItem(
                      index,
                      'quantity',
                      Math.max(1, parseInt(e.target.value, 10) || 1),
                    )
                  }
                  className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 focus:outline-none"
                />
              </div>

              <button
                type="button"
                onClick={() => removeFleetItem(index)}
                disabled={fleet.length <= 1}
                className="mt-4 p-1.5 rounded-lg text-on-surface-variant hover:bg-error/10 hover:text-error transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label={t('common.delete', 'Supprimer')}
              >
                <span className="material-symbols-outlined text-lg">
                  delete
                </span>
              </button>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={addFleetItem}
          className="mt-3 flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary-container transition-colors"
        >
          <span className="material-symbols-outlined text-lg">add</span>
          {t('financial.add_vehicle', 'Ajouter un vehicule')}
        </button>
      </div>

      {/* Parameters */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {t('financial.parameters', 'Parametres')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="text-[10px] font-bold uppercase tracking-widest text-outline block mb-2">
              {t('financial.duration_years', 'Duree (annees)')}: {durationYears}
            </label>
            <input
              type="range"
              min={1}
              max={10}
              value={durationYears}
              onChange={(e) => setDurationYears(parseInt(e.target.value, 10))}
              className="w-full accent-primary"
            />
            <div className="flex justify-between text-[10px] text-on-surface-variant mt-1">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeEvolution}
                onChange={(e) => setIncludeEvolution(e.target.checked)}
                className="rounded accent-primary w-4 h-4"
              />
              <span className="text-sm text-on-surface">
                {t('financial.include_evolution', 'Evolution annuelle')}
              </span>
            </label>
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeComparison}
                onChange={(e) => setIncludeComparison(e.target.checked)}
                className="rounded accent-primary w-4 h-4"
              />
              <span className="text-sm text-on-surface">
                {t(
                  'financial.include_comparison',
                  'Comparaison motorisations',
                )}
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Calculate Button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          size="lg"
          isLoading={loading}
          onClick={handleSubmit}
          data-testid="calculate-button"
        >
          <span className="material-symbols-outlined mr-2 text-lg">
            calculate
          </span>
          {t('financial.calculate_tco', 'Calculer TCO')}
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-error-container/30 text-error rounded-xl p-4 flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">error</span>
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6" data-testid="tco-results">
          <FleetAggregation fleetResult={result.fleet_tco} />

          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('financial.comparison', 'Comparaison des vehicules')}
            </h3>
            <TCOComparisonCards vehicles={result.fleet_tco.vehicles} />
          </div>

          {result.evolution && result.evolution.length > 0 && (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
                {t('financial.tco_evolution', 'Evolution du TCO')}
              </h3>
              <TCOEvolutionChart data={result.evolution} />
            </div>
          )}

          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('financial.cost_breakdown', 'Decomposition des couts')}
            </h3>
            <VehicleTCOBreakdown vehicles={result.fleet_tco.vehicles} />
          </div>

          {result.motorization_comparisons &&
            result.motorization_comparisons.length > 0 && (
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
                  {t(
                    'financial.motorization_comparison',
                    'Comparaison des motorisations',
                  )}
                </h3>
                <MotorizationTable
                  comparisons={result.motorization_comparisons}
                />
              </div>
            )}
        </div>
      )}
    </div>
  );
}
