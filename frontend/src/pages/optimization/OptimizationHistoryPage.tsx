import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { useOptimizationStore } from '@/stores/optimizationStore';

function StatusChip({ status }: { status: string }) {
  let bg: string;
  let text: string;

  switch (status) {
    case 'completed':
      bg = 'bg-primary/10';
      text = 'text-primary';
      break;
    case 'failed':
      bg = 'bg-error-container';
      text = 'text-error';
      break;
    case 'running':
      bg = 'bg-tertiary/10';
      text = 'text-tertiary';
      break;
    default:
      bg = 'bg-surface-container-high';
      text = 'text-on-surface-variant';
      break;
  }

  return (
    <span
      className={`inline-block rounded-md px-2.5 py-0.5 text-xs font-sans font-medium ${bg} ${text}`}
    >
      {status}
    </span>
  );
}

export function OptimizationHistoryPage() {
  const { t } = useTranslation();
  const { history, isLoading, error, fetchHistory, clearError } =
    useOptimizationStore();

  const [page, setPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const paginatedHistory = history.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.max(1, Math.ceil(history.length / pageSize));

  const handlePrev = () => {
    setPage((p) => Math.max(1, p - 1));
  };

  const handleNext = () => {
    setPage((p) => Math.min(totalPages, p + 1));
  };

  // Loading state
  if (isLoading && history.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-primary"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span className="text-sm font-sans text-on-surface-variant">
            {t('common.loading', 'Loading...')}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            to="/optimization"
            className="text-sm font-sans text-primary font-medium hover:underline flex items-center gap-1"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            {t('common.back', 'Back')}
          </Link>
          <h1 className="font-sans text-3xl font-black tracking-tight text-on-surface">
            {t('optimization.history_title', 'Optimization History')}
          </h1>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-error-container rounded-lg p-4 mb-4 flex items-center justify-between">
          <p className="text-error text-sm font-sans">{error}</p>
          <button
            onClick={clearError}
            className="text-error text-sm font-sans font-medium hover:underline ml-4 cursor-pointer"
          >
            {t('common.dismiss', 'Dismiss')}
          </button>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && history.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center">
          <svg
            className="mx-auto mb-3 w-12 h-12 text-on-surface-variant/40"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="font-sans text-base font-semibold text-on-surface mb-1">
            {t('optimization.history_empty_title', 'No optimization runs found')}
          </p>
          <p className="text-sm font-sans text-on-surface-variant mb-4">
            {t(
              'optimization.history_empty_desc',
              'Run an optimization to see results here.',
            )}
          </p>
          <Link
            to="/optimization"
            className="text-sm font-sans font-medium text-primary hover:underline"
          >
            {t('optimization.go_to_optimization', 'Go to Optimization')}
          </Link>
        </div>
      )}

      {/* Table */}
      {history.length > 0 && (
        <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-auto">
            <table className="w-full text-sm font-sans">
              <thead>
                <tr className="bg-surface-container-low">
                  <th className="text-left py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_date', 'Date')}
                  </th>
                  <th className="text-left py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_site', 'Site')}
                  </th>
                  <th className="text-left py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_condition', 'Condition')}
                  </th>
                  <th className="text-left py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_status', 'Status')}
                  </th>
                  <th className="text-right py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_vehicles', 'Vehicles')}
                  </th>
                  <th className="text-right py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_distance', 'Distance')}
                  </th>
                  <th className="text-right py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_duration', 'Duration')}
                  </th>
                  <th className="text-right py-3 px-4 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                    {t('optimization.col_actions', 'Actions')}
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedHistory.map((item) => {
                  const m = item.metrics as Record<string, unknown>;
                  const vehicles =
                    typeof m.total_vehicles_used === 'number'
                      ? m.total_vehicles_used
                      : '-';
                  const distance =
                    typeof m.total_distance_km === 'number'
                      ? `${(m.total_distance_km as number).toFixed(1)} km`
                      : '-';
                  const duration =
                    typeof m.total_duration_minutes === 'number'
                      ? `${(m.total_duration_minutes as number).toFixed(0)} min`
                      : '-';

                  return (
                    <tr
                      key={item.id}
                      className="hover:bg-surface-bright transition-colors"
                    >
                      <td className="py-3 px-4 text-on-surface">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-on-surface">
                        {item.site_name ?? '-'}
                      </td>
                      <td className="py-3 px-4 text-on-surface">
                        {item.condition_type}
                      </td>
                      <td className="py-3 px-4">
                        <StatusChip status={item.status} />
                      </td>
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {vehicles}
                      </td>
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {distance}
                      </td>
                      <td className="py-3 px-4 text-right text-on-surface tabular-nums">
                        {duration}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/optimization/${item.id}`}
                          className="text-sm font-sans font-medium text-primary hover:underline"
                        >
                          {t('common.view', 'View')}
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between py-3 px-4 bg-surface-container-low">
              <span className="text-xs font-sans text-on-surface-variant">
                {t('common.page', 'Page')} {page} / {totalPages}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={handlePrev}
                  disabled={page <= 1}
                  className="px-3 py-1.5 text-xs font-sans font-medium rounded-md bg-surface-container-high text-on-surface disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer hover:bg-surface-container transition-colors"
                >
                  {t('common.prev', 'Prev')}
                </button>
                <button
                  onClick={handleNext}
                  disabled={page >= totalPages}
                  className="px-3 py-1.5 text-xs font-sans font-medium rounded-md bg-surface-container-high text-on-surface disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer hover:bg-surface-container transition-colors"
                >
                  {t('common.next', 'Next')}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
