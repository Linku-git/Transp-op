import { useState, useCallback } from 'react';
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
} from '@vis.gl/react-google-maps';
import { generateStops } from '@/api/sotreg';
import { extractApiError } from '@/lib/apiError';
import type {
  StopGenerateRequest,
  StopGenerateResponse,
  GeneratedStopResult,
} from '@/types/sotreg';

/* ── Constants ────────────────────────────────────────────────────────────── */

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA = { lat: 33.5731, lng: -7.5898 };
const DEFAULT_ZOOM = 12;
const MAP_ID = 'STOP_GENERATOR_MAP';
const PRIMARY = '#0058be';

/* ── Helpers ──────────────────────────────────────────────────────────────── */

function fmtNum(value: number, decimals = 0): string {
  return value.toLocaleString('fr-MA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/* ── Stop pin marker ─────────────────────────────────────────────────────── */

function StopPin({ count }: { count: number }) {
  const size = Math.min(40, Math.max(24, 20 + count * 2));
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: PRIMARY,
        border: '2px solid white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: Math.max(10, Math.min(14, 8 + count)),
        fontWeight: 700,
        fontFamily: 'Inter, sans-serif',
        boxSizing: 'border-box',
        cursor: 'pointer',
        boxShadow: '0 1px 4px rgba(0,0,0,0.25)',
      }}
    >
      {count}
    </div>
  );
}

/* ── Map content ─────────────────────────────────────────────────────────── */

function StopMapContent({ stops }: { stops: GeneratedStopResult[] }) {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  const handleMarkerClick = useCallback((idx: number) => {
    setSelectedIdx((prev) => (prev === idx ? null : idx));
  }, []);

  const selected = selectedIdx !== null ? stops[selectedIdx] : null;

  return (
    <>
      {stops.map((stop, idx) => (
        <AdvancedMarker
          key={stop.cluster_id}
          position={{ lat: stop.centroid_lat, lng: stop.centroid_lng }}
          onClick={() => handleMarkerClick(idx)}
          zIndex={3}
        >
          <StopPin count={stop.employee_count} />
        </AdvancedMarker>
      ))}

      {selectedIdx !== null && selected && (
        <InfoWindow
          position={{ lat: selected.centroid_lat, lng: selected.centroid_lng }}
          onCloseClick={() => setSelectedIdx(null)}
        >
          <div className="font-sans text-sm min-w-[180px] p-1">
            <p className="font-semibold text-on-surface mb-1">
              Arret #{selected.cluster_id}
            </p>
            <div className="space-y-0.5 text-xs text-on-surface-variant">
              <p>
                <span className="font-medium text-on-surface">Employes :</span>{' '}
                {selected.employee_count}
              </p>
              <p>
                <span className="font-medium text-on-surface">Rayon :</span>{' '}
                {fmtNum(selected.catchment_radius_m)} m
              </p>
              <p>
                <span className="font-medium text-on-surface">Centroide :</span>{' '}
                {selected.centroid_lat.toFixed(5)}, {selected.centroid_lng.toFixed(5)}
              </p>
              <p>
                <span className="font-medium text-on-surface">Source :</span>{' '}
                {selected.source}
              </p>
            </div>
          </div>
        </InfoWindow>
      )}
    </>
  );
}

/* ── Legend overlay ───────────────────────────────────────────────────────── */

