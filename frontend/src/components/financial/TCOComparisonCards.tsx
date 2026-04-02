import { useTranslation } from 'react-i18next';
import type { TCOVehicleResult } from '@/types/financial';

interface TCOComparisonCardsProps {
  vehicles: TCOVehicleResult[];
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

export function TCOComparisonCards({ vehicles }: TCOComparisonCardsProps) {
  const { t } = useTranslation();

  if (vehicles.length === 0) {
    return (
      <p className="text-sm text-on-surface-variant">
        {t('common.no_data', 'Aucune donnee')}
      </p>
    );
  }

  const minTCO = Math.min(...vehicles.map((v) => v.tco_per_vehicle));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {vehicles.map((vehicle, index) => {
        const isLowest = vehicle.tco_per_vehicle === minTCO;
        return (
          <div
            key={`${vehicle.vehicle_type}-${vehicle.motorization}-${index}`}
            data-testid="tco-comparison-card"
            className={[
              'bg-surface-container-lowest rounded-xl shadow-sm border p-6 transition-all',
              isLowest
                ? 'border-primary ring-2 ring-primary/20'
                : 'border-outline-variant/10',
            ].join(' ')}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="font-sans text-sm font-bold text-on-surface">
                  {VEHICLE_TYPE_LABELS[vehicle.vehicle_type] ??
                    vehicle.vehicle_type}
                </h4>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  {MOTORIZATION_LABELS[vehicle.motorization] ??
                    vehicle.motorization}
                </p>
              </div>
              <span className="inline-flex items-center justify-center min-w-[1.5rem] h-6 px-2 rounded-full text-xs font-bold bg-primary/10 text-primary">
                x{vehicle.quantity}
              </span>
            </div>

            {isLowest && (
              <div className="flex items-center gap-1 mb-3">
                <span className="material-symbols-outlined text-primary text-base">
                  emoji_events
                </span>
                <span className="text-[10px] font-bold uppercase tracking-widest text-primary">
                  {t('financial.lowest_tco', 'TCO le plus bas')}
                </span>
              </div>
            )}

            <div className="space-y-2 mb-4">
              <div className="flex justify-between items-baseline">
                <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  {t('financial.tco_per_vehicle', 'TCO / vehicule')}
                </span>
                <span className="text-lg font-bold text-on-surface">
                  {formatMAD(vehicle.tco_per_vehicle)}
                </span>
              </div>
              <div className="flex justify-between items-baseline">
                <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant">
                  {t('financial.tco_total', 'TCO total')}
                </span>
                <span className="text-sm font-medium text-on-surface">
                  {formatMAD(vehicle.tco_total)}
                </span>
              </div>
            </div>

            <div className="border-t border-outline-variant/10 pt-3 space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">
                  {t('financial.purchase', 'Achat')}
                </span>
                <span className="text-on-surface font-medium">
                  {formatMAD(vehicle.purchase_price)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">
                  {t('financial.maintenance', 'Maintenance')}
                </span>
                <span className="text-on-surface font-medium">
                  {formatMAD(vehicle.maintenance_total)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-on-surface-variant">
                  {t('financial.energy', 'Energie')}
                </span>
                <span className="text-on-surface font-medium">
                  {formatMAD(vehicle.energy_total)}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
