import { useState } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import type { MeetingZone } from '@/types/optimization';

interface MeetingZoneMarkerProps {
  zone: MeetingZone;
}

export function MeetingZoneMarker({ zone }: MeetingZoneMarkerProps) {
  const [open, setOpen] = useState(false);
  const pos = { lat: zone.lat, lng: zone.lng };

  return (
    <>
      <AdvancedMarker position={pos} onClick={() => setOpen(true)} zIndex={5}>
        <div
          style={{
            width: 18,
            height: 18,
            borderRadius: '50%',
            background: zone.pmr_accessible ? '#93c5fd' : '#0058be',
            opacity: 0.85,
            border: '2px solid #0058be',
            boxSizing: 'border-box',
            cursor: 'pointer',
          }}
        />
      </AdvancedMarker>

      {open && (
        <InfoWindow position={pos} onCloseClick={() => setOpen(false)}>
          <div className="font-sans text-sm p-1">
            <p className="font-semibold text-on-surface">
              Zone de Rencontre {zone.cluster_index + 1}
            </p>
            <p className="text-on-surface-variant">{zone.employee_count} employés</p>
            {zone.road_name && (
              <p className="text-on-surface-variant">{zone.road_name}</p>
            )}
            {zone.pmr_accessible && (
              <p className="text-blue-600 font-medium">Accessible PMR</p>
            )}
          </div>
        </InfoWindow>
      )}
    </>
  );
}
