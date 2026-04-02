import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import type { Optimization, OptimizationMetrics } from '@/types/optimization';

interface SiteBreakdownProps {
  optimization: Optimization;
}

function SummaryRow({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="font-sans text-sm text-on-surface-variant">{label}</span>
      <span className="font-sans text-sm font-semibold text-on-surface tabular-nums">
        {value}
      </span>
    </div>
  );
}

function ConditionChip({ condition }: { condition: string }) {
  const chipStyles: Record<string, string> = {
    normal: 'bg-primary/10 text-primary',
    rain: 'bg-surface-container-high text-on-surface-variant',
    strike: 'bg-error-container text-error',
    peak: 'bg-tertiary/10 text-tertiary',
    night: 'bg-surface-container-high text-on-surface-variant',
  };

  const style =
    chipStyles[condition] ?? 'bg-surface-container text-on-surface-variant';

  return (
    <span
      className={`inline-block rounded-md px-2.5 py-0.5 text-xs font-sans font-medium capitalize ${style}`}
    >
      {condition}
    </span>
  );
}

export function SiteBreakdown({ optimization }: SiteBreakdownProps) {
  const { t } = useTranslation();

  const siteName = useMemo(() => {
    // Derive site name from the first route that has one
    for (const route of optimization.routes) {
      if (route.site_name) return route.site_name;
    }
    return t('optimization.unknown_site', 'Site inconnu');
  }, [optimization.routes, t]);

  const metrics = optimization.metrics as OptimizationMetrics | null;
  const hasMetrics =
    metrics !== null && typeof metrics.total_employees === 'number';

  const totalDistance = useMemo(() => {
    if (hasMetrics && metrics) {
      return metrics.total_distance_km.toFixed(1);
    }
    // Fallback: sum from routes
    const sum = optimization.routes.reduce(
      (acc, r) => acc + (r.total_distance_km ?? 0),
      0,
    );
    return sum.toFixed(1);
  }, [optimization.routes, hasMetrics, metrics]);

  const totalEmployees = useMemo(() => {
    if (hasMetrics && metrics) {
      return metrics.total_employees;
    }
    // Fallback: sum from clusters
    return optimization.clusters.reduce(
      (acc, c) => acc + c.employee_count,
      0,
    );
  }, [optimization.clusters, hasMetrics, metrics]);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      {/* Site name header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-sans text-base font-semibold text-on-surface">
          {siteName}
        </h3>
        <ConditionChip condition={optimization.condition_type} />
      </div>

      {/* Summary rows */}
      <div className="bg-surface-container rounded-lg px-4 py-1 divide-on-surface-variant/0">
        <SummaryRow
          label={t('optimization.breakdown_clusters', 'Clusters')}
          value={optimization.clusters.length}
        />
        <SummaryRow
          label={t('optimization.breakdown_routes', 'Routes')}
          value={optimization.routes.length}
        />
        <SummaryRow
          label={t('optimization.breakdown_employees', 'Employes')}
          value={totalEmployees}
        />
        <SummaryRow
          label={t('optimization.breakdown_distance', 'Distance totale')}
          value={`${totalDistance} km`}
        />
      </div>

      {/* Optimization metadata */}
      <div className="mt-4 flex flex-wrap items-center gap-3">
        {optimization.target_date && (
          <span className="font-sans text-xs text-on-surface-variant">
            {t('optimization.breakdown_date', 'Date cible')}:{' '}
            <span className="text-on-surface font-medium">
              {optimization.target_date}
            </span>
          </span>
        )}
        <span className="font-sans text-xs text-on-surface-variant">
          {t('optimization.breakdown_status', 'Statut')}:{' '}
          <span className="text-on-surface font-medium capitalize">
            {optimization.status}
          </span>
        </span>
      </div>
    </div>
  );
}
