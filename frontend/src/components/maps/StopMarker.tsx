import { useState } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import type { PointArret } from '@/types/vehicle';

interface StopMarkerProps {
  stop: PointArret;
}

export function StopMarker({ stop }: StopMarkerProps) {
  const [open, setOpen] = useState(false);
  const pos = { lat: stop.lat, lng: stop.lng };

  return (
    <>
      <AdvancedMarker position={pos} onClick={() => setOpen(true)} zIndex={5}>
        <div
          style={{
            width: 16,
            height: 16,
            borderRadius: 3,
            background: '#1a6b3a',
            border: '2px solid white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: 8,
            fontWeight: 'bold',
            fontFamily: 'sans-serif',
            boxSizing: 'border-box',
            cursor: 'pointer',
            boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
          }}
        >
          A
        </div>
      </AdvancedMarker>

      {open && (
        <InfoWindow position={pos} onCloseClick={() => setOpen(false)}>
          <div className="font-sans text-sm text-on-surface min-w-[160px] p-1">
            <p className="font-semibold text-on-surface">{stop.nom}</p>
            <p className="text-xs font-mono text-on-surface-variant mt-0.5">{stop.code}</p>
            {stop.ville && (
              <p className="text-xs text-on-surface-variant mt-1">{stop.ville}</p>
            )}
            {stop.prestataire && (
              <p className="text-xs text-on-surface-variant">{stop.prestataire}</p>
            )}
            {stop.correspondance_tb && (
              <p className="text-xs text-on-surface-variant mt-1">
                TB: {stop.correspondance_tb}
              </p>
            )}
            {!stop.is_active && (
              <span className="inline-block mt-1.5 rounded-md bg-red-100 text-red-700 px-2 py-0.5 text-xs font-medium">
                Inactif
              </span>
            )}
          </div>
        </InfoWindow>
      )}
    </>
  );
}
