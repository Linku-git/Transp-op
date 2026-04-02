import { Circle, Popup } from 'react-leaflet';
import type { OptimizationCluster } from '@/types/optimization';

interface ClusterRegionProps {
  cluster: OptimizationCluster;
  color?: string;
}

export function ClusterRegion({ cluster, color = '#0058be' }: ClusterRegionProps) {
  // Radius based on employee count (min 200m, max 2000m)
  const radius = Math.min(200 + cluster.employee_count * 50, 2000);

  return (
    <Circle
      center={[cluster.centroid_lat, cluster.centroid_lng]}
      radius={radius}
      pathOptions={{
        color,
        fillColor: color,
        fillOpacity: 0.12,
        weight: 1.5,
        dashArray: '4 6',
      }}
    >
      <Popup>
        <div className="font-sans text-sm">
          <p className="font-semibold text-on-surface">
            Cluster ({cluster.employee_count} employees)
          </p>
          {cluster.pmr_count > 0 && (
            <p className="text-on-surface-variant">PMR: {cluster.pmr_count}</p>
          )}
        </div>
      </Popup>
    </Circle>
  );
}
