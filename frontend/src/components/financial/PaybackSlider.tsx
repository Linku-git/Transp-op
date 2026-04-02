import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

interface PaybackSliderProps {
  paybackMonths: number | null;
  totalInvestment: number;
  roiTotal: number;
}

function formatMAD(value: number): string {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M MAD`;
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(0)}k MAD`;
  }
  return `${value.toFixed(0)} MAD`;
}

export function PaybackSlider({
  paybackMonths,
  totalInvestment,
  roiTotal,
}: PaybackSliderProps) {
  const { t } = useTranslation();

  const colorClass = useMemo(() => {
    if (paybackMonths === null) return 'text-on-surface-variant';
    if (paybackMonths < 12) return 'text-green-600';
    if (paybackMonths <= 24) return 'text-amber-600';
    return 'text-red-600';
  }, [paybackMonths]);

  const bgClass = useMemo(() => {
    if (paybackMonths === null) return 'bg-surface-container-high';
    if (paybackMonths < 12) return 'bg-green-50';
    if (paybackMonths <= 24) return 'bg-amber-50';
    return 'bg-red-50';
  }, [paybackMonths]);

  return (
    <div
      data-testid="payback-slider"
      className={`${bgClass} rounded-xl p-6 flex flex-col items-center gap-3`}
    >
      <span className={`material-symbols-outlined text-3xl ${colorClass}`}>
        schedule
      </span>

      <div className="text-center">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
          {t('financial.payback_period', 'Delai de retour')}
        </p>
        <p className={`text-4xl font-black font-sans ${colorClass}`} data-testid="payback-months">
          {paybackMonths !== null ? paybackMonths.toFixed(1) : '--'}
        </p>
        <p className="text-sm text-on-surface-variant">
          {t('financial.months', 'mois')}
        </p>
      </div>

      <div className="w-full border-t border-outline-variant/10 pt-3 mt-1 grid grid-cols-2 gap-4 text-center">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('financial.investment', 'Investissement')}
          </p>
          <p className="text-sm font-bold text-on-surface mt-0.5">
            {formatMAD(totalInvestment)}
          </p>
        </div>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('financial.annual_roi', 'ROI annuel')}
          </p>
          <p className="text-sm font-bold text-on-surface mt-0.5">
            {formatMAD(roiTotal)}
          </p>
        </div>
      </div>
    </div>
  );
}
