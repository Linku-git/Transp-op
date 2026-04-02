import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { REPORT_FORMATS } from '@/types/reports';
import type { ReportFormat } from '@/types/reports';
import { Button } from '@/components/ui/Button';

interface ParameterConfigPanelProps {
  onGenerate: (format: string) => void;
  isGenerating: boolean;
}

const FORMAT_LABELS: Record<ReportFormat, string> = {
  pdf: 'PDF',
  xlsx: 'Excel (.xlsx)',
};

export function ParameterConfigPanel({
  onGenerate,
  isGenerating,
}: ParameterConfigPanelProps) {
  const { t } = useTranslation();
  const [selectedFormat, setSelectedFormat] = useState<ReportFormat>('pdf');

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <h2 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        {t('reports.parameters', 'Parametres de generation')}
      </h2>

      <div className="space-y-4">
        <div>
          <label className="text-[10px] font-bold uppercase tracking-widest text-outline block mb-2">
            {t('reports.format', 'Format')}
          </label>
          <div className="flex gap-3">
            {REPORT_FORMATS.map((fmt) => (
              <label
                key={fmt}
                className={[
                  'flex items-center gap-2 rounded-lg px-4 py-2 cursor-pointer border transition-all',
                  selectedFormat === fmt
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-outline-variant/10 bg-surface-container-high/50 text-on-surface',
                ].join(' ')}
              >
                <input
                  type="radio"
                  name="report-format"
                  value={fmt}
                  checked={selectedFormat === fmt}
                  onChange={() => setSelectedFormat(fmt)}
                  className="sr-only"
                />
                <span
                  className={[
                    'w-4 h-4 rounded-full border-2 flex items-center justify-center',
                    selectedFormat === fmt
                      ? 'border-primary'
                      : 'border-outline-variant',
                  ].join(' ')}
                >
                  {selectedFormat === fmt && (
                    <span className="w-2 h-2 rounded-full bg-primary" />
                  )}
                </span>
                <span className="text-sm font-medium">
                  {FORMAT_LABELS[fmt]}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div className="pt-2">
          <Button
            onClick={() => onGenerate(selectedFormat)}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <span className="flex items-center gap-2">
                <span className="material-symbols-outlined animate-spin text-base">
                  progress_activity
                </span>
                {t('reports.generating', 'Generation en cours...')}
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <span className="material-symbols-outlined text-base">
                  download
                </span>
                {t('reports.generate', 'Generer le rapport')}
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
