import { useState } from 'react';
import { Circle, InfoWindow } from '@react-google-maps/api';
import type { OptimizationCluster } from '@/types/optimization';

interface ClusterRegionProps {
  cluster: OptimizationCluster;
  color?: string;
}

export function ClusterRegion({ cluster, color = '#0058be' }: ClusterRegionProps) {
  const [open, setOpen] = useState(false);
  // Radius based on employee count (min 200 m, max 2 000 m)
  const radius = Math.min(200 + cluster.employee_count * 50, 2000);
  const center: google.maps.LatLngLiteral = {
    lat: cluster.centroid_lat,
    lng: cluster.centroid_lng,
  };

  return (
    <>
      <Circle
        center={center}
        radius={radius}
        options={{
          strokeColor: color,
          strokeOpacity: 0.7,
          strokeWeight: 1.5,
          fillColor: color,
          fillOpacity: 0.12,
          clickable: true,
        }}
        onClick={() => setOpen(true)}
      />
      {open && (
        <InfoWindow
          position={center}
          onCloseClick={() => setOpen(false)}
        >
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
