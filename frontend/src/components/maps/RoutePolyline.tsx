import { useState } from 'react';
import { Polyline, InfoWindow } from '@react-google-maps/api';
import type { OptimizationRoute } from '@/types/optimization';

// Google encoded polyline decoder
function decodePolyline(encoded: string): google.maps.LatLngLiteral[] {
  const points: google.maps.LatLngLiteral[] = [];
  let index = 0;
  let lat = 0;
  let lng = 0;

  while (index < encoded.length) {
    let shift = 0;
    let result = 0;
    let byte: number;
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    lat += result & 1 ? ~(result >> 1) : result >> 1;

    shift = 0;
    result = 0;
    do {
      byte = encoded.charCodeAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    lng += result & 1 ? ~(result >> 1) : result >> 1;

    points.push({ lat: lat / 1e5, lng: lng / 1e5 });
  }
  return points;
}

const ROUTE_COLORS = [
  '#0058be',
  '#d97706',
  '#7c3aed',
  '#dc2626',
  '#495e8a',
  '#059669',
  '#924700',
  '#ca8a04',
];

interface RoutePolylineProps {
  route: OptimizationRoute;
  index: number;
  isSelected?: boolean;
}

export function RoutePolyline({
  route,
  index,
  isSelected = false,
}: RoutePolylineProps) {
  const [infoPos, setInfoPos] = useState<google.maps.LatLngLiteral | null>(null);
  const color = ROUTE_COLORS[index % ROUTE_COLORS.length];

  const path: google.maps.LatLngLiteral[] = route.polyline
    ? decodePolyline(route.polyline)
    : route.ordered_stops.map((s) => ({ lat: s.lat, lng: s.lng }));

  if (path.length < 2) return null;

  const midpoint = path[Math.floor(path.length / 2)];

  return (
    <>
      <Polyline
        path={path}
        options={{
          strokeColor: color,
          strokeWeight: isSelected ? 5 : 3,
          strokeOpacity: isSelected ? 1 : 0.75,
          clickable: true,
        }}
        onClick={() => setInfoPos(midpoint)}
      />
      {infoPos && (
        <InfoWindow
          position={infoPos}
          onCloseClick={() => setInfoPos(null)}
        >
          <div className="font-sans text-sm min-w-[180px] p-1">
            <div className="flex items-center gap-2 mb-1">
              <span
                className="inline-block w-3 h-3 rounded-sm flex-shrink-0"
                style={{ backgroundColor: color }}
              />
              <span className="font-semibold text-on-surface">
                {route.vehicle_type ?? 'Véhicule'} ({route.vehicle_capacity ?? '?'} places)
              </span>
            </div>
            <p className="text-on-surface-variant">
              Arrêts: {route.ordered_stops.filter((s) => s.is_pickup).length}
            </p>
            {route.total_distance_km != null && (
              <p className="text-on-surface-variant">
                Distance: {Number(route.total_distance_km).toFixed(1)} km
              </p>
            )}
            {route.total_time_minutes != null && (
              <p className="text-on-surface-variant">
                Durée: {Number(route.total_time_minutes).toFixed(0)} min
              </p>
            )}
          </div>
        </InfoWindow>
      )}
    </>
  );
}
