import { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import type { Site } from '@/types/site';

interface SiteMarkerProps {
  site: Site;
  color?: string;
}

function siteIcon(color: string): google.maps.Icon {
  const c = encodeURIComponent(color);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22"><circle cx="11" cy="11" r="9" fill="${c}" fill-opacity="0.9" stroke="white" stroke-width="2"/><text x="11" y="15" text-anchor="middle" font-size="9" fill="white" font-family="sans-serif" font-weight="bold">S</text></svg>`;
  return {
    url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
    scaledSize: new window.google.maps.Size(22, 22),
    anchor: new window.google.maps.Point(11, 11),
  };
}

export function SiteMarker({ site, color = '#041627' }: SiteMarkerProps) {
  const [open, setOpen] = useState(false);
  const pos: google.maps.LatLngLiteral = { lat: site.lat, lng: site.lng };

  return (
    <>
      <Marker
        position={pos}
        icon={siteIcon(color)}
        onClick={() => setOpen(true)}
        zIndex={10}
      />
      {open && (
        <InfoWindow
          position={pos}
          onCloseClick={() => setOpen(false)}
        >
          <div className="font-sans text-sm text-on-surface min-w-[140px] rounded-lg p-1">
            <p className="font-medium text-on-surface">{site.name}</p>
            <p className="text-xs text-on-surface-variant mt-0.5">{site.code}</p>
            <p className="text-xs text-on-surface-variant mt-1">{site.city}</p>
            <p className="text-xs text-on-surface-variant">
              {site.num_shifts} equipe{site.num_shifts > 1 ? 's' : ''}
            </p>
          </div>
        </InfoWindow>
      )}
    </>
  );
}
