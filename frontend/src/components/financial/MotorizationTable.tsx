import { useTranslation } from 'react-i18next';
import type { TCOMotorizationComparison } from '@/types/financial';

interface MotorizationTableProps {
  comparisons: TCOMotorizationComparison[];
}

const VEHICLE_TYPE_LABELS: Record<string, string> = {
  minibus: 'Minibus',
  midibus: 'Midibus',
  bus_standard: 'Bus Standard',
  grand_bus: 'Grand Bus',
  vehicule_leger: 'Vehicule Leger',
};

const MOTORIZATION_LABELS: Record<string, string> = {
  diesel: 'Diesel',
  hybrid: 'Hybride',
  electric: 'Electrique',
  hydrogen: 'Hydrogene',
  gnv: 'GNV',
};

function formatMAD(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'MAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function MotorizationTable({ comparisons }: MotorizationTableProps) {
  const { t } = useTranslation();

  if (comparisons.length === 0) {
    return (
      <p className="text-sm text-on-surface-variant">
        {t('common.no_data', 'Aucune donnee')}
      </p>
    );
  }

  return (
    <div className="space-y-6" data-testid="motorization-table">
      {comparisons.map((comparison) => {
        const minTCO = Math.min(
          ...comparison.motorizations.map((m) => m.tco_per_vehicle),
        );

        return (
          <div key={comparison.vehicle_type}>
            <h4 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-3">
              {VEHICLE_TYPE_LABELS[comparison.vehicle_type] ??
                comparison.vehicle_type}
            </h4>
            <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="text-left px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('financial.motorization', 'Motorisation')}
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('financial.purchase', 'Achat')}
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('financial.maintenance_yr', 'Maintenance/an')}
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('financial.energy_km', 'Energie/km')}
                    </th>
                    <th className="text-right px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
                      {t('financial.tco_5y', 'TCO 5 ans')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {comparison.motorizations.map((motor) => {
                    const isCheapest = motor.tco_per_vehicle === minTCO;
                    return (
                      <tr
                        key={motor.motorization}
                        data-testid="motorization-row"
                        className={[
                          'hover:bg-surface-bright transition-colors',
                          isCheapest ? 'bg-green-50/50' : '',
                        ].join(' ')}
                      >
                        <td className="px-4 py-2.5 font-medium text-on-surface">
                          <div className="flex items-center gap-2">
                            {MOTORIZATION_LABELS[motor.motorization] ??
                              motor.motorization}
                            {isCheapest && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-green-50 text-green-700">
                                {t('financial.cheapest', 'Meilleur')}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-2.5 text-right text-on-surface">
                          {formatMAD(motor.purchase_price)}
                        </td>
                        <td className="px-4 py-2.5 text-right text-on-surface">
                          {formatMAD(motor.annual_maintenance_cost)}
                        </td>
                        <td className="px-4 py-2.5 text-right text-on-surface">
                          {motor.energy_cost_per_km.toFixed(2)} MAD
                        </td>
                        <td className="px-4 py-2.5 text-right font-bold text-on-surface">
                          {formatMAD(motor.tco_per_vehicle)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
}
