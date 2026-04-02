import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import { getReportHistory } from '@/api/reports';
import { Button } from '@/components/ui/Button';
import type { GeneratedReport, ReportHistoryResponse } from '@/types/reports';
import { REPORT_TYPES } from '@/types/reports';

const REPORT_TYPE_LABELS: Record<string, string> = Object.fromEntries(
  REPORT_TYPES.map((rt) => [rt.key, rt.label]),
);

export function ReportListPage() {
  const { t } = useTranslation();
  const [history, setHistory] = useState<ReportHistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [filterType, setFilterType] = useState('');

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = { page, page_size: 20 };
      if (filterType) params.report_type = filterType;
      const data = await getReportHistory(
        params as { report_type?: string; page?: number; page_size?: number },
      );
      setHistory(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : t('common.error', 'Une erreur est survenue');
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [page, filterType, t]);

  useEffect(() => {
    void fetchHistory();
  }, [fetchHistory]);

  const handleDownload = (report: GeneratedReport) => {
    if (report.file_url) {
      window.open(report.file_url, '_blank');
    }
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '-';
    try {
      return new Intl.DateTimeFormat('fr-FR', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(new Date(dateStr));
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-on-surface font-sans">
            {t('reports.title', 'Rapports')}
          </h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {t('reports.subtitle', 'Historique des rapports generes.')}
          </p>
        </div>
        <Link to="/reports/generate">
          <Button>
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-base">add</span>
              {t('reports.generate_new', 'Generer un nouveau rapport')}
            </span>
          </Button>
        </Link>
      </div>

      {/* Filter */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-4">
        <div className="flex items-center gap-4">
          <label className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('reports.filter_type', 'Filtrer par type')}
          </label>
          <select
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value);
              setPage(1);
            }}
            className="bg-surface-container-high/50 border-none rounded-lg px-3 py-1.5 text-sm text-on-surface focus:ring-2 focus:ring-primary/20"
          >
            <option value="">
              {t('reports.all_types', 'Tous les types')}
            </option>
            {REPORT_TYPES.map((rt) => (
              <option key={rt.key} value={rt.key}>
                {rt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-error-container/30 text-error rounded-xl border border-error/10 p-4 text-sm">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12 text-on-surface-variant text-sm">
          {t('common.loading', 'Chargement...')}
        </div>
      )}

      {/* Table */}
      {!loading && !error && history && (
        <>
          {history.data.length === 0 ? (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-12 text-center">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-3 block">
                description
              </span>
              <p className="text-sm text-on-surface-variant">
                {t('reports.empty', 'Aucun rapport genere.')}
              </p>
              <Link to="/reports/generate" className="inline-block mt-4">
                <Button>
                  {t('reports.generate_first', 'Generer votre premier rapport')}
                </Button>
              </Link>
            </div>
          ) : (
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="text-left px-4 py-3 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('reports.col_type', 'Type')}
                    </th>
                    <th className="text-left px-4 py-3 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('reports.col_format', 'Format')}
                    </th>
                    <th className="text-left px-4 py-3 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('reports.col_date', 'Date')}
                    </th>
                    <th className="text-right px-4 py-3 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('reports.col_actions', 'Actions')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {history.data.map((report) => (
                    <tr
                      key={report.id}
                      className="hover:bg-surface-bright transition-colors"
                    >
                      <td className="px-4 py-3 text-on-surface font-medium">
                        {REPORT_TYPE_LABELS[report.report_type] ??
                          report.report_type}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center rounded-md bg-primary/10 text-primary px-2 py-0.5 text-xs font-medium uppercase">
                          {report.format ?? '-'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-on-surface-variant">
                        {formatDate(report.generated_at)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {report.file_url ? (
                          <button
                            type="button"
                            onClick={() => handleDownload(report)}
                            className="inline-flex items-center gap-1 text-primary hover:text-primary-container transition-colors cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-base">
                              download
                            </span>
                            <span className="text-xs font-medium">
                              {t('reports.download', 'Telecharger')}
                            </span>
                          </button>
                        ) : (
                          <span className="text-xs text-on-surface-variant/50">
                            -
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              {history.pages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t border-outline-variant/10">
                  <span className="text-xs text-on-surface-variant">
                    {t('reports.pagination_info', 'Page {{page}} sur {{pages}} ({{total}} rapports)', {
                      page: history.page,
                      pages: history.pages,
                      total: history.total,
                    })}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      className="px-3 py-1 text-xs rounded-lg border border-outline-variant/10 text-on-surface-variant hover:bg-surface-container-low/50 disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
                    >
                      {t('common.previous', 'Precedent')}
                    </button>
                    <button
                      type="button"
                      disabled={page >= history.pages}
                      onClick={() => setPage((p) => p + 1)}
                      className="px-3 py-1 text-xs rounded-lg border border-outline-variant/10 text-on-surface-variant hover:bg-surface-container-low/50 disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
                    >
                      {t('common.next', 'Suivant')}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
