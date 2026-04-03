import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useEmployeeStore } from '@/stores/employeeStore';
import { useSiteStore } from '@/stores/siteStore';
import { MapView } from '@/components/maps/MapView';
import { EmployeeMarker } from '@/components/maps/EmployeeMarker';
import { SiteMarker } from '@/components/maps/SiteMarker';
import { StopMarker } from '@/components/maps/StopMarker';
import { Skeleton } from '@/components/ui/Skeleton';
import { listPointsArret } from '@/api/vehicles';
import type { Employee } from '@/types/employee';
import type { Site } from '@/types/site';
import type { PointArret } from '@/types/vehicle';

const SITE_COLORS: string[] = [
  '#0058be', '#924700', '#7c3aed', '#495e8a',
  '#be185d', '#4d7c0f', '#9333ea', '#c2410c', '#0891b2', '#a16207',
];

function getSiteColor(siteId: string, siteIds: string[]): string {
  const idx = siteIds.indexOf(siteId);
  return SITE_COLORS[idx >= 0 ? idx % SITE_COLORS.length : 0];
}

type LayerKey = 'employees' | 'sites' | 'stops';

const LAYER_META: Record<LayerKey, { label: string; icon: string; color: string }> = {
  employees: { label: 'Employés',        icon: 'group',         color: '#0058be' },
  sites:     { label: 'Sites',           icon: 'location_on',   color: '#495e8a' },
  stops:     { label: "Points d'Arrêt",  icon: 'directions_bus', color: '#1a6b3a' },
};

/* ─── Collapsed filter rail ─────────────────────────────────────────────── */

function CollapsedPanel({
  layers, onToggleLayer, onExpand, empCount, siteCount, stopCount,
}: {
  layers: Record<LayerKey, boolean>;
  onToggleLayer: (k: LayerKey) => void;
  onExpand: () => void;
  empCount: number; siteCount: number; stopCount: number;
}) {
  const counts: Record<LayerKey, number> = { employees: empCount, sites: siteCount, stops: stopCount };

  return (
    <div className="w-14 shrink-0 bg-white border-r border-slate-200 flex flex-col items-center py-3 gap-1">
      {/* Expand button */}
      <button
        onClick={onExpand}
        title="Ouvrir les filtres"
        className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors mb-1"
      >
        <span className="material-symbols-outlined text-xl">chevron_right</span>
      </button>

      <div className="w-8 h-px bg-slate-200 mb-1" />

      {/* Layer toggle icons */}
      {(Object.keys(LAYER_META) as LayerKey[]).map((key) => {
        const meta = LAYER_META[key];
        const active = layers[key];
        return (
          <button
            key={key}
            onClick={() => onToggleLayer(key)}
            title={`${meta.label} (${counts[key]})`}
            className={[
              'relative w-9 h-9 flex items-center justify-center rounded-lg transition-colors',
              active ? 'text-white' : 'bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-700',
            ].join(' ')}
            style={active ? { backgroundColor: meta.color } : undefined}
          >
            <span className="material-symbols-outlined text-xl leading-none"
              style={active ? { fontVariationSettings: "'FILL' 1" } : undefined}>
              {meta.icon}
            </span>
            {/* Count badge */}
            <span
              className={[
                'absolute -top-1 -right-1 min-w-[16px] h-4 px-0.5 rounded-full text-[9px] font-bold flex items-center justify-center',
                active ? 'bg-white text-slate-700' : 'bg-slate-300 text-white',
              ].join(' ')}
            >
              {counts[key]}
            </span>
          </button>
        );
      })}
    </div>
  );
}

/* ─── Expanded filter panel ─────────────────────────────────────────────── */

