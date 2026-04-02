import { useCallback } from 'react';
import { GoogleMap, Marker, useJsApiLoader } from '@react-google-maps/api';
import { useTranslation } from 'react-i18next';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA_LAT = 33.57;
const CASABLANCA_LNG = -7.59;
const DEFAULT_ZOOM = 14;

const MAP_OPTIONS: google.maps.MapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: false,
  mapTypeControl: false,
  fullscreenControl: false,
};

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
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
  });

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

  const handleMapClick = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (e.latLng) {
        handleChange(e.latLng.lat(), e.latLng.lng());
      }
    },
    [handleChange],
  );

  const handleDragEnd = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (e.latLng) {
        handleChange(e.latLng.lat(), e.latLng.lng());
      }
    },
    [handleChange],
  );

  if (loadError) {
    return (
      <div className="flex flex-col gap-2">
        <div
          className="rounded-lg overflow-hidden flex items-center justify-center bg-surface-container font-sans text-sm text-on-surface-variant"
          style={{ height }}
        >
          Erreur de chargement de la carte
        </div>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className="flex flex-col gap-2">
        <div
          className="rounded-lg overflow-hidden bg-surface-container/30 animate-pulse"
          style={{ height }}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="rounded-lg overflow-hidden" style={{ height }}>
        <GoogleMap
          mapContainerStyle={{ height: '100%', width: '100%' }}
          center={{ lat: centerLat, lng: centerLng }}
          zoom={DEFAULT_ZOOM}
          options={MAP_OPTIONS}
          onClick={handleMapClick}
        >
          <Marker
            position={{ lat: centerLat, lng: centerLng }}
            draggable
            onDragEnd={handleDragEnd}
          />
        </GoogleMap>
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
