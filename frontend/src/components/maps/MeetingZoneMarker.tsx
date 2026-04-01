import { CircleMarker, Popup } from 'react-leaflet';
import type { MeetingZone } from '@/types/optimization';

interface MeetingZoneMarkerProps {
  zone: MeetingZone;
}

export function MeetingZoneMarker({ zone }: MeetingZoneMarkerProps) {
  return (
    <CircleMarker
      center={[zone.lat, zone.lng]}
      radius={8}
      pathOptions={{
        color: '#006b5c',
        fillColor: zone.pmr_accessible ? '#68fadd' : '#006b5c',
        fillOpacity: 0.7,
        weight: 2,
      }}
    >
      <Popup>
        <div className="font-sans text-sm">
          <p className="font-semibold text-on-surface">
            Meeting Zone {zone.cluster_index + 1}
          </p>
          <p className="text-on-surface-variant">
            {zone.employee_count} employees
          </p>
          {zone.road_name && (
            <p className="text-on-surface-variant">{zone.road_name}</p>
          )}
          {zone.pmr_accessible && (
            <p className="text-secondary">PMR Accessible</p>
          )}
        </div>
      </Popup>
    </CircleMarker>
  );
}
