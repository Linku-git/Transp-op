import type { RiskStop } from '../../api/rti';

export function WaitTimeHeatmap({ stops }: { stops: RiskStop[] }) {
  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        Temps d'attente par arrêt
      </p>
      {stops.length === 0 ? (
        <p className="text-sm text-on-surface-variant text-center py-8">Aucun arrêt</p>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {stops.map((stop) => {
            const risk = stop.composite_risk_score;
            const barColor = risk >= 0.7 ? 'bg-red-500' : risk >= 0.4 ? 'bg-amber-400' : 'bg-green-500';
            return (
              <div key={stop.id} className="flex items-center gap-3">
                <span className="text-sm w-32 truncate" title={stop.stop_name}>
                  {stop.stop_name}
                </span>
                <div className="flex-1 bg-surface-container-high rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${barColor} transition-all`}
                    style={{ width: `${Math.min(risk * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-on-surface-variant w-10 text-right">
                  {(risk * 100).toFixed(0)}%
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
