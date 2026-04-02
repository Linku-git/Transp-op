import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { calculateROI } from '@/api/financial';
import { Button } from '@/components/ui/Button';
import { WaterfallChart } from '@/components/financial/WaterfallChart';
import { PaybackSlider } from '@/components/financial/PaybackSlider';
import { DAFExportButton } from '@/components/financial/DAFExportButton';
import type { ROICalculateRequest, ROICalculateResponse } from '@/types/financial';

interface FormField {
  key: keyof ROICalculateRequest;
  label: string;
  defaultValue: number;
  step?: number;
  min?: number;
  max?: number;
  suffix?: string;
}

const FORM_FIELDS: FormField[] = [
  { key: 'headcount', label: 'Effectif', defaultValue: 500, min: 1 },
  { key: 'daily_cost', label: 'Cout journalier (MAD)', defaultValue: 350, min: 0 },
  { key: 'baseline_absence_rate', label: 'Taux absence actuel (%)', defaultValue: 7, step: 0.1, min: 0, max: 100 },
  { key: 'target_absence_rate', label: 'Taux absence cible (%)', defaultValue: 4, step: 0.1, min: 0, max: 100 },
  { key: 'replacement_cost', label: 'Cout remplacement (MAD)', defaultValue: 500, min: 0 },
  { key: 'turnover_rate_before', label: 'Turnover avant (%)', defaultValue: 18, step: 0.1, min: 0, max: 100 },
  { key: 'turnover_rate_after', label: 'Turnover apres (%)', defaultValue: 12, step: 0.1, min: 0, max: 100 },
  { key: 'annual_travel_hours', label: 'Heures trajet / an', defaultValue: 300, min: 0 },
  { key: 'engagement_rate', label: 'Taux engagement (%)', defaultValue: 60, step: 1, min: 0, max: 100 },
  { key: 'training_hour_cost', label: 'Cout heure formation (MAD)', defaultValue: 150, min: 0 },
  { key: 'total_investment', label: 'Investissement total (MAD)', defaultValue: 3000000, min: 0 },
];

function formatMAD(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k`;
  }
  return value.toFixed(0);
}

function buildDefaultValues(): Record<string, number> {
  const values: Record<string, number> = {};
  for (const field of FORM_FIELDS) {
    values[field.key] = field.defaultValue;
  }
  return values;
}

export function ROICalculatorTab() {
  const { t } = useTranslation();

  const [formValues, setFormValues] = useState<Record<string, number>>(buildDefaultValues);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ROICalculateResponse | null>(null);

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
      const request: ROICalculateRequest = {
        headcount: formValues['headcount'] ?? 500,
        daily_cost: formValues['daily_cost'] ?? 350,
        baseline_absence_rate: formValues['baseline_absence_rate'] ?? 7,
        target_absence_rate: formValues['target_absence_rate'] ?? 4,
        replacement_cost: formValues['replacement_cost'] ?? 500,
        turnover_rate_before: formValues['turnover_rate_before'] ?? 18,
        turnover_rate_after: formValues['turnover_rate_after'] ?? 12,
        annual_travel_hours: formValues['annual_travel_hours'] ?? 300,
        engagement_rate: formValues['engagement_rate'] ?? 60,
        training_hour_cost: formValues['training_hour_cost'] ?? 150,
        total_investment: formValues['total_investment'] ?? 3000000,
      };
      const response = await calculateROI(request);
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-on-surface font-sans">
            {t('financial.roi_title', 'Calculateur ROI')}
          </h2>
          <p className="text-sm text-on-surface-variant mt-1">
            {t(
              'financial.roi_subtitle',
              'Evaluez le retour sur investissement de votre programme de mobilite.',
            )}
          </p>
        </div>
        <DAFExportButton />
      </div>

      {/* Form */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
          {t('financial.roi_parameters', 'Parametres ROI')}
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FORM_FIELDS.map((field) => (
            <div key={field.key} className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-outline font-sans">
                {field.label}
              </label>
              <input
                type="number"
                step={field.step ?? 1}
                min={field.min}
                max={field.max}
                value={formValues[field.key] ?? field.defaultValue}
                onChange={(e) => updateField(field.key, e.target.value)}
                data-testid={`roi-input-${field.key}`}
                className="w-full bg-surface-container-high/50 border-none rounded-lg p-3 text-on-surface font-sans text-sm outline-none transition-shadow focus:ring-2 focus:ring-primary/20"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Calculate Button */}
      <div className="flex justify-end">
        <Button
          variant="primary"
          size="lg"
          isLoading={loading}
          onClick={handleSubmit}
          data-testid="calculate-roi-button"
        >
          <span className="material-symbols-outlined mr-2 text-lg">calculate</span>
          {t('financial.calculate_roi', 'Calculer ROI')}
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
        <div className="space-y-6" data-testid="roi-results">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('financial.roi_total_label', 'ROI Total')}
              </p>
              <p className="text-3xl font-black text-primary mt-1">
                {formatMAD(result.roi_total)} MAD
              </p>
            </div>
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('financial.roi_percentage', 'ROI %')}
              </p>
              <p className="text-3xl font-black text-green-600 mt-1">
                {result.roi_percentage.toFixed(1)}%
              </p>
            </div>
            <PaybackSlider
              paybackMonths={result.payback_months}
              totalInvestment={result.total_investment}
              roiTotal={result.roi_total}
            />
          </div>

          {/* Waterfall Chart */}
          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('financial.roi_levers', 'Leviers de ROI')}
            </h3>
            <WaterfallChart data={result} />
          </div>

          {/* Detailed Breakdown */}
          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
            <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('financial.roi_breakdown', 'Decomposition detaillee')}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: t('financial.roi_absenteeism', 'Absenteisme'), value: result.roi_absenteeism, color: 'text-green-700' },
                { label: t('financial.roi_retention', 'Retention'), value: result.roi_retention, color: 'text-green-600' },
                { label: t('financial.roi_fleet', 'Flotte'), value: result.roi_fleet_optimization, color: 'text-green-500' },
                { label: t('financial.roi_journey', 'Trajet'), value: result.roi_journey, color: 'text-green-400' },
              ].map((item) => (
                <div key={item.label} className="bg-surface-container-low/50 rounded-lg p-4">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                    {item.label}
                  </p>
                  <p className={`text-lg font-black mt-1 ${item.color}`}>
                    {formatMAD(item.value)} MAD
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
