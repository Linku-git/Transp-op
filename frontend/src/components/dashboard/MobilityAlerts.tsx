import { useTranslation } from 'react-i18next';
import type { MobilityCoverage, ShadowZones } from '@/types/hr';

interface MobilityAlertsProps {
  coverage: MobilityCoverage;
  shadowZones: ShadowZones;
}

interface AlertItem {
  type: 'critical' | 'warning';
  icon: string;
  message: string;
}

export function MobilityAlerts({ coverage, shadowZones }: MobilityAlertsProps) {
  const { t } = useTranslation();

  const alerts: AlertItem[] = [];

  if (coverage.coverage_pct < 60) {
    alerts.push({
      type: 'critical',
      icon: 'error',
      message: t('hr.alert_low_coverage', 'Couverture mobilite critique: {{pct}}% (seuil: 60%)', {
        pct: coverage.coverage_pct.toFixed(1),
      }),
    });
  }

  if (shadowZones.shadow_zone_pct > 10) {
    alerts.push({
      type: 'warning',
      icon: 'warning',
      message: t('hr.alert_shadow_zones', 'Zones d\'ombre elevees: {{pct}}% des employes (seuil: 10%)', {
        pct: shadowZones.shadow_zone_pct.toFixed(1),
      }),
    });
  }

  if (alerts.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2" data-testid="mobility-alerts">
      {alerts.map((alert, index) => {
        const isCritical = alert.type === 'critical';
        const containerClass = isCritical
          ? 'bg-error-container/30 border-error/20 text-error'
          : 'bg-amber-50 border-amber-200 text-amber-700';

        return (
          <div
            key={index}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${containerClass}`}
            data-testid={`alert-${alert.type}`}
            role="alert"
          >
            <span className="material-symbols-outlined text-xl flex-shrink-0">
              {alert.icon}
            </span>
            <p className="font-sans text-sm font-medium">{alert.message}</p>
          </div>
        );
      })}
    </div>
  );
}
