import { useState } from 'react';
import { StopsAnalysisSection } from './sections/StopsAnalysisSection';
import { FleetOptimizerSection } from './sections/FleetOptimizerSection';
import { RouteViewerSection } from './sections/RouteViewerSection';

type TabId = 'stops' | 'fleet' | 'routes';

const TABS: { id: TabId; label: string; icon: string; desc: string }[] = [
  {
    id: 'stops',
    label: 'Arrêts & Clusters',
    icon: 'location_on',
    desc: 'Carte des points d\'arrêt, scores de marche, analyse de couverture',
  },
  {
    id: 'fleet',
    label: 'Optimisation Flotte',
    icon: 'bolt',
    desc: 'Algorithme VRP, taux de remplissage, économies financières',
  },
  {
    id: 'routes',
    label: 'Visualisation Routes',
    icon: 'route',
    desc: 'Parcourir les trajets, voir les itinéraires sur la carte',
  },
];

export function OptimizationHubPage() {
  const [activeTab, setActiveTab] = useState<TabId>('routes');

  return (
    <div className="flex flex-col gap-6">
      {/* ── Page header ─────────────────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span className="material-symbols-outlined text-blue-600 text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>
            route
          </span>
          Optimisation Transport
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Analyse des arrêts · Optimisation VRP de la flotte · Visualisation des routes
        </p>
      </div>

      {/* ── Tab navigation ─────────────────────────────────────────────── */}
      <div className="flex gap-3">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={[
              'flex flex-col items-start gap-1 rounded-xl border px-4 py-3 text-left transition-all flex-1',
              activeTab === tab.id
                ? 'border-blue-500 bg-blue-50 shadow-sm'
                : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50',
            ].join(' ')}
          >
            <div className="flex items-center gap-2">
              <span
                className={['material-symbols-outlined text-xl', activeTab === tab.id ? 'text-blue-600' : 'text-slate-400'].join(' ')}
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                {tab.icon}
              </span>
              <span className={['text-sm font-bold', activeTab === tab.id ? 'text-blue-700' : 'text-slate-700'].join(' ')}>
                {tab.label}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">{tab.desc}</p>
          </button>
        ))}
      </div>

      {/* ── Tab content ─────────────────────────────────────────────────── */}
      {activeTab === 'stops' && <StopsAnalysisSection />}
      {activeTab === 'fleet' && <FleetOptimizerSection />}
      {activeTab === 'routes' && <RouteViewerSection />}
    </div>
  );
}
