import { CircleMarker, Popup } from 'react-leaflet';
import type { Site } from '@/types/site';

interface SiteMarkerProps {
  site: Site;
  color?: string;
}

export function SiteMarker({ site, color = '#041627' }: SiteMarkerProps) {
  return (
    <CircleMarker
      center={[site.lat, site.lng]}
      radius={10}
      pathOptions={{
        fillColor: color,
        fillOpacity: 0.9,
        color,
        weight: 2,
        opacity: 0.7,
      }}
    >
      <Popup>
        <div className="font-sans text-sm text-on-surface min-w-[140px] rounded-lg">
          <p className="font-medium text-on-surface">{site.name}</p>
          <p className="text-xs text-on-surface-variant mt-0.5">{site.code}</p>
          <p className="text-xs text-on-surface-variant mt-1">{site.city}</p>
          <p className="text-xs text-on-surface-variant">
            {site.num_shifts} equipe{site.num_shifts > 1 ? 's' : ''}
          </p>
        </div>
      </Popup>
    </CircleMarker>
  );
}
