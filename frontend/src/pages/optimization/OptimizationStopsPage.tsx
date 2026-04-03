import { StopsAnalysisSection } from './sections/StopsAnalysisSection';

export function OptimizationStopsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>location_on</span>
          Arrêts & Clusters
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">Carte des points d'arrêt · Scores de marche · Analyse de couverture</p>
      </div>
      <StopsAnalysisSection />
    </div>
  );
}
