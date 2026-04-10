import { Fragment, useState, useMemo, useCallback } from 'react';
import {
  APIProvider,
  Map,
  AdvancedMarker,
  InfoWindow,
  Polyline,
} from '@vis.gl/react-google-maps';
import type { ZFELigneResult, ZFEEndpointResult } from '@/types/sotreg';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA = { lat: 33.5731, lng: -7.5898 };
const DEFAULT_ZOOM = 11;
const MAP_ID = 'ZFE_MAP';

const COLOR_SAFE = '#0058be';
const COLOR_ZFE = '#dc2626';
const COLOR_LINE_SAFE = '#0058be';
const COLOR_LINE_ZFE = '#dc2626';
const COLOR_LINE_MIXED = '#d97706';

/* ── Types ──────────────────────────────────────────────────────────────── */

interface SelectedMarker {
  ligneIdx: number;
  endpoint: 'origin' | 'dest';
}

interface ZFEMapOverlayProps {
  zfeResults: ZFELigneResult[];
  className?: string;
  withProvider?: boolean;
}

/* ── Pin marker ─────────────────────────────────────────────────────────── */

function ZFEPin({
  inZfe,
  label,
}: {
  inZfe: boolean;
  label: string;
}) {
  const bg = inZfe ? COLOR_ZFE : COLOR_SAFE;
  return (
    <div
      style={{
        width: 24,
        height: 24,
        borderRadius: '50%',
        background: bg,
        border: '2px solid white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: 10,
        fontWeight: 700,
        fontFamily: 'Inter, sans-serif',
        boxSizing: 'border-box',
        cursor: 'pointer',
        boxShadow: '0 1px 4px rgba(0,0,0,0.25)',
      }}
      title={label}
    >
      {label.charAt(0).toUpperCase()}
    </div>
  );
}

/* ── InfoWindow content ─────────────────────────────────────────────────── */

