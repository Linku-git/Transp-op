import type { RiskMapStop } from '../../api/security';

export function RiskStopMap({ stops }: { stops: RiskMapStop[] }) {
  const getColor = (score: number) => {
    if (score > 0.7) return 'bg-red-500';
    if (score > 0.3) return 'bg-amber-400';
    return 'bg-green-500';
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Carte des arrêts à risque
        </p>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Faible</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-400" /> Moyen</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Élevé</span>
        </div>
      </div>
      <div className="w-full h-56 bg-surface-container rounded-lg flex items-center justify-center text-on-surface-variant text-sm mb-4">
        <div className="text-center">
          <span className="material-symbols-outlined text-4xl opacity-30">map</span>
          <p className="mt-2">{stops.length} arrêts sur la carte</p>
        </div>
      </div>
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {stops.map((stop) => (
          <div key={stop.id} className="flex items-center gap-2 text-sm py-1">
            <span className={`w-2 h-2 rounded-full flex-shrink-0 ${getColor(stop.composite_risk_score)}`} />
            <span className="flex-1 truncate">{stop.stop_name}</span>
            <span className="text-xs text-on-surface-variant">{(stop.composite_risk_score * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
