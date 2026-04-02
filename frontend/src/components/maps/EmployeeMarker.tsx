import { useState } from 'react';
import { AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps';
import { useTranslation } from 'react-i18next';
import type { Employee } from '@/types/employee';

interface EmployeeMarkerProps {
  employee: Employee;
  color?: string;
}

export function EmployeeMarker({
  employee,
  color = '#0058be',
}: EmployeeMarkerProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  if (employee.lat === null || employee.lng === null) return null;

  const pos = { lat: employee.lat, lng: employee.lng };
  const fullName = `${employee.first_name} ${employee.last_name}`;

  return (
    <>
      <AdvancedMarker position={pos} onClick={() => setOpen(true)}>
        <div
          style={{
            width: 14,
            height: 14,
            borderRadius: '50%',
            background: color,
            opacity: 0.85,
            border: '1.5px solid white',
            boxSizing: 'border-box',
            cursor: 'pointer',
          }}
        />
      </AdvancedMarker>

      {open && (
        <InfoWindow position={pos} onCloseClick={() => setOpen(false)}>
          <div className="font-sans text-sm text-on-surface min-w-[160px] p-1">
            <p className="font-medium text-on-surface">{fullName}</p>
            <p className="text-xs text-on-surface-variant mt-0.5">{employee.matricule}</p>
            {employee.site_name && (
              <p className="text-xs text-on-surface-variant mt-1">{employee.site_name}</p>
            )}
            {employee.shift_time && (
              <p className="text-xs text-on-surface-variant">{employee.shift_time}</p>
            )}
            {employee.current_transport_mode && (
              <p className="text-xs text-on-surface-variant">{employee.current_transport_mode}</p>
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
