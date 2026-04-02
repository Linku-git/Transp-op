import { useTranslation } from 'react-i18next';
import { REPORT_TYPES } from '@/types/reports';

interface ReportTypeSelectorProps {
  selectedType: string | null;
  onSelect: (type: string) => void;
}

export function ReportTypeSelector({
  selectedType,
  onSelect,
}: ReportTypeSelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h2 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        {t('reports.select_type', 'Type de rapport')}
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {REPORT_TYPES.map((rt) => {
          const isSelected = selectedType === rt.key;
          return (
            <button
              key={rt.key}
              type="button"
              onClick={() => onSelect(rt.key)}
              className={[
                'flex flex-col items-center gap-2 rounded-xl p-4 transition-all cursor-pointer',
                'border-2 text-center',
                isSelected
                  ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                  : 'border-outline-variant/10 bg-surface-container-lowest hover:border-outline-variant/30 hover:bg-surface-container-low/50',
              ].join(' ')}
            >
              <span
                className={[
                  'material-symbols-outlined text-3xl',
                  isSelected ? 'text-primary' : 'text-on-surface-variant',
                ].join(' ')}
              >
                {rt.icon}
              </span>
              <span
                className={[
                  'text-xs font-medium',
                  isSelected ? 'text-primary' : 'text-on-surface',
                ].join(' ')}
              >
                {t(`reports.type_${rt.key}`, rt.label)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
