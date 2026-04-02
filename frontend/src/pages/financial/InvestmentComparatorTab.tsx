import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { compareInvestments } from '@/api/financial';
import { Button } from '@/components/ui/Button';
import { InvestmentComparatorCards } from '@/components/financial/InvestmentComparatorCards';
import type { InvestmentCompareRequest, InvestmentCompareResponse } from '@/types/financial';

interface FormField {
  key: keyof InvestmentCompareRequest;
  label: string;
  defaultValue: number;
  step?: number;
  min?: number;
}

const FORM_FIELDS: FormField[] = [
  { key: 'vehicle_count', label: 'Nombre de vehicules', defaultValue: 10, min: 1 },
  { key: 'headcount', label: 'Effectif transporte', defaultValue: 300, min: 1 },
  { key: 'annual_trips', label: 'Trajets annuels', defaultValue: 60000, min: 1 },
  { key: 'duration_years', label: 'Duree (annees)', defaultValue: 5, min: 1 },
];

function buildDefaultValues(): Record<string, number> {
  const values: Record<string, number> = {};
  for (const field of FORM_FIELDS) {
    values[field.key] = field.defaultValue;
  }
  return values;
}

export function InvestmentComparatorTab() {
  const { t } = useTranslation();

  const [formValues, setFormValues] = useState<Record<string, number>>(buildDefaultValues);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<InvestmentCompareResponse | null>(null);

  const updateField = useCallback((key: string, value: string) => {
    setFormValues((prev) => ({
      ...prev,
      [key]: parseFloat(value) || 0,
    }));
  }, []);

  const handleSubmit = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const request: InvestmentCompareRequest = {
        vehicle_count: formValues['vehicle_count'] ?? 10,
        headcount: formValues['headcount'] ?? 300,
        annual_trips: formValues['annual_trips'] ?? 60000,
        duration_years: formValues['duration_years'] ?? 5,
      };
      const response = await compareInvestments(request);
      setResult(response);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : t('common.error', 'Une erreur est survenue');
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [formValues, t]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-on-surface font-sans">
          {t('financial.comparator_title', 'Comparateur de modeles')}
        </h2>
        <p className="text-sm text-on-surface-variant mt-1">
          {t(
            'financial.comparator_subtitle',
            'Comparez CAPEX, Mise a disposition et OPEX pour votre flotte.',
          )}
        </p>
      </div>

      {/* Form */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {t('financial.comparator_params', 'Parametres de comparaison')}
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FORM_FIELDS.map((field) => (
            <div key={field.key} className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                {field.label}
              </label>
              <input
                type="number"
                step={field.step ?? 1}
                min={field.min}
                value={formValues[field.key] ?? field.defaultValue}
                onChange={(e) => updateField(field.key, e.target.value)}
                data-testid={`comparator-input-${field.key}`}
                className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none transition-shadow focus:ring-2 focus:ring-primary/20"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Compare Button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          size="lg"
          isLoading={loading}
          onClick={handleSubmit}
          data-testid="compare-button"
        >
          <span className="material-symbols-outlined mr-2 text-lg">compare_arrows</span>
          {t('financial.compare', 'Comparer')}
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-error-container/30 text-error rounded-xl p-4 flex items-center gap-2">
          <span className="material-symbols-outlined text-lg">error</span>
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Empty State */}
      {!result && !loading && !error && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant/30 mb-4">
            compare_arrows
          </span>
          <p className="text-sm text-on-surface-variant">
            {t(
              'financial.comparator_empty',
              'Renseignez les parametres et cliquez sur Comparer pour voir les resultats.',
            )}
          </p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6" data-testid="comparator-results">
          <InvestmentComparatorCards
            models={result.models}
            recommendation={result.recommendation}
          />

          {/* Recommendation Banner */}
          <div className="bg-primary/5 rounded-xl border border-primary/10 p-4 flex items-start gap-3">
            <span className="material-symbols-outlined text-primary text-xl mt-0.5">
              lightbulb
            </span>
            <div>
              <p className="text-sm font-bold text-on-surface">
                {t('financial.recommendation', 'Recommandation')}
              </p>
              <p className="text-sm text-on-surface-variant mt-0.5">
                {result.recommendation.reason}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
