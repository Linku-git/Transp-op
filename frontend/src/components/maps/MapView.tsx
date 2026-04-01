import { type ReactNode } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import L from 'leaflet';
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

const CASABLANCA: [number, number] = [33.57, -7.59];
const DEFAULT_ZOOM = 12;

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
  return (
    <div
      className={['rounded-lg overflow-hidden', className].join(' ')}
      style={{ height }}
    >
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {children}
      </MapContainer>
    </div>
  );
}
