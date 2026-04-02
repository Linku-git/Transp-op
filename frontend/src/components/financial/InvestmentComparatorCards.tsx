import { useTranslation } from 'react-i18next';

import { Badge } from '@/components/ui/Badge';
import type {
  InvestmentModelResult,
  InvestmentRecommendation,
} from '@/types/financial';

interface InvestmentComparatorCardsProps {
  models: InvestmentModelResult[];
  recommendation: InvestmentRecommendation;
}

const MODEL_ICONS: Record<string, string> = {
  capex: 'directions_bus',
  mise_a_disposition: 'handshake',
  opex: 'local_taxi',
};

function formatMAD(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M MAD`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k MAD`;
  }
  return `${value.toFixed(0)} MAD`;
}

export function InvestmentComparatorCards({
  models,
  recommendation,
}: InvestmentComparatorCardsProps) {
  const { t } = useTranslation();

  return (
    <div data-testid="investment-comparator-cards" className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {models.map((model) => {
        const isRecommended = model.model === recommendation.recommended_model;
        return (
          <div
            key={model.model}
            data-testid="investment-model-card"
            className={[
              'bg-surface-container-lowest rounded-xl shadow-sm border p-6 flex flex-col gap-4 transition-all',
              isRecommended
                ? 'border-primary/40 ring-2 ring-primary/20'
                : 'border-outline-variant/10',
            ].join(' ')}
          >
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-xl text-on-surface-variant">
                  {MODEL_ICONS[model.model] ?? 'payments'}
                </span>
                <h4 className="text-sm font-bold text-on-surface">{model.label}</h4>
              </div>
              {isRecommended && (
                <Badge variant="info">
                  {t('financial.recommended', 'Recommande')}
                </Badge>
              )}
            </div>

            {/* Total cost */}
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                {t('financial.total_cost', 'Cout total')}
              </p>
              <p className="text-2xl font-black text-on-surface mt-0.5">
                {formatMAD(model.total_cost)}
              </p>
              <p className="text-xs text-on-surface-variant">
                {model.duration_years} {t('financial.years', 'ans')} / {model.vehicle_count}{' '}
                {t('financial.vehicles', 'vehicules')}
              </p>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-outline-variant/10">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  {t('financial.annual_cost', 'Cout annuel')}
                </p>
                <p className="text-sm font-bold text-on-surface mt-0.5">
                  {formatMAD(model.annual_cost)}
                </p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  {t('financial.cost_employee', 'Cout / employe')}
                </p>
                <p className="text-sm font-bold text-on-surface mt-0.5">
                  {formatMAD(model.cost_per_employee)}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  {t('financial.cost_trip', 'Cout / trajet')}
                </p>
                <p className="text-sm font-bold text-on-surface mt-0.5">
                  {model.cost_per_trip.toFixed(2)} MAD
                </p>
              </div>
            </div>

            {/* Recommendation reason */}
            {isRecommended && (
              <div className="bg-primary/5 rounded-lg p-3 mt-auto">
                <p className="text-xs text-primary font-medium">
                  {recommendation.reason}
                </p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
