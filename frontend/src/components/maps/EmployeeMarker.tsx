import { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import { useTranslation } from 'react-i18next';
import type { Employee } from '@/types/employee';

interface EmployeeMarkerProps {
  employee: Employee;
  color?: string;
}

function circleIcon(color: string): google.maps.Icon {
  const c = encodeURIComponent(color);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"><circle cx="7" cy="7" r="5.5" fill="${c}" fill-opacity="0.85" stroke="white" stroke-width="1.5"/></svg>`;
  return {
    url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
    scaledSize: new window.google.maps.Size(14, 14),
    anchor: new window.google.maps.Point(7, 7),
  };
}

export function EmployeeMarker({
  employee,
  color = '#0058be',
}: EmployeeMarkerProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  if (employee.lat === null || employee.lng === null) {
    return null;
  }

  const pos: google.maps.LatLngLiteral = { lat: employee.lat, lng: employee.lng };
  const fullName = `${employee.first_name} ${employee.last_name}`;

  return (
    <>
      <Marker
        position={pos}
        icon={circleIcon(color)}
        onClick={() => setOpen(true)}
      />
      {open && (
        <InfoWindow
          position={pos}
          onCloseClick={() => setOpen(false)}
        >
          <div className="font-sans text-sm text-on-surface min-w-[160px] rounded-lg p-1">
            <p className="font-medium text-on-surface">{fullName}</p>
            <p className="text-xs text-on-surface-variant mt-0.5">
              {employee.matricule}
            </p>
            {employee.site_name && (
              <p className="text-xs text-on-surface-variant mt-1">
                {employee.site_name}
              </p>
            )}
            {employee.shift_time && (
              <p className="text-xs text-on-surface-variant">
                {employee.shift_time}
              </p>
            )}
            {employee.current_transport_mode && (
              <p className="text-xs text-on-surface-variant">
                {employee.current_transport_mode}
              </p>
            )}
            {employee.is_pmr && (
              <span className="inline-block mt-1.5 rounded-md bg-blue-100 text-blue-800 px-2 py-0.5 text-xs font-medium">
                {t('employees.badges.pmr', 'PMR')}
              </span>
            )}
          </div>
        </InfoWindow>
      )}
    </>
  );
}
