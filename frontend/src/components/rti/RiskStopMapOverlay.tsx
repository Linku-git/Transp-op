import type { RiskStop } from '../../api/rti';

export function RiskStopMapOverlay({ stops }: { stops: RiskStop[] }) {
  const critical = stops.filter((s) => s.is_critical);
  const normal = stops.filter((s) => !s.is_critical);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Arrêts à risque
        </p>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" />
            Critique ({critical.length})
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            Normal ({normal.length})
          </span>
        </div>
      </div>

      {/* Map placeholder — Google Maps would render here */}
      <div className="w-full h-64 bg-surface-container rounded-lg flex items-center justify-center text-on-surface-variant text-sm">
        <div className="text-center">
          <span className="material-symbols-outlined text-4xl opacity-30">map</span>
          <p className="mt-2">{stops.length} arrêts affichés sur la carte</p>
        </div>
      </div>

      {/* Stop list below map */}
      {critical.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-semibold text-error mb-2">Arrêts critiques</p>
          <div className="space-y-1">
            {critical.map((stop) => (
              <div key={stop.id} className="flex items-center justify-between text-sm py-1">
                <span>{stop.stop_name}</span>
                <span className="text-xs bg-error-container/30 text-error px-2 py-0.5 rounded">
                  {(stop.composite_risk_score * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
