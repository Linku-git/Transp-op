import { FleetOptimizerSection } from './sections/FleetOptimizerSection';

export function OptimizationFleetPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
          Optimisation Flotte
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">Algorithme VRP · Taux de remplissage · Économies financières</p>
      </div>
      <FleetOptimizerSection />
    </div>
  );
}
