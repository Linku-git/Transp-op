import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { AdvancedMarker, InfoWindow, Polyline, useMapsLibrary } from '@vis.gl/react-google-maps';
import { MapView } from '@/components/maps/MapView';

/* ── KML helpers ──────────────────────────────────────────────────────────── */
function buildKml(tripId: string, path: google.maps.LatLngLiteral[], label?: string): string {
  const coords = path.map((p) => `${p.lng},${p.lat},0`).join('\n                ');
  return `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Trip ${tripId}</name>
    <description>${label ?? tripId}</description>
    <Style id="route">
      <LineStyle><color>ffFF6600</color><width>4</width></LineStyle>
    </Style>
    <Placemark>
      <name>${label ?? 'Route'}</name>
      <styleUrl>#route</styleUrl>
      <LineString>
        <tessellate>1</tessellate>
        <coordinates>
                ${coords}
        </coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>`;
}

function downloadKml(tripId: string, path: google.maps.LatLngLiteral[], label?: string) {
  const blob = new Blob([buildKml(tripId, path, label)], { type: 'application/vnd.google-earth.kml+xml' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `trip_${tripId.slice(0, 8)}.kml`;
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ── Route cache (localStorage) ─────────────────────────────────────────── */
function setCachedRoute(tripId: string, path: google.maps.LatLngLiteral[]) {
  try { localStorage.setItem(`route_${tripId}`, JSON.stringify({ path, ts: Date.now() })); } catch { /* storage full */ }
}

/* ── RouteSnapper: manual-trigger, chunked waypoints, error reporting ────── */
const MAX_WPS_PER_LEG = 8;

interface RouteSnapperProps {
  tripId: string | null;
  origin: google.maps.LatLngLiteral | null;
  destination: google.maps.LatLngLiteral | null;
  waypoints: google.maps.LatLngLiteral[];
  trigger: number;
  onRouteReady: (path: google.maps.LatLngLiteral[]) => void;
  onLoading: (v: boolean) => void;
  onSnapError: (msg: string | null) => void;
}

function RouteSnapper({ tripId, origin, destination, waypoints, trigger, onRouteReady, onLoading, onSnapError }: RouteSnapperProps) {
  const routesLib = useMapsLibrary('routes');
  const lastTriggerRef = useRef(0);
  const runningRef = useRef(false);

  useEffect(() => {
    if (!routesLib || !tripId || !origin || !destination || trigger === 0) return;
    if (lastTriggerRef.current === trigger) return;
    if (runningRef.current) return;
    lastTriggerRef.current = trigger;
    runningRef.current = true;
    onLoading(true);
    onSnapError(null);

    // Build route segments (chunk waypoints, max MAX_WPS_PER_LEG per DirectionsService call)
    type Pt = google.maps.LatLngLiteral;
    const allWps = waypoints;
    const segments: { orig: Pt; dest: Pt; wps: Pt[] }[] = [];

    if (allWps.length <= MAX_WPS_PER_LEG) {
      segments.push({ orig: origin, dest: destination, wps: allWps });
    } else {
      // Build multi-leg: split waypoints into chunks, each leg is consecutive stops
      const allPoints: Pt[] = [origin, ...allWps, destination];
      for (let i = 0; i < allPoints.length - 1; i += MAX_WPS_PER_LEG) {
        const slice = allPoints.slice(i, i + MAX_WPS_PER_LEG + 1);
        segments.push({ orig: slice[0], dest: slice[slice.length - 1], wps: slice.slice(1, -1) });
      }
    }

    const svc = new routesLib.DirectionsService();
    let fullPath: Pt[] = [];
    let segIdx = 0;

    function runSeg() {
      if (segIdx >= segments.length) {
        setCachedRoute(tripId!, fullPath);
        onRouteReady(fullPath);
        onLoading(false);
        runningRef.current = false;
        return;
      }
      const { orig, dest, wps } = segments[segIdx++];
      svc.route(
        {
          origin: orig,
          destination: dest,
          waypoints: wps.map((wp) => ({ location: wp, stopover: true })),
          travelMode: routesLib!.TravelMode.DRIVING,
          optimizeWaypoints: false,
        },
        (result, status) => {
          if (status === 'OK' && result?.routes[0]) {
            const path = result.routes[0].overview_path.map((pt) => ({ lat: pt.lat(), lng: pt.lng() }));
            fullPath = [...fullPath, ...path];
            runSeg();
          } else {
            const msg = status === 'REQUEST_DENIED'
              ? 'Directions API non autorisée — vérifiez la clé Google Maps'
              : status === 'ZERO_RESULTS'
              ? 'Aucun itinéraire routier trouvé pour ce trajet'
              : `Erreur API: ${status}`;
            onSnapError(msg);
            onLoading(false);
            runningRef.current = false;
          }
        }
      );
    }
    runSeg();
  }, [routesLib, tripId, trigger]);

  return null;
}
import { listConfigurationPlans } from '@/api/vehicles';
import {
  getPlanTrips, getTripDetail,
  type TripItem, type TripDetail,
} from '@/api/transportOptimization';
import type { ConfigurationPlan } from '@/types/vehicle';

/* ── constants ────────────────────────────────────────────────────────────── */
const VEHICLE_COLOR: Record<string, string> = {
  AUTOCAR: 'bg-sky-100 text-sky-700',
  MINIBUS: 'bg-indigo-100 text-indigo-700',
  MINICAR: 'bg-pink-100 text-pink-700',
};
const SHIFT_COLOR: Record<string, string> = {
  P1: 'bg-blue-100 text-blue-700',
  P2: 'bg-amber-100 text-amber-700',
  P3: 'bg-green-100 text-green-700',
  N:  'bg-slate-100 text-slate-600',
  S:  'bg-purple-100 text-purple-700',
};
const KHOURIBGA: [number, number] = [32.886, -6.907];

function fillColor(pct: number): string {
  if (pct >= 70) return '#10b981';
  if (pct >= 50) return '#f59e0b';
  return '#ef4444';
}

function Badge({ text, cls }: { text: string; cls?: string }) {
  return (
    <span className={['inline-block rounded-full px-2 py-0.5 text-[10px] font-bold whitespace-nowrap', cls ?? 'bg-slate-100 text-slate-600'].join(' ')}>
      {text}
    </span>
  );
}

/* ── Capacity gauge ────────────────────────────────────────────────────────── */
function CapacityGauge({ fill_pct, capacity, passengers }: { fill_pct: number; capacity: number; passengers: number }) {
  const color = fillColor(fill_pct);
  const seats = Array.from({ length: Math.min(capacity, 60) }, (_, i) => i < passengers);
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400">Capacité véhicule</span>
        <span className="font-bold" style={{ color }}>{fill_pct}% rempli</span>
      </div>
      <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, fill_pct)}%`, backgroundColor: color }} />
      </div>
      <div className="flex flex-wrap gap-0.5">
        {seats.map((filled, i) => (
          <span key={i} className={['w-3 h-3 rounded-sm', filled ? 'opacity-100' : 'opacity-20'].join(' ')} style={{ backgroundColor: filled ? color : '#e2e8f0' }} />
        ))}
      </div>
      <p className="text-[10px] text-slate-400">{passengers} passagers estimés sur {capacity} places</p>
    </div>
  );
}

/* ── Stop badge on map ────────────────────────────────────────────────────── */
function StopPin({ index, label, type }: { index: number; label: string; type: 'start' | 'end' | 'stop' }) {
  const bg = type === 'start' ? '#10b981' : type === 'end' ? '#ef4444' : '#3b82f6';
  return (
    <div className="flex flex-col items-center" title={label}>
      <div
        className="w-7 h-7 rounded-full border-2 border-white shadow-md flex items-center justify-center text-white text-[10px] font-black"
        style={{ backgroundColor: bg }}
      >
        {type === 'start' ? '▶' : type === 'end' ? '⬛' : index}
      </div>
      <div className="w-0 h-0" style={{ borderLeft: '4px solid transparent', borderRight: '4px solid transparent', borderTop: `6px solid ${bg}` }} />
    </div>
  );
}

/* ── Main Component ───────────────────────────────────────────────────────── */
export function RouteViewerSection() {
  const [plans, setPlans] = useState<ConfigurationPlan[]>([]);
  const [planId, setPlanId] = useState('');
  const [trips, setTrips] = useState<TripItem[]>([]);
  const [total, setTotal] = useState(0);
  const [tripsLoading, setTripsLoading] = useState(false);
  const [selectedTrip, setSelectedTrip] = useState<TripItem | null>(null);
  const [detail, setDetail] = useState<TripDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [openInfoId, setOpenInfoId] = useState<string | null>(null);
  const [roadPath, setRoadPath] = useState<google.maps.LatLngLiteral[]>([]);
  const [dirLoading, setDirLoading] = useState(false);
  const [snapTrigger, setSnapTrigger] = useState(0);
  const [snapError, setSnapError] = useState<string | null>(null);

  // Filters
  const [shift, setShift] = useState('');
  const [ar, setAr] = useState('');
  const [secteur, setSecteur] = useState('');
  const [prestataire, setPrestataire] = useState('');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 40;

  const totalPages = Math.ceil(total / PAGE_SIZE);

  // Load plans
  useEffect(() => {
    listConfigurationPlans({ page_size: 50 }).then((r) => {
      const items = r.items ?? [];
      setPlans(items);
      const current = items.find((p) => p.is_current) ?? items[0];
      if (current) setPlanId(current.id);
    });
  }, []);

  // Load trips
  const loadTrips = useCallback(async () => {
    if (!planId) return;
    setTripsLoading(true);
    try {
      const filters: Record<string, unknown> = { page, page_size: PAGE_SIZE };
      if (shift) filters.shift = shift;
      if (ar) filters.aller_retour = ar;
      if (secteur) filters.secteur = secteur;
      if (prestataire) filters.prestataire = prestataire;
      const r = await getPlanTrips(planId, filters);
      setTrips(r.trips);
      setTotal(r.total);
    } finally {
      setTripsLoading(false);
    }
  }, [planId, page, shift, ar, secteur, prestataire]);

  useEffect(() => { loadTrips(); }, [loadTrips]);

  // Load trip detail
  const loadDetail = useCallback(async (trip: TripItem) => {
    setSelectedTrip(trip);
    setDetailLoading(true);
    setDetail(null);
    setRoadPath([]);
    setDirLoading(false);
    setSnapTrigger(0);
    setSnapError(null);
    try {
      setDetail(await getTripDetail(trip.id));
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const handleCalculateRoute = useCallback(() => {
    if (!detail) return;
    setRoadPath([]);
    setSnapError(null);
    if (selectedTrip?.id) localStorage.removeItem(`route_${selectedTrip.id}`);
    setSnapTrigger((t) => t + 1);
  }, [detail, selectedTrip]);

  const resetPage = () => setPage(1);

  // Map polyline coords
  const polylineCoords = useMemo(() => {
    if (!detail) return [];
    const pts: { lat: number; lng: number }[] = [];
    if (detail.start_point?.lat && detail.start_point.lng) pts.push({ lat: detail.start_point.lat, lng: detail.start_point.lng });
    for (const wp of detail.waypoints) {
      if (wp.lat && wp.lng) pts.push({ lat: wp.lat, lng: wp.lng });
    }
    if (detail.end_point?.lat && detail.end_point.lng) pts.push({ lat: detail.end_point.lat, lng: detail.end_point.lng });
    return pts;
  }, [detail]);

  const mapCenter = useMemo((): [number, number] => {
    if (polylineCoords.length > 0) return [polylineCoords[0].lat, polylineCoords[0].lng];
    return KHOURIBGA;
  }, [polylineCoords]);

  const mapZoom = polylineCoords.length >= 2 ? 11 : 10;

  // Derived snap inputs
  const snapOrigin = useMemo(() => {
    if (!detail) return null;
    if (detail.start_point?.lat && detail.start_point.lng)
      return { lat: detail.start_point.lat, lng: detail.start_point.lng };
    const first = detail.waypoints.find((wp) => wp.lat && wp.lng);
    return first ? { lat: first.lat!, lng: first.lng! } : null;
  }, [detail]);
  const snapDest = useMemo(() => {
    if (!detail) return null;
    if (detail.end_point?.lat && detail.end_point.lng)
      return { lat: detail.end_point.lat, lng: detail.end_point.lng };
    const wps = detail.waypoints.filter((wp) => wp.lat && wp.lng);
    if (wps.length > 0) return { lat: wps[wps.length - 1].lat!, lng: wps[wps.length - 1].lng! };
    return null;
  }, [detail]);
  const snapWaypoints = useMemo(() =>
    detail?.waypoints.filter((wp) => wp.lat && wp.lng).map((wp) => ({ lat: wp.lat!, lng: wp.lng! })) ?? [],
    [detail]);

  // The path to draw — road-snapped when available, else straight-line fallback
  const activePath = roadPath.length >= 2 ? roadPath : polylineCoords;

  const handleRouteReady = useCallback((path: google.maps.LatLngLiteral[]) => { setRoadPath(path); }, []);
  const handleDirLoading = useCallback((v: boolean) => { setDirLoading(v); }, []);

  const selectCls = 'bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 appearance-none';

  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 256px)' }}>
      {/* ── Toolbar ─────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 bg-white border border-slate-100 rounded-xl px-3 py-2 mb-3 shrink-0">
        <select value={planId} onChange={(e) => { setPlanId(e.target.value); resetPage(); setSelectedTrip(null); setDetail(null); }}
          className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-sm text-slate-700 appearance-none min-w-[180px]">
          {plans.map((p) => <option key={p.id} value={p.id}>{p.name}{p.is_current ? ' ✓' : ''}</option>)}
        </select>
        <div className="w-px h-4 bg-slate-200" />
        <select value={shift} onChange={(e) => { setShift(e.target.value); resetPage(); }} className={selectCls}>
          <option value="">Tous shifts</option>
          {['P1','P2','P3','N','S'].map((s) => <option key={s}>Shift {s}</option>)}
        </select>
        <select value={ar} onChange={(e) => { setAr(e.target.value); resetPage(); }} className={selectCls}>
          <option value="">A/R</option>
          <option value="ALLER">Aller</option>
          <option value="RETOUR">Retour</option>
        </select>
        <select value={secteur} onChange={(e) => { setSecteur(e.target.value); resetPage(); }} className={selectCls}>
          <option value="">Tous secteurs</option>
          {['KHOURIBGA','OUEDZEM','BOULANOIR','BOUJNIBA','HATTANE','FQUIH BEN SALEH'].map((s) => <option key={s}>{s}</option>)}
        </select>
        <select value={prestataire} onChange={(e) => { setPrestataire(e.target.value); resetPage(); }} className={selectCls}>
          <option value="">Tous prestataires</option>
          {['STCR','S.TOURISME','MANAVETTE','CTM','SOTREG'].map((p) => <option key={p}>{p}</option>)}
        </select>
        {(shift || ar || secteur || prestataire) && (
          <button onClick={() => { setShift(''); setAr(''); setSecteur(''); setPrestataire(''); resetPage(); }}
            className="text-xs text-slate-400 hover:text-slate-700 flex items-center gap-1">
            <span className="material-symbols-outlined text-sm">close</span>Effacer
          </button>
        )}
        <span className="ml-auto text-xs text-slate-400">
          {tripsLoading ? 'Chargement…' : `${total} trajets`}
        </span>
      </div>

      {/* ── Main two-panel layout — fills all remaining height ──────── */}
      <div className="flex gap-3 flex-1 min-h-0">

        {/* ── Left: trip list ──────────────────────────────────────── */}
        <div className="w-72 shrink-0 flex flex-col bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="px-4 py-2 bg-slate-50 border-b border-slate-100 flex items-center justify-between shrink-0">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Trajets</p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
                className="px-1.5 py-0.5 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30 text-xs">‹</button>
              <span className="text-[10px] text-slate-400">{page}/{totalPages || 1}</span>
              <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}
                className="px-1.5 py-0.5 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30 text-xs">›</button>
            </div>
          </div>
          <div className="overflow-y-auto flex-1">
            {tripsLoading && (
              <div className="flex items-center justify-center h-24 text-slate-400 text-xs">
                <span className="material-symbols-outlined text-2xl animate-spin mr-2">progress_activity</span>Chargement…
              </div>
            )}
            {!tripsLoading && trips.length === 0 && (
              <p className="text-center py-8 text-xs text-slate-400">Aucun trajet</p>
            )}
            {trips.map((trip) => (
              <button
                key={trip.id}
                onClick={() => loadDetail(trip)}
                className={[
                  'w-full text-left px-3 py-2.5 border-b border-slate-50 hover:bg-blue-50/50 transition-colors',
                  selectedTrip?.id === trip.id ? 'bg-blue-50 border-l-2 border-l-blue-500' : '',
                ].join(' ')}
              >
                <div className="flex items-center gap-1.5 mb-0.5 flex-wrap">
                  <span className="text-xs font-black text-slate-700">{trip.poste}</span>
                  {trip.shift && <Badge text={trip.shift} cls={SHIFT_COLOR[trip.shift] ?? 'bg-slate-100 text-slate-600'} />}
                  {trip.aller_retour && (
                    <Badge text={trip.aller_retour === 'ALLER' ? '→' : '←'}
                      cls={trip.aller_retour === 'ALLER' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'} />
                  )}
                  {trip.type_vehicule && (
                    <Badge text={trip.type_vehicule} cls={VEHICLE_COLOR[trip.type_vehicule] ?? 'bg-slate-100 text-slate-600'} />
                  )}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-400">
                  <span className="material-symbols-outlined text-[11px]">schedule</span>
                  {trip.heure_depart ?? '?'} → {trip.heure_arrivee ?? '?'}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-400">
                  <span className="truncate max-w-[110px]">{trip.point_depart}</span>
                  <span>→</span>
                  <span className="truncate max-w-[110px]">{trip.point_arrivee}</span>
                </div>
                <div className="mt-1 h-1 rounded-full bg-slate-100 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${Math.min(100, trip.fill_pct)}%`, backgroundColor: fillColor(trip.fill_pct) }} />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ── Right: map area ──────────────────────────────────────── */}
        <div className="flex-1 flex flex-col min-h-0 gap-2">

          {!selectedTrip ? (
            <div className="flex-1 bg-slate-50 rounded-xl border border-slate-200 border-dashed flex flex-col items-center justify-center gap-3 text-center p-8">
              <span className="material-symbols-outlined text-5xl text-slate-300">route</span>
              <p className="text-sm font-semibold text-slate-400">Sélectionnez un trajet pour voir la route sur la carte</p>
              <p className="text-xs text-slate-300">Les arrêts, l'itinéraire et les informations du véhicule s'afficheront ici</p>
            </div>
          ) : (
            <>
              {/* Compact trip header bar */}
              <div className="bg-white border border-slate-100 rounded-xl px-4 py-2 flex items-center gap-3 shrink-0 flex-wrap">
                <div className="flex items-center gap-2 flex-wrap flex-1 min-w-0">
                  <span className="text-sm font-black text-slate-800">Poste {selectedTrip.poste}</span>
                  {selectedTrip.shift && <Badge text={`Shift ${selectedTrip.shift}`} cls={SHIFT_COLOR[selectedTrip.shift] ?? ''} />}
                  {selectedTrip.aller_retour && (
                    <Badge text={selectedTrip.aller_retour} cls={selectedTrip.aller_retour === 'ALLER' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'} />
                  )}
                  {selectedTrip.type_vehicule && <Badge text={selectedTrip.type_vehicule} cls={VEHICLE_COLOR[selectedTrip.type_vehicule] ?? ''} />}
                  <span className="text-[11px] text-slate-400">{selectedTrip.conducteur || '—'} · {selectedTrip.prestataire}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0 text-xs text-slate-500">
                  <span><span className="text-slate-400">Départ</span> <strong>{selectedTrip.heure_depart ?? '—'}</strong></span>
                  <span><span className="text-slate-400">Arrivée</span> <strong>{selectedTrip.heure_arrivee ?? '—'}</strong></span>
                  <span><span className="text-slate-400">Dist.</span> <strong>{selectedTrip.km != null ? `${selectedTrip.km} km` : '—'}</strong></span>
                  <span><span className="text-slate-400">Rot.</span> <strong>{selectedTrip.rot ?? '—'}</strong></span>
                  <span><strong style={{ color: fillColor(selectedTrip.fill_pct) }}>{selectedTrip.fill_pct}%</strong> <span className="text-slate-400">rempli</span></span>

                  {/* Snap status */}
                  {dirLoading && (
                    <span className="flex items-center gap-1 text-blue-500 text-[10px] font-medium animate-pulse">
                      <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>Calcul itinéraire…
                    </span>
                  )}
                  {!dirLoading && roadPath.length >= 2 && (
                    <span className="flex items-center gap-1 text-emerald-600 text-[10px] font-bold bg-emerald-50 rounded-full px-2 py-0.5">
                      <span className="material-symbols-outlined text-sm">alt_route</span>Itinéraire GPS actif
                    </span>
                  )}

                  {/* Calculer l'itinéraire button */}
                  {!detailLoading && detail && snapOrigin && snapDest && (
                    <button
                      onClick={handleCalculateRoute}
                      disabled={dirLoading}
                      className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg px-3 py-1.5 text-[11px] font-bold transition-colors shadow-sm"
                      title="Calculer l'itinéraire en suivant les routes réelles (Google Maps Directions)"
                    >
                      <span className="material-symbols-outlined text-sm">navigation</span>
                      Calculer l'itinéraire
                    </button>
                  )}

                  {activePath.length >= 2 && (
                    <button
                      onClick={() => downloadKml(selectedTrip!.id, activePath, `Poste ${selectedTrip!.poste} – Shift ${selectedTrip!.shift}`)}
                      className="flex items-center gap-1 text-blue-500 hover:text-blue-700 font-medium text-xs"
                      title="Télécharger KML"
                    >
                      <span className="material-symbols-outlined text-sm">download</span>KML
                    </button>
                  )}
                  {detail?.google_maps_url && (
                    <a href={detail.google_maps_url} target="_blank" rel="noreferrer"
                      className="flex items-center gap-1 text-blue-500 hover:text-blue-700 font-medium text-xs">
                      <span className="material-symbols-outlined text-sm">open_in_new</span>Maps
                    </a>
                  )}
                </div>
              </div>

              {/* Snap error banner */}
              {snapError && (
                <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 text-xs text-amber-800 shrink-0">
                  <span className="material-symbols-outlined text-base text-amber-500">warning</span>
                  <span>{snapError}</span>
                  <span className="ml-1 text-amber-500">— L'itinéraire en ligne droite est affiché à la place.</span>
                </div>
              )}

              {/* Map + side panel — fills remaining height */}
              <div className="flex-1 flex gap-2 min-h-0">

                {/* Map — fills all height */}
                <div className="relative flex-1 min-h-0">
                  {detailLoading && (
                    <div className="absolute inset-0 z-20 bg-white/80 rounded-xl flex items-center justify-center">
                      <span className="material-symbols-outlined text-3xl animate-spin text-blue-500">progress_activity</span>
                    </div>
                  )}
                  <MapView center={mapCenter} zoom={mapZoom} height="100%" className="rounded-xl h-full">
                    <RouteSnapper
                      tripId={selectedTrip?.id ?? null}
                      origin={snapOrigin}
                      destination={snapDest}
                      waypoints={snapWaypoints}
                      trigger={snapTrigger}
                      onRouteReady={handleRouteReady}
                      onLoading={handleDirLoading}
                      onSnapError={setSnapError}
                    />
                    {detail && (
                      <>
                        {activePath.length >= 2 && (
                          <Polyline path={activePath}
                            strokeColor={roadPath.length >= 2 ? '#10b981' : '#3b82f6'}
                            strokeOpacity={0.85}
                            strokeWeight={4}
                          />
                        )}
                        {detail.start_point?.lat && detail.start_point.lng && (
                          <AdvancedMarker
                            position={{ lat: detail.start_point.lat, lng: detail.start_point.lng }}
                            onClick={() => setOpenInfoId(openInfoId === 'start' ? null : 'start')}
                          >
                            <StopPin index={0} label={detail.start_point.label || ''} type="start" />
                            {openInfoId === 'start' && (
                              <InfoWindow position={{ lat: detail.start_point.lat, lng: detail.start_point.lng! }} onCloseClick={() => setOpenInfoId(null)}>
                                <div className="text-xs"><p className="font-bold text-emerald-700">Départ</p><p>{detail.start_point.label}</p><p className="text-slate-400 mt-1">{selectedTrip.heure_depart}</p></div>
                              </InfoWindow>
                            )}
                          </AdvancedMarker>
                        )}
                        {detail.waypoints.map((wp, i) => wp.lat && wp.lng ? (
                          <AdvancedMarker key={`wp-${i}`} position={{ lat: wp.lat, lng: wp.lng }}
                            onClick={() => setOpenInfoId(openInfoId === `wp-${i}` ? null : `wp-${i}`)}>
                            <StopPin index={i + 1} label={wp.label} type="stop" />
                            {openInfoId === `wp-${i}` && (
                              <InfoWindow position={{ lat: wp.lat, lng: wp.lng! }} onCloseClick={() => setOpenInfoId(null)}>
                                <div className="text-xs"><p className="font-bold text-blue-700">Arrêt {i + 1}</p><p>{wp.label}</p></div>
                              </InfoWindow>
                            )}
                          </AdvancedMarker>
                        ) : null)}
                        {detail.end_point?.lat && detail.end_point.lng && (
                          <AdvancedMarker
                            position={{ lat: detail.end_point.lat, lng: detail.end_point.lng }}
                            onClick={() => setOpenInfoId(openInfoId === 'end' ? null : 'end')}
                          >
                            <StopPin index={-1} label={detail.end_point.label || ''} type="end" />
                            {openInfoId === 'end' && (
                              <InfoWindow position={{ lat: detail.end_point.lat, lng: detail.end_point.lng! }} onCloseClick={() => setOpenInfoId(null)}>
                                <div className="text-xs"><p className="font-bold text-red-600">Arrivée</p><p>{detail.end_point.label}</p><p className="text-slate-400 mt-1">{selectedTrip.heure_arrivee}</p></div>
                              </InfoWindow>
                            )}
                          </AdvancedMarker>
                        )}
                      </>
                    )}
                  </MapView>
                </div>

                {/* Side panel: stops sequence + capacity — same height as map, internal scroll */}
                {detail && (
                  <div className="w-60 shrink-0 flex flex-col gap-2 overflow-y-auto">
                    {/* Capacity gauge */}
                    <div className="bg-white rounded-xl border border-slate-100 p-3 shrink-0">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Capacité</p>
                      <CapacityGauge
                        fill_pct={selectedTrip.fill_pct}
                        capacity={selectedTrip.capacity}
                        passengers={selectedTrip.estimated_passengers}
                      />
                    </div>
                    {/* Circuit info */}
                    <div className="bg-white rounded-xl border border-slate-100 p-3 shrink-0">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Circuit</p>
                      <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                        <div><p className="text-slate-400">Secteur</p><p className="font-semibold">{selectedTrip.secteur || '—'}</p></div>
                        <div><p className="text-slate-400">Entité</p><p className="font-semibold truncate">{selectedTrip.entite || '—'}</p></div>
                        <div><p className="text-slate-400">T.KM</p><p className="font-semibold">{selectedTrip.t_km != null ? `${selectedTrip.t_km} km` : '—'}</p></div>
                        <div><p className="text-slate-400">Coût/j</p><p className="font-semibold">{selectedTrip.estimated_cost_mad} MAD</p></div>
                        <div className="col-span-2"><p className="text-slate-400">Code circuit</p><p className="font-mono text-[10px] truncate">{selectedTrip.arrets_circuit || '—'}</p></div>
                      </div>
                    </div>
                    {/* Stops sequence */}
                    <div className="bg-white rounded-xl border border-slate-100 p-3 flex-1">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                        Arrêts ({(detail.waypoints?.length ?? 0) + 2})
                      </p>
                      <div className="flex flex-col gap-1.5">
                        {detail.start_point && (
                          <div className="flex items-center gap-2">
                            <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-white text-[8px] font-black shrink-0">▶</div>
                            <div className="min-w-0">
                              <p className="text-[11px] font-semibold text-slate-700 truncate">{detail.start_point.label}</p>
                              <p className="text-[9px] text-slate-400">{selectedTrip.heure_depart}</p>
                            </div>
                          </div>
                        )}
                        {detail.waypoints.map((wp, i) => (
                          <div key={i} className="flex items-center gap-2 ml-0.5">
                            <div className="w-1 h-3 bg-slate-200 rounded ml-2" />
                            <div className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center text-white text-[8px] font-black shrink-0">{i + 1}</div>
                            <div className="flex items-center gap-1 min-w-0">
                              <p className="text-[11px] text-slate-600 truncate">{wp.label}</p>
                              {wp.lat ? <span className="text-[8px] text-emerald-400 shrink-0">●</span> : <span className="text-[8px] text-slate-300 shrink-0">○</span>}
                            </div>
                          </div>
                        ))}
                        {detail.end_point && (
                          <div className="flex items-center gap-2 mt-0.5">
                            <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center text-white text-[8px] font-black shrink-0">■</div>
                            <div className="min-w-0">
                              <p className="text-[11px] font-semibold text-slate-700 truncate">{detail.end_point.label}</p>
                              <p className="text-[9px] text-slate-400">{selectedTrip.heure_arrivee}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
