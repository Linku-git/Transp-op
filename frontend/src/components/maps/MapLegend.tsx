import type { LayerVisibility } from '@/types/optimization';

interface MapLegendProps {
  layers: LayerVisibility;
  onToggle: (layer: keyof LayerVisibility) => void;
  routeCount?: number;
  selectedRouteId: string | null;
  routeIds?: string[];
  onSelectRoute?: (id: string | null) => void;
}

const LAYER_CONFIG: {
  key: keyof LayerVisibility;
  label: string;
  color: string;
}[] = [
  { key: 'siteMarker', label: 'Site', color: '#041627' },
  { key: 'employees', label: 'Employees', color: '#2563eb' },
  { key: 'clusters', label: 'Clusters', color: '#0058be' },
  { key: 'routes', label: 'Routes', color: '#d97706' },
  { key: 'meetingZones', label: 'Meeting Zones', color: '#0058be' },
  { key: 'accessLegs', label: 'Access Legs', color: '#495e8a' },
];

export function MapLegend({
  layers,
  onToggle,
  routeCount = 0,
  selectedRouteId,
  routeIds = [],
  onSelectRoute,
}: MapLegendProps) {
  return (
    <div
      className="absolute top-4 right-4 z-[1000] bg-white/90 backdrop-blur-md rounded-xl shadow-lg p-4 min-w-52"
      style={{ backdropFilter: 'blur(12px)', border: '1px solid rgba(255,255,255,0.2)' }}
    >
      <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-3">
        Layers
      </p>
      <div className="space-y-2">
        {LAYER_CONFIG.map(({ key, label, color }) => (
          <label
            key={key}
            className="flex items-center gap-2 cursor-pointer text-sm font-sans"
          >
            <input
              type="checkbox"
              checked={layers[key]}
              onChange={() => onToggle(key)}
              className="rounded accent-primary focus:ring-primary"
            />
            <span
              className="inline-block w-3 h-3 rounded-sm"
              style={{ backgroundColor: color }}
            />
            <span className="text-on-surface-variant">{label}</span>
          </label>
        ))}
      </div>

      {routeCount > 0 && onSelectRoute && (
        <div
          className="mt-3 pt-3"
          style={{ borderTop: '1px solid rgba(196,198,205,0.15)' }}
        >
          <p className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">
            Routes ({routeCount})
          </p>
          <button
            onClick={() => onSelectRoute(null)}
            className={`block w-full text-left text-xs px-2 py-1 rounded mb-1 ${
              selectedRouteId === null
                ? 'bg-surface-container text-on-surface'
                : 'text-on-surface-variant hover:bg-surface-container-low'
            }`}
          >
            All routes
          </button>
          {routeIds.map((id, idx) => (
            <button
              key={id}
              onClick={() => onSelectRoute(id)}
              className={`block w-full text-left text-xs px-2 py-1 rounded mb-1 ${
                selectedRouteId === id
                  ? 'bg-surface-container text-on-surface'
                  : 'text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              Route {idx + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
