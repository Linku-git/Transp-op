import { useTranslation } from 'react-i18next';
import type { RetentionImpact } from '@/types/hr';

interface RetentionImpactCardProps {
  data: RetentionImpact;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'MAD',
    maximumFractionDigits: 0,
  }).format(value);
}

export function RetentionImpactCard({ data }: RetentionImpactCardProps) {
  const { t } = useTranslation();

  const withTransportPct =
    data.departed_total > 0
      ? (data.departed_with_transport / data.departed_total) * 100
      : 0;
  const withoutTransportPct =
    data.departed_total > 0
      ? (data.departed_without_transport / data.departed_total) * 100
      : 0;

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        {t('hr.retention_title', 'Impact Retention')}
      </h3>

      {/* Main metric: annual savings */}
      <div className="mb-5">
        <p className="font-sans text-3xl font-bold text-primary" data-testid="annual-savings">
          {formatCurrency(data.estimated_annual_savings)}
        </p>
        <p className="font-sans text-xs text-on-surface-variant mt-1">
          {t('hr.estimated_savings', 'Economies annuelles estimees')}
        </p>
      </div>

      {/* Metric grid */}
      <div className="grid grid-cols-3 gap-4 mb-5">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('hr.turnover_rate', 'Taux de turnover')}
          </p>
          <p className="font-sans text-lg font-semibold text-on-surface" data-testid="turnover-rate">
            {data.turnover_rate_pct.toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('hr.departed_total', 'Departs total')}
          </p>
          <p className="font-sans text-lg font-semibold text-on-surface">
            {data.departed_total}
          </p>
        </div>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('hr.replacement_cost', 'Cout remplacement')}
          </p>
          <p className="font-sans text-lg font-semibold text-on-surface">
            {formatCurrency(data.avg_replacement_cost)}
          </p>
        </div>
      </div>

      {/* Visual bar: departed with vs without transport */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
          {t('hr.departure_breakdown', 'Repartition des departs')}
        </p>
        <div className="flex h-4 rounded-full overflow-hidden bg-surface-container-high/50" data-testid="departure-bar">
          <div
            className="bg-primary transition-all"
            style={{ width: `${withTransportPct}%` }}
            title={`${t('hr.with_transport', 'Avec transport')}: ${data.departed_with_transport}`}
          />
          <div
            className="bg-error transition-all"
            style={{ width: `${withoutTransportPct}%` }}
            title={`${t('hr.without_transport', 'Sans transport')}: ${data.departed_without_transport}`}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="font-sans text-xs text-primary">
            {t('hr.with_transport', 'Avec transport')}: {data.departed_with_transport}
          </span>
          <span className="font-sans text-xs text-error">
            {t('hr.without_transport', 'Sans transport')}: {data.departed_without_transport}
          </span>
        </div>
      </div>
    </div>
  );
}
