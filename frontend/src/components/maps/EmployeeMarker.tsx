import { CircleMarker, Popup } from 'react-leaflet';
import { useTranslation } from 'react-i18next';
import type { Employee } from '@/types/employee';

interface EmployeeMarkerProps {
  employee: Employee;
  color?: string;
}

export function EmployeeMarker({
  employee,
  color = '#006b5c',
}: EmployeeMarkerProps) {
  const { t } = useTranslation();

  if (employee.lat === null || employee.lng === null) {
    return null;
  }

  const fullName = `${employee.first_name} ${employee.last_name}`;

  return (
    <CircleMarker
      center={[employee.lat, employee.lng]}
      radius={6}
      pathOptions={{
        fillColor: color,
        fillOpacity: 0.85,
        color,
        weight: 2,
        opacity: 0.6,
      }}
    >
      <Popup>
        <div className="font-sans text-sm text-on-surface min-w-[160px]">
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
            <span className="inline-block mt-1.5 rounded-md bg-secondary-container text-on-secondary-container px-2 py-0.5 text-xs font-medium">
              {t('employees.badges.pmr', 'PMR')}
            </span>
          )}
        </div>
      </Popup>
    </CircleMarker>
  );
}
