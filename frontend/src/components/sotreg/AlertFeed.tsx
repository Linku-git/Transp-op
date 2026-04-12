/**
 * AlertFeed — Scrolling real-time alert list with severity color coding.
 *
 * Displays geofence, route deviation, maintenance, and speed alerts
 * with timestamps and click-to-locate functionality.
 *
 * Session 122 — M8 Real-Time Operations.
 */
import { useRef, useState } from 'react';
import type { OperationAlert } from '../../stores/operationsStore';

interface AlertFeedProps {
  alerts: OperationAlert[];
  onLocateVehicle: (vehicleId: string, lat: number, lng: number) => void;
}

const SEVERITY_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  info: { icon: 'info', color: 'text-blue-600', bg: 'bg-blue-50' },
  warning: { icon: 'warning', color: 'text-amber-600', bg: 'bg-amber-50' },
  critical: { icon: 'error', color: 'text-red-600', bg: 'bg-red-50' },
};

const TYPE_LABELS: Record<string, string> = {
  geofence_alert: 'Geofence',
  route_deviation: 'Deviation',
  maintenance: 'Maintenance',
  speed: 'Vitesse',
};

export function AlertFeed({ alerts, onLocateVehicle }: AlertFeedProps) {
  const [_paused, setPaused] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  return (
    <div
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-5"
      data-testid="alert-feed"
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Alertes Temps Reel ({alerts.length})
        </h3>
        {alerts.length > 0 && (
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        )}
      </div>

      {alerts.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-4">
          <span className="material-symbols-outlined text-lg block mb-1">
            notifications_none
          </span>
          Aucune alerte
        </p>
      ) : (
        <div
          ref={listRef}
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          className="space-y-1.5 max-h-[280px] overflow-y-auto"
        >
          {alerts.map((a) => {
            const sev = SEVERITY_CONFIG[a.severity] || SEVERITY_CONFIG.info;
            return (
              <button
                key={a.id}
                onClick={() => onLocateVehicle(a.vehicleId, a.lat, a.lng)}
                className={`w-full flex items-start gap-2 px-3 py-2 rounded-lg text-left ${sev.bg} hover:opacity-80 transition-opacity`}
              >
                <span className={`material-symbols-outlined text-sm mt-0.5 ${sev.color}`}>
                  {sev.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] font-bold uppercase text-on-surface-variant">
                      {TYPE_LABELS[a.type] || a.type}
                    </span>
                    <span className="text-[10px] text-on-surface-variant opacity-60 ml-auto">
                      {new Date(a.timestamp * 1000).toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                      })}
                    </span>
                  </div>
                  <p className="text-xs text-on-surface truncate">{a.message}</p>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
