import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { ShadowZones } from '@/types/hr';

interface ShadowZonesListProps {
  data: ShadowZones;
}

const VISIBLE_LIMIT = 20;

export function ShadowZonesList({ data }: ShadowZonesListProps) {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  const visibleEmployees = showAll
    ? data.employees
    : data.employees.slice(0, VISIBLE_LIMIT);

  return (
    <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
      <div className="px-6 pt-5 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
            {t('hr.shadow_zones_title', 'Zones d\'ombre')}
          </h3>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700">
            {data.shadow_zone_count} {t('hr.employees_label', 'employes')} (&gt;{data.threshold_km}km)
          </span>
        </div>
        <span className="font-sans text-xs text-on-surface-variant">
          {data.shadow_zone_pct.toFixed(1)}% {t('hr.of_total', 'du total')}
        </span>
      </div>

      {data.employees.length === 0 ? (
        <div className="px-6 pb-5">
          <p className="font-sans text-sm text-on-surface-variant">
            {t('hr.no_shadow_zones', 'Aucun employe en zone d\'ombre.')}
          </p>
        </div>
      ) : (
        <>
          <table className="w-full">
            <thead>
              <tr className="bg-surface-container-low/50">
                <th className="text-left px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  {t('hr.col_employee', 'Employe')}
                </th>
                <th className="text-left px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  {t('hr.col_location', 'Localisation')}
                </th>
                <th className="text-right px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  {t('hr.col_distance', 'Distance')}
                </th>
                <th className="text-left px-6 py-2 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                  {t('hr.col_mode', 'Mode')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {visibleEmployees.map((emp) => (
                <tr key={emp.id} className="hover:bg-surface-bright" data-testid="shadow-zone-row">
                  <td className="px-6 py-3 text-sm font-sans text-on-surface">
                    {emp.name}
                  </td>
                  <td className="px-6 py-3 text-sm font-sans text-on-surface-variant">
                    {emp.quartier}, {emp.city}
                  </td>
                  <td className="px-6 py-3 text-sm font-sans text-on-surface-variant text-right">
                    {emp.distance_km.toFixed(1)} km
                  </td>
                  <td className="px-6 py-3 text-sm font-sans text-on-surface-variant">
                    {emp.primary_mode}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {data.employees.length > VISIBLE_LIMIT && !showAll && (
            <div className="px-6 py-3 border-t border-outline-variant/10">
              <button
                type="button"
                onClick={() => setShowAll(true)}
                className="font-sans text-sm text-primary hover:text-primary-container font-medium"
              >
                {t('hr.see_more', 'Voir plus')} ({data.employees.length - VISIBLE_LIMIT} {t('hr.remaining', 'restants')})
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
