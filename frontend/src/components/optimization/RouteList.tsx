import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type { OptimizationRoute } from '@/types/optimization';

const ROUTE_COLORS = [
  '#006b5c',
  '#d97706',
  '#7c3aed',
  '#dc2626',
  '#2563eb',
  '#059669',
  '#db2777',
  '#ca8a04',
] as const;

interface RouteListProps {
  routes: OptimizationRoute[];
}

function formatDuration(minutes: number | null): string {
  if (minutes === null || minutes === undefined) return '--';
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return `${h}h${m.toString().padStart(2, '0')}`;
}

function formatEta(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  if (m === 0) return `${s}s`;
  return `${m}m${s.toString().padStart(2, '0')}s`;
}

function RouteRow({
  route,
  index,
}: {
  route: OptimizationRoute;
  index: number;
}) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);

  const color = ROUTE_COLORS[index % ROUTE_COLORS.length];
  const pickupStops = route.ordered_stops.filter((s) => s.is_pickup);
  const stopCount = pickupStops.length;

  const toggle = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  return (
    <div className="bg-surface-container-lowest rounded-lg overflow-hidden">
      {/* Collapsed header */}
      <button
        onClick={toggle}
        type="button"
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-surface-container-low transition-colors duration-150 cursor-pointer"
      >
        {/* Color dot */}
        <span
          className="w-3 h-3 rounded-full flex-shrink-0"
          style={{ backgroundColor: color }}
        />

        {/* Vehicle type */}
        <span className="font-sans text-sm font-medium text-on-surface flex-1 truncate">
          {route.vehicle_type ?? t('optimization.vehicle', 'Vehicule')}{' '}
          {route.vehicle_capacity != null && (
            <span className="text-on-surface-variant font-normal">
              ({route.vehicle_capacity} {t('optimization.seats', 'places')})
            </span>
          )}
        </span>

        {/* Stop count */}
        <span className="font-sans text-xs text-on-surface-variant tabular-nums">
          {stopCount} {t('optimization.stops', 'arrets')}
        </span>

        {/* Distance */}
        <span className="font-sans text-xs text-on-surface-variant tabular-nums w-16 text-right">
          {route.total_distance_km != null
            ? `${route.total_distance_km.toFixed(1)} km`
            : '--'}
        </span>

        {/* Duration */}
        <span className="font-sans text-xs text-on-surface-variant tabular-nums w-14 text-right">
          {formatDuration(route.total_time_minutes)}
        </span>

        {/* Chevron */}
        <span
          className="text-on-surface-variant text-sm transition-transform duration-200 flex-shrink-0"
          style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)' }}
        >
          {'\u25B8'}
        </span>
      </button>

      {/* Expanded stop list */}
      {expanded && (
        <div className="px-4 pb-4 pt-0">
          <div className="bg-surface-container rounded-lg p-3">
            {route.ordered_stops.length === 0 ? (
              <p className="font-sans text-xs text-on-surface-variant">
                {t('optimization.no_stops', 'Aucun arret')}
              </p>
            ) : (
              <ol className="space-y-2">
                {route.ordered_stops.map((stop, stopIdx) => (
                  <li
                    key={`${route.id}-stop-${stopIdx}`}
                    className="flex items-center gap-3"
                  >
                    {/* Step number */}
                    <span className="font-display text-xs font-bold text-on-surface-variant w-5 text-right tabular-nums">
                      {stopIdx + 1}
                    </span>

                    {/* Vertical connector dot */}
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{
                        backgroundColor: stop.is_pickup ? color : '#44474c',
                      }}
                    />

                    {/* Stop details */}
                    <div className="flex-1 min-w-0">
                      <span className="font-sans text-xs text-on-surface">
                        {stop.is_pickup
                          ? t('optimization.pickup', 'Prise en charge')
                          : t('optimization.dropoff', 'Depot')}
                      </span>
                      {stop.employee_id && (
                        <span className="font-sans text-xs text-on-surface-variant ml-2 truncate">
                          {stop.employee_id.slice(0, 8)}...
                        </span>
                      )}
                    </div>

                    {/* ETA */}
                    <span className="font-sans text-xs text-on-surface-variant tabular-nums">
                      ETA {formatEta(stop.eta_seconds)}
                    </span>

                    {/* Cumulative distance */}
                    <span className="font-sans text-xs text-on-surface-variant tabular-nums w-14 text-right">
                      {(stop.cumulative_distance_meters / 1000).toFixed(1)} km
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function RouteList({ routes }: RouteListProps) {
  const { t } = useTranslation();

  if (routes.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-lg p-8 flex items-center justify-center">
        <p className="font-sans text-sm text-on-surface-variant">
          {t('optimization.no_routes', 'Aucune route disponible')}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {/* Column headers */}
      <div className="flex items-center gap-3 px-4 py-2">
        <span className="w-3" /> {/* Color dot spacer */}
        <span className="font-sans text-xs font-medium text-on-surface-variant flex-1">
          {t('optimization.route_vehicle', 'Vehicule')}
        </span>
        <span className="font-sans text-xs font-medium text-on-surface-variant">
          {t('optimization.route_stops', 'Arrets')}
        </span>
        <span className="font-sans text-xs font-medium text-on-surface-variant w-16 text-right">
          {t('optimization.route_distance', 'Dist.')}
        </span>
        <span className="font-sans text-xs font-medium text-on-surface-variant w-14 text-right">
          {t('optimization.route_duration', 'Duree')}
        </span>
        <span className="w-3.5" /> {/* Chevron spacer */}
      </div>

      {/* Route rows */}
      {routes.map((route, idx) => (
        <RouteRow key={route.id} route={route} index={idx} />
      ))}
    </div>
  );
}
