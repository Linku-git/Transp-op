import { type ReactNode, useEffect, useRef } from 'react';
import { APIProvider, Map, useMap } from '@vis.gl/react-google-maps';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? '';
const CASABLANCA: [number, number] = [33.57, -7.59];
const DEFAULT_ZOOM = 12;

/* ── CameraController: flies to a new location without locking pan/zoom ── */
function CameraController({
  center,
  zoom,
}: {
  center: google.maps.LatLngLiteral;
  zoom: number;
}) {
  const map = useMap();
  const prevLat = useRef<number | null>(null);
  const prevLng = useRef<number | null>(null);

  useEffect(() => {
    if (!map) return;
    if (prevLat.current === center.lat && prevLng.current === center.lng) return;
    prevLat.current = center.lat;
    prevLng.current = center.lng;
    map.panTo(center);
    map.setZoom(zoom);
  }, [map, center.lat, center.lng, zoom]);

  return null;
}

interface MapViewProps {
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
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY} region="MA">
        <Map
          defaultCenter={gCenter}
          defaultZoom={zoom}
          mapId="DEMO_MAP_ID"
          streetViewControl={false}
          mapTypeControl={false}
          fullscreenControl={true}
          zoomControl={true}
          gestureHandling="greedy"
          style={{ height: '100%', width: '100%' }}
        >
          <CameraController center={gCenter} zoom={zoom} />
          {children}
        </Map>
      </APIProvider>
    </div>
  );
}
