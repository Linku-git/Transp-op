import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FileUpload } from '@/components/ui/FileUpload';
import { Tabs } from '@/components/ui/Tabs';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { ValidationErrors } from '@/components/import/ValidationErrors';
import { SheetPreview } from '@/components/import/SheetPreview';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  previewExcel,
  importExcel,
  importSheet,
} from '@/api/import';
import type { ImportResult, SheetResult } from '@/types/import';

type Step = 'upload' | 'preview' | 'done';

export function ExcelImportPage() {
  const { t } = useTranslation();

  const [step, setStep] = useState<Step>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [previewResult, setPreviewResult] = useState<ImportResult | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [activeSheet, setActiveSheet] = useState<string>('');
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [isLoadingImport, setIsLoadingImport] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetState = useCallback(() => {
    setStep('upload');
    setFile(null);
    setPreviewResult(null);
    setImportResult(null);
    setActiveSheet('');
    setIsLoadingPreview(false);
    setIsLoadingImport(false);
    setError(null);
  }, []);

  const handleFileSelected = useCallback(
    async (selectedFile: File) => {
      setFile(selectedFile);
      setError(null);
      setIsLoadingPreview(true);
      setStep('preview');

      try {
        const result = await previewExcel(selectedFile);
        setPreviewResult(result);
        if (result.sheets.length > 0) {
          setActiveSheet(result.sheets[0].sheet);
        }
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : t('common.error');
        setError(message);
        setStep('upload');
        setFile(null);
      } finally {
        setIsLoadingPreview(false);
      }
    },
    [t],
  );

  const handleImportAll = useCallback(async () => {
    if (!file) return;
    setError(null);
    setIsLoadingImport(true);

    try {
      const result = await importExcel(file);
      setImportResult(result);
      setStep('done');
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : t('common.error');
      setError(message);
    } finally {
      setIsLoadingImport(false);
    }
  }, [file, t]);

  const handleImportSheet = useCallback(
    async (sheetName: string) => {
      if (!file) return;
      setError(null);
      setIsLoadingImport(true);

      try {
        const result = await importSheet(file, sheetName);
        setImportResult(result);
        setStep('done');
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : t('common.error');
        setError(message);
      } finally {
        setIsLoadingImport(false);
      }
    },
    [file, t],
  );

  const activeSheetResult: SheetResult | undefined =
    previewResult?.sheets.find((s) => s.sheet === activeSheet);

  const totalRowsParsed =
    previewResult?.sheets.reduce((sum, s) => sum + s.rows_parsed, 0) ?? 0;
  const totalRowsImported =
    previewResult?.sheets.reduce((sum, s) => sum + s.rows_imported, 0) ?? 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <nav className="flex items-center gap-1.5 text-xs font-sans text-on-surface-variant mb-2">
            <span>{t('common.dashboard', 'Tableau de bord')}</span>
            <span>/</span>
            <span className="text-primary font-medium">{t('import.title')}</span>
          </nav>
          <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
            {t('import.title')}
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary">
            {t('import.download_template', 'Telecharger le modele')}
          </Button>
          <Button>
            {t('import.initialize', 'Initialiser le processus')}
          </Button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-lg p-4 mb-6">
          <p className="text-error text-sm font-sans">{error}</p>
        </div>
      )}

      {/* Step 1: Upload */}
      {step === 'upload' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-8">
            <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-6">
              {t('import.upload_zone', 'Zone de depot')}
            </h2>
            <div className="border-2 border-dashed border-outline-variant/30 rounded-xl p-10 hover:border-primary/50 transition-colors">
              <div className="flex flex-col items-center gap-4">
                <svg className="h-12 w-12 text-primary hover:scale-110 transition-transform" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <p className="text-sm text-on-surface-variant font-sans text-center">
                  {t('import.upload_hint')}
                </p>
              </div>
              <div className="mt-6">
                <FileUpload
                  onFile={handleFileSelected}
                  accept=".xlsx,.xls"
                  isLoading={false}
                />
              </div>
            </div>
          </div>
          <div className="bg-surface-container-highest rounded-xl p-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
              {t('import.validation_summary', 'Resume de validation')}
            </h2>
            <p className="text-sm text-on-surface-variant font-sans">
              {t('import.no_file_yet', 'Aucun fichier selectionne. Deposez un fichier Excel pour demarrer.')}
            </p>
          </div>
        </div>
      )}

      {/* Step 2: Preview (loading) */}
      {step === 'preview' && isLoadingPreview && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-8">
          <div className="max-w-md mx-auto space-y-4">
            <p className="text-sm text-on-surface-variant font-sans text-center">
              {t('import.analyzing')}
            </p>
            <ProgressBar value={100} label={t('import.preview_progress')} variant="primary" />
          </div>
        </div>
      )}

      {/* Step 2: Preview (results) */}
      {step === 'preview' && !isLoadingPreview && previewResult && (
        <div className="space-y-6">
          {/* Summary card */}
          <Card>
            <div className="p-6">
              <h2 className="font-sans text-sm font-bold uppercase tracking-widest text-on-surface-variant mb-4">
                {t('import.preview_summary')}
              </h2>
              <div className="flex flex-wrap gap-6">
                <SummaryStat
                  label={t('import.total_sheets')}
                  value={previewResult.sheets.length}
                />
                <SummaryStat
                  label={t('import.total_rows')}
                  value={totalRowsParsed}
                />
                <SummaryStat
                  label={t('import.total_importable')}
                  value={totalRowsImported}
                />
                <SummaryStat
                  label={t('import.total_errors')}
                  value={previewResult.total_errors}
                  isError={previewResult.total_errors > 0}
                />
              </div>
            </div>
          </Card>

          {/* Sheet tabs */}
          {previewResult.sheets.length > 0 && (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10">
              <Tabs
                tabs={previewResult.sheets.map((s) => ({
                  key: s.sheet,
                  label: s.sheet,
                }))}
                activeKey={activeSheet}
                onChange={setActiveSheet}
              />

              {activeSheetResult && (
                <div className="p-6 space-y-6">
                  {/* Sheet stats */}
                  <div className="flex flex-wrap gap-4">
                    <Badge variant="neutral">
                      {t('import.rows_parsed')}: {activeSheetResult.rows_parsed}
                    </Badge>
                    <Badge variant="success">
                      {t('import.rows_imported')}: {activeSheetResult.rows_imported}
                    </Badge>
                    {activeSheetResult.rows_skipped > 0 && (
                      <Badge variant="warning">
                        {t('import.rows_skipped')}: {activeSheetResult.rows_skipped}
                      </Badge>
                    )}
                    {activeSheetResult.errors.length > 0 && (
                      <Badge variant="danger">
                        {t('import.errors_count', { count: activeSheetResult.errors.length })}
                      </Badge>
                    )}
                  </div>

                  {/* Sheet stats summary */}
                  <SheetPreview
                    data={[{
                      [t('import.rows_parsed')]: activeSheetResult.rows_parsed,
                      [t('import.rows_imported')]: activeSheetResult.rows_imported,
                      [t('import.rows_skipped')]: activeSheetResult.rows_skipped,
                      [t('import.errors_count')]: activeSheetResult.errors.length,
                    }]}
                    maxRows={10}
                  />

                  {/* Validation errors for this sheet */}
                  {activeSheetResult.errors.length > 0 && (
                    <ValidationErrors errors={activeSheetResult.errors} />
                  )}

                  {/* Import single sheet button */}
                  <div className="flex justify-end">
                    <Button
                      variant="secondary"
                      onClick={() => handleImportSheet(activeSheetResult.sheet)}
                      disabled={isLoadingImport}
                    >
                      {isLoadingImport
                        ? t('common.loading')
                        : t('import.import_sheet')}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Empty sheets state */}
          {previewResult.sheets.length === 0 && (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-8 text-center">
              <p className="text-sm text-on-surface-variant font-sans">
                {t('import.no_sheets')}
              </p>
            </div>
          )}

          {/* Action bar */}
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={resetState}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleImportAll}
              disabled={isLoadingImport || previewResult.sheets.length === 0}
            >
              {isLoadingImport
                ? t('common.loading')
                : t('import.import_all')}
            </Button>
          </div>
        </div>
      )}

      {/* Step 3: Done */}
      {step === 'done' && importResult && (
        <div className="space-y-6">
          {/* Success / error summary */}
          <Card>
            <div className="p-6">
              <h2 className="font-sans text-lg font-semibold text-on-surface mb-4">
                {importResult.total_errors === 0
                  ? t('import.success_title')
                  : t('import.partial_success_title')}
              </h2>

              <div className="space-y-4">
                {importResult.sheets.map((sheet) => (
                  <div
                    key={sheet.sheet}
                    className="bg-surface-container rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-sans text-sm font-medium text-on-surface">
                        {sheet.sheet}
                      </span>
                      {sheet.errors.length === 0 ? (
                        <Badge variant="success">{t('import.status_ok')}</Badge>
                      ) : (
                        <Badge variant="danger">
                          {t('import.errors_count', { count: sheet.errors.length })}
                        </Badge>
                      )}
                    </div>
                    <div className="flex gap-4 text-xs text-on-surface-variant font-sans">
                      <span>
                        {t('import.rows_parsed')}: {sheet.rows_parsed}
                      </span>
                      <span>
                        {t('import.rows_imported')}: {sheet.rows_imported}
                      </span>
                      {sheet.rows_skipped > 0 && (
                        <span>
                          {t('import.rows_skipped')}: {sheet.rows_skipped}
                        </span>
                      )}
                    </div>
                    {sheet.errors.length > 0 && (
                      <div className="mt-3">
                        <ValidationErrors errors={sheet.errors} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* Reset button */}
          <div className="flex justify-center">
            <Button variant="ghost" onClick={resetState}>
              {t('import.new_import')}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function SummaryStat({
  label,
  value,
  isError = false,
}: {
  label: string;
  value: number;
  isError?: boolean;
}) {
  return (
    <div className="flex flex-col">
      <span className="text-xs font-sans text-on-surface-variant">{label}</span>
      <span
        className={[
          'font-sans text-2xl font-black tabular-nums',
          isError ? 'text-error' : 'text-on-surface',
        ].join(' ')}
      >
        {value}
      </span>
    </div>
  );
}
