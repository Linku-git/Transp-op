import { Polyline, Popup } from 'react-leaflet';
import type { OptimizationRoute } from '@/types/optimization';

// Simple polyline decoder (Google's encoded polyline format)
function decodePolyline(encoded: string): [number, number][] {
  const points: [number, number][] = [];
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

    points.push([lat / 1e5, lng / 1e5]);
  }
  return points;
}

// Color palette for different routes
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
  const color = ROUTE_COLORS[index % ROUTE_COLORS.length];

  if (!route.polyline) {
    // Fallback: draw straight lines between stops
    const positions: [number, number][] = route.ordered_stops.map(
      (stop) => [stop.lat, stop.lng] as [number, number],
    );
    if (positions.length < 2) return null;

    return (
      <Polyline
        positions={positions}
        pathOptions={{
          color,
          weight: isSelected ? 5 : 3,
          opacity: isSelected ? 1 : 0.7,
        }}
      >
        <Popup>
          <RoutePopupContent route={route} color={color} />
        </Popup>
      </Polyline>
    );
  }

  const positions = decodePolyline(route.polyline);

  return (
    <Polyline
      positions={positions}
      pathOptions={{
        color,
        weight: isSelected ? 5 : 3,
        opacity: isSelected ? 1 : 0.7,
      }}
    >
      <Popup>
        <RoutePopupContent route={route} color={color} />
      </Popup>
    </Polyline>
  );
}

function RoutePopupContent({
  route,
  color,
}: {
  route: OptimizationRoute;
  color: string;
}) {
  return (
    <div className="font-sans text-sm min-w-48">
      <div className="flex items-center gap-2 mb-1">
        <span
          className="inline-block w-3 h-3 rounded-sm"
          style={{ backgroundColor: color }}
        />
        <span className="font-semibold text-on-surface">
          {route.vehicle_type ?? 'Vehicle'} ({route.vehicle_capacity ?? '?'}{' '}
          places)
        </span>
      </div>
      <p className="text-on-surface-variant">
        Stops: {route.ordered_stops.filter((s) => s.is_pickup).length}
      </p>
      {route.total_distance_km != null && (
        <p className="text-on-surface-variant">
          Distance: {route.total_distance_km.toFixed(1)} km
        </p>
      )}
      {route.total_time_minutes != null && (
        <p className="text-on-surface-variant">
          Duration: {route.total_time_minutes.toFixed(0)} min
        </p>
      )}
    </div>
  );
}
