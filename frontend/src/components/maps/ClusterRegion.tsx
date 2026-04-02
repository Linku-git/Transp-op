import { useState } from 'react';
import { Circle, InfoWindow } from '@vis.gl/react-google-maps';
import type { OptimizationCluster } from '@/types/optimization';

interface ClusterRegionProps {
  cluster: OptimizationCluster;
  color?: string;
}

export function ClusterRegion({ cluster, color = '#0058be' }: ClusterRegionProps) {
  const [open, setOpen] = useState(false);
  const radius = Math.min(200 + cluster.employee_count * 50, 2000);
  const center = { lat: cluster.centroid_lat, lng: cluster.centroid_lng };

  return (
    <>
      <Circle
        center={center}
        radius={radius}
        strokeColor={color}
        strokeOpacity={0.7}
        strokeWeight={1.5}
        fillColor={color}
        fillOpacity={0.12}
        onClick={() => setOpen(true)}
      />
      {open && (
        <InfoWindow position={center} onCloseClick={() => setOpen(false)}>
          <div className="font-sans text-sm p-1">
            <p className="font-semibold text-on-surface">
              Cluster ({cluster.employee_count} employés)
            </p>
            {cluster.pmr_count > 0 && (
              <p className="text-on-surface-variant">PMR: {cluster.pmr_count}</p>
            )}
          </div>
        </InfoWindow>
      )}
    </>
  );
}