function StopLegend({ result }: { result: StopGenerateResponse }) {
  return (
    <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-md rounded-xl shadow-lg border border-white/20 p-3 font-sans z-10">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
        Resultats DBSCAN
      </p>
      <div className="space-y-1 text-xs text-on-surface">
        <div className="flex items-center gap-2">
          <span
            className="inline-block w-3 h-3 rounded-full flex-shrink-0"
            style={{ background: PRIMARY }}
          />
          {result.stops_generated} arrets generes
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block w-3 h-3 rounded-full flex-shrink-0 bg-slate-300" />
          {result.noise_count} points bruit
        </div>
      </div>
      <div className="mt-2 pt-2 border-t border-outline-variant/15 text-xs text-on-surface-variant">
        eps={result.eps_m}m / min_pts={result.min_pts}
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */

export function StopGeneratorPanel() {
  /* Form state */
  const [epsM, setEpsM] = useState<number>(500);
  const [minPts, setMinPts] = useState<number>(5);

  /* Async state */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StopGenerateResponse | null>(null);

  const handleGenerate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const req: StopGenerateRequest = {
        eps_m: epsM,
        min_pts: minPts,
      };
      const res = await generateStops(req);
      setResult(res);
    } catch (err) {
      setError(extractApiError(err, 'Erreur lors de la generation des arrets'));
    } finally {
      setLoading(false);
    }
  }, [epsM, minPts]);

  /* ── Render ─────────────────────────────────────────────────────────────── */

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6 font-sans">
      {/* Header */}
      <div className="flex items-center gap-2 mb-5">
        <span className="material-symbols-outlined text-primary text-xl">
          add_location_alt
        </span>
        <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
          Generateur d&apos;arrets (DBSCAN)
        </h3>
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        {/* eps_m */}
        <div>
          <label
            htmlFor="sg-eps"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Rayon eps (m)
          </label>
          <input
            id="sg-eps"
            type="number"
            min={50}
            max={5000}
            step={50}
            value={epsM}
            onChange={(e) => setEpsM(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>

        {/* min_pts */}
        <div>
          <label
            htmlFor="sg-minpts"
            className="block text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1.5"
          >
            Min points
          </label>
          <input
            id="sg-minpts"
            type="number"
            min={2}
            max={50}
            step={1}
            value={minPts}
            onChange={(e) => setMinPts(Number(e.target.value))}
            className="w-full bg-surface-container-high/50 border-none rounded-lg px-3 py-2 text-sm text-on-surface focus:ring-2 focus:ring-primary/20 outline-none"
          />
        </div>
      </div>

      {/* Generate button */}
      <button
        type="button"
        onClick={handleGenerate}
        disabled={loading}
        className="inline-flex items-center gap-2 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20 px-5 py-2.5 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <span className="material-symbols-outlined animate-spin text-base">
              progress_activity
            </span>
            Generation en cours...
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-base">
              hub
            </span>
            Generer les arrets
          </>
        )}
      </button>

      {/* Error state */}
      {error && (
        <div className="mt-4 flex items-start gap-2 bg-error-container/30 text-error rounded-lg px-4 py-3">
          <span className="material-symbols-outlined text-base mt-0.5">
            error
          </span>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="mt-6 space-y-5">
          {/* Summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Arrets generes
              </p>
              <p className="text-2xl font-bold text-primary">
                {result.stops_generated}
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                Points bruit
              </p>
              <p className="text-2xl font-bold text-on-surface">
                {result.noise_count}
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                eps utilise
              </p>
              <p className="text-2xl font-bold text-on-surface">
                {fmtNum(result.eps_m)}<span className="text-sm font-normal text-on-surface-variant"> m</span>
              </p>
            </div>
            <div className="bg-surface-container-low rounded-lg p-4 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
                min_pts utilise
              </p>
              <p className="text-2xl font-bold text-on-surface">
                {result.min_pts}
              </p>
            </div>
          </div>

          {/* Google Maps */}
          {result.stops.length > 0 && (
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
                Carte des arrets
              </p>
              <APIProvider apiKey={GOOGLE_MAPS_API_KEY} region="MA">
                <div
                  className="relative rounded-xl overflow-hidden border border-outline-variant/10"
                  style={{ height: 450 }}
                >
                  <Map
                    defaultCenter={CASABLANCA}
                    defaultZoom={DEFAULT_ZOOM}
                    mapId={MAP_ID}
                    streetViewControl={false}
                    mapTypeControl={false}
                    fullscreenControl={true}
                    zoomControl={true}
                    gestureHandling="greedy"
                    style={{ height: '100%', width: '100%' }}
                  >
                    <StopMapContent stops={result.stops} />
                  </Map>
                  <StopLegend result={result} />
                </div>
              </APIProvider>
            </div>
          )}

          {/* Stop list table */}
          {result.stops.length > 0 && (
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
                Liste des arrets
              </p>
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-surface-container-low/50">
                        <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-4 py-3">
                          #
                        </th>
                        <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-4 py-3">
                          Centroide
                        </th>
                        <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-4 py-3">
                          Employes
                        </th>
                        <th className="text-right text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-4 py-3">
                          Rayon (m)
                        </th>
                        <th className="text-left text-[10px] font-black uppercase tracking-widest text-on-surface-variant px-4 py-3">
                          Source
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant/10">
                      {result.stops.map((stop) => (
                        <tr
                          key={stop.cluster_id}
                          className="hover:bg-surface-bright transition-colors"
                        >
                          <td className="px-4 py-3 font-medium text-on-surface">
                            {stop.cluster_id}
                          </td>
                          <td className="px-4 py-3 text-on-surface-variant font-mono text-xs">
                            {stop.centroid_lat.toFixed(5)}, {stop.centroid_lng.toFixed(5)}
                          </td>
                          <td className="px-4 py-3 text-right">
                            <span className="inline-flex items-center gap-1 bg-primary/10 text-primary rounded-full px-2.5 py-0.5 text-xs font-semibold">
                              <span className="material-symbols-outlined text-xs">
                                person
                              </span>
                              {stop.employee_count}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right text-on-surface">
                            {fmtNum(stop.catchment_radius_m)}
                          </td>
                          <td className="px-4 py-3 text-on-surface-variant text-xs">
                            {stop.source}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Empty stops state */}
          {result.stops.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12">
              <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-3">
                location_off
              </span>
              <p className="text-sm text-on-surface-variant">
                Aucun arret genere avec ces parametres. Essayez d&apos;augmenter eps ou de diminuer min_pts.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
