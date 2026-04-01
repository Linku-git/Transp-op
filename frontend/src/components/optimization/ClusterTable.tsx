import { useTranslation } from 'react-i18next';
import type { OptimizationCluster } from '@/types/optimization';

interface ClusterTableProps {
  clusters: OptimizationCluster[];
}

function truncateCoord(value: number): string {
  return value.toFixed(4);
}

export function ClusterTable({ clusters }: ClusterTableProps) {
  const { t } = useTranslation();

  if (clusters.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-lg p-8 flex items-center justify-center">
        <p className="font-sans text-sm text-on-surface-variant">
          {t('optimization.no_clusters', 'Aucun cluster disponible')}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-surface-container-lowest rounded-lg overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-surface-container">
            <th className="text-left font-sans text-xs font-medium text-on-surface-variant px-4 py-3">
              #
            </th>
            <th className="text-right font-sans text-xs font-medium text-on-surface-variant px-4 py-3">
              {t('optimization.cluster_employees', 'Employes')}
            </th>
            <th className="text-right font-sans text-xs font-medium text-on-surface-variant px-4 py-3">
              PMR
            </th>
            <th className="text-left font-sans text-xs font-medium text-on-surface-variant px-4 py-3">
              {t('optimization.cluster_centroid', 'Centroide')}
            </th>
          </tr>
        </thead>
        <tbody>
          {clusters.map((cluster, idx) => (
            <tr
              key={cluster.id}
              className="transition-colors duration-100 hover:bg-surface-container-low"
            >
              <td className="px-4 py-3 font-sans text-sm text-on-surface tabular-nums">
                {idx + 1}
              </td>
              <td className="px-4 py-3 font-sans text-sm text-on-surface tabular-nums text-right">
                {cluster.employee_count}
              </td>
              <td className="px-4 py-3 text-right">
                {cluster.pmr_count > 0 ? (
                  <span className="inline-block rounded-md bg-secondary-container text-on-secondary-container px-2 py-0.5 text-xs font-sans font-medium tabular-nums">
                    {cluster.pmr_count}
                  </span>
                ) : (
                  <span className="font-sans text-sm text-on-surface-variant tabular-nums">
                    0
                  </span>
                )}
              </td>
              <td className="px-4 py-3 font-sans text-xs text-on-surface-variant tabular-nums">
                {truncateCoord(cluster.centroid_lat)}, {truncateCoord(cluster.centroid_lng)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