function ExpandedPanel({
  layers, onToggleLayer, onCollapse,
  sites,
  siteFilter, onSiteFilter,
  shiftFilter, onShiftFilter,
  villeFilter, onVilleFilter,
  prestataireFilter, onPrestataireFilter,
  pmrOnly, onPmrOnly,
  activeOnly, onActiveOnly,
  stopActiveOnly, onStopActiveOnly,
  villes, prestataires,
  empCount, siteCount, stopCount,
  visibleSiteIds, siteIds,
}: {
  layers: Record<LayerKey, boolean>;
  onToggleLayer: (k: LayerKey) => void;
  onCollapse: () => void;
  sites: Site[];
  siteFilter: string; onSiteFilter: (v: string) => void;
  shiftFilter: string; onShiftFilter: (v: string) => void;
  villeFilter: string; onVilleFilter: (v: string) => void;
  prestataireFilter: string; onPrestataireFilter: (v: string) => void;
  pmrOnly: boolean; onPmrOnly: (v: boolean) => void;
  activeOnly: boolean; onActiveOnly: (v: boolean) => void;
  stopActiveOnly: boolean; onStopActiveOnly: (v: boolean) => void;
  villes: string[];
  prestataires: string[];
  empCount: number; siteCount: number; stopCount: number;
  visibleSiteIds: string[]; siteIds: string[];
}) {
  const selectCls = 'w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-on-surface text-xs outline-none focus:ring-2 focus:ring-primary/20 appearance-none transition-shadow';
  const checkCls  = 'w-3.5 h-3.5 rounded accent-primary shrink-0';
  const counts: Record<LayerKey, number> = { employees: empCount, sites: siteCount, stops: stopCount };

  /* Legend entries */
  const legendEntries: { label: string; color: string; shape: 'circle' | 'square' }[] = [];
  if (layers.sites) legendEntries.push({ label: 'Site', color: '#495e8a', shape: 'circle' });
  if (layers.employees) {
    for (const id of visibleSiteIds) {
      const site = sites.find((s) => s.id === id);
      if (site) legendEntries.push({ label: `${site.code} — ${site.name}`, color: getSiteColor(id, siteIds), shape: 'circle' });
    }
  }
  if (layers.stops) legendEntries.push({ label: "Point d'Arrêt", color: '#1a6b3a', shape: 'square' });

  return (
    <div className="w-72 shrink-0 bg-white border-r border-slate-200 flex flex-col overflow-hidden">
      {/* Panel header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
        <p className="text-[11px] font-black uppercase tracking-widest text-slate-500">Filtres</p>
        <button
          onClick={onCollapse}
          title="Réduire"
          className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
        >
          <span className="material-symbols-outlined text-lg leading-none">chevron_left</span>
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-5">

        {/* Layer toggles */}
        <div className="flex flex-col gap-1.5">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Couches</p>
          {(Object.keys(LAYER_META) as LayerKey[]).map((key) => {
            const meta = LAYER_META[key];
            const active = layers[key];
            return (
              <button
                key={key}
                onClick={() => onToggleLayer(key)}
                className={[
                  'flex items-center gap-3 w-full rounded-xl px-3 py-2.5 text-xs font-semibold transition-all',
                  active ? 'text-white shadow-sm' : 'bg-slate-50 text-slate-600 hover:bg-slate-100',
                ].join(' ')}
                style={active ? { backgroundColor: meta.color } : undefined}
              >
                <span
                  className="material-symbols-outlined text-base leading-none shrink-0"
                  style={active ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  {meta.icon}
                </span>
                <span className="flex-1 text-left">{meta.label}</span>
                <span className={[
                  'font-mono tabular-nums text-[10px] px-1.5 py-0.5 rounded-full shrink-0',
                  active ? 'bg-white/25 text-white' : 'bg-slate-200 text-slate-500',
                ].join(' ')}>
                  {counts[key]}
                </span>
              </button>
            );
          })}
        </div>

        <div className="h-px bg-slate-100" />

        {/* Shared site filter */}
        {(layers.employees || layers.stops) && (
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Site</label>
            <select value={siteFilter} onChange={(e) => onSiteFilter(e.target.value)} className={selectCls}>
              <option value="">Tous les sites</option>
              {sites.map((s) => (
                <option key={s.id} value={s.id}>{s.code} — {s.name}</option>
              ))}
            </select>
          </div>
        )}

        {/* Employee-specific filters */}
        {layers.employees && (
          <>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Équipe</label>
              <select value={shiftFilter} onChange={(e) => onShiftFilter(e.target.value)} className={selectCls}>
                <option value="">Toutes les équipes</option>
                {['Poste 1','Poste 2','Poste 3','Normal','Sirène'].map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input type="checkbox" className={checkCls} checked={pmrOnly} onChange={(e) => onPmrOnly(e.target.checked)} />
                <span className="text-xs text-slate-600">PMR uniquement</span>
              </label>
              <label className="flex items-center gap-2.5 cursor-pointer select-none">
                <input type="checkbox" className={checkCls} checked={activeOnly} onChange={(e) => onActiveOnly(e.target.checked)} />
                <span className="text-xs text-slate-600">Actifs uniquement</span>
              </label>
            </div>
          </>
        )}

        {/* Stop-specific filters */}
        {layers.stops && (
          <>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Ville</label>
              <select value={villeFilter} onChange={(e) => onVilleFilter(e.target.value)} className={selectCls}>
                <option value="">Toutes les villes</option>
                {villes.map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-wide text-slate-400">Prestataire</label>
              <select value={prestataireFilter} onChange={(e) => onPrestataireFilter(e.target.value)} className={selectCls}>
                <option value="">Tous les prestataires</option>
                {prestataires.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <label className="flex items-center gap-2.5 cursor-pointer select-none">
              <input type="checkbox" className={checkCls} checked={stopActiveOnly} onChange={(e) => onStopActiveOnly(e.target.checked)} />
              <span className="text-xs text-slate-600">Actifs uniquement</span>
            </label>
          </>
        )}

        {/* Legend */}
        {legendEntries.length > 0 && (
          <>
            <div className="h-px bg-slate-100" />
            <div className="flex flex-col gap-2">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Légende</p>
              {legendEntries.map((e, i) => (
                <div key={i} className="flex items-center gap-2.5">
                  <span
                    className="shrink-0"
                    style={{
                      display: 'inline-block',
                      width: e.shape === 'square' ? 10 : 12,
                      height: e.shape === 'square' ? 10 : 12,
                      borderRadius: e.shape === 'square' ? 2 : '50%',
                      backgroundColor: e.color,
                    }}
                  />
                  <span className="text-[11px] text-slate-500 truncate">{e.label}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ─── Page ───────────────────────────────────────────────────────────────── */

const KHOURIBGA: [number, number] = [32.88, -6.91];

export function UnifiedMapPage() {
  const [searchParams] = useSearchParams();
  const initialLayer = (searchParams.get('layer') as LayerKey | null) ?? 'employees';

  const { employees, isLoading: empLoading, fetchEmployees } = useEmployeeStore();
  const { sites, isLoading: sitesLoading, fetchSites } = useSiteStore();
  const [stops, setStops] = useState<PointArret[]>([]);
  const [stopsLoading, setStopsLoading] = useState(false);

  const [panelExpanded, setPanelExpanded] = useState(true);

  const [layers, setLayers] = useState<Record<LayerKey, boolean>>({
    employees: initialLayer === 'employees',
    sites:     initialLayer === 'sites',
    stops:     initialLayer === 'stops',
  });

  const [siteFilter, setSiteFilter]               = useState('');
  const [shiftFilter, setShiftFilter]             = useState('');
  const [villeFilter, setVilleFilter]             = useState('');
  const [prestataireFilter, setPrestataireFilter] = useState('');
  const [pmrOnly, setPmrOnly]                     = useState(false);
  const [activeOnly, setActiveOnly]               = useState(true);
  const [stopActiveOnly, setStopActiveOnly]       = useState(true);

  useEffect(() => {
    fetchEmployees({ page: 1, page_size: 500 });
    fetchSites({ page: 1, page_size: 100 });
    setStopsLoading(true);
    listPointsArret({ page_size: 200 })
      .then((res) => setStops(res.items))
      .finally(() => setStopsLoading(false));
  }, [fetchEmployees, fetchSites]);

  const toggleLayer = useCallback((k: LayerKey) => {
    setLayers((prev) => ({ ...prev, [k]: !prev[k] }));
  }, []);

  const siteIds = useMemo(() => sites.map((s) => s.id), [sites]);

  const filteredEmployees = useMemo((): Employee[] => {
    if (!layers.employees) return [];
    let r = employees.filter((e) => e.lat !== null && e.lng !== null);
    if (siteFilter)  r = r.filter((e) => e.site_id === siteFilter);
    if (shiftFilter) r = r.filter((e) => e.shift_time === shiftFilter);
    if (pmrOnly)     r = r.filter((e) => e.is_pmr);
    if (activeOnly)  r = r.filter((e) => e.active);
    return r;
  }, [employees, layers.employees, siteFilter, shiftFilter, pmrOnly, activeOnly]);

  const filteredSites = useMemo((): Site[] => {
    if (!layers.sites) return [];
    return sites.filter((s) => s.lat && s.lng);
  }, [sites, layers.sites]);

  const filteredStops = useMemo((): PointArret[] => {
    if (!layers.stops) return [];
    let r = stops;
    if (siteFilter)        r = r.filter((s) => s.site_id === siteFilter);
    if (villeFilter)       r = r.filter((s) => s.ville === villeFilter);
    if (prestataireFilter) r = r.filter((s) => s.prestataire === prestataireFilter);
    if (stopActiveOnly)    r = r.filter((s) => s.is_active);
    return r;
  }, [stops, layers.stops, siteFilter, villeFilter, prestataireFilter, stopActiveOnly]);

  const villes       = useMemo(() => [...new Set(stops.map((s) => s.ville).filter(Boolean) as string[])].sort(), [stops]);
  const prestataires = useMemo(() => [...new Set(stops.map((s) => s.prestataire).filter(Boolean) as string[])].sort(), [stops]);

  const visibleSiteIds = useMemo(() => {
    const ids = new Set(filteredEmployees.map((e) => e.site_id));
    return siteIds.filter((id) => ids.has(id));
  }, [filteredEmployees, siteIds]);

  const isLoading = empLoading || sitesLoading || stopsLoading;

  const mapHeight = 'calc(100vh - 9rem)';

  if (isLoading && employees.length === 0 && sites.length === 0 && stops.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rectangular" className="w-full" height={mapHeight} />
      </div>
    );
  }

  const sharedFilterProps = {
    layers, onToggleLayer: toggleLayer,
    sites,
    siteFilter, onSiteFilter: setSiteFilter,
    shiftFilter, onShiftFilter: setShiftFilter,
    villeFilter, onVilleFilter: setVilleFilter,
    prestataireFilter, onPrestataireFilter: setPrestataireFilter,
    pmrOnly, onPmrOnly: setPmrOnly,
    activeOnly, onActiveOnly: setActiveOnly,
    stopActiveOnly, onStopActiveOnly: setStopActiveOnly,
    villes, prestataires,
    empCount: filteredEmployees.length,
    siteCount: filteredSites.length,
    stopCount: filteredStops.length,
    visibleSiteIds, siteIds,
  };

  return (
    <div className="flex flex-col" style={{ height: mapHeight }}>
      {/* Header — outside the flex row */}
      <div className="flex items-center justify-between mb-3 shrink-0">
        <div>
          <h1 className="font-sans text-2xl font-black text-on-surface tracking-tight flex items-center gap-2">
            <span
              className="material-symbols-outlined text-primary text-2xl"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              map
            </span>
            Carte
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Vue géographique — employés, sites & points d'arrêt
          </p>
        </div>
        <div className="flex items-center gap-2">
          {layers.employees && (
            <span className="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-medium">
              {filteredEmployees.length} employé(s)
            </span>
          )}
          {layers.sites && (
            <span className="bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full text-xs font-medium">
              {filteredSites.length} site(s)
            </span>
          )}
          {layers.stops && (
            <span className="bg-green-50 text-green-700 px-2.5 py-1 rounded-full text-xs font-medium">
              {filteredStops.length} arrêt(s)
            </span>
          )}
        </div>
      </div>

      {/* Body — filter panel + map side by side */}
      <div className="flex flex-1 rounded-xl overflow-hidden border border-slate-200 shadow-sm min-h-0">
        {/* Filter panel */}
        {panelExpanded ? (
          <ExpandedPanel {...sharedFilterProps} onCollapse={() => setPanelExpanded(false)} />
        ) : (
          <CollapsedPanel
            layers={layers}
            onToggleLayer={toggleLayer}
            onExpand={() => setPanelExpanded(true)}
            empCount={filteredEmployees.length}
            siteCount={filteredSites.length}
            stopCount={filteredStops.length}
          />
        )}

        {/* Map — takes remaining width, no overlays */}
        <div className="flex-1 min-w-0">
          <MapView center={KHOURIBGA} zoom={12} height="100%">
            {filteredEmployees.map((emp) => (
              <EmployeeMarker
                key={emp.id}
                employee={emp}
                color={getSiteColor(emp.site_id, siteIds)}
              />
            ))}
            {filteredSites.map((site) => (
              <SiteMarker key={site.id} site={site} />
            ))}
            {filteredStops.map((stop) => (
              <StopMarker key={stop.id} stop={stop} />
            ))}
          </MapView>
        </div>
      </div>
    </div>
  );
}
