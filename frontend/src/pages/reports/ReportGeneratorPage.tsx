import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { generateReport } from '@/api/reports';
import { ParameterConfigPanel } from '@/components/reports/ParameterConfigPanel';
import { ReportTypeSelector } from '@/components/reports/ReportTypeSelector';
import { Toast } from '@/components/ui/Toast';
import { REPORT_TYPES } from '@/types/reports';

const SUPPORTED_TYPES = new Set(
  ['modal_analysis', 'fleet_utilization', 'volunteer_driver', 'hr_mobility'],
);

export function ReportGeneratorPage() {
  const { t } = useTranslation();
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{
    visible: boolean;
    message: string;
    type: 'success' | 'error' | 'info';
  }>({ visible: false, message: '', type: 'info' });

  const selectedLabel =
    REPORT_TYPES.find((rt) => rt.key === selectedType)?.label ?? '';

  const isSupported = selectedType !== null && SUPPORTED_TYPES.has(selectedType);

  const handleGenerate = async (format: string) => {
    if (!selectedType) return;
    setIsGenerating(true);
    setError(null);

    try {
      const blob = await generateReport(selectedType, format);

      const extension = format === 'xlsx' ? 'xlsx' : 'pdf';
      const filename = `${selectedType}_${new Date().toISOString().slice(0, 10)}.${extension}`;

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setToast({
        visible: true,
        message: t('reports.generate_success', 'Rapport genere avec succes.'),
        type: 'success',
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : t('common.error', 'Une erreur est survenue');
      setError(message);
      setToast({
        visible: true,
        message,
        type: 'error',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-on-surface font-sans">
            {t('reports.generate_title', 'Generer un rapport')}
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {t(
              'reports.generate_subtitle',
              'Selectionnez le type de rapport et le format souhaite.',
            )}
          </p>
        </div>
        <Link to="/reports">
          <button
            type="button"
            className="flex items-center gap-2 text-sm text-primary hover:text-primary-container transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-base">
              arrow_back
            </span>
            {t('reports.back_to_list', 'Retour a la liste')}
          </button>
        </Link>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container/30 text-error rounded-xl border border-error/10 p-4 text-sm">
          {error}
        </div>
      )}

      {/* Step 1: Select type */}
      <ReportTypeSelector
        selectedType={selectedType}
        onSelect={setSelectedType}
      />

      {/* Step 2: Configure and generate */}
      {selectedType && (
        <>
          {isSupported ? (
            <div className="space-y-4">
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-4">
                <div className="flex items-center gap-3">
                  <span className="material-symbols-outlined text-primary">
                    info
                  </span>
                  <p className="text-sm text-on-surface">
                    {t('reports.selected_report', 'Rapport selectionne :')}{' '}
                    <span className="font-semibold">{selectedLabel}</span>
                  </p>
                </div>
              </div>
              <ParameterConfigPanel
                onGenerate={handleGenerate}
                isGenerating={isGenerating}
              />
            </div>
          ) : (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-8 text-center">
              <span className="material-symbols-outlined text-3xl text-on-surface-variant/40 mb-2 block">
                construction
              </span>
              <p className="text-sm text-on-surface-variant">
                {t(
                  'reports.type_not_available',
                  'Ce type de rapport n\'est pas encore disponible.',
                )}
              </p>
            </div>
          )}
        </>
      )}

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.visible}
        onClose={() => setToast((prev) => ({ ...prev, visible: false }))}
      />
    </div>
  );
}
