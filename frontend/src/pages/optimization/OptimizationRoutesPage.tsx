import { RouteViewerSection } from './sections/RouteViewerSection';

export function OptimizationRoutesPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>route</span>
          Visualisation Routes
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">Parcourir les trajets · Itinéraires sur la carte · Snap to road</p>
      </div>
      <RouteViewerSection />
    </div>
  );
}