function EndpointInfo({
  ligne,
  endpoint,
  data,
}: {
  ligne: ZFELigneResult;
  endpoint: 'origin' | 'dest';
  data: ZFEEndpointResult;
}) {
  const endpointLabel = endpoint === 'origin' ? 'Origine' : 'Destination';
  return (
    <div className="font-sans text-sm min-w-[200px] p-1">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="font-semibold text-on-surface">
          {ligne.ligne_code} &mdash; {ligne.ligne_name}
        </span>
      </div>

      <div className="flex items-center gap-1.5 mb-1">
        <span
          className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
          style={{ background: data.is_in_zfe ? COLOR_ZFE : COLOR_SAFE }}
        />
        <span className="text-on-surface-variant">
          {endpointLabel} {data.is_in_zfe ? 'en ZFE' : 'hors ZFE'}
        </span>
      </div>

      {data.is_in_zfe && data.zone_name && (
        <div className="mt-1 space-y-0.5">
          <p className="text-xs text-on-surface-variant">
            <span className="font-medium text-on-surface">Zone :</span>{' '}
            {data.zone_name}
          </p>
          {data.restriction_level && (
            <p className="text-xs text-on-surface-variant">
              <span className="font-medium text-on-surface">Restriction :</span>{' '}
              {data.restriction_level}
            </p>
          )}
          {data.allowed_crit_air && data.allowed_crit_air.length > 0 && (
            <p className="text-xs text-on-surface-variant">
              <span className="font-medium text-on-surface">Crit&apos;Air :</span>{' '}
              {data.allowed_crit_air.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/* ── Legend overlay ──────────────────────────────────────────────────────── */

function ZFELegend({
  total,
  inZfe,
}: {
  total: number;
  inZfe: number;
}) {
  return (
    <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-md rounded-xl shadow-lg border border-white/20 p-3 font-sans z-10">
      <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-2">
        Legende ZFE
      </p>

      <div className="space-y-1.5">
        <div className="flex items-center gap-2 text-xs text-on-surface">
          <span
            className="inline-block w-3 h-3 rounded-full flex-shrink-0"
            style={{ background: '#16a34a' }}
          />
          Hors ZFE
        </div>
        <div className="flex items-center gap-2 text-xs text-on-surface">
          <span
            className="inline-block w-3 h-3 rounded-full flex-shrink-0"
            style={{ background: COLOR_ZFE }}
          />
          En ZFE
        </div>
      </div>

      <div className="mt-2 pt-2 border-t border-outline-variant/15">
        <p className="text-xs text-on-surface-variant">
          <span className="font-semibold text-on-surface">{inZfe}</span>/{total} lignes en ZFE
        </p>
      </div>
    </div>
  );
}

/* ── Map content (rendered inside APIProvider / Map) ─────────────────────── */

function ZFEMapContent({
  zfeResults,
}: {
  zfeResults: ZFELigneResult[];
}) {
  const [selected, setSelected] = useState<SelectedMarker | null>(null);

  const handleMarkerClick = useCallback(
    (ligneIdx: number, endpoint: 'origin' | 'dest') => {
      setSelected((prev) => {
        if (prev && prev.ligneIdx === ligneIdx && prev.endpoint === endpoint) {
          return null;
        }
        return { ligneIdx, endpoint };
      });
    },
    [],
  );

  const selectedLigne = selected !== null ? zfeResults[selected.ligneIdx] : null;
  const selectedData =
    selected !== null && selectedLigne
      ? selected.endpoint === 'origin'
        ? selectedLigne.origin
        : selectedLigne.dest
      : null;
  const selectedPosition =
    selectedData !== null
      ? { lat: selectedData.lat, lng: selectedData.lng }
      : null;

  return (
    <>
      {zfeResults.map((result, idx) => {
        const originPos = { lat: result.origin.lat, lng: result.origin.lng };
        const destPos = { lat: result.dest.lat, lng: result.dest.lng };

        const bothInZfe =
          result.origin.is_in_zfe && result.dest.is_in_zfe;
        const noneInZfe =
          !result.origin.is_in_zfe && !result.dest.is_in_zfe;
        const lineColor = bothInZfe
          ? COLOR_LINE_ZFE
          : noneInZfe
            ? COLOR_LINE_SAFE
            : COLOR_LINE_MIXED;

        return (
          <Fragment key={result.ligne_id}>
            {/* Polyline connecting origin to destination */}
            <Polyline
              path={[originPos, destPos]}
              strokeColor={lineColor}
              strokeWeight={2.5}
              strokeOpacity={0.6}
            />

            {/* Origin marker */}
            <AdvancedMarker
              position={originPos}
              onClick={() => handleMarkerClick(idx, 'origin')}
              zIndex={result.origin.is_in_zfe ? 5 : 3}
            >
              <ZFEPin
                inZfe={result.origin.is_in_zfe}
                label="O"
              />
            </AdvancedMarker>

            {/* Destination marker */}
            <AdvancedMarker
              position={destPos}
              onClick={() => handleMarkerClick(idx, 'dest')}
              zIndex={result.dest.is_in_zfe ? 5 : 3}
            >
              <ZFEPin
                inZfe={result.dest.is_in_zfe}
                label="D"
              />
            </AdvancedMarker>
          </Fragment>
        );
      })}

      {/* InfoWindow for selected marker */}
      {selected !== null && selectedLigne && selectedData && selectedPosition && (
        <InfoWindow
          position={selectedPosition}
          onCloseClick={() => setSelected(null)}
        >
          <EndpointInfo
            ligne={selectedLigne}
            endpoint={selected.endpoint}
            data={selectedData}
          />
        </InfoWindow>
      )}
    </>
  );
}

/* ── Main component ─────────────────────────────────────────────────────── */

export function ZFEMapOverlay({
  zfeResults,
  className,
  withProvider = true,
}: ZFEMapOverlayProps) {
  const lignesInZfe = useMemo(
    () => zfeResults.filter((r) => r.any_endpoint_in_zfe).length,
    [zfeResults],
  );

  /* Empty state */
  if (zfeResults.length === 0) {
    return (
      <div
        className={[
          'flex flex-col items-center justify-center bg-surface-container-lowest rounded-xl border border-outline-variant/10 shadow-sm p-12 font-sans',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <span className="material-symbols-outlined text-4xl text-on-surface-variant/40 mb-3">
          map
        </span>
        <p className="text-sm text-on-surface-variant">
          Aucune donnee ZFE disponible
        </p>
      </div>
    );
  }

  const mapContent = (
    <div
      className={[
        'relative rounded-xl overflow-hidden font-sans',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      style={{ height: '100%', minHeight: 400 }}
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
        <ZFEMapContent zfeResults={zfeResults} />
      </Map>

      {/* Legend overlay */}
      <ZFELegend total={zfeResults.length} inZfe={lignesInZfe} />
    </div>
  );

  if (!withProvider) {
    return mapContent;
  }

  return (
    <APIProvider apiKey={GOOGLE_MAPS_API_KEY} region="MA">
      {mapContent}
    </APIProvider>
  );
}
