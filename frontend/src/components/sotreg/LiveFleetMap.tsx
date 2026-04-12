/**
 * LiveFleetMap — Real-time vehicle positions on a map placeholder.
 *
 * In production, this would use @vis.gl/react-google-maps APIProvider + Map.
 * This component provides the glassmorphism overlays and vehicle list
 * that sit on top of the map surface.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useMemo } from 'react';
import type { VehicleMarker } from '../../stores/operationsStore';

interface LiveFleetMapProps {
  vehicles: VehicleMarker[];
  selectedVehicleId: string | null;
  onSelectVehicle: (id: string) => void;
}

export function LiveFleetMap({ vehicles, selectedVehicleId, onSelectVehicle }: LiveFleetMapProps) {
  const vehicleCount = vehicles.length;
  const activeCount = useMemo(
    () => vehicles.filter((v) => Date.now() / 1000 - v.lastUpdate < 60).length,
    [vehicles],
  );

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden h-full min-h-[400px]"
      data-testid="live-fleet-map"
    >
      {/* Map container — in production uses APIProvider + Map from @vis.gl/react-google-maps */}
      <div className="relative h-full bg-surface-container flex items-center justify-center">
        {vehicleCount === 0 ? (
          <div className="text-center text-on-surface-variant">
            <span className="material-symbols-outlined text-4xl mb-2 block">directions_bus</span>
            <p className="text-sm">Aucun vehicule en ligne</p>
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col">
            {/* Map header overlay */}
            <div className="absolute top-3 left-3 z-10 bg-white/90 backdrop-blur-md rounded-xl shadow-lg border border-white/20 px-4 py-2 flex items-center gap-3">
              <span className="material-symbols-outlined text-primary">satellite_alt</span>
              <div>
                <p className="text-xs font-bold text-on-surface">{vehicleCount} vehicules</p>
                <p className="text-[10px] text-on-surface-variant">
                  {activeCount} actifs (&lt; 60s)
                </p>
              </div>
            </div>

            {/* Vehicle list overlay */}
            <div className="absolute bottom-3 left-3 right-3 z-10 bg-white/90 backdrop-blur-md rounded-xl shadow-lg border border-white/20 p-3 max-h-[150px] overflow-y-auto">
              <div className="space-y-1">
                {vehicles.slice(0, 10).map((v) => (
                  <button
                    key={v.id}
                    onClick={() => onSelectVehicle(v.id)}
                    className={`w-full flex items-center gap-2 px-2 py-1 rounded text-xs transition-colors ${
                      selectedVehicleId === v.id
                        ? 'bg-primary/10 text-primary'
                        : 'hover:bg-surface-container-high/50 text-on-surface-variant'
                    }`}
                  >
                    <span className="material-symbols-outlined text-sm">directions_bus</span>
                    <span className="font-medium">{v.ligneName}</span>
                    <span className="ml-auto">{v.speed.toFixed(0)} km/h</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Placeholder map background */}
            <div className="flex-1 bg-gradient-to-br from-blue-50 to-surface-container flex items-center justify-center text-on-surface-variant text-sm">
              <span className="material-symbols-outlined text-6xl opacity-20">map</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
