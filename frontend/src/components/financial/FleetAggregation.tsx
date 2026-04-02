import { useTranslation } from 'react-i18next';
import type { TCOFleetResult } from '@/types/financial';

interface FleetAggregationProps {
  fleetResult: TCOFleetResult;
}

function formatMAD(value: number): string {
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'MAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function FleetAggregation({ fleetResult }: FleetAggregationProps) {
  const { t } = useTranslation();

  const averageCost =
    fleetResult.vehicle_count > 0
      ? fleetResult.fleet_tco_total / fleetResult.vehicle_count
      : 0;

  return (
    <div
      data-testid="fleet-aggregation"
      className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6"
    >
      <h3 className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-4">
        {t('financial.fleet_summary', 'Resume de la flotte')}
      </h3>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
            {t('financial.fleet_tco_total', 'TCO total flotte')}
          </p>
          <p
            className="text-2xl font-bold text-primary"
            data-testid="fleet-tco-total"
          >
            {formatMAD(fleetResult.fleet_tco_total)}
          </p>
        </div>

        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
            {t('financial.vehicle_count', 'Nombre de vehicules')}
          </p>
          <p className="text-2xl font-bold text-on-surface">
            {fleetResult.vehicle_count}
          </p>
        </div>

        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
            {t('financial.avg_cost_vehicle', 'Cout moyen / vehicule')}
          </p>
          <p className="text-2xl font-bold text-on-surface">
            {formatMAD(averageCost)}
          </p>
        </div>

        <div>
          <p className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant mb-1">
            {t('financial.duration', 'Duree')}
          </p>
          <p className="text-2xl font-bold text-on-surface">
            {fleetResult.duration_years}{' '}
            <span className="text-sm font-normal text-on-surface-variant">
              {t('financial.years', 'ans')}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
