import { useState } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import type { Site } from '@/types/site';

interface SiteMarkerProps {
  site: Site;
  color?: string;
}

export function SiteMarker({ site, color = '#041627' }: SiteMarkerProps) {
  const [open, setOpen] = useState(false);
  const pos = { lat: site.lat, lng: site.lng };

  return (
    <>
      <AdvancedMarker position={pos} onClick={() => setOpen(true)} zIndex={10}>
        <div
          style={{
            width: 22,
            height: 22,
            borderRadius: '50%',
            background: color,
            border: '2px solid white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: 9,
            fontWeight: 'bold',
            fontFamily: 'sans-serif',
            boxSizing: 'border-box',
            cursor: 'pointer',
          }}
        >
          S
        </div>
      </AdvancedMarker>

      {open && (
        <InfoWindow position={pos} onCloseClick={() => setOpen(false)}>
          <div className="font-sans text-sm text-on-surface min-w-[140px] p-1">
            <p className="font-medium text-on-surface">{site.name}</p>
            <p className="text-xs text-on-surface-variant mt-0.5">{site.code}</p>
            <p className="text-xs text-on-surface-variant mt-1">{site.city}</p>
            <p className="text-xs text-on-surface-variant">
              {site.num_shifts} shift{site.num_shifts > 1 ? 's' : ''}
            </p>
          </div>
        </InfoWindow>
      )}
    </>
  );
}
