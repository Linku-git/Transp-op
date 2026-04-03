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

/* ─── Filter panel ──────────────────────────────────────────────────────── */

function FilterPanel({
  layers, onToggleLayer,
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
}: {
  layers: Record<LayerKey, boolean>;
  onToggleLayer: (k: LayerKey) => void;
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
}) {
  const selectCls = 'w-full bg-white/60 border border-white/40 rounded-lg p-2 text-on-surface font-sans text-xs outline-none focus:ring-2 focus:ring-primary/30 appearance-none';
  const checkCls = 'w-3.5 h-3.5 rounded accent-primary';

  const layerBtn = (key: LayerKey, label: string, count: number, color: string) => (
    <button
      key={key}
      onClick={() => onToggleLayer(key)}
      className={[
        'flex items-center gap-2 w-full rounded-lg px-3 py-2 text-xs font-medium transition-all',
        layers[key]
          ? 'text-white shadow-sm'
          : 'bg-white/30 text-on-surface-variant hover:bg-white/50',
      ].join(' ')}
      style={layers[key] ? { backgroundColor: color } : undefined}
    >
      <span className="flex-1 text-left">{label}</span>
      <span className={['font-mono tabular-nums text-[10px] px-1.5 py-0.5 rounded-full', layers[key] ? 'bg-white/20 text-white' : 'bg-surface-container text-on-surface-variant'].join(' ')}>
        {count}
      </span>
    </button>
  );

  return (
    <div className="absolute top-4 left-4 z-[1000] bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/30 p-4 w-64 flex flex-col gap-4">
      <p className="font-sans text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
        Couches
      </p>

      <div className="flex flex-col gap-1.5">
        {layerBtn('employees', 'Employés', empCount, '#0058be')}
        {layerBtn('sites',     'Sites',    siteCount, '#495e8a')}
        {layerBtn('stops',     "Points d'Arrêt", stopCount, '#1a6b3a')}
      </div>

      <div className="h-px bg-surface-container-high" />

      {/* Shared site filter (for employees + stops) */}
      {(layers.employees || layers.stops) && (
        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-semibold uppercase tracking-wide text-on-surface-variant">Site</label>
          <select value={siteFilter} onChange={(e) => onSiteFilter(e.target.value)} className={selectCls}>
            <option value="">Tous les sites</option>
            {sites.map((s) => (
              <option key={s.id} value={s.id}>{s.code} — {s.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Employees-specific filters */}
      {layers.employees && (
        <>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-semibold uppercase tracking-wide text-on-surface-variant">Équipe</label>
            <select value={shiftFilter} onChange={(e) => onShiftFilter(e.target.value)} className={selectCls}>
              <option value="">Toutes les équipes</option>
              {['Poste 1','Poste 2','Poste 3','Normal','Sirène'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" className={checkCls} checked={pmrOnly} onChange={(e) => onPmrOnly(e.target.checked)} />
              <span className="text-xs text-on-surface-variant">PMR uniquement</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" className={checkCls} checked={activeOnly} onChange={(e) => onActiveOnly(e.target.checked)} />
              <span className="text-xs text-on-surface-variant">Actifs uniquement</span>
            </label>
          </div>
        </>
      )}

      {/* Points d'arrêt filters */}
      {layers.stops && (
        <>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-semibold uppercase tracking-wide text-on-surface-variant">Ville</label>
            <select value={villeFilter} onChange={(e) => onVilleFilter(e.target.value)} className={selectCls}>
              <option value="">Toutes les villes</option>
              {villes.map((v) => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] font-semibold uppercase tracking-wide text-on-surface-variant">Prestataire</label>
            <select value={prestataireFilter} onChange={(e) => onPrestataireFilter(e.target.value)} className={selectCls}>
              <option value="">Tous les prestataires</option>
              {prestataires.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" className={checkCls} checked={stopActiveOnly} onChange={(e) => onStopActiveOnly(e.target.checked)} />
            <span className="text-xs text-on-surface-variant">Actifs uniquement</span>
          </label>
        </>
      )}
    </div>
  );
}

/* ─── Legend ─────────────────────────────────────────────────────────────── */

function Legend({
  layers, sites, siteIds,
}: {
  layers: Record<LayerKey, boolean>;
  sites: Site[];
  siteIds: string[];
}) {
  const entries: { label: string; color: string; shape: 'circle' | 'square' }[] = [];

  if (layers.sites) {
    entries.push({ label: 'Site', color: '#495e8a', shape: 'circle' });
  }
  if (layers.employees) {
    const uniqueSites = sites.filter((s) => siteIds.includes(s.id));
    for (const s of uniqueSites) {
      entries.push({ label: `${s.code} — ${s.name}`, color: getSiteColor(s.id, siteIds), shape: 'circle' });
    }
  }
  if (layers.stops) {
    entries.push({ label: "Point d'Arrêt", color: '#1a6b3a', shape: 'square' });
  }

  if (entries.length === 0) return null;

  return (
    <div className="absolute bottom-4 left-4 z-[1000] bg-white/90 backdrop-blur-xl rounded-xl shadow-lg border border-white/30 p-4 max-w-[220px]">
      <p className="font-sans text-[10px] font-black uppercase tracking-widest text-on-surface-variant mb-2">
        Légende
      </p>
      <div className="flex flex-col gap-1.5">
        {entries.map((e, i) => (
          <div key={i} className="flex items-center gap-2">
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
            <span className="text-[11px] text-on-surface-variant font-sans truncate">{e.label}</span>
          </div>
        ))}
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

  /* Unique site IDs for stable color mapping */
  const siteIds = useMemo(() => sites.map((s) => s.id), [sites]);

  /* Filtered data */
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
    if (siteFilter)          r = r.filter((s) => s.site_id === siteFilter);
    if (villeFilter)         r = r.filter((s) => s.ville === villeFilter);
    if (prestataireFilter)   r = r.filter((s) => s.prestataire === prestataireFilter);
    if (stopActiveOnly)      r = r.filter((s) => s.is_active);
    return r;
  }, [stops, layers.stops, siteFilter, villeFilter, prestataireFilter, stopActiveOnly]);

  /* Derived filter options */
  const villes       = useMemo(() => [...new Set(stops.map((s) => s.ville).filter(Boolean) as string[])].sort(), [stops]);
  const prestataires = useMemo(() => [...new Set(stops.map((s) => s.prestataire).filter(Boolean) as string[])].sort(), [stops]);

  /* Visible site IDs for legend */
  const visibleSiteIds = useMemo(() => {
    const ids = new Set(filteredEmployees.map((e) => e.site_id));
    return siteIds.filter((id) => ids.has(id));
  }, [filteredEmployees, siteIds]);

  const isLoading = empLoading || sitesLoading || stopsLoading;

  if (isLoading && employees.length === 0 && sites.length === 0 && stops.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton variant="text" className="w-48 h-8" />
        <Skeleton variant="rectangular" className="w-full" height="calc(100vh - 8rem)" />
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-sans text-3xl font-black text-on-surface tracking-tight flex items-center gap-3">
            <span className="material-symbols-outlined text-primary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              map
            </span>
            Carte
          </h1>
          <p className="text-sm text-on-surface-variant mt-0.5">
            Vue géographique — employés, sites & points d'arrêt
          </p>
        </div>
        <div className="flex items-center gap-3 text-sm text-on-surface-variant">
          {layers.employees && (
            <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">
              {filteredEmployees.length} employé(s)
            </span>
          )}
          {layers.sites && (
            <span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-medium">
              {filteredSites.length} site(s)
            </span>
          )}
          {layers.stops && (
            <span className="bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
              {filteredStops.length} arrêt(s)
            </span>
          )}
        </div>
      </div>

      {/* Map + overlays */}
      <div className="relative">
        <MapView
          center={KHOURIBGA}
          zoom={12}
          height="calc(100vh - 9rem)"
        >
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

        <FilterPanel
          layers={layers}
          onToggleLayer={toggleLayer}
          sites={sites}
          siteFilter={siteFilter} onSiteFilter={setSiteFilter}
          shiftFilter={shiftFilter} onShiftFilter={setShiftFilter}
          villeFilter={villeFilter} onVilleFilter={setVilleFilter}
          prestataireFilter={prestataireFilter} onPrestataireFilter={setPrestataireFilter}
          pmrOnly={pmrOnly} onPmrOnly={setPmrOnly}
          activeOnly={activeOnly} onActiveOnly={setActiveOnly}
          stopActiveOnly={stopActiveOnly} onStopActiveOnly={setStopActiveOnly}
          villes={villes}
          prestataires={prestataires}
          empCount={filteredEmployees.length}
          siteCount={filteredSites.length}
          stopCount={filteredStops.length}
        />

        <Legend
          layers={layers}
          sites={sites}
          siteIds={visibleSiteIds}
        />
      </div>
    </div>
  );
}
