import { type ReactNode } from 'react';
import { APIProvider, Map } from '@vis.gl/react-google-maps';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA: [number, number] = [33.57, -7.59];
const DEFAULT_ZOOM = 12;

interface MapViewProps {
  /** [lat, lng] tuple — preserved from Leaflet interface */
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
  const gCenter = { lat: center[0], lng: center[1] };

  return (
    <div
      className={['rounded-xl overflow-hidden font-sans', className].join(' ')}
      style={{ height }}
    >
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
        <Map
          center={gCenter}
          zoom={zoom}
          mapId="DEMO_MAP_ID"
          streetViewControl={false}
          mapTypeControl={false}
          fullscreenControl={true}
          zoomControl={true}
          gestureHandling="auto"
          style={{ height: '100%', width: '100%' }}
        >
          {children}
        </Map>
      </APIProvider>
    </div>
  );
}
