import { useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { useTranslation } from 'react-i18next';
import L from 'leaflet';
import type { LeafletMouseEvent, Marker as LeafletMarker } from 'leaflet';
import 'leaflet/dist/leaflet.css';

/* Fix default marker icons — Leaflet loses them when bundled by Vite */
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
});

const CASABLANCA_LAT = 33.57;
const CASABLANCA_LNG = -7.59;
const DEFAULT_ZOOM = 12;

interface MapPickerProps {
  lat: number;
  lng: number;
  onChange: (lat: number, lng: number) => void;
  height?: string;
}

function ClickHandler({ onChange }: { onChange: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e: LeafletMouseEvent) {
      onChange(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function DraggableMarker({
  lat,
  lng,
  onChange,
}: {
  lat: number;
  lng: number;
  onChange: (lat: number, lng: number) => void;
}) {
  const markerRef = useRef<LeafletMarker>(null);

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker) {
          const position = marker.getLatLng();
          onChange(position.lat, position.lng);
        }
      },
    }),
    [onChange],
  );

  return (
    <Marker
      draggable
      eventHandlers={eventHandlers}
      position={[lat, lng]}
      ref={markerRef}
    />
  );
}

export function MapPicker({
  lat,
  lng,
  onChange,
  height = '300px',
}: MapPickerProps) {
  const { t } = useTranslation();
  const centerLat = lat || CASABLANCA_LAT;
  const centerLng = lng || CASABLANCA_LNG;

  const handleChange = useCallback(
    (newLat: number, newLng: number) => {
      onChange(
        Math.round(newLat * 1_000_000) / 1_000_000,
        Math.round(newLng * 1_000_000) / 1_000_000,
      );
    },
    [onChange],
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="rounded-lg overflow-hidden" style={{ height }}>
        <MapContainer
          center={[centerLat, centerLng]}
          zoom={DEFAULT_ZOOM}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <DraggableMarker lat={centerLat} lng={centerLng} onChange={handleChange} />
          <ClickHandler onChange={handleChange} />
        </MapContainer>
      </div>
      <p className="text-sm text-on-surface-variant font-sans">
        {t('sites.form.map_hint', 'Cliquez sur la carte ou deplacez le marqueur pour definir la position')}
        {' — '}
        <span className="tabular-nums">
          {centerLat.toFixed(6)}, {centerLng.toFixed(6)}
        </span>
      </p>
    </div>
  );
}
