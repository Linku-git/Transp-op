import { type ReactNode } from 'react';
import { GoogleMap, useJsApiLoader } from '@react-google-maps/api';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA: [number, number] = [33.57, -7.59];
const DEFAULT_ZOOM = 12;

const MAP_OPTIONS: google.maps.MapOptions = {
  disableDefaultUI: false,
  zoomControl: true,
  streetViewControl: false,
  mapTypeControl: false,
  fullscreenControl: true,
  styles: [
    { featureType: 'poi', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    { featureType: 'transit', elementType: 'labels', stylers: [{ visibility: 'off' }] },
  ],
};

interface MapViewProps {
  /** [lat, lng] tuple — matches existing Leaflet interface */
  center?: [number, number];
  zoom?: number;
  height?: string;
  children?: ReactNode;
  className?: string;
}

export function MapView({
  center = CASABLANCA,
  zoom = DEFAULT_ZOOM,
  height = '100%',
  children,
  className = '',
}: MapViewProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
  });

  const gCenter: google.maps.LatLngLiteral = { lat: center[0], lng: center[1] };

  if (loadError) {
    return (
      <div
        className={[
          'rounded-xl overflow-hidden flex items-center justify-center',
          'bg-surface-container font-sans text-sm text-on-surface-variant',
          className,
        ].join(' ')}
        style={{ height }}
      >
        Erreur de chargement de la carte
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div
        className={['rounded-xl overflow-hidden bg-surface-container/30 animate-pulse', className].join(' ')}
        style={{ height }}
      />
    );
  }

  return (
    <div
      className={['rounded-xl overflow-hidden font-sans', className].join(' ')}
      style={{ height }}
    >
      <GoogleMap
        mapContainerStyle={{ height: '100%', width: '100%' }}
        center={gCenter}
        zoom={zoom}
        options={MAP_OPTIONS}
      >
        {children}
      </GoogleMap>
    </div>
  );
}
