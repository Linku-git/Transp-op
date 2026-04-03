import { useCallback } from 'react';
import { APIProvider, Map, AdvancedMarker } from '@vis.gl/react-google-maps';
import { useTranslation } from 'react-i18next';
import type { MapMouseEvent } from '@vis.gl/react-google-maps';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA_LAT = 33.57;
const CASABLANCA_LNG = -7.59;
const DEFAULT_ZOOM = 14;

interface MapPickerProps {
  lat: number;
  lng: number;
  onChange: (lat: number, lng: number) => void;
  height?: string;
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

  const snap = useCallback(
    (rawLat: number, rawLng: number) => {
      onChange(
        Math.round(rawLat * 1_000_000) / 1_000_000,
        Math.round(rawLng * 1_000_000) / 1_000_000,
      );
    },
    [onChange],
  );

  const handleMapClick = useCallback(
    (e: MapMouseEvent) => {
      if (e.detail.latLng) {
        snap(e.detail.latLng.lat, e.detail.latLng.lng);
      }
    },
    [snap],
  );

  const handleDragEnd = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (e.latLng) {
        snap(e.latLng.lat(), e.latLng.lng());
      }
    },
    [snap],
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="rounded-lg overflow-hidden" style={{ height }}>
        <APIProvider apiKey={GOOGLE_MAPS_API_KEY} region="MA">
          <Map
            center={{ lat: centerLat, lng: centerLng }}
            zoom={DEFAULT_ZOOM}
            mapId="DEMO_MAP_ID"
            streetViewControl={false}
            mapTypeControl={false}
            fullscreenControl={false}
            gestureHandling="auto"
            style={{ height: '100%', width: '100%' }}
            onClick={handleMapClick}
          >
            <AdvancedMarker
              position={{ lat: centerLat, lng: centerLng }}
              draggable
              onDragEnd={handleDragEnd}
            />
          </Map>
        </APIProvider>
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
