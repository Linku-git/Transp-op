import { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import type { MeetingZone } from '@/types/optimization';

function meetingZoneIcon(pmrAccessible: boolean): google.maps.Icon {
  const fill = pmrAccessible ? '%2393c5fd' : '%230058be';
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"><circle cx="9" cy="9" r="7" fill="${fill}" fill-opacity="0.85" stroke="%230058be" stroke-width="2"/></svg>`;
  return {
    url: `data:image/svg+xml;charset=UTF-8,${svg}`,
    scaledSize: new window.google.maps.Size(18, 18),
    anchor: new window.google.maps.Point(9, 9),
  };
}

interface MeetingZoneMarkerProps {
  zone: MeetingZone;
}

export function MeetingZoneMarker({ zone }: MeetingZoneMarkerProps) {
  const [open, setOpen] = useState(false);
  const pos: google.maps.LatLngLiteral = { lat: zone.lat, lng: zone.lng };

  return (
    <>
      <Marker
        position={pos}
        icon={meetingZoneIcon(zone.pmr_accessible)}
        onClick={() => setOpen(true)}
        zIndex={5}
      />
      {open && (
        <InfoWindow
          position={pos}
          onCloseClick={() => setOpen(false)}
        >
          <div className="font-sans text-sm p-1">
            <p className="font-semibold text-on-surface">
              Zone de Rencontre {zone.cluster_index + 1}
            </p>
            <p className="text-on-surface-variant">
              {zone.employee_count} employés
            </p>
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
